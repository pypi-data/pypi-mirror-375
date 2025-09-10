import sys
import gzip
import logging
import numpy as np
import polars as pl

from typing import Any, TextIO
from matplotlib.colors import ListedColormap, rgb2hex

from ..track.types import NO_DATA_TRACK_OPTS, Track, TrackType


def map_value_colors(
    df: pl.DataFrame,
    map_col: str | None = None,
    map_values: dict[Any, Any] | None = None,
    use_item_rgb: bool = False,
) -> pl.DataFrame:
    def rgb_to_hex(srs: pl.Series) -> pl.Series:
        color_hex = []
        for elem in srs:
            if elem.startswith("#"):
                color_hex.append(elem)
            else:
                rgb = tuple(int(e) / 255 for e in elem.split(","))
                assert len(rgb) == 3, f"Invalid item_rgb format for {rgb}"
                color_hex.append(rgb2hex(rgb))
        return pl.Series(name="color", values=color_hex)

    if "item_rgb" in df.columns and use_item_rgb:
        # Convert colors from rgb str -> rgb tuple -> hex
        df = df.with_columns(color=rgb_to_hex(df["item_rgb"]))
    elif map_col:
        if map_values:
            val_color_mapping = map_values
        else:
            unique_vals = df[map_col].unique(maintain_order=True)
            # Generate random number of colors.
            colors = np.random.rand(len(unique_vals), 3)
            cmap = ListedColormap(colors)
            val_color_mapping = {
                val: rgb2hex(color)
                for val, color in zip(
                    unique_vals, cmap(np.linspace(0, 1, len(unique_vals)))
                )
            }
        df = df.with_columns(
            color=pl.col(map_col)
            .cast(pl.String)
            # If not in mapping, set to gray.
            .replace(val_color_mapping, default="#808080")
        )

    return df


def adj_by_ctg_coords(df: pl.DataFrame, colname: str) -> pl.DataFrame:
    return df.with_columns(
        chrom_name=pl.col(colname).str.extract(r"(chr[\dXY]+)").fill_null(""),
        # Use simplified coordinates if possible, otherwise, take everything.
        ctg_st=pl.col(colname).str.extract(r":(\d+)-").cast(pl.Int64).fill_null(0),
    ).with_columns(
        **{
            f"{colname}_st": pl.col(f"{colname}_st") - pl.col("ctg_st"),
            f"{colname}_end": pl.col(f"{colname}_end") - pl.col("ctg_st"),
        }
    )


def no_data_log_message(i: int, title: str | None, col: str):
    logging.error(
        f"No data for track {i} ({title=}). "
        f"Check that data is in absolute coordinates and/or is in the correct column ({col}). "
        "Skipping..."
    )


def get_min_max_track(
    tracks: list[Track], typ: str, default_col: str = "chrom_st"
) -> tuple[Track, int]:
    track = None
    if typ == "min":
        pos: int | float = sys.maxsize
    else:
        pos = 0

    for i, trk in enumerate(tracks):
        if trk.opt == TrackType.SelfIdent:
            col = "x"
        # Skip tracks which carry no data.
        elif trk.opt in NO_DATA_TRACK_OPTS:
            continue
        else:
            col = default_col
        if typ == "min":
            trk_data = trk.data.filter(pl.col(col) >= 0)
            if trk_data.is_empty():
                no_data_log_message(i, trk.title, col)
                continue
            trk_min = trk_data[col].min()
            assert isinstance(trk_min, (float, int))
            assert not isinstance(trk_min, bool)
            if trk_min < pos:
                track = trk
                pos = trk_min
        else:
            if trk.data.is_empty():
                no_data_log_message(i, trk.title, col)
                continue
            trk_max = trk.data[col].max()
            assert isinstance(trk_max, (float, int))
            assert not isinstance(trk_max, bool)
            if not trk_max:
                logging.error(f"No max value for track {i} ({trk.title=}).")
                continue
            if trk_max > pos:
                track = trk
                pos = trk_max
    if not track:
        raise ValueError(
            f"No {typ} track. Check that bedfile is not empty, contains the correct chrom, and/or has correct columns."
        )
    return track, int(pos)


def header_info(infile: str | TextIO) -> tuple[int, int]:
    """
    Get header info.

    # Returns
    1. Skip [0|1] rows for header.
    2. Number of elems.
    """
    fname = infile if isinstance(infile, str) else infile.name
    with gzip.open(fname, "rt") if fname.endswith(".gz") else open(fname, "rt") as fh:
        try:
            header = next(fh)
        except StopIteration:
            return 0, 0

    skip_rows = 1
    header_elems = header.split("\t")
    for elem in header_elems:
        try:
            # Has numeric column. Is not header.
            _ = int(elem)
            return 0, len(header_elems)
        except ValueError:
            pass

    return skip_rows, len(header_elems)
