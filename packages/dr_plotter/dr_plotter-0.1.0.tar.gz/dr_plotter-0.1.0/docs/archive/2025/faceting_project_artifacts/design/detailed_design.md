# Faceted Plotting: Detailed Architecture Design

## Overview

This document specifies the complete architectural design for native faceting support in dr_plotter, including all key design decisions and implementation details.

**Architecture**: Hybrid approach combining simple method-based API for common cases with rich configuration objects for advanced scenarios.

**Requirements Reference**: See [`faceted_plotting_requirements.md`](./faceted_plotting_requirements.md) for complete functional requirements.

## Core Architecture

### Hybrid API Design

**Simple API** (Design 3 approach):
```python
# Direct parameter passing for common cases
fm.plot_faceted(
    data=df, plot_type="line", 
    rows="metric", cols="recipe", lines="model_size",
    x="step", y="value"
)
```

**Advanced API** (Design 2 approach):
```python  
# Rich configuration for complex scenarios
faceting = FacetingConfig(
    rows="metric", cols="recipe", lines="model_size",
    row_order=["pile-valppl", "mmlu_avg"],
    target_rows=[0, 1],
    x_labels=[["Perplexity", None], ["Accuracy", None]],
    xlim=[[(0, 50000), None], [None, (1000, 60000)]]
)
fm.plot_faceted(data=df, plot_type="line", faceting=faceting, x="step", y="value")
```

**Mixed usage** (best of both):
```python
# Config provides complex settings, direct params for simple overrides
fm.plot_faceted(data=df, plot_type="line", faceting=complex_config, target_row=0)
```

## Key Design Decisions

### 1. Parameter Resolution Strategy

**Decision**: Direct parameters override `FacetingConfig` parameters (config as defaults).

**Rationale**: 
- Intuitive mental model: config provides defaults, direct params provide specific overrides
- Enables progressive complexity: start with config, override specific aspects
- Consistent with common library patterns

**Implementation**:
```python
def _resolve_faceting_config(self, faceting: Optional[FacetingConfig], **kwargs) -> FacetingConfig:
    if faceting is None:
        return FacetingConfig(**kwargs)
    
    # Create merged config with direct params overriding config values
    config_dict = asdict(faceting)
    for key, value in kwargs.items():
        if hasattr(FacetingConfig, key) and value is not None:
            config_dict[key] = value
    
    return FacetingConfig(**config_dict)
```

### 2. Configuration File Structure

**Decision**: 
- Remove unused `SubplotFacetingConfig` from `figure_config.py`
- Create new `faceting_config.py` file for `FacetingConfig`
- Keep other configs in their existing locations

**File Structure**:
```
src/dr_plotter/
├── faceting_config.py     # FacetingConfig (new)
├── figure_config.py       # FigureConfig (existing, cleaned)  
├── legend_manager.py      # LegendConfig (existing)
└── __init__.py           # Import coordination
```

**Import Pattern**:
```python
from dr_plotter.faceting_config import FacetingConfig
from dr_plotter.figure_config import FigureConfig  
from dr_plotter.legend_manager import LegendConfig
```

### 3. Grid Size Determination

**Decision**: Auto-calculate grid size for wrapped layouts and validate against existing FigureManager state.

**Logic**:
```python
def _compute_facet_grid(self, data: pd.DataFrame, rows: str, cols: str, 
                       ncols: int, nrows: int) -> Tuple[int, int]:
    if rows and cols:
        # Explicit grid: dimensions from unique data values
        n_rows = len(data[rows].unique())
        n_cols = len(data[cols].unique())
    elif rows and ncols:
        # Wrapped rows: calculate needed rows
        n_items = len(data[rows].unique())
        n_rows = (n_items + ncols - 1) // ncols  # Ceiling division
        n_cols = ncols
    elif cols and nrows:
        # Wrapped cols: calculate needed cols  
        n_items = len(data[cols].unique())
        n_cols = (n_items + nrows - 1) // nrows
        n_rows = nrows
    
    # Validate against existing FigureManager grid
    if hasattr(self, '_grid_shape') and self._grid_shape != (n_rows, n_cols):
        if self._has_existing_plots():
            raise ValueError(f"Computed grid {n_rows}×{n_cols} conflicts with existing plots")
        else:
            # Resize figure manager to accommodate
            self._resize_grid(n_rows, n_cols)
    
    return n_rows, n_cols
```

### 4. Style Coordination Scope

**Decision**: Figure-level style coordination persists across multiple `plot_faceted()` calls.

**Rationale**:
- Essential for layered faceting: same data values must have consistent styling across layers
- Enables complex composite visualizations (scatter + trend lines + confidence intervals)
- Matches user mental model for building up complex plots

