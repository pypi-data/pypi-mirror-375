# Faceted Plotting API Reference

## Overview

Dr_plotter's faceting system provides automatic subplot layout and consistent styling for multi-dimensional data visualization. This replaces manual subplot management with intelligent automatic layout.

## Core Classes

### FigureManager.plot_faceted()

**Signature:**
```python
def plot_faceted(
    self, 
    data: pd.DataFrame, 
    plot_type: str, 
    faceting: Optional[FacetingConfig] = None,
    **kwargs
) -> None:
```

**Parameters:**

- `data`: DataFrame containing the data to plot. Must contain columns specified in faceting dimensions.
- `plot_type`: Type of plot to create. Supports all standard dr_plotter plot types: 'line', 'scatter', 'bar', 'fill_between', 'heatmap', etc.
- `faceting`: Optional FacetingConfig object. If None, uses parameters from kwargs.
- `**kwargs`: Faceting parameters (used if faceting=None) and plot styling parameters.

**Faceting Parameters (in kwargs):**

**Core Dimensions:**
- `rows`: Column name to facet across rows. Each unique value gets a row.
- `cols`: Column name to facet across columns. Each unique value gets a column.
- `lines`: Column name for within-subplot grouping (hue). Creates different colored/styled lines/points within each subplot.

**Note:** Grid dimensions are controlled by FigureConfig. Faceting parameters only specify data mapping.

**Targeting (for layered faceting):**
- `target_row`: Plot only in specific row (0-indexed).
- `target_col`: Plot only in specific column (0-indexed).
- `target_rows`: Plot only in specific rows (list of integers).
- `target_cols`: Plot only in specific columns (list of integers).

**Subplot Configuration:**
- `x_labels`: Custom x-axis labels for each subplot. Must match grid dimensions.
- `y_labels`: Custom y-axis labels for each subplot.
- `xlim`: Custom x-axis limits for each subplot.
- `ylim`: Custom y-axis limits for each subplot.

**Plot Data:**
- `x`: Column name for x-axis data.
- `y`: Column name for y-axis data.

**Examples:**

Basic 2D faceting:
```python
fm.plot_faceted(data, 'line', rows='metric', cols='dataset', 
                lines='model', x='step', y='value')
```

Grid layout with FigureConfig:
```python
# Grid size controlled by FigureConfig
fm = FigureManager(figure=FigureConfig(rows=2, cols=3))
fm.plot_faceted(data, 'scatter', rows='metric', cols='dataset',
                x='step', y='value', alpha=0.6)
```

Targeted plotting:
```python
fm.plot_faceted(highlight_data, 'line', rows='metric', cols='dataset',
                target_row=0, target_cols=[1, 2], 
                x='step', y='value', color='red', linewidth=3)
```

### FacetingConfig

**Purpose:** Configuration object for faceted plotting with automatic subplot layout.

**Parameters:**

**Core Dimensions:**
- `rows`: Column name to facet across rows
- `cols`: Column name to facet across columns  
- `lines`: Column name for within-subplot grouping


**Value Ordering:**
- `row_order`: Custom ordering for row dimension values
- `col_order`: Custom ordering for column dimension values
- `lines_order`: Custom ordering for lines dimension values

**Targeting:**
- `target_row`: Plot only in specific row (0-indexed)
- `target_col`: Plot only in specific column (0-indexed)
- `target_rows`: Plot only in specific rows
- `target_cols`: Plot only in specific columns

**Plot Parameters:**
- `x`: Column name for x-axis data
- `y`: Column name for y-axis data

**Subplot Configuration:**
- `x_labels`: Custom x-axis labels (nested list matching grid dimensions)
- `y_labels`: Custom y-axis labels
- `xlim`: Custom x-axis limits
- `ylim`: Custom y-axis limits

**Advanced Features:**
- `subplot_titles`: Subplot titles (string template or nested list)
- `title_template`: Template for automatic subplot titles
- `empty_subplot_strategy`: How to handle empty subplots ('warn', 'error', 'silent')
- `color_wrap`: Whether to wrap colors when more groups than colors available

**Examples:**

Basic grid:
```python
config = FacetingConfig(rows='metric', cols='dataset', lines='model')
```

Explicit grid (controlled by FigureConfig):
```python
config = FacetingConfig(rows='metric', cols='dataset', lines='model_size')
```

Custom configuration:
```python
config = FacetingConfig(
    rows='metric', cols='dataset',
    x_labels=[['Time', 'Steps'], ['Hours', 'Epochs']],
    xlim=[[(0, 100), (0, 200)], [(50, 150), (100, 300)]]
)
```

## Key Behaviors

### Style Coordination
- Same 'lines' dimension values get consistent colors across all subplots
- Colors are assigned automatically using theme-aware cycles
- Style coordination works across multiple plot_faceted() calls (layered plotting)

### Grid Layout
- Grid dimensions computed automatically from data dimensions
- FigureManager grid size must match computed facet grid exactly
- Clear error messages guide users to correct FigureConfig dimensions

### Error Handling
- Missing columns trigger helpful error messages with suggestions
- Grid size mismatches are detected and reported clearly
- Configuration conflicts are caught with recovery guidance

### Performance
- Optimized data preparation with groupby operations
- Caching for grid computation metadata
- Memory-efficient style coordination with LRU eviction
- Fast paths for single subplots and small datasets

### Integration
- Works with existing dr_plotter themes
- Compatible with legend system
- Consistent parameter patterns with other dr_plotter methods
- Preserves all standard plot styling parameters

## Advanced Usage Patterns

### Layered Faceting
Create complex visualizations by calling plot_faceted multiple times on the same FigureManager:

```python
# Base layer
fm.plot_faceted(scatter_data, 'scatter', rows='metric', cols='dataset',
                lines='model', x='step', y='value', alpha=0.4)

# Trend layer - same colors automatically
fm.plot_faceted(trend_data, 'line', rows='metric', cols='dataset',
                lines='model', x='step', y='trend', linewidth=2)
```

### Selective Targeting
Use targeting for highlighting specific subplots:

```python
# All subplots
fm.plot_faceted(data, 'line', rows='metric', cols='dataset', ...)

# Highlight specific subplots only
fm.plot_faceted(highlight_data, 'scatter', rows='metric', cols='dataset',
                target_rows=[0], target_cols=[1, 2], s=100, color='red')
```

### Grid Layouts  
Handle many categories with explicit grid dimensions:

```python
# Create 3×4 grid with FigureConfig
fm = FigureManager(figure=FigureConfig(rows=3, cols=4))
fm.plot_faceted(data, 'plot_type', rows='category', cols='subcategory')
```

## Common Patterns

### Training Curves
```python
fm.plot_faceted(data, 'line', rows='metric', cols='dataset',
                lines='model_size', x='epoch', y='value')
```

### Hyperparameter Sweeps  
```python
fm.plot_faceted(data, 'scatter', rows='metric', cols='optimizer',
                lines='learning_rate', x='batch_size', y='performance')
```

### A/B Testing Results
```python
fm.plot_faceted(data, 'bar', rows='metric', cols='treatment_group',
                lines='user_segment', x='time_period', y='conversion_rate')
```

### Model Comparisons
```python
fm.plot_faceted(data, 'line', rows='benchmark', cols='model_family',
                lines='model_size', x='dataset_size', y='accuracy')
```