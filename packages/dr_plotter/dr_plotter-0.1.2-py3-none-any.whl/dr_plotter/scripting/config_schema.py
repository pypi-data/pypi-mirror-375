from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

EXAMPLE_CONFIG = {
    "rows_by": None,
    "cols_by": None,
    "wrap_by": "model_size",
    "max_cols": 4,
    "hue_by": "dataset",
    "alpha_by": "seed",
    "size_by": None,
    "marker_by": None,
    "style_by": None,
    "fixed": {"metric": "loss"},
    "order": {"model_size": ["1B", "7B", "30B", "70B", "180B"]},
    "exclude": {"dataset": ["deprecated_data"]},
    "rows": 1,
    "cols": 1,
    "figsize": [12.0, 8.0],
    "tight_layout": True,
    "tight_layout_pad": 1.0,
    "subplot_width": 3.5,
    "subplot_height": 3.0,
    "auto_titles": True,
    "legend_strategy": "grouped",
    "save_dir": "./plots",
    "pause": 5,
}

MINIMAL_CONFIG = {
    "wrap_by": "params",
    "hue_by": "data",
    "fixed": {"metric": "pile-valppl"},
    "legend_strategy": "figure",
}


def write_example_config(path: str | Path, minimal: bool = False) -> None:
    config = MINIMAL_CONFIG if minimal else EXAMPLE_CONFIG
    path = Path(path)
    with path.open("w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def load_config(config_path: str | Path) -> dict[str, Any]:
    config_path = Path(config_path)
    with config_path.open() as f:
        config_data = yaml.safe_load(f)
    return config_data
