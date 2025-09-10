# dr_plotter: Configuration-Driven Plotting for Research Data

`dr_plotter` is a plotting framework built on matplotlib that provides structured configuration management for research visualizations. The library emphasizes reproducible plots through declarative configuration and automated CLI generation.

```bash
# Easy installation
uv add dr_plotter
```

## Core Architecture

The library is organized around three primary components:

### Configuration System
Plot specifications are defined through dataclass-based configuration objects:
- `LayoutConfig`: Grid layout, figure sizing, axis properties
- `FacetingConfig`: Multi-panel plotting with dimension-based grouping  
- `LegendConfig`: Legend positioning and styling strategies
- `StyleConfig`: Theme application and visual styling
- `PlotConfig`: Composite configuration combining the above

### Figure Management
The `FigureManager` provides controlled plotting contexts:

```python
from dr_plotter import FigureManager
from dr_plotter.configs import PlotConfig

with FigureManager(PlotConfig(layout={"rows": 2, "cols": 2})) as fm:
    fm.plot("scatter", 0, 0, data, x="time", y="value")
    fm.plot("line", 0, 1, data, x="time", y="metric") 
```

### Dynamic CLI System
The framework automatically generates command-line interfaces from configuration dataclasses. This eliminates manual CLI maintenance and ensures configuration consistency.

```bash
# Generate 70+ options automatically from config definitions
uv run dr-plotter dataset.parquet \
    --x time --y value \
    --rows-by experiment --cols-by condition \
    --pause 5
```

The CLI system provides:
- Automatic option generation from dataclass field definitions
- Type-aware argument parsing and validation
- Configuration file support (YAML)
- Real-time parameter validation through construction-based checking

## Faceted Plotting

The faceting system supports multi-dimensional data visualization through systematic subplot organization:

```python
from dr_plotter.configs import FacetingConfig

faceting = FacetingConfig(
    rows_by="experiment",     # Organize rows by experiment variable
    cols_by="condition",      # Organize columns by condition variable  
    wrap_by=None,            # Alternative: wrap panels in sequence
    fixed={"dataset": "A"},   # Fix certain dimensions
    order={"condition": ["control", "treatment"]}  # Control panel ordering
)
```

The system automatically:
- Partitions data based on specified dimensions
- Calculates appropriate grid layouts
- Maintains consistent styling across panels
- Handles missing data combinations

## Installation

```bash
uv sync
```

## Usage Examples

**Note**: The `examples/` directory contains legacy code that is currently incompatible with the current architecture and will not execute successfully.

## CLI Plot Showcases

The `scripts/` directory contains modern CLI-driven plot showcases that demonstrate the full plotting capabilities with comprehensive parameter exploration. Each showcase has been migrated from legacy examples to use the new CLI framework and modern data generation.

### Available Plot Types

| Plot Type | Script | Description |
|-----------|--------|-------------|
| **Line Plots** | `plot_line.py` | Time series, ML training curves, A/B test results with multiple visual encodings |
| **Violin Plots** | `plot_violin.py` | Distribution shapes for categorical and statistical data analysis |
| **Scatter Plots** | `plot_scatter.py` | Multi-dimensional data exploration with color/marker encoding |
| **Bar Plots** | `plot_bar.py` | Categorical comparisons with multiple aggregation methods |
| **Heatmaps** | `plot_heatmap.py` | Matrix visualization, correlation analysis, density mapping |
| **Contour Plots** | `plot_contour.py` | Gaussian mixtures and density visualization |

### Quick Start Examples

```bash
# Line plots with different data types
uv run python scripts/plot_line.py --data-type ml_training --pause 5
uv run python scripts/plot_line.py --data-type ab_test --groups 4 --time-points 50

# Violin plots for distribution analysis  
uv run python scripts/plot_violin.py --data-type distribution --pause 5
uv run python scripts/plot_violin.py --categories 6 --n-samples 200

# Scatter plots with multi-dimensional encoding
uv run python scripts/plot_scatter.py --experiments 3 --conditions 3 --pause 5
uv run python scripts/plot_scatter.py --data-type categorical --figsize "(18,12)"

# Bar plots with different aggregations
uv run python scripts/plot_bar.py --aggregate count --categories 5 --pause 5
uv run python scripts/plot_bar.py --data-type multi_dimensional --aggregate sum

# Heatmaps and correlation matrices
uv run python scripts/plot_heatmap.py --pattern-type correlation --colormap coolwarm --pause 5
uv run python scripts/plot_heatmap.py --matrix-rows 10 --matrix-cols 12 --colormap viridis

# Contour density plots
uv run python scripts/plot_contour.py --density-levels 15 --colormap plasma --pause 5
uv run python scripts/plot_contour.py --n-samples 500 --colormap coolwarm
```

### Preset Configurations

Each plot type includes curated preset configurations in the `configs/` directory for common use cases:

```bash
# Use preset configurations for consistent styling
uv run python scripts/plot_line.py --config configs/line_presets.yaml
uv run python scripts/plot_violin.py --config configs/violin_presets.yaml  
uv run python scripts/plot_scatter.py --config configs/scatter_presets.yaml
uv run python scripts/plot_bar.py --config configs/bar_presets.yaml
uv run python scripts/plot_heatmap.py --config configs/heatmap_presets.yaml
uv run python scripts/plot_contour.py --config configs/contour_presets.yaml
```

