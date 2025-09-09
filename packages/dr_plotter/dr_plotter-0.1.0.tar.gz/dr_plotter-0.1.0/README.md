# dr_plotter: A Declarative Plotting Library for Researchers

`dr_plotter` is a high-level plotting library for Python, designed to make it easy for researchers to create a wide range of publication-quality plots with minimal effort. It is built on top of `matplotlib` and `pandas`, and it provides a simple, declarative API for creating complex visualizations.

```
# To update datadec import
uv lock --upgrade-package datadec
```

## Features

*   **Declarative API:** Create complex plots with just a few lines of code.
*   **Extensible:** Easily add your own custom plotters and styles.
*   **Consistent:** A consistent and predictable API that is easy to learn and use.
*   **Powerful:** Built on top of `matplotlib` and `pandas`, so you can always drop down to the lower-level APIs when you need more control.

## Quickstart

```python
import dr_plotter.api as drp
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from plot_data import ExampleData

# Get some simple data
_data = ExampleData.simple_scatter()

# Create a plot
fig, ax = drp.scatter(data, x="x", y="y", title="Quickstart Scatter Plot")

# Show the plot
show_or_save_plot(fig, None, "01_quickstart")
```

For many more increasingly complex examples see `examples/`.

## Installation

```bash
uv sync
```

## Design Philosophy

`dr_plotter` is built on a foundation of strong design principles. We believe that a plotting library should be:

*   **Intuitive and Consistent:** The API should be easy to learn and use, with no surprising behavior.
*   **Flexible and Extensible:** You should be able to create any plot you need, and it should be easy to add new plotters and styles.
*   **Robust and Developer-Friendly:** The library should be well-tested and provide clear, informative error messages.

To learn more about our design philosophy, please see our [Design Philosophy document](./docs/DESIGN_PHILOSOPHY.md).

## Contributing

We welcome all contributions, from simple bug fixes to new feature proposals. To get started, please see our [Contributing Guide](./docs/CONTRIBUTING.md).
