import os

import fire

from ds_plotting.cleanup import move_files
from ds_plotting.config import Config
from ds_plotting.parse import parse
from ds_plotting.plot import plot
from ds_plotting.read_crux_common import read_crux_common


def plot_fit(
    folder: str,
    crux_common: str | None = None,
    height: int = 200,
    width: int = 2000,
    zero: bool = False,
    reference_file: str | None = None,
    rolling_window: int | None = None,
    silent: bool = False,
    cleanup: bool = True,
    save_chart: bool = True,
):
    config = Config(
        folder=folder,
        crux_common=crux_common or read_crux_common(crux_common),
        height=height,
        width=width,
        zero=zero,
        reference_file=reference_file,
        rolling_window=rolling_window,
        silent=silent,
        cleanup=cleanup,
        save_chart=save_chart,
    )

    df = parse(config)
    chart = plot(df, config)
    if config.save_chart:
        chart.save(os.path.join(config.folder, "chart.html"))
    if config.cleanup:
        move_files(df, config)
    chart.show()


if __name__ == "__main__":
    fire.Fire(plot_fit)