Each preset file contains 5-6 different configurations optimized for:
- **Basic usage**: Default parameters for immediate results
- **Publication ready**: Professional formatting with proper spacing and legends  
- **High density**: Large datasets with optimized rendering
- **Custom styling**: Alternative colormaps, layouts, and visual encodings
- **Specialized analysis**: Domain-specific parameter combinations

### CLI Framework Features

All showcase scripts provide comprehensive CLI interfaces with 40+ parameters automatically generated from the configuration system:

- **Data Generation**: Control sample sizes, patterns, seeds for reproducibility
- **Layout Control**: Figure size, subplot arrangement, spacing, titles
- **Visual Encoding**: Colors, markers, line styles, transparency, grouping
- **Legend Management**: Positioning, strategies (per-subplot vs figure-wide)
- **Output Options**: Save directories, display duration, file formats
- **Advanced Faceting**: Multi-dimensional subplot organization

```bash
# View all available options for any plot type
uv run python scripts/plot_line.py --help
uv run python scripts/plot_violin.py --help
# ... etc for all plot types
```

### Parameter Exploration Examples

The CLI framework enables rapid visual parameter exploration:

```bash
# Explore different layout strategies
uv run python scripts/plot_line.py --figsize "(20,10)" --legend-strategy figure
uv run python scripts/plot_violin.py --figsize "(16,8)" --legend-position "[0.5,0.02]"

# Test various data generation patterns
uv run python scripts/plot_scatter.py --data-type time_series --n-samples 300
uv run python scripts/plot_bar.py --data-type distribution --aggregate count

# Experiment with visual styling
uv run python scripts/plot_heatmap.py --colormap inferno --matrix-rows 12
uv run python scripts/plot_contour.py --density-levels 20 --colormap hot

# Combine custom parameters with presets
uv run python scripts/plot_line.py --config configs/line_presets.yaml --seed 999 --pause 3
```

### Basic CLI Usage

```bash
# Scatter plot with faceting by parameter values
uv run dr-plotter data.parquet \
    --x step --y loss --rows-by model_type

# Time series with custom layout  
uv run dr-plotter data.parquet \
    --x time --y accuracy --plot-type line \
    --figsize "(15, 8)" --no-tight-layout
```

### Programmatic Usage

```python
from dr_plotter import FigureManager
from dr_plotter.configs import PlotConfig, LayoutConfig, FacetingConfig

# Configure multi-panel layout
config = PlotConfig(
    layout=LayoutConfig(rows=2, cols=3, figsize=(18, 12)),
    faceting=FacetingConfig(rows_by="experiment", cols_by="metric")
)

# Create faceted visualization
with FigureManager(config) as fm:
    fm.plot_faceted(data, "scatter", faceting=config.faceting)
```

### CLI Workflow for Custom Scripts

Build your own CLI scripts using the streamlined workflow pattern:

```python
from dr_plotter import FigureManager
from dr_plotter.scripting import CLIWorkflowConfig, execute_cli_workflow, dimensional_plotting_cli, load_dataset
import click

@click.command()
@click.argument("dataset_path")
@dimensional_plotting_cli()  # Auto-generates 70+ CLI options
def main(dataset_path: str, **kwargs):
    # Define your workflow configuration
    workflow_config = CLIWorkflowConfig(
        data_loader=lambda _: load_dataset(dataset_path),
        default_params={"batch_size": 32},           # Provide sensible defaults
        fixed_params={"model_type": "transformer"},  # Enforce script requirements  
        allowed_unused={"save_dir", "pause"}         # Accept these extra params
    )
    
    # Execute the complete workflow (config + validation + data loading)
    df, plot_config = execute_cli_workflow(kwargs, workflow_config)
    
    # Create your visualization - faceting handled automatically!
    with FigureManager(plot_config) as fm:
        fm.plot_faceted(df, "scatter")  # plot_config.faceting used automatically
    
    # Handle output
    show_or_save_plot(fm.fig, kwargs.get("save_dir"), kwargs.get("pause", 5))

if __name__ == "__main__":
    main()
```

The workflow pattern provides automatic configuration building, validation, and data loading in a single function call. All CLI parameters are handled seamlessly, with clear error messages for any validation issues.

### Data Generation

Test data can be generated using the built-in functions:

```python
from dr_plotter.scripting.plot_data import experimental_data, matrix_data

# Generate time series data
data = experimental_data(
    pattern_type="time_series", 
    n_samples=200, 
    time_points=50
)

# Generate matrix data for heatmaps
matrix = matrix_data(
    rows=10, cols=8, 
    pattern_type="correlation"
)
```

## Design Philosophy

The library implements several core principles:

- **Configuration-Driven**: All plot specifications are declarative and serializable
- **Type Safety**: Comprehensive type hints and runtime validation
- **Reproducibility**: Consistent output from identical configurations
- **Extensibility**: Modular architecture supporting custom components
- **Research-Focused**: Optimized for scientific visualization workflows

For detailed design principles, see [docs/DESIGN_PHILOSOPHY.md](./docs/DESIGN_PHILOSOPHY.md).

## Contributing

Contributions are welcome. See [docs/CONTRIBUTING.md](./docs/CONTRIBUTING.md) for guidelines.
