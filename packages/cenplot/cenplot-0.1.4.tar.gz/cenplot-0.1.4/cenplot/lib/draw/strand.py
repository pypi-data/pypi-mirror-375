from matplotlib.axes import Axes
from matplotlib.patches import FancyArrowPatch
from cenplot.lib.draw.utils import draw_uniq_entry_legend, format_ax
from cenplot.lib.track.types import Track, TrackPosition


def draw_strand(
    ax: Axes,
    track: Track,
    *,
    zorder: float = 1.0,
    legend_ax: Axes | None = None,
):
    """
    Draw strand plot on axis with the given `Track`.
    """
    hide_x = track.options.hide_x
    fwd_color = (
        track.options.fwd_color if track.options.fwd_color else track.options.DEF_COLOR
    )
    rev_color = (
        track.options.rev_color if track.options.rev_color else track.options.DEF_COLOR
    )
    scale = track.options.scale
    legend = track.options.legend

    if track.pos != TrackPosition.Overlap:
        spines = (
            ("right", "left", "top", "bottom") if hide_x else ("right", "left", "top")
        )
    else:
        spines = None

    format_ax(
        ax,
        xticks=hide_x,
        xticklabel_fontsize=track.options.fontsize,
        yticks=True,
        yticklabel_fontsize=track.options.fontsize,
        spines=spines,
    )

    ylim = ax.get_ylim()
    height = ylim[1] - ylim[0]

    for row in track.data.iter_rows(named=True):
        # sample arrow
        start = row["chrom_st"]
        end = row["chrom_end"]
        strand = row["strand"]
        if strand == "-":
            tmp_start = start
            start = end
            end = tmp_start
            color = rev_color
        else:
            color = fwd_color

        if track.options.use_item_rgb:
            color = row["color"]

        arrow = FancyArrowPatch(
            (start, height * 0.5),
            (end, height * 0.5),
            mutation_scale=scale,
            color=color,
            clip_on=False,
            zorder=zorder,
            label=row["name"],
        )
        ax.add_patch(arrow)

    if legend_ax and legend:
        draw_uniq_entry_legend(
            legend_ax,
            track,
            ref_ax=ax,
            ncols=track.options.legend_ncols,
            loc="center",
        )
