# surfsci

`surfsci` is a set of scripts for handling and maniplulating surface science x-ray data.

[![PyPI - Version](https://img.shields.io/pypi/v/surfsci.svg)](https://pypi.org/project/surfsci)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/surfsci.svg)](https://pypi.org/project/surfsci)

-----

## Table of Contents

- [Installation](#installation)
- [X-ray](#x-ray)
- [License](#license)

## Installation

```console
pip install surfsci
```

## X-ray Photoelectron Spectroscopy

This is just a convenience wrapper around [xps](https://pypi.org/project/xps/)

```python
from surfsci import xps
```

## X-ray

### X-ray Diffratometer 500 / 5000

Conversion script for _asc_ to _xy_ format. Handy if you want easily parsable data or want to use [fityk](https://fityk.nieto.pl/).

```sh
surfsci-xy-conv my_xrd_data.asc
```

This will generate _my_xrd_data.xy_

### MAX3D G-Pol 2D X-ray data

Plot and x-y data for the _*.gpol_ files produced by the [MAX3D detector at McMaster](https://max3d.mcmaster.ca/doc/index.html). Usage,

```sh
surfsci-gpol my_data_file.gpol
```

## License

`surfsci` is distributed under the terms of the [BSD-2-Clause](https://spdx.org/licenses/BSD-2-Clause.html) license.
