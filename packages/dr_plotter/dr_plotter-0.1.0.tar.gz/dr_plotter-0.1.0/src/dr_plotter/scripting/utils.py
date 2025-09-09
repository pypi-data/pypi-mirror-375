import argparse
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt


def setup_arg_parser(
    description: str = "dr_plotter example script",
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--save-dir",
        type=str,
        default=None,
        help="Save the plot(s) to the specified directory instead of displaying them.",
    )
    parser.add_argument(
        "--pause", type=int, default=5, help="Duration in seconds to display the plot."
    )
    return parser


def show_or_save_plot(fig: Any, args: Any, filename: str) -> None:
    if args.save_dir:
        save_dir = Path(args.save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        savename = save_dir / f"{filename}.png"
        fig.savefig(savename, dpi=300)
        print(f"Plot saved to {savename}")
    else:
        plt.show(block=False)
        plt.pause(args.pause)

    plt.close(fig)


def create_and_render_plot(
    ax: Any, plotter_class: Any, plotter_args: Any, **kwargs: Any
) -> None:
    plotter = plotter_class(*plotter_args, **kwargs)
    plotter.render(ax)
