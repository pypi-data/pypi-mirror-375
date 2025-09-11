# Hourglass Diffusion Transformers (HDiT)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.7%2B-green)](https://www.python.org/)
[![PyTorch Version](https://img.shields.io/badge/PyTorch-2.0%2B-orange)](https://pytorch.org/)

## Overview
This repository provides a **​​non-official​**​ implementation of the ​​Hourglass Diffusion Transformer (HDiT)​​ model, as proposed in the paper "Scalable High-Resolution Pixel-Space Image Synthesis with Hourglass Diffusion Transformers" by Crowson et al. (ICML 2024).

The original work introduces a diffusion-based transformer architecture capable of generating high-resolution images directly in pixel space, with computational cost scaling linearly with respect to resolution. This package extracts the main HDiT part from the original repository ([k-diffusion](https://github.com/crowsonkb/k-diffusion)).

### Key Features:
* **Scalable**: Supports high-resolution image synthesis.
* **Efficient**: Achieves significantly lower computational cost compared to the traditional Diffusion Transformer (DiT).

## Installation
Install the package using pip:
```bash
pip install hdit
```

## Usage
### Example Code:
Initialize the model backbone and use it in the diffusion model.
```python
from hdit import HDiT

model = HDiT(
   in_channels=3,
   out_channels=3,
   patch_size=[4, 4],
   widths=[128, 256],
   middle_width=512,
   depths=[2, 2],
   middle_depth=4,
   mapping_width=256,
   mapping_depth=2
)
```

## Citation
Please cite the original paper. For more details, visit the official​​ [arXiv page](https://arxiv.org/abs/2401.11605).
```bibtex
@InProceedings{crowson2024hourglass,
    title = {Scalable High-Resolution Pixel-Space Image Synthesis with Hourglass Diffusion Transformers},
    author = {Crowson, Katherine and Baumann, Stefan Andreas and Birch, Alex and Abraham, Tanishq Mathew and Kaplan, Daniel Z and Shippole, Enrico},
    booktitle = {Proceedings of the 41st International Conference on Machine Learning},
    pages = {9550--9575},
    year = {2024},
    editor = {Salakhutdinov, Ruslan and Kolter, Zico and Heller, Katherine and Weller, Adrian and Oliver, Nuria and Scarlett, Jonathan and Berkenkamp, Felix},
    volume = {235},
    series = {Proceedings of Machine Learning Research},
    month = {21--27 Jul},
    publisher = {PMLR},
    pdf = {https://raw.githubusercontent.com/mlresearch/v235/main/assets/crowson24a/crowson24a.pdf},
    url = {https://proceedings.mlr.press/v235/crowson24a.html},
    abstract = {We present the Hourglass Diffusion Transformer (HDiT), an image-generative model that exhibits linear scaling with pixel count, supporting training at high resolution (e.g. $1024 \times 1024$) directly in pixel-space. Building on the Transformer architecture, which is known to scale to billions of parameters, it bridges the gap between the efficiency of convolutional U-Nets and the scalability of Transformers. HDiT trains successfully without typical high-resolution training techniques such as multiscale architectures, latent autoencoders or self-conditioning. We demonstrate that HDiT performs competitively with existing models on ImageNet $256^2$, and sets a new state-of-the-art for diffusion models on FFHQ-$1024^2$. Code is available at https://github.com/crowsonkb/k-diffusion.}
}
```
