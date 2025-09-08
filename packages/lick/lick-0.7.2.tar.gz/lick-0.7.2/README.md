# lick
[![PyPI](https://img.shields.io/pypi/v/lick.svg?logo=pypi&logoColor=white&label=PyPI)](https://pypi.org/project/lick/)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/la-niche/lick/main.svg)](https://results.pre-commit.ci/latest/github/la-niche/lick/main)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/charliermarsh/ruff)


Line Integral Convolution Knit : clothe a 2D field (ex: density field) with a LIC texture,
given two vector fields (ex: velocity (vx, vy)).

This package builds on top of [rLIC](https://pypi.org/project/rlic), adding
post-processing and visualization functionalities.

Authors: Gaylor Wafflard-Fernandez, Clément Robert

Author-email: gaylor.wafflard@univ-grenoble-alpes.fr

<p align="center">
    <img src="https://raw.githubusercontent.com/la-niche/lick/main/imgs/lick.png" width="600"></a>
</p>

## Installation

Install with `pip`

```
pip install lick
```

To import lick:

```python
import lick as lk
```

The important functions are `lick_box` and `lick_box_plot`. While `lick_box` interpolates the data and perform a line integral convolution, `lick_box_plot` directly plots the final image. Use `lick_box` if you want to have more control of the plots you want to do with the lic. Use `lick_box_plot` if you want to take advantage of the fine-tuning of the pcolormesh parameters.

## Example

```python
import numpy as np
import matplotlib.pyplot as plt
from lick import lick_box_plot

fig, ax = plt.subplots()
x = np.geomspace(0.1, 10, 128)
y = np.geomspace(0.1, 5, 128)
a, b = np.meshgrid(x, y)
v1 = np.cos(a)
v2 = np.sin(b)
field = v1 ** 2 + v2 ** 2
lick_box_plot(
    fig,
    ax,
    x,
    y,
    v1,
    v2,
    field,
    size_interpolated=256,
    xmin=1,
    xmax=9,
    ymin=1,
    ymax=4,
    niter_lic=5,
    kernel_length=64,
    cmap="inferno",
    stream_density=0.5
)
plt.show()
```
