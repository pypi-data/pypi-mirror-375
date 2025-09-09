# Faceted Plotting Migration Guide

This guide helps you migrate from manual subplot management to dr_plotter's native faceting system.

## Why Migrate?

**Before faceting** - Manual subplot management requires:
- 95+ lines of boilerplate code for complex grids
- Manual data filtering and subsetting
- Manual color/marker coordination across subplots  
- Complex legend management
- Error-prone subplot indexing

**After faceting** - Single API call:
- 5 lines of code for the same result
- Automatic data organization and layout
- Consistent styling across subplots and layers
- Integrated legend management  
- Robust error handling and validation

## Migration Patterns

### Pattern 1: Basic Grid Layout

**Before:**
```python
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
metrics = ['train_loss', 'val_loss']
datasets = ['squad', 'glue', 'c4'] 
colors = {'7B': 'blue', '13B': 'orange', '30B': 'green'}

for i, metric in enumerate(metrics):
    for j, dataset in enumerate(datasets):
        ax = axes[i, j]
        subset = data[(data['metric'] == metric) & (data['dataset'] == dataset)]
        
        for model in ['7B', '13B', '30B']:
            model_data = subset[subset['model_size'] == model]
            ax.plot(model_data['step'], model_data['value'], 
                   color=colors[model], label=model, linewidth=2)
        
        ax.set_title(f'{metric} - {dataset}')
        ax.set_xlabel('Step')
        ax.set_ylabel('Value')
        if i == 0 and j == 0:
            ax.legend()
```

**After:**
```python
fm.plot_faceted(
    data=data, plot_type='line',
    rows='metric', cols='dataset', lines='model_size',
    x='step', y='value', linewidth=2
)
```

### Pattern 2: Wrapped Layouts  

**Before:**
```python
# Complex logic to arrange 6 metrics in 2×3 grid
metrics = data['metric'].unique()
n_metrics = len(metrics)
n_cols = 3
n_rows = (n_metrics + n_cols - 1) // n_cols  # Ceiling division

fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 10))
axes = axes.flatten()

for i, metric in enumerate(metrics):
    if i >= len(axes):
        break
    ax = axes[i]
    # ... plotting logic ...
    
# Hide unused subplots
for i in range(n_metrics, len(axes)):
    axes[i].set_visible(False)
```

**After:**
```python  
# Create explicit 2×3 grid with FigureConfig
fm = FigureManager(figure=FigureConfig(rows=2, cols=3))
fm.plot_faceted(
    data=data, plot_type='scatter',
    rows='metric', cols='dataset',  # Explicit grid dimensions
    lines='model_size', x='step', y='value'
)
```

### Pattern 3: Layered Plots

**Before:**
```python  
# Layer 1: Scatter
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
# ... complex subplot management for scatter ...

# Layer 2: Lines - must manually ensure color consistency  
colors_used = {}  # Track colors from first layer
for i, metric in enumerate(metrics):
    for j, dataset in enumerate(datasets):
        ax = axes[i, j]
        # ... complex logic to reuse same colors ...
```

**After:**
```python
# Layer 1: Scatter
fm.plot_faceted(scatter_data, 'scatter', 
               rows='metric', cols='dataset', lines='model_size',
               x='step', y='value', alpha=0.4)

# Layer 2: Lines - colors automatically coordinated!
fm.plot_faceted(line_data, 'line',
               rows='metric', cols='dataset', lines='model_size', 
               x='step', y='value', linewidth=2)
```

## Step-by-Step Migration

### Step 1: Identify Your Grid Structure
- **Rows dimension**: What varies across rows?
- **Columns dimension**: What varies across columns?  
- **Lines dimension**: What creates different colors/markers within subplots?

### Step 2: Replace Manual Subplot Creation
```python
# Replace this:
fig, axes = plt.subplots(n_rows, n_cols)

# With this:
fm = FigureManager(figure=FigureConfig(rows=n_rows, cols=n_cols))
```

