# dr_plotter Configuration Examples

This directory contains example YAML configuration files for the dr_plotter CLI framework.

## Files

- **`example_config.yaml`** - Complete configuration showing all available options
- **`minimal_config.yaml`** - Minimal configuration with common settings  
- **`demo_config.yaml`** - Configuration used by the demo script

## Usage

```bash
# Use with demo script
uv run python scripts/plot_scaling_demo.py --config configs/example_config.yaml

# Use with your own applications
from dr_plotter.scripting import CLIConfig
config = CLIConfig.from_yaml('configs/example_config.yaml')
```

## Configuration Structure

The YAML files mirror dr_plotter's config objects:

```yaml
faceting:          # → FacetingConfig options
  rows_and_cols: model_size
  hue_by: dataset
  fixed_dimensions:
    metric: loss
    
layout:            # → Layout options
  subplot_width: 3.5
  subplot_height: 3.0
  
legend:            # → LegendConfig options
  strategy: grouped
  
output:            # → Output options
  save_dir: ./plots
```

See the example files for complete option references.