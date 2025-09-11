# SatViz

SatSim source code was developed under contract with AFRL/RDSM, and is approved for public release under Public Affairs release approval #AFRL-2022-1116.

The SatSimJS widget for Jupyter and Marimo.

![SatViz](https://raw.githubusercontent.com/ssc-ai/satviz/main/image.png)

## Installation

```sh
pip install satviz
```

or with [uv](https://github.com/astral-sh/uv):

```sh
uv add satviz
```

## Usage

Jupyter

```python
from satviz import SatSimJS
w = SatSimJS(height_px=1000)
w
```

## Release

To build and publish a release to PyPI:

1. Bump `version` in `pyproject.toml`.
2. Build and validate locally:

   ```sh
   python -m pip install --upgrade build twine
   python -m build
   twine check dist/*
   ```

3. Publish:

   - Manual: `twine upload dist/*` (requires a `__token__` PyPI API token)
   - CI: push a tag like `v0.1.0` to trigger GitHub Actions. Configure the
     `PYPI_API_TOKEN` repository secret with your PyPI token.

Marimo

```python
import marimo as mo
from satviz import SatSimJS

widget = SatSimJS(height_px=900)
w = mo.ui.anywidget(widget)
w
```