**Implementation**:
```python
class FigureManager:
    def __init__(self, ...):
        # ...existing init...
        self._facet_style_coordinator = None
    
    def plot_faceted(self, ...):
        # Initialize or reuse style coordinator
        if self._facet_style_coordinator is None:
            self._facet_style_coordinator = FacetStyleCoordinator()
        
        # Coordinate styling across all calls
        style_map = self._facet_style_coordinator.get_styles(lines, lines_order, **kwargs)
```

### 5. Validation Strategy

**Decision**: Strict, eager validation with helpful error messages.

**Target Parameter Validation**:
```python
def _validate_targeting(self, target_row: int, target_col: int, 
                       grid_rows: int, grid_cols: int):
    if target_row is not None and not (0 <= target_row < grid_rows):
        raise ValueError(f"target_row={target_row} invalid for {grid_rows}×{grid_cols} grid")
    if target_col is not None and not (0 <= target_col < grid_cols):  
        raise ValueError(f"target_col={target_col} invalid for {grid_rows}×{grid_cols} grid")
```

**Data Column Validation**:
```python
def _validate_data_columns(self, data: pd.DataFrame, rows: str, cols: str, 
                          lines: str, x: str, y: str):
    required_cols = [c for c in [rows, cols, lines, x, y] if c is not None]
    missing_cols = [c for c in required_cols if c not in data.columns]
    
    if missing_cols:
        available = sorted(data.columns.tolist())
        raise ValueError(f"Missing columns {missing_cols}. Available: {available}")
```

### 6. Empty Subplot Handling

**Decision**: Issue warning and continue, with configurable behavior.

**Implementation**:
```python
@dataclass 
class FacetingConfig:
    # ... other fields ...
    empty_subplot_strategy: str = "warn"  # "warn", "error", "silent"

def _handle_empty_subplots(self, missing_combinations: List[Tuple], strategy: str):
    if not missing_combinations:
        return
        
    if strategy == "error":
        raise ValueError(f"Missing data combinations: {missing_combinations}")
    elif strategy == "warn":
        warnings.warn(f"Empty subplots for combinations: {missing_combinations}")
    # "silent" does nothing
```

## Implementation Architecture

### Core FigureManager Method

```python
class FigureManager:
    def plot_faceted(self, data: pd.DataFrame, plot_type: str,
                    faceting: Optional[FacetingConfig] = None,
                    # Direct parameters for simple cases
                    rows: Optional[str] = None, cols: Optional[str] = None,
                    lines: Optional[str] = None, ncols: Optional[int] = None,
                    nrows: Optional[int] = None, target_row: Optional[int] = None,
                    target_col: Optional[int] = None, x: Optional[str] = None,
                    y: Optional[str] = None, **plot_kwargs) -> None:
        
        # 1. Resolve configuration (direct params override faceting config)
        config = self._resolve_faceting_config(faceting, 
                                               rows=rows, cols=cols, lines=lines,
                                               ncols=ncols, nrows=nrows,
                                               target_row=target_row, target_col=target_col,
                                               x=x, y=y, **plot_kwargs)
        
        # 2. Validate data and configuration
        self._validate_faceting_inputs(data, config)
        
        # 3. Compute grid layout and targeting
        grid_layout = self._compute_facet_grid(data, config)
        target_positions = self._resolve_targeting(config, grid_layout)
        
        # 4. Prepare data subsets for each target subplot
        data_subsets = self._prepare_facet_data(data, config, grid_layout, target_positions)
        
        # 5. Coordinate styling across subplots
        style_coordinator = self._get_or_create_style_coordinator()
        
        # 6. Execute plots for each target position
        for (row, col) in target_positions:
            if (row, col) in data_subsets:
                subplot_data = data_subsets[(row, col)]
                subplot_styles = style_coordinator.get_subplot_styles(
                    row, col, config.lines, subplot_data, **plot_kwargs)
                
                # Apply nested list parameters (labels, limits)
                self._apply_subplot_configuration(row, col, config)
                
                # Execute the actual plot
                self.plot(plot_type, row, col, subplot_data,
                         x=config.x, y=config.y, hue_by=config.lines,
                         **subplot_styles)
```

### Decomposed Helper Methods

