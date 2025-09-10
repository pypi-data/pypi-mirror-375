import os
import logging
import numpy as np

from matplotlib.axes import Axes
from matplotlib.figure import Figure


from .settings import PlotSettings
from .hor import draw_hor, draw_hor_ort
from .label import draw_label
from .self_ident import draw_self_ident
from .strand import draw_strand
from .line import draw_line
from .bar import draw_bar
from .legend import draw_legend
from .local_self_ident import draw_local_self_ident
from .utils import create_subplots, format_ax, set_both_labels
from ..io.utils import get_min_max_track
from ..track.types import Track, TrackType, TrackPosition, LegendPosition


def plot_tracks(
    tracks: list[Track],
    settings: PlotSettings,
    outdir: str | None = None,
    chrom: str | None = None,
) -> tuple[Figure, np.ndarray, list[str]]:
    """
    Plot a single centromere figure from a list of `Track`s.

    # Args
    * `tracks`
        * List of tracks to plot. The order in the list determines placement on the figure.
    * `settings`
        * Settings for output plots.
    * `outdir`
        * Output directory.
        * If not provided, does not output files.
    * `chrom`
        * Chromosome label. Replaces {chrom} format string in title if provided and sets output filenames.
        * If not provided, defaults to "out".

    # Returns
    * Figure, its axes, and the output filename(s).

    # Usage
    ```python
    import cenplot

    chrom = "chm13_chr10:38568472-42561808"
    track_list, settings = cenplot.read_tracks("tracks_example_api.toml", chrom=chrom)
    fig, axes, _ = cenplot.plot_tracks(track_list.tracks, settings)
    ```
    """
    # Show chrom trimmed of spaces for logs and filenames.
    logging.info(f"Plotting {len(tracks)} tracks.")

    if not settings.xlim:
        # Get min and max position of all tracks for this cen.
        _, min_st_pos = get_min_max_track(tracks, typ="min")
        _, max_end_pos = get_min_max_track(tracks, typ="max", default_col="chrom_end")
    else:
        min_st_pos = settings.xlim[0]
        max_end_pos = settings.xlim[1]

    # # Scale height based on track length.
    # adj_height = height * (trk_max_end / max_end_pos)
    # height = height if adj_height == 0 else adj_height

    fig, axes, track_indices = create_subplots(
        tracks,
        settings,
    )
    if settings.legend_pos == LegendPosition.Left:
        track_col, legend_col = 1, 0
    else:
        track_col, legend_col = 0, 1

    track_labels: list[str] = []

    def get_track_label(
        chrom: str | None, track: Track, all_track_labels: list[str]
    ) -> str:
        if not track.title or not chrom:
            return ""
        try:
            fmt_track_label = track.title.format(chrom=chrom)
        except KeyError:
            fmt_track_label = track.title

        track_label = fmt_track_label.encode("ascii", "ignore").decode("unicode_escape")

        # Update track label for each overlap.
        if track.pos == TrackPosition.Overlap:
            try:
                track_label = f"{all_track_labels[-1]}\n{track_label}"
            except IndexError:
                pass

        return track_label

    num_hor_split = 0
    legend_tracks: list[tuple[Axes, Track]] = []
    for idx, track in enumerate(tracks):
        track_row = track_indices[idx]
        track_label = get_track_label(chrom, track, track_labels)
        # Store label if more overlaps.
        track_labels.append(track_label)

        try:
            track_ax: Axes = axes[track_row, track_col]
        except IndexError:
            print(f"Cannot get track ({track_row, track_col}) for {track}.")
            continue
        try:
            legend_ax: Axes | None = axes[track_row, legend_col]
        except IndexError:
            legend_ax = None

        # Set xaxis limits
        track_ax.set_xlim(min_st_pos, max_end_pos)

        # Set labels for both x and y axis.
        set_both_labels(track_label, track_ax, track)

        if legend_ax:
            # Make legend title invisible for HORs split after 1.
            if track.opt == TrackType.HORSplit:
                legend_ax_legend = legend_ax.get_legend()
                if legend_ax_legend and num_hor_split != 0:
                    legend_title = legend_ax_legend.get_title()
                    legend_title.set_alpha(0.0)
                num_hor_split += 1

            # Minimalize all legend cols except self-ident
            if track.opt != TrackType.SelfIdent or (
                track.opt == TrackType.SelfIdent and not track.options.legend
            ):
                format_ax(
                    legend_ax,
                    grid=True,
                    xticks=True,
                    xticklabel_fontsize=track.options.legend_fontsize,
                    yticks=True,
                    yticklabel_fontsize=track.options.legend_fontsize,
                    spines=("right", "left", "top", "bottom"),
                )
            else:
                format_ax(
                    legend_ax,
                    grid=True,
                    xticklabel_fontsize=track.options.legend_fontsize,
                    yticklabel_fontsize=track.options.legend_fontsize,
                    spines=("right", "top"),
                )

        if track.opt == TrackType.Legend:
            # Draw after everything else.
            legend_tracks.append((track_ax, track))
        elif track.opt == TrackType.Position:
            # Hide everything but x-axis
            format_ax(
                track_ax,
                grid=True,
                xticklabel_fontsize=track.options.legend_fontsize,
                yticks=True,
                yticklabel_fontsize=track.options.legend_fontsize,
                spines=("right", "left", "top"),
            )
        elif track.opt == TrackType.Spacer:
            # Hide everything.
            format_ax(
                track_ax,
                grid=True,
                xticks=True,
                yticks=True,
                spines=("right", "left", "top", "bottom"),
            )
        else:
            # Switch track option. {bar, label, ident, hor}
            # Add legend.
            if track.opt == TrackType.HOR or track.opt == TrackType.HORSplit:
                draw_fn = draw_hor
            elif track.opt == TrackType.HOROrt:
                draw_fn = draw_hor_ort
            elif track.opt == TrackType.Label:
                draw_fn = draw_label
            elif track.opt == TrackType.SelfIdent:
                draw_fn = draw_self_ident
            elif track.opt == TrackType.LocalSelfIdent:
                draw_fn = draw_local_self_ident
            elif track.opt == TrackType.Bar:
                draw_fn = draw_bar
            elif track.opt == TrackType.Line:
                draw_fn = draw_line
            elif track.opt == TrackType.Strand:
                draw_fn = draw_strand
            else:
                raise ValueError("Invalid TrackType. Unreachable.")

            draw_fn(
                ax=track_ax,
                legend_ax=legend_ax,
                track=track,
                zorder=idx,
            )

    # Draw after all elements added.
    for ax, track_legend in legend_tracks:
        draw_legend(ax, axes, track_legend, track_col)

    # Add title
    if settings.title:
        if chrom:
            title = settings.title.format(chrom=chrom)
        else:
            title = settings.title
        fig.suptitle(
            title,
            x=settings.title_x,
            y=settings.title_y,
            horizontalalignment=settings.title_horizontalalignment,
            fontsize=settings.title_fontsize,
        )
    # Pad between axes.
    fig.set_layout_engine(layout=settings.layout, h_pad=settings.axis_h_pad)

    outfiles = []

    if outdir:
        os.makedirs(outdir, exist_ok=True)
        if isinstance(settings.format, str):
            output_format = [settings.format]
        else:
            output_format = settings.format

        # PNG must always be plotted last.
        # Matplotlib modifies figure settings causing formatting errors in vectorized image formats (svg, pdf)
        png_output = "png" in output_format
        if png_output:
            output_format.remove("png")

        fname = chrom if chrom else "out"
        for fmt in output_format:
            outfile = os.path.join(outdir, f"{fname}.{fmt}")
            fig.savefig(outfile, dpi=settings.dpi, transparent=settings.transparent)
            outfiles.append(outfile)

        if png_output:
            outfile = os.path.join(outdir, f"{fname}.png")
            fig.savefig(
                outfile,
                dpi=settings.dpi,
                transparent=settings.transparent,
            )
            outfiles.append(outfile)

    return fig, axes, outfiles
