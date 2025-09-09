# Memory Compaction Continuation Guide

## Project Context

**Working on:** Creating systematic plotting scripts for ML evaluation data using dr_plotter's new faceting system.

**Location:** `/Users/daniellerothermel/drotherm/repos/dr_plotter/` (primary), `/Users/daniellerothermel/drotherm/repos/datadec/` (data source)

## What We Just Completed ✅

### Major Achievement: Faceting System Implementation
- **Successfully completed Chunk 6: Validation & Polish** of dr_plotter's native faceting support
- All 5 tasks completed: Error Handling, Performance Optimization, API Consistency, Documentation, Edge Cases
- **94/94 faceting tests passing, 141/141 total tests passing**
- System is production-ready and robust

### Key Files Created/Modified:
- `examples/faceted_plotting_guide.py` - Comprehensive examples (working)
- `docs/reference/api/faceting_migration_guide.md` - Migration documentation 
- `docs/reference/api/faceting_api_reference.md` - Complete API reference
- `examples/07_faceted_training_curves_refactored.py` - **Just created** - refactored example using new faceting system

### Core Faceting System Features Working:
- **2D faceted plotting**: `fm.plot_faceted(data, plot_type, rows='metric', cols='dataset', lines='model_size', x='step', y='value')`
- **Layered faceting**: Multiple plot calls with consistent color coordination
- **Targeting**: Selective subplot plotting (`target_row=0, target_cols=[1,2]`)
- **Performance optimized**: <0.1s for typical operations
- **Robust error handling**: Helpful validation messages with suggestions

## Current Task: Systematic ML Evaluation Plotting

### The User's Vision:
Create systematic plots for ML training evaluation data with pattern:
- **Core structure**: `cols='model_sizes'`, `rows='recipes'`, mean line + individual seeds (lower alpha)
- **Iterative approach**: Start simple, then expand systematically
- **Multiple groupings**: All ppl metrics together, all acc metrics together, etc.
- **Dimension collapse**: All recipes for given size, all sizes for given metric
- **Production system**: Scripts + organized output in datadec repo

### Data Structure (from datadec library):
```python
# DataDecide class provides:
dd.full_eval    # Individual seed data  
dd.mean_eval    # Aggregated across seeds
# Columns: ['params', 'data', 'seed', 'step'] + metric columns
# params = model_sizes, data = recipes, step = training steps
```

### Metric Classification (from datadec.constants):
```python
PPL_TYPES = ['pile-valppl', 'wikitext_103-valppl', 'c4_en-valppl', ...]  # Perplexity metrics
OLMES_TASKS = ['mmlu_average', 'arc_challenge', 'boolq', ...]  # "OLMES" = accuracy metrics
ALL_MODEL_SIZE_STRS = ['4M', '6M', '8M', '10M', '14M', '16M', '20M', '60M', '90M', '150M', '300M', '530M', '750M', '1B']
```

## What I Was Just About To Do

### Phase 1: Just Completed ✅ 
- ✅ Refactored `06_faceted_training_curves.py` → `07_faceted_training_curves_refactored.py`
- ✅ Demonstrated data melting from wide→long format for faceting
- ✅ Showed 95+ lines→15 lines reduction using new faceting system

### Phase 2: Next Steps (What to continue)
**Create systematic plotting script framework:**

1. **Data preparation utilities** - Handle mean vs seeds, metric melting, filtering
2. **Core plotting scripts** - Different plot types following the user's pattern
3. **Systematic organization** - File naming, directory structure in datadec repo

### Planned Script Structure:
```python
# Script types to create:
create_single_metric_plots(metric_name, mean_and_seeds=True)     # Single metric, all sizes/recipes
create_ppl_group_plots()                                         # All PPL metrics together
create_olmes_group_plots()                                       # All OLMES metrics together  
create_size_chunk_plots(chunk_idx=0)                           # Model sizes in chunks of 3-4
create_recipe_comparison_plots()                               # All recipes, single metric
create_size_comparison_plots()                                 # All sizes, single recipe
```

### Key Implementation Details:

**Data Melting Pattern (from refactored example):**
```python
melted_df = filtered_df.melt(
    id_vars=["params", "data", "step"],  # Keep these
    value_vars=target_metrics,           # Melt these into single column
    var_name="metric",                   # New column name for metric names
    value_name="value"                   # New column name for metric values
)
```

**Faceting Pattern:**
```python
fm.plot_faceted(
    data=melted_df,
    plot_type="line",
    rows="data",        # recipes across rows (user preference)
    cols="params",      # model_sizes across columns  
    lines="metric",     # metrics get different colors
    x="step",
    y="value"
)
```

## Technical Environment

- **Branch:** `08-28-facets` 
- **Python environment:** `uv` managed
- **Test command:** `uv run python examples/07_faceted_training_curves_refactored.py`
- **Key imports:** 
  ```python
  from datadec import DataDecide
  import datadec.constants
  from dr_plotter.figure import FigureManager
  from dr_plotter.figure_config import FigureConfig
  ```

## Continue By:

1. **Test the refactored example** to make sure it works
2. **Create systematic plotting script framework** following the planned structure
3. **Implement mean+seeds visualization** pattern (mean line + individual seed points/lines with lower alpha)
4. **Build out different metric groupings** (ppl, olmes, size chunks, etc.)
5. **Add systematic file naming and organization** for datadec repo output

The user was very excited about the progress and ready to "jump in" to the systematic plotting creation. The faceting system is working perfectly and ready for production use.