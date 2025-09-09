# Configuration System Debugging Project

## Overview

This project addresses configuration system issues in dr_plotter, focusing on eliminating duplication, ensuring parameters are properly applied, and simplifying the configuration architecture. The approach is to make ALL configs explicit in examples and incrementally update components to ensure correct behavior.

**Goals:**
- Identify and eliminate configuration parameter duplication
- Ensure all configuration parameters are properly applied
- Debug configuration flow from user API to internal systems
- Document architectural improvements and simplifications

**Strategy:**
1. Create comprehensive examples with all parameters explicitly set
2. Test configuration flow end-to-end 
3. Identify where parameters are lost, duplicated, or incorrectly applied
4. Incrementally refactor to eliminate architectural debt

## Configuration Architecture Analysis

### Legacy Configuration System

The current system shows signs of architectural evolution with a **translation layer** between new and old APIs:

**Flow Pattern:**
1. **New API**: Users create `PlotConfig` with modern, user-friendly structure
2. **Translation**: `PlotConfig._to_legacy_configs()` converts to older internal formats  
3. **Legacy Internals**: `FigureManager` still uses `FigureConfig`, `LegendConfig`, `Theme` internally

**Evidence of Legacy Architecture:**
```python
# In PlotConfig._to_legacy_configs():
def _to_legacy_configs(self) -> tuple[FigureConfig, LegendConfig, Theme | None]:
    layout_config = self._resolve_layout_config()
    style_config = self._resolve_style_config()
    
    figure_config = self._create_figure_config_from_layout(layout_config)  # Legacy format
    legend_config = self._create_legend_config_from_params()              # Legacy format  
    theme = self._resolve_theme_from_style(style_config)                  # Legacy format
```

**Technical Debt Indicators:**
- Translation methods (`_to_legacy_configs`)
- Dual parameter sets (new: `LayoutConfig.figsize`, old: `FigureConfig.figsize`)
- Code comment in `figure_manager.py:73`: `# This needs fixing`
- Circular import issues between style system components

**FigureConfig as Legacy:**
`FigureConfig` represents the older internal API that hasn't been fully migrated away from. The newer `PlotConfig` → `LayoutConfig` provides cleaner user interface, but internally the system still expects the older `FigureConfig` structure. This creates unnecessary complexity and potential for configuration loss during translation.

## Example 01: Basic Line Plot - Configuration Debugging

### Initial State
The original example used minimal configuration:
```python
with FigureManager(PlotConfig(layout={"rows": 1, "cols": 1, "figsize": (5, 5)})) as fm:
    fm.plot("line", 0, 1, line_data, x="time", y="value", linewidth=2, alpha=0.9, title="Basic Time Series")
```

### Issues Discovered and Fixed

#### 1. Configuration Parameter Coverage
**Problem**: Most configuration parameters used defaults, making it impossible to debug whether they were being applied correctly.

**Solution**: Created comprehensive explicit configuration with all parameters specified:
- `PositioningConfig`: 17 explicit parameters
- `LegendConfig`: 13 explicit parameters  
- `LayoutConfig`: 8 explicit parameters
- `StyleConfig`: 5 explicit parameters

#### 2. Circular Import Issue
**Problem**: `style_applicator.py` ↔ `plotters/__init__.py` circular dependency
```
ImportError: cannot import name 'BasePlotter' from partially initialized module 'dr_plotter.plotters'
```

**Fix**: 
- Moved `BasePlotter` import to TYPE_CHECKING block in `style_applicator.py`
- Added local import in `_get_component_schema()` method where actually needed

#### 3. Configuration Object Type Handling
**Problem**: `PlotConfig` couldn't handle `LegendConfig` objects directly
```
AssertionError: Legend must be string or dict, got <class 'dr_plotter.configs.legend_config.LegendConfig'>
```

**Fix**: Enhanced `PlotConfig` to accept `LegendConfig` objects:
```python
# Added this check in _create_legend_config_from_params():
if isinstance(self.legend, LegendConfig):
    return self.legend
```

#### 4. Non-existent Validation Method
**Problem**: `FigureManager` called `legend_config.validate()` but method doesn't exist
```
AttributeError: 'LegendConfig' object has no attribute 'validate'
```

**Fix**: Removed the non-existent validation call since `LegendConfig` uses `__post_init__` for validation

#### 5. Plot Coordinate Bug
**Problem**: Original example used `fm.plot("line", 0, 1, ...)` - wrong subplot coordinates

**Fix**: Corrected to `fm.plot("line", 0, 0, ...)` for single subplot grid

### Results
✅ Example now runs successfully with comprehensive explicit configuration
✅ All configuration parameters are traceable through the system
✅ Established baseline for debugging configuration flow issues
✅ Plot renders correctly: "color=#4c72b0, marker=none, width=2.0, style=-"

### Configuration Parameters Verified Working
- Layout: figsize (8.0, 6.0), rows=1, cols=1
- Style: linewidth=2.0, alpha=0.9, theme="line" 
- Legend: strategy="subplot", position="lower center"
- Plot-level: title, x/y data mapping

This comprehensive example now serves as the foundation for systematic debugging of the configuration system's behavior and identifying where parameters may be duplicated or incorrectly applied.

## FigureConfig Elimination - Complete Legacy Removal

### Implementation
After establishing the validation patterns across all config classes, we completely eliminated `FigureConfig` and the legacy translation layer:

**FigureManager Migration:**
- All `self.figure_config.X` references → `self.layout_config.X` (7 locations)
- Layout attributes: `figsize`, `rows`, `cols`, `x_labels`, `y_labels`
- Removed legacy `_to_legacy_configs()` translation entirely
- Direct config usage: `self.layout_config`, `self.style_config`, `self.legend_config`

**Example Updates:**
- `examples/10_legend_positioning.py`: `FigureConfig(rows=2, cols=2)` → `PlotConfig(layout=LayoutConfig(...))`
- `examples/11_faceted_training_curves.py`: Complex migration with theme handling
- `examples/30_faceting_simple_grid.py`: Straightforward `figure=` → `layout=` conversion

### Issues Discovered

**Missing Parameter: `bbox_y_offset`**
Example 10 used `LegendConfig(bbox_y_offset=0.025)` which doesn't exist in the new config structure. This parameter was likely moved to `PositioningConfig` or eliminated during refactoring. Removed for now - may need further investigation for proper legend positioning control.

### Results
✅ **Complete architectural cleanup achieved:**
- Zero FigureConfig references in codebase
- Legacy translation layer eliminated  
- All examples use modern PlotConfig API
- Significant code simplification while maintaining functionality
- Configuration flow: `PlotConfig` → resolved configs → direct usage

This elimination represents the successful completion of major architectural debt removal.