### Step 3: Replace Manual Data Filtering
```python
# Replace complex filtering:
for i, row_val in enumerate(row_values):
    for j, col_val in enumerate(col_values):
        subset = data[(data[row_dim] == row_val) & (data[col_dim] == col_val)]
        
# With automatic faceting:
fm.plot_faceted(data, plot_type, rows=row_dim, cols=col_dim, ...)
```

### Step 4: Replace Manual Color Coordination
```python
# Replace manual color management:
colors = {'A': 'blue', 'B': 'orange', 'C': 'green'}
for group in groups:
    ax.plot(..., color=colors[group])

# With automatic coordination:
fm.plot_faceted(data, plot_type, ..., lines='group_column')
```

### Step 5: Simplify Legend Management
```python
# Replace complex legend logic:
handles, labels = [], []
for ax in axes.flat:
    h, l = ax.get_legend_handles_labels()
    handles.extend(h)
    labels.extend(l)
# ... deduplication and positioning ...

# With automatic legend:
# Legends are handled automatically by faceting system
```

## Common Pitfalls and Solutions

### Pitfall 1: Column Name Confusion
```python
# Wrong - using display names
fm.plot_faceted(data, 'line', rows='Train Loss', cols='Squad Dataset')

# Right - using actual column names  
fm.plot_faceted(data, 'line', rows='metric', cols='dataset')
```

### Pitfall 2: Forgetting Grid Setup
```python
# Wrong - grid too small for faceted data
fm = FigureManager(figure=FigureConfig(rows=1, cols=1))  
fm.plot_faceted(data, 'line', rows='metric', cols='dataset')  # Error!

# Right - appropriate grid size
fm = FigureManager(figure=FigureConfig(rows=2, cols=3))
fm.plot_faceted(data, 'line', rows='metric', cols='dataset')
```

### Pitfall 3: Mixed Parameter Styles
```python
# Inconsistent - some params in config, some direct
config = FacetingConfig(rows='metric', cols='dataset') 
fm.plot_faceted(data, 'line', faceting=config, lines='model')  # Mixed

# Better - all in config or all direct
fm.plot_faceted(data, 'line', rows='metric', cols='dataset', lines='model')
```

## Performance Considerations

### Large Datasets
```python
# For datasets > 10K rows, consider filtering first:
recent_data = data[data['step'] > 500]  # Filter before faceting
fm.plot_faceted(recent_data, 'line', ...)
```

### Many Subplots  
```python
# For >20 subplots, use explicit grid dimensions:
fm = FigureManager(figure=FigureConfig(rows=5, cols=4))  # 20 subplots in 5×4 grid
fm.plot_faceted(data, 'scatter', rows='metric', cols='dataset')
```

### Multiple Layers
```python
# Create all layers before styling adjustments:
fm.plot_faceted(layer1_data, 'scatter', ...)
fm.plot_faceted(layer2_data, 'line', ...)  
fm.plot_faceted(layer3_data, 'line', ...)
# Then apply figure-level styling
```

## Benefits Summary

✅ **95% code reduction** - From 95+ lines to 5 lines
✅ **Automatic color coordination** - Same values get same colors  
✅ **Layered plotting** - Multiple plot calls on same grid
✅ **Targeted plotting** - Selective subplot targeting
✅ **Error prevention** - Robust validation and helpful errors
✅ **Consistent API** - Follows dr_plotter patterns
✅ **Performance optimized** - Efficient for large datasets
✅ **Extensible** - Easy to add new plot types and features

### Axis Sharing

For shared axes across subplots, use FigureConfig's `subplot_kwargs`:

```python
# Share x-axis across all subplots
fm = FigureManager(figure=FigureConfig(
    rows=2, cols=3,
    subplot_kwargs={"sharex": True}
))

# Share y-axis within rows only  
fm = FigureManager(figure=FigureConfig(
    rows=2, cols=3, 
    subplot_kwargs={"sharey": "row"}
))

# Share both axes
fm = FigureManager(figure=FigureConfig(
    rows=2, cols=3,
    subplot_kwargs={"sharex": True, "sharey": True}
))
```

Start with basic 2D faceting and gradually adopt advanced features as needed!