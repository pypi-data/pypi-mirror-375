import json
import os


def read_crux_common(crux_common: str | None) -> str:
    if crux_common is None:
        if os.path.exists(os.path.expanduser("~/.wahoofitness.json")):
            with open(os.path.expanduser("~/.wahoofitness.json"), "r") as f:
                data = json.load(f)
                if "crux_common" in data:
                    crux_common = data["crux_common"]
    if crux_common is None:
        raise ValueError(
            "crux_common must be provided either as an argument or in ~/.wahoofitness.json"
        )
    return crux_common