```python
def _resolve_faceting_config(self, faceting: Optional[FacetingConfig], **kwargs) -> FacetingConfig:
    """Merge faceting config with direct parameters, direct params take precedence."""
    
def _validate_faceting_inputs(self, data: pd.DataFrame, config: FacetingConfig) -> None:
    """Eager validation of all data columns and configuration parameters."""
    
def _compute_facet_grid(self, data: pd.DataFrame, config: FacetingConfig) -> GridLayout:
    """Compute grid dimensions and coordinate mappings."""
    
def _resolve_targeting(self, config: FacetingConfig, grid: GridLayout) -> List[Tuple[int, int]]:
    """Determine which subplot positions to target for plotting."""
    
def _prepare_facet_data(self, data: pd.DataFrame, config: FacetingConfig, 
                       grid: GridLayout, targets: List[Tuple]) -> Dict[Tuple, pd.DataFrame]:
    """Subset data for each target subplot position."""
    
def _get_or_create_style_coordinator(self) -> FacetStyleCoordinator:
    """Get existing or create new style coordinator for figure-level consistency."""
    
def _apply_subplot_configuration(self, row: int, col: int, config: FacetingConfig) -> None:
    """Apply nested list parameters (x_labels, xlim, etc.) to specific subplot."""
```

### FacetingConfig Definition

```python
# faceting_config.py
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

@dataclass
class FacetingConfig:
    # Core dimensions
    rows: Optional[str] = None
    cols: Optional[str] = None  
    lines: Optional[str] = None
    
    # Layout control
    ncols: Optional[int] = None
    nrows: Optional[int] = None
    
    # Ordering and filtering
    row_order: Optional[List[str]] = None
    col_order: Optional[List[str]] = None
    lines_order: Optional[List[str]] = None
    
    # Targeting
    target_row: Optional[int] = None
    target_col: Optional[int] = None
    target_rows: Optional[List[int]] = None
    target_cols: Optional[List[int]] = None
    
    # Data mapping
    x: Optional[str] = None
    y: Optional[str] = None
    
    # Per-subplot control (preserving FigureConfig nested list pattern)
    x_labels: Optional[List[List[Optional[str]]]] = None
    y_labels: Optional[List[List[Optional[str]]]] = None
    xlim: Optional[List[List[Optional[Tuple[float, float]]]]] = None
    ylim: Optional[List[List[Optional[Tuple[float, float]]]]] = None
    
    # Subplot titles
    subplot_titles: Optional[str | List[List[Optional[str]]]] = None
    title_template: Optional[str] = None
    
    # Axis sharing
    shared_x: Optional[str | bool] = None  # "all", "row", "col", True, False
    shared_y: Optional[str | bool] = None
    
    # Behavior control
    empty_subplot_strategy: str = "warn"  # "warn", "error", "silent"
    
    # Styling control
    color_wrap: bool = False
    
    def validate(self) -> None:
        """Validate configuration consistency."""
        # Layout validation
        if self.rows and self.cols and (self.ncols or self.nrows):
            raise ValueError("Cannot specify both explicit grid (rows+cols) and wrap layout (ncols/nrows)")
        
        if not (self.rows or self.cols):
            raise ValueError("Must specify at least one of: rows, cols")
        
        # Targeting validation
        if self.target_row is not None and self.target_rows is not None:
            raise ValueError("Cannot specify both target_row and target_rows")
        
        # Add other validation logic...
```

## Integration Points

### Import Structure
```python
# __init__.py updates
from dr_plotter.faceting_config import FacetingConfig
# Existing imports remain unchanged
```

### Backward Compatibility
- All existing FigureManager functionality unchanged
- No changes to existing plot() methods
- FigureConfig nested list behavior preserved and extended

### Testing Strategy
- Unit tests for each decomposed helper method
- Integration tests for complete faceting workflows  
- Edge case tests for validation and error handling
- Performance tests for large datasets and complex grids

## Usage Examples

### Simple Case
```python
fm.plot_faceted(data=df, plot_type="line", rows="metric", cols="recipe", 
               lines="model_size", x="step", y="value")
```

### Complex Configuration
```python
config = FacetingConfig(
    rows="metric", cols="recipe", lines="model_size",
    row_order=["pile-valppl", "mmlu_avg"],
    col_order=["C4", "Dolma1.7", "FineWeb-Edu"], 
    lines_order=["4M", "6M", "8M", "10M"],
    x_labels=[["Steps", "Steps", "Training Steps"],
              ["Steps", "Steps", "Steps"]],
    shared_y="row"
)
fm.plot_faceted(data=df, plot_type="line", faceting=config, x="step", y="value")
```

### Layered Faceting  
```python
# Base layer
fm.plot_faceted(data=scatter_data, plot_type="scatter", 
               rows="metric", cols="recipe", lines="model_size",
               x="step", y="value", alpha=0.6)

# Overlay layer (config overrides for targeting)
fm.plot_faceted(data=trend_data, plot_type="line", 
               rows="metric", cols="recipe", lines="model_size",
               target_row=0, x="step", y="trend", linewidth=2)
```

This design provides maximum flexibility while maintaining simplicity for common cases and clear extensibility for future requirements.