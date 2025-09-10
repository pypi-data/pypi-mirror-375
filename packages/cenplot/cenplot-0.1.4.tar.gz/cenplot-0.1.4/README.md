# `CenPlot`
[![PyPI - Version](https://img.shields.io/pypi/v/cenplot)](https://pypi.org/project/cenplot/)
[![CI](https://github.com/logsdon-lab/cenplot/actions/workflows/main.yaml/badge.svg)](https://github.com/logsdon-lab/cenplot/actions/workflows/main.yaml)
[![docs](https://github.com/logsdon-lab/cenplot/actions/workflows/docs.yaml/badge.svg)](https://github.com/logsdon-lab/cenplot/actions/workflows/docs.yaml)

Library for producing centromere figures.

<table>
  <tr>
    <td>
      <figure float="left">
          <img align="middle" src="docs/example_cdr.png" width="100%">
          <figcaption>CDR plot.</figcaption>
      </figure>
      <figure float="left">
          <img align="middle" src="docs/example_split_hor.png" width="100%">
          <figcaption>HOR plot.</figcaption>
      </figure>
    </td>
    <td>
      <figure float="left">
          <img align="middle" src="docs/example_multiple.png" width="100%">
          <figcaption>Combined plot.</figcaption>
      </figure>
      <figure float="left">
          <img align="middle" src="docs/example_ident.png" width="100%">
          <figcaption>Identity plots.</figcaption>
      </figure>
    </td>
  </tr>
</table>

## Getting Started
Install the package from `pypi`.
```bash
pip install cenplot
```

## CLI
Generating a split HOR tracks using the `cenplot draw` command and an input layout.
```bash
# examples/example_cli.sh
cenplot draw \
-t examples/tracks_hor.toml \
-c "chm13_chr10:38568472-42561808" \
-p 4 \
-d plots \
-o "plot/merged_image.png"
```

## Python API
The same HOR track can be created with a few lines of code.
```python
# examples/example_api.py
from cenplot import plot_tracks, read_tracks

chrom = "chm13_chr10:38568472-42561808"
track_list, settings = read_tracks("examples/tracks_hor.toml", chrom=chrom)
fig, axes, _ = plot_tracks(track_list.tracks, settings)
```

## Development
Requires `Git LFS` to pull test files.
Create a `venv`, build `cenplot`, and install it. Also, generate the docs.
```bash
git lfs install && git lfs pull
make dev && make build && make install
pdoc ./cenplot -o docs/
```

## Documentation
Read the documentation [here](https://logsdon-lab.github.io/CenPlot/cenplot.html).
