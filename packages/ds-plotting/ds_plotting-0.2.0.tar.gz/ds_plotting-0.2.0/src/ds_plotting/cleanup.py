import glob
import logging
import os

import polars as pl

from ds_plotting.config import Config


def move_files(df: pl.DataFrame, config: Config) -> None:
    files = df["file"].unique()
    for file in files:
        # if not exists, create a hidden folder with the same name but a dot prefix
        hidden_folder = os.path.join(config.folder, f".crfittool_{file}")
        if not os.path.exists(hidden_folder):
            os.makedirs(hidden_folder)
        # try to move all files into that hidden folder that contain the
        # file name and end in .csv
        for f in glob.glob(os.path.join(config.folder, f"*{file}*.csv")):
            try:
                os.rename(f, os.path.join(hidden_folder, os.path.basename(f)))
            except Exception as e:
                logging.warning(f"Failed to move {f} to {hidden_folder}: {e}")
