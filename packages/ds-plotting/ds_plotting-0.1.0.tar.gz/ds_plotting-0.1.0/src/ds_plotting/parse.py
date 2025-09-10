import glob
import logging
import os

import polars as pl
import pycrux

from ds_plotting.config import Config


def parse(config: Config) -> pl.DataFrame:
    _df_list: list[pl.DataFrame] = []
    crux = pycrux.Crux(config.crux_common)

    files = (
        glob.glob(os.path.join(config.folder, "*.fit"))
        + glob.glob(os.path.join(config.folder, "*.FIT"))
        + glob.glob(os.path.join(config.folder, "*.Fit"))
    )
    for file in files:
        try:
            _df = (
                pl.DataFrame(crux.read_fit(file))
                .with_columns(
                    file=pl.lit(os.path.basename(file)),
                    folder=pl.lit(config.folder),
                )
                .select(
                    "timestamp",
                    "file",
                    "folder",
                    "cad_rpm",
                    "pwr_watts",
                    "spd_mps",
                )
            )
            if config.rolling_window:
                _df = _df.with_columns(
                    pl.col("cad_rpm", "pwr_watts", "spd_mps").rolling_mean(
                        window_size=config.rolling_window, center=True
                    )
                )

            _df_list.append(_df)
        except Exception as e:
            logging.warning(f"Failed to read {file}: {e}")

    try:
        df = pl.concat(_df_list, how="diagonal_relaxed")
    except Exception as e:
        raise ValueError(f"Failed to create df: {e}") from e

    try:
        # Try to convert "timestamp" which looks like this: 2025-09-04T08:00:46.000Z to datetime
        df = df.with_columns(
            pl.col("timestamp").str.strptime(
                pl.Datetime, format="%Y-%m-%dT%H:%M:%S%.3fZ"
            )
        )
    except Exception as e:
        logging.warning(f"Failed to convert timestamp: {e}")

    try:
        # drop columns that are all null

        def drop_columns_that_are_all_null(_df: pl.DataFrame) -> pl.DataFrame:
            return _df[
                [s.name for s in _df if not (s.null_count() == _df.height)]
            ]

        df = df.pipe(drop_columns_that_are_all_null)
    except Exception as e:
        logging.warning(f"Failed to drop columns that are all null: {e}")

    if (
        config.reference_file is not None
        and config.reference_file in df["file"].unique()
    ):
        df = (
            df.join(
                df.filter(pl.col("file") == config.reference_file)
                .select("timestamp", "pwr_watts")
                .rename({"pwr_watts": "pwr_watts_reference"}),
                on="timestamp",
                how="left",
            )
            .with_columns(
                pwr_watts_diff=pl.col("pwr_watts")
                - pl.col("pwr_watts_reference")
            )
            .with_columns(
                pwr_watts_diff_hyb=100
                * pl.col("pwr_watts_diff")
                / pl.col("pwr_watts_reference").clip(250, None)
            )
        )

    return df
