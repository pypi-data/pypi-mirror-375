from dataclasses import dataclass


@dataclass
class Config:
    folder: str
    crux_common: str
    height: int = 300
    width: int = 2000
    zero: bool = False
    reference_file: str | None = None
    rolling_window: int | None = None
    silent: bool = False
    cleanup: bool = True
    save_chart: bool = True
