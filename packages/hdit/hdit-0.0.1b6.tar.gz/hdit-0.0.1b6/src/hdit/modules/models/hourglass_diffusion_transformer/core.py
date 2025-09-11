from typing import overload, Optional, Callable, Dict, Sequence, Tuple, Any, List
from functools import reduce
from typing import Union
from einops import rearrange
import numpy as np
import torch
from torch import nn
import torch._dynamo
from ....utils.args_context import ArgsContext
from ... import flags
from . import layers
from ...attention.axial_rope import make_axial_pos
from ...supplies import apply_wd, zero_init, RMSNorm, LinearGEGLU, Linear, TokenMerge, TokenSplit, TokenSplitWithoutSkip, Identity
from ...things import default_block_builders


if flags.get_use_compile():
    torch._dynamo.config.cache_size_limit = max(64, torch._dynamo.config.cache_size_limit)
    torch._dynamo.config.suppress_errors = True


# Helpers
def downscale_pos(pos):
    pos = rearrange(pos, "... (h nh) (w nw) e -> ... h w (nh nw) e", nh=2, nw=2)
    return torch.mean(pos, dim=-2)


def filter_params(function, module):
    for param in module.parameters():
        tags = getattr(param, "_tags", set())
        if function(tags):
            yield param


# Rotary position embeddings
@flags.compile_wrap
def apply_rotary_emb(x, theta, conj=False):
    out_dtype = x.dtype
    dtype = reduce(torch.promote_types, (x.dtype, theta.dtype, torch.float32))
    d = theta.shape[-1]
    assert d * 2 <= x.shape[-1]
    x1, x2, x3 = x[..., :d], x[..., d : d * 2], x[..., d * 2 :]
    x1, x2, theta = x1.to(dtype), x2.to(dtype), theta.to(dtype)
    cos, sin = torch.cos(theta), torch.sin(theta)
    sin = -sin if conj else sin
    y1 = x1 * cos - x2 * sin
    y2 = x2 * cos + x1 * sin
    y1, y2 = y1.to(out_dtype), y2.to(out_dtype)
    return torch.cat((y1, y2, x3), dim=-1)


class Level(nn.ModuleList):
    def forward(self, x, *args, **kwargs):
        for layer in self:
            x = layer(x, *args, **kwargs)
        return x


# Mapping network
class MappingFeedForwardBlock(nn.Module):
    def __init__(self, d_model, d_ff, dropout=0.0):
        super().__init__()
        self.norm = RMSNorm(d_model)
        self.up_proj = apply_wd(LinearGEGLU(d_model, d_ff, bias=False))
        self.dropout = nn.Dropout(dropout)
        self.down_proj = apply_wd(zero_init(Linear(d_ff, d_model, bias=False)))

    def forward(self, x):
        skip = x
        x = self.norm(x)
        x = self.up_proj(x)
        x = self.dropout(x)
        x = self.down_proj(x)
        return x + skip


class MappingNetwork(nn.Module):
    def __init__(self, n_layers, d_model, d_ff, dropout=0.0):
        super().__init__()
        self.in_norm = RMSNorm(d_model)
        self.blocks = nn.ModuleList([MappingFeedForwardBlock(d_model, d_ff, dropout=dropout) for _ in range(n_layers)])
        self.out_norm = RMSNorm(d_model)

    def forward(self, x):
        x = self.in_norm(x)
        for block in self.blocks:
            x = block(x)
        x = self.out_norm(x)
        return x


def _make_list(input):
    if input is None:
        input = []
    elif not isinstance(input, Sequence):
        input = [input]
    return input


def _make_dims(input_dims, list):
    if input_dims is None or not isinstance(input_dims, Sequence):
        input_dims = [input_dims for _ in range(len(list))]
    else:
        input_dims += [None for _ in range(len(list) - len(input_dims))]
    return input_dims


def _pop_first_residual(residuals):
    first_item = residuals[0]
    if len(residuals) > 1:
        other_items = residuals[1:]
    else:
        other_items = residuals[0:0]
    return first_item, other_items


class HourglassVisionTransformer(nn.Module):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        patch_size: int = [4, 4],
        widths: Sequence[int] = [128, 256],
        middle_width: int = 512,
        depths: Sequence[int] = [2, 2],
        middle_depth: int = 4,
        block_builders: Dict[int, Callable[[ArgsContext], nn.Module]] = default_block_builders,
        mapping_width: Optional[int] = None,
        mapping_depth: Optional[int] = None,
        mapping_feed_forward_dim: Optional[int] = None,
        mapping_dropout: Optional[float] = None,
        guidance_modules: Union[nn.Module, Sequence[nn.Module], None] = None,
        guidance_dims: Union[int, Sequence[Optional[int]], None] = None,
        is_global_condition_module_prior: bool = True,
        global_condition_initialization_modules: Union[nn.Module, Sequence[nn.Module], None] = None,
        global_condition_guidance_modules: Union[nn.Module, Sequence[nn.Module], None] = None,
        global_condition_guidance_dims: Union[int, Sequence[Optional[int]], None] = None
    ):
        super().__init__()
        
        self.block_builders = block_builders

        self.patch_in = TokenMerge(in_channels, widths[0], patch_size)
        
        global_condition_initialization_modules = _make_list(global_condition_initialization_modules)
        global_condition_guidance_modules = _make_list(global_condition_guidance_modules)
        global_condition_guidance_dims = _make_dims(global_condition_guidance_dims, global_condition_guidance_modules)
        self.global_condition_initialization_modules = nn.ModuleList(global_condition_initialization_modules)
        self.global_condition_guidance_modules = nn.ModuleList(global_condition_guidance_modules)
        self.global_condition_guidance_module_projections = nn.ModuleList([
            Linear(mapping_width if layer_cond_guidance_dim is None else layer_cond_guidance_dim, mapping_width, bias=False) for layer_cond_guidance_dim in global_condition_guidance_dims
        ])

        guidance_modules = _make_list(guidance_modules)
        guidance_dims = _make_dims(guidance_dims, guidance_modules)
        self.guidance_modules = nn.ModuleList(guidance_modules)
        self.guidance_modules_projections = nn.ModuleList([
            Linear(mapping_width if guidance_dim is None else guidance_dim, mapping_width, bias=False) for guidance_dim in guidance_dims
        ])
        
        self.is_global_condition_module_prior = is_global_condition_module_prior
        
        self.mapping_width = mapping_width
        if mapping_feed_forward_dim is None and mapping_width is not None:
            mapping_feed_forward_dim = mapping_width * 3
        if all(value is not None for value in (mapping_depth, mapping_width, mapping_feed_forward_dim, mapping_dropout)):
            self.mapping = MappingNetwork(mapping_depth, mapping_width, mapping_feed_forward_dim, dropout=mapping_dropout)

        self.down_levels, self.up_levels = nn.ModuleList(), nn.ModuleList()
        num_half_levels = len(widths)
        self.num_total_levels = 2 * num_half_levels + 1
        for i, (width, depth) in enumerate(zip(widths, depths)):
            self.down_levels.append(Level([self.build_block(width, j, i) for j in range(depth)]))
            self.up_levels.append(Level([self.build_block(width, j + depth, self.num_total_levels - 1 - i) for j in range(depth)]))
        self.middle_level = Level([self.build_block(middle_width, j, num_half_levels) for j in range(middle_depth)])
        
        no_middle_widths = widths
        no_first_widths = np.concatenate((widths[1:], [middle_width]))

        self.merges = nn.ModuleList([TokenMerge(width_1, width_2) for width_1, width_2 in zip(no_middle_widths, no_first_widths)])
        self.splits = nn.ModuleList([TokenSplit(width_2, width_1) for width_1, width_2 in zip(no_middle_widths, no_first_widths)])

        self.out_norm = RMSNorm(widths[0])
        self.patch_out = TokenSplitWithoutSkip(widths[0], out_channels, patch_size)
        nn.init.zeros_(self.patch_out.proj.weight)
        
        del self.block_builders
    
    def build_block(self, width: int, block_index: int, level_index: int) -> nn.Module:
        args_context = ArgsContext(
            width=width,
            mapping_width=self.mapping_width,
            block_index=block_index,
            level_index=level_index
        )
        if level_index in self.block_builders.keys():
            return self.block_builders[level_index](args_context)
        else:
            return Identity()
    
    def initialize_block_mapping_arguments(self, *args) -> Tuple[Optional[torch.Tensor], Tuple[Any, ...]]:
        return None, args

    def block_parameters(self, block_mapping = None, *args) -> Tuple[Optional[torch.Tensor], List[torch.Tensor]]:
        global_condition_args_length = len(args) - len(self.guidance_modules)
        
        def generate_guidance_projections():
            length_guidance_modules_projections = len(self.guidance_modules_projections)
            for i, guidance_module in enumerate(self.guidance_modules):
                guidance_emb = guidance_module(args[global_condition_args_length + i])
                if i < length_guidance_modules_projections:
                    yield self.guidance_modules_projections[i](guidance_emb)
                else:
                    break
        guidance_projections_block_mapping = sum(generate_guidance_projections())
        
        global_condition_args = list(args[:global_condition_args_length])
        global_condition_initialized = [init_module(global_condition_args[i]) for i, init_module in enumerate(self.global_condition_initialization_modules)]
        global_condition_initialized = global_condition_initialized + global_condition_args[len(global_condition_initialized):]
        if self.is_global_condition_module_prior:
            post_block_mapping = guidance_projections_block_mapping
        else:
            def generate_global_condition_guidance_projections():
                length_global_condition_guidance_module_projections = len(self.global_condition_guidance_module_projections)
                for i, global_condition_guidance_module in enumerate(self.global_condition_guidance_modules):
                    global_condition_guidance_emb = global_condition_guidance_module(global_condition_initialized[i])
                    if i < length_global_condition_guidance_module_projections:
                        yield self.global_condition_guidance_module_projections[i](global_condition_guidance_emb)
                    else:
                        break
            global_condition_guidance_projections = sum(generate_global_condition_guidance_projections())
            
            post_block_mapping = guidance_projections_block_mapping + global_condition_guidance_projections
        if isinstance(post_block_mapping, torch.Tensor):
            if block_mapping is None:
                block_mapping = post_block_mapping
            else:
                block_mapping = block_mapping + post_block_mapping
        return block_mapping, global_condition_initialized
    
    def add_residual(self, input, residual: Optional[torch.Tensor]) -> torch.Tensor:
        if residual is None:
            return input
        else:
            return input + residual.to(input.dtype)
    
    def prepare_shallow_residuals(self, shallow_residuals: Optional[Sequence[torch.Tensor]]) -> List[torch.Tensor]:
        all_levels_length = self.num_total_levels
        shallow_residuals_list = shallow_residuals
        shallow_residuals = np.empty(all_levels_length, dtype=object)
        if shallow_residuals_list is not None:
            shallow_residuals_list = np.fromiter(shallow_residuals_list, dtype=object)
            shallow_residuals_length = len(shallow_residuals_list)
            if shallow_residuals_length < all_levels_length:
                shallow_residuals[:shallow_residuals_length] = shallow_residuals_list
            else:
                shallow_residuals[:] = shallow_residuals_list[:shallow_residuals_length]
        return shallow_residuals
    
    def split_shallow_residuals(self, shallow_residuals) -> Tuple[List[torch.Tensor], List[torch.Tensor], List[torch.Tensor]]:
        num_half_levels = len(self.down_levels)
        return shallow_residuals[:num_half_levels], shallow_residuals[num_half_levels:-num_half_levels], shallow_residuals[-num_half_levels:]
    
    def split_deep_residuals(self, deep_residuals) -> Tuple[Optional[List[torch.Tensor]], Optional[List[torch.Tensor]]]:
        num_half_levels = len(self.down_levels)
        if isinstance(deep_residuals, Sequence):
            if len(deep_residuals) > num_half_levels:
                return deep_residuals[num_half_levels:], deep_residuals[:num_half_levels]
            else:
                return None, deep_residuals
        else:
            return None, None
    
    def patch_positionally(self, input: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        # Patching
        input = input.movedim(-3, -1)
        input = self.patch_in(input)
        # TODO: pixel aspect ratio for nonsquare patches
        pos = make_axial_pos(input.shape[-3], input.shape[-2], device=input.device).view(input.shape[-3], input.shape[-2], 2)
        return input, pos
    
    def make_block_mapping(self, block_mapping = None, *args) -> Tuple[Optional[torch.Tensor], List[torch.Tensor]]:
        # Mapping Network
        block_mapping, layer_cond = self.block_parameters(block_mapping, *args)
        if block_mapping is not None:
            block_mapping = self.mapping(block_mapping)
        return block_mapping, layer_cond
    
    def down_sample(self, input, shallow_residuals, position, block_mapping, global_condition) -> Tuple[torch.Tensor, torch.Tensor, List[torch.Tensor], List[torch.Tensor]]:
        skips, positions = [], []
        for down_level, merge in zip(self.down_levels, self.merges):
            first_item, shallow_residuals = _pop_first_residual(shallow_residuals)
            input = self.add_residual(down_level(input, position, block_mapping, *global_condition), first_item)
            skips.append(input)
            positions.append(position)
            input = merge(input)
            position = downscale_pos(position)
        return input, position, skips, positions
    
    def middle_sample(self, input, shallow_residuals, position, block_mapping, global_condition) -> torch.Tensor:
        first_item, shallow_residuals = _pop_first_residual(shallow_residuals)
        input = self.add_residual(self.middle_level(input, position, block_mapping, *global_condition), first_item)
        return input
    
    def middle_skip_connect(self, input, deep_residuals) -> torch.Tensor:
        if isinstance(deep_residuals, Sequence):
            skip_item = deep_residuals.pop()
            input = self.add_residual(input, skip_item)
        return input
    
    def up_sample(self, input, shallow_residuals, skips, positions, block_mapping, global_condition, *, deep_residuals) -> torch.Tensor:
        if isinstance(deep_residuals, Sequence):
            def split_skip(split, input, skip):
                skip_item = deep_residuals.pop()
                return split(input, skip + skip_item)
        else:
            def split_skip(split, input, skip):
                return split(input, skip)
                
        for up_level, split, skip, position in reversed(list(zip(self.up_levels, self.splits, skips, positions))):
            first_item, shallow_residuals = _pop_first_residual(shallow_residuals)
            input = split_skip(split, input, skip)
            input = self.add_residual(up_level(input, position, block_mapping, *global_condition), first_item)
        return input
    
    def unpatch(self, input: torch.Tensor) -> torch.Tensor:
        # Unpatching
        input = self.out_norm(input)
        input = self.patch_out(input)
        input = input.movedim(-1, -3)
        return input

    @overload
    def forward(self, input, guidance, *args, shallow_residuals: Optional[Sequence[Optional[torch.Tensor]]] = None, deep_residuals: Optional[Sequence[Optional[torch.Tensor]]] = None) -> torch.Tensor:
        ...
    
    @overload
    def forward(self, input, global_condition, guidance, *args, shallow_residuals: Optional[Sequence[Optional[torch.Tensor]]] = None, deep_residuals: Optional[Sequence[Optional[torch.Tensor]]] = None) -> torch.Tensor:
        ...

    @overload
    def forward(self, input, local_condition, guidance, *args, shallow_residuals: Optional[Sequence[Optional[torch.Tensor]]] = None, deep_residuals: Optional[Sequence[Optional[torch.Tensor]]] = None) -> torch.Tensor:
        ...
    
    @overload
    def forward(self, input, local_condition, global_condition, guidance, *args, shallow_residuals: Optional[Sequence[Optional[torch.Tensor]]] = None, deep_residuals: Optional[Sequence[Optional[torch.Tensor]]] = None) -> torch.Tensor:
        ...

    def forward(self, input: torch.Tensor, *args, shallow_residuals: Optional[Sequence[Optional[torch.Tensor]]] = None, deep_residuals: Optional[Sequence[Optional[torch.Tensor]]] = None) -> torch.Tensor:
        shallow_residuals = self.prepare_shallow_residuals(shallow_residuals)
        down_shallow_residuals, middle_shallow_residuals, up_shallow_residuals = self.split_shallow_residuals(shallow_residuals)
        middle_deep_residuals, up_deep_residuals = self.split_deep_residuals(deep_residuals)
        
        input, position = self.patch_positionally(input)
        
        block_mapping, args = self.initialize_block_mapping_arguments(*args)
        block_mapping, global_condition = self.make_block_mapping(block_mapping, *args)

        # Hourglass Transformer
        input, position, skips, positions = self.down_sample(input, down_shallow_residuals, position, block_mapping, global_condition)
        input = self.middle_sample(input, middle_shallow_residuals, position, block_mapping, global_condition)
        input = self.middle_skip_connect(input, middle_deep_residuals)
        input = self.up_sample(input, up_shallow_residuals, skips, positions, block_mapping, global_condition, deep_residuals=up_deep_residuals)

        input = self.unpatch(input)
        return input


class HourglassDiffusionTransformer(HourglassVisionTransformer):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        condition_channels: Optional[int] = None,
        patch_size: int = [4, 4],
        widths: Sequence[int] = [128, 256], # [384, 768]
        middle_width: int = 512, # 1536
        depths: Sequence[int] = [2, 2],
        middle_depth: int = 4, # 16
        block_builders: Dict[int, Callable[[ArgsContext], nn.Module]] = default_block_builders,
        mapping_width: int = 256, # 768
        mapping_depth: int = 2,
        mapping_feed_forward_dim: Optional[int] = None,
        mapping_dropout: float = 0.,
        guidance_modules: Union[nn.Module, Sequence[nn.Module], None] = None,
        guidance_dims: Union[int, Sequence[Optional[int]], None] = None,
        is_global_condition_module_prior: bool = True,
        global_condition_initialization_modules: Union[nn.Module, Sequence[nn.Module], None] = None,
        global_condition_guidance_modules: Union[nn.Module, Sequence[nn.Module], None] = None,
        global_condition_guidance_dims: Union[int, Sequence[Optional[int]], None] = None
    ):
        if condition_channels is None:
            condition_channels = 0
        
        super().__init__(
            in_channels + condition_channels,
            out_channels,
            patch_size,
            widths,
            middle_width,
            depths,
            middle_depth,
            block_builders,
            mapping_width,
            mapping_depth,
            mapping_feed_forward_dim,
            mapping_dropout,
            guidance_modules,
            guidance_dims,
            is_global_condition_module_prior,
            global_condition_initialization_modules,
            global_condition_guidance_modules,
            global_condition_guidance_dims
        )
        
        self.condition_channels = condition_channels

        self.time_embedding = layers.FourierFeatures(1, mapping_width)
        self.time_projection = Linear(mapping_width, mapping_width, bias=False)
    
    def initialize_block_mapping_arguments(self, timestep, *args):
        # Timestep embedding
        time_embedded = self.time_embedding(timestep.view(-1, 1))
        block_mapping = self.time_projection(time_embedded)
        return block_mapping, args
    
    def concatenate_condition_channels(self, input: torch.Tensor, *args):
        if self.condition_channels > 0:
            input = torch.cat([input, args[0]], dim=1)
            args = args[1:]
        return input, args

    @overload
    def forward(self, input, timestep, guidance, *args, shallow_residuals: Optional[Sequence[Optional[torch.Tensor]]] = None, deep_residuals: Optional[Sequence[Optional[torch.Tensor]]] = None):
        ...
    
    @overload
    def forward(self, input, timestep, global_condition, guidance, *args, shallow_residuals: Optional[Sequence[Optional[torch.Tensor]]] = None, deep_residuals: Optional[Sequence[Optional[torch.Tensor]]] = None):
        ...

    @overload
    def forward(self, input, timestep, local_condition, guidance, *args, shallow_residuals: Optional[Sequence[Optional[torch.Tensor]]] = None, deep_residuals: Optional[Sequence[Optional[torch.Tensor]]] = None):
        ...
    
    @overload
    def forward(self, input, timestep, local_condition, global_condition, guidance, *args, shallow_residuals: Optional[Sequence[Optional[torch.Tensor]]] = None, deep_residuals: Optional[Sequence[Optional[torch.Tensor]]] = None):
        ...

    def forward(self, input: torch.Tensor, timestep, *args, shallow_residuals: Optional[Sequence[Optional[torch.Tensor]]] = None, deep_residuals: Optional[Sequence[Optional[torch.Tensor]]] = None):
        input, args = self.concatenate_condition_channels(input, *args)
        return super().forward(input, timestep, *args, shallow_residuals=shallow_residuals, deep_residuals=deep_residuals)