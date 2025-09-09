import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager


def create_ml_training_data() -> pd.DataFrame:
    np.random.seed(42)
    data = []

    for step in range(0, 1000, 10):
        for metric in ["train_loss", "val_loss", "train_acc", "val_acc"]:
            for model_size in ["7B", "13B", "30B", "65B"]:
                for dataset in ["squad", "glue", "c4"]:
                    if metric.endswith("loss"):
                        value = 2.0 * np.exp(-step / 300) + np.random.normal(0, 0.1)
                    else:
                        value = 0.9 * (1 - np.exp(-step / 400)) + np.random.normal(
                            0, 0.05
                        )

                    data.append(
                        {
                            "step": step,
                            "metric": metric,
                            "model_size": model_size,
                            "dataset": dataset,
                            "value": value,
                        }
                    )

    return pd.DataFrame(data)


def example_1_basic_2d_faceting() -> None:
    print("=== Example 1: Basic 2D Faceting ===")

    data = create_ml_training_data()

    with FigureManager(
        PlotConfig(layout={"rows": 4, "cols": 3, "figsize": (18, 16)})
    ) as fm:
        fm.plot_faceted(
            data=data,
            plot_type="line",
            rows="metric",
            cols="dataset",
            lines="model_size",
            x="step",
            y="value",
            linewidth=2,
            alpha=0.8,
        )

        print(
            f"Created {4 * 3} subplots with {len(data['model_size'].unique())} "
            f"consistently colored model sizes"
        )
        print("Same model sizes have identical colors across all subplots")


def example_2_grid_layouts() -> None:
    print("\n=== Example 2: Explicit Grid Layouts ===")

    data = create_ml_training_data()
    metrics = ["train_loss", "val_loss", "train_acc", "val_acc", "train_f1", "val_f1"]
    data = data[data["metric"].isin(metrics)]

    # Create row/col grid coordinates for 6 metrics in 2x3 layout
    data = data.copy()
    metric_to_grid = {
        "train_loss": (0, 0),
        "val_loss": (0, 1),
        "train_acc": (0, 2),
        "val_acc": (1, 0),
        "train_f1": (1, 1),
        "val_f1": (1, 2),
    }
    data["metric_row"] = data["metric"].map(lambda m: metric_to_grid[m][0])
    data["metric_col"] = data["metric"].map(lambda m: metric_to_grid[m][1])

    with FigureManager(
        PlotConfig(layout={"rows": 2, "cols": 3, "figsize": (18, 12)})
    ) as fm:
        fm.plot_faceted(
            data=data,
            plot_type="scatter",
            rows="metric_row",
            cols="metric_col",
            lines="model_size",
            x="step",
            y="value",
            alpha=0.6,
            s=20,
        )

        print("Arranged 6 metrics into 2×3 grid using explicit row/col mapping")
        print("Better use of figure space than 6×1 or 1×6 layouts")


def example_3_layered_faceting() -> None:
    print("\n=== Example 3: Layered Faceting ===")

    data = create_ml_training_data()

    scatter_data = data[data["step"] % 50 == 0]
    line_data = data[data["step"] % 20 == 0]

    with FigureManager(
        PlotConfig(layout={"rows": 4, "cols": 3, "figsize": (18, 16)})
    ) as fm:
        fm.plot_faceted(
            data=scatter_data,
            plot_type="scatter",
            rows="metric",
            cols="dataset",
            lines="model_size",
            x="step",
            y="value",
            alpha=0.4,
            s=30,
        )

        fm.plot_faceted(
            data=line_data,
            plot_type="line",
            rows="metric",
            cols="dataset",
            lines="model_size",
            x="step",
            y="value",
            linewidth=2,
            alpha=0.8,
        )

        print("Created layered visualization:")
        print("- Scatter points showing data distribution")
        print("- Line trends with SAME colors as scatter points")
        print("Model sizes have consistent colors across both layers")


def example_4_targeted_plotting() -> None:
    print("\n=== Example 4: Targeted Plotting ===")

    data = create_ml_training_data()

    with FigureManager(
        PlotConfig(layout={"rows": 4, "cols": 3, "figsize": (18, 16)})
    ) as fm:
        fm.plot_faceted(
            data=data,
            plot_type="line",
            rows="metric",
            cols="dataset",
            lines="model_size",
            x="step",
            y="value",
            alpha=0.6,
            linewidth=1,
        )

        # Filter data for specific cell we want to highlight at position (row 0, col 1)
        highlight_data = data[
            (data["model_size"] == "65B")
            & (data["metric"] == data["metric"].unique()[0])  # First metric (row 0)
            & (data["dataset"] == data["dataset"].unique()[1])  # Col 1 (second dataset)
        ]

        # Use target_row and target_col to place the highlighted data at
        # specific positions
        fm.plot_faceted(
            data=highlight_data,
            plot_type="line",
            rows="metric",
            cols="dataset",
            lines="model_size",
            x="step",
            y="value",
            linewidth=4,
            color="red",
            target_row=0,  # First row (corresponds to the first metric)
            target_col=1,  # Second column (corresponds to the second dataset)
        )

        # Plot the second highlight at position (0, 2)
        highlight_data_col2 = data[
            (data["model_size"] == "65B")
            & (data["metric"] == data["metric"].unique()[0])  # First metric (row 0)
            & (data["dataset"] == data["dataset"].unique()[2])  # Third dataset (col 2)
        ]

        fm.plot_faceted(
            data=highlight_data_col2,
            plot_type="line",
            rows="metric",
            cols="dataset",
            lines="model_size",
            x="step",
            y="value",
            linewidth=4,
            color="red",
            target_row=0,  # First row
            target_col=2,  # Third column
        )

        print("Created targeted overlay:")
        print("- Base lines for all models in all subplots")
        print("- Thick red highlight for best model in specific subplots only")
        print("- Using target_row and target_col to position overlays precisely")


def example_5_custom_subplot_configuration() -> None:
    print("\n=== Example 5: Custom Subplot Configuration ===")

    data = create_ml_training_data()

    x_labels = [
        ["Training Steps", "Training Steps", "Training Steps"],
        ["Validation Steps", "Validation Steps", "Validation Steps"],
    ]

    xlim = [[(0, 500), (0, 800), (100, 900)], [(50, 600), (0, 1000), (200, 800)]]

    with FigureManager(
        PlotConfig(layout={"rows": 4, "cols": 3, "figsize": (18, 16)})
    ) as fm:
        fm.plot_faceted(
            data=data,
            plot_type="scatter",
            rows="metric",
            cols="dataset",
            lines="model_size",
            x_labels=x_labels,
            xlim=xlim,
            x="step",
            y="value",
            alpha=0.7,
            s=25,
        )

        print("Applied custom configuration:")
        print("- Different x-axis labels for each subplot")
        print("- Different x-axis limits for each subplot")
        print("- Per-subplot control while maintaining color coordination")


def example_6_migration_comparison() -> None:
    print("\n=== Example 6: Migration Comparison ===")

    data = create_ml_training_data().head(200)

    print("BEFORE FACETING (manual subplot management):")
    print("```python")
    print("# 95+ lines of code required:")
    print("fig, axes = plt.subplots(2, 3, figsize=(18, 10))")
    print("metrics = sorted(data['metric'].unique())")
    print("datasets = sorted(data['dataset'].unique())")
    print("model_colors = {'7B': 'blue', '13B': 'orange', ...}")
    print("")
    print("for i, metric in enumerate(metrics[:2]):")
    print("    for j, dataset in enumerate(datasets):")
    print("        ax = axes[i, j]")
    print("        subset = data[(data['metric'] == metric) &")
    print("                     (data['dataset'] == dataset)]")
    print("        for model in sorted(subset['model_size'].unique()):")
    print("            model_data = subset[subset['model_size'] == model]")
    print("            ax.plot(model_data['step'], model_data['value'],")
    print("                   color=model_colors[model], label=model)")
    print("        ax.set_title(f'{metric} - {dataset}')")
    print("        ax.set_xlabel('Step')")
    print("        ax.set_ylabel('Value')")
    print("# ... more lines for legend coordination, styling, etc.")
    print("```")

    print("\nAFTER FACETING (single API call):")
    print("```python")
    print("# 5 lines of code:")
    print("fm.plot_faceted(")
    print("    data=data, plot_type='line',")
    print("    rows='metric', cols='dataset', lines='model_size',")
    print("    x='step', y='value'")
    print(")")
    print("```")

    with FigureManager(
        PlotConfig(layout={"rows": 4, "cols": 3, "figsize": (18, 16)})
    ) as fm:
        fm.plot_faceted(
            data=data,
            plot_type="line",
            rows="metric",
            cols="dataset",
            lines="model_size",
            x="step",
            y="value",
        )

        print("\nFaceting Benefits:")
        print("- Reduced from 95+ lines to 5 lines (95% reduction)")
        print("- Automatic color coordination across subplots")
        print("- Automatic grid layout computation")
        print("- Automatic legend management")
        print("- Support for layered plots and targeting")
        print("- Consistent with dr_plotter API patterns")


if __name__ == "__main__":
    print("Dr_Plotter Faceted Plotting Guide")
    print("=" * 50)

    example_1_basic_2d_faceting()
    example_2_grid_layouts()
    example_3_layered_faceting()
    example_4_targeted_plotting()
    example_5_custom_subplot_configuration()
    example_6_migration_comparison()

    print("\n" + "=" * 50)
    print("All examples completed!")
    print("Try modifying the examples to explore different faceting patterns.")

    # Show the plots for 5 seconds, then close
    plt.show(block=True)
    time.sleep(5)
    plt.close()
