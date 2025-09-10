import altair as alt
import polars as pl

from ds_plotting.altair_config import AltairConfig
from ds_plotting.config import Config


def plot(df: pl.DataFrame, config: Config) -> alt.Chart:
    AltairConfig.setup()

    if not config.silent:
        print("\nIf you want to define a reference, use the flag")
        print("--reference_file=<filename>")
        print("Options are:")
        for file in df["file"].unique():
            print(f"""--reference_file="{file}" """)
    interval = alt.selection_interval(encodings=["x"])
    legend_sel = alt.selection_point(fields=["file"], bind="legend")

    def make_zoomable_chart(y, color_col="file", title: str | None = None):
        scaleargs = {"zero": config.zero}
        if title and "Error" in title:
            scaleargs["domainMid"] = 0

        base = alt.Chart(df).encode(
            x=alt.X("timestamp:T", title="Timestamp"),
            y=alt.Y(f"{y}:Q", title=title, scale=alt.Scale(**scaleargs)),
            color=alt.Color(f"{color_col}:N"),
            opacity=alt.condition(legend_sel, alt.value(1), alt.value(0.1)),
        )

        # TOP: focus (filtered by brush)
        chart = (
            base.transform_filter(interval)
            .transform_filter(legend_sel)
            .mark_line()
            .properties(
                width=config.width, height=config.height, title=config.folder
            )
        )

        # BOTTOM: overview with same brush
        view = (
            base.mark_line()
            .add_params(interval)
            .properties(width=config.width, height=60)
        )

        # Mean table over selected window
        table = (
            base.transform_filter(interval)
            .transform_filter(legend_sel)
            .mark_text(align="center", fontSize=30)
            .encode(
                x=alt.X("file:N", title=None, axis=alt.Axis(labelLimit=0)),
                text=alt.Text(f"mean({y}):Q", format=".2f"),
                y=alt.value(0),
            )
            .properties(width=config.width, height=30, title=f"Mean {y}")
        )

        return alt.vconcat(chart, view, table, spacing=10)

    charts = [
        make_zoomable_chart("pwr_watts", title="Power (Watts)"),
    ]
    if "pwr_watts_diff" in df.columns:
        charts.append(
            make_zoomable_chart("pwr_watts_diff", title="Power Error (Watts) ")
        )
    if "pwr_watts_diff_hyb" in df.columns:
        charts.append(
            make_zoomable_chart(
                "pwr_watts_diff_hyb", title="Hyb. Power Error (%) "
            )
        )
    charts.append(
        make_zoomable_chart("cad_rpm", title="Cadence (RPM)"),
    )
    charts.append(
        make_zoomable_chart("spd_mps", title="Speed (m/s)"),
    )

    chart = alt.vconcat(*charts, spacing=80).resolve_scale(
        y="independent", color="independent"
    )

    # Add sliders + interactions at the top level so they affect both charts
    return chart.add_params(legend_sel)
