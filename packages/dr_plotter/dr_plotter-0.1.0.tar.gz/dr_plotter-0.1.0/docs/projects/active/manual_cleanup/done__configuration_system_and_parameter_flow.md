# Completed: Configuration System and Parameter Flow Fixes

## Theme-to-Matplotlib Parameter Flow Issue - RESOLVED

### Problem Discovered
**Root Issue**: Theme values for matplotlib-specific parameters were not being passed to matplotlib plotting functions, causing a disconnect between theme configuration and actual plot behavior.

**Specific Example**: 
- `VIOLIN_THEME` sets `showmeans=True` 
- `ViolinPlotter._collect_artists_to_style()` expected `cmeans` to exist in matplotlib's return dictionary
- But matplotlib's `violinplot()` never received `showmeans=True`, so it used default `showmeans=False`
- Result: `KeyError: 'cmeans'` when trying to style non-existent parts

**Architecture Gap**: 
- `_filtered_plot_kwargs` only includes user-provided kwargs, not theme values
- Theme values live in the styler system but never reach matplotlib
- Each plotter likely has this same bug for their matplotlib-specific parameters

### Solution Implemented

**1. Created `BasePlotter._build_plot_args()` method** (lines 223-233 in base.py):
```python
def _build_plot_args(self) -> Dict[str, Any]:
    main_plot_params = self.component_schema.get("plot", {}).get("main", set())
    plot_args = {}
    for key in main_plot_params:
        if key in self._filtered_plot_kwargs:
            plot_args[key] = self._filtered_plot_kwargs[key]  # User precedence
        else:
            style = self.styler.get_style(key)
            if style is not None:
                plot_args[key] = style  # Theme fallback
    return plot_args
```

**Key Design Principles**:
- Uses existing `component_schema["plot"]["main"]` to define matplotlib parameters
- Proper precedence: user kwargs > theme values > matplotlib defaults
- Generic solution that works for all plotters automatically

**2. Handled Parameter Conflicts in ViolinPlotter** (lines 170-175):
- Manual positioning parameters (`positions`, `widths`) can conflict with theme values
- Solution: Use theme/user values when available, fall back to calculated values
- Warn users when their settings override calculated positioning

### Testing Strategy

**Verification Method**:
```python
# Before fix
plotter._filtered_plot_kwargs  # Empty or missing theme values
# After fix  
plotter._build_plot_args()     # Should include theme values
```

**Visual Test**: Create plots with theme defaults vs. explicit user overrides to verify precedence works correctly.

## Artist Property Extraction Utilities - COMPLETED

### Problem Discovered
**Duplicate Logic**: Found that `ViolinPlotter._create_proxy_artist_from_bodies()` and `plot_data_extractor.extract_colors()` were doing very similar matplotlib artist property extraction, but with different approaches:

**Violin Plotter Approach** (original, 39 lines):
- Complex nested conditionals for color extraction
- Error fallbacks to `get_error_color()` that hide bugs
- Manual array/color handling with defensive programming
- Duplicated logic for facecolor and edgecolor extraction

**Plot Data Extractor Approach** (cleaner):
- Uses `mcolors.to_rgba()` for consistent conversion
- Clear assertions that fail fast when expectations violated
- Systematic handling of matplotlib artist types
- Much more concise and maintainable

### Solution Implemented

**1. Created `src/dr_plotter/artist_utils.py`** with atomic extraction functions:
```python
def extract_facecolor_from_polycollection(obj: PolyCollection) -> RGBA
def extract_edgecolor_from_polycollection(obj: PolyCollection) -> RGBA  
def extract_alpha_from_artist(obj) -> float
def extract_single_color_from_polycollection_list(bodies: List[PolyCollection]) -> RGBA
# ... etc
```

**Key Design Principles**:
- **Atomic responsibilities**: Each function does one specific extraction
- **Fail fast**: Use assertions instead of error fallbacks
- **Consistent conversion**: Always use `mcolors.to_rgba()` for color handling
- **Clear naming**: Function names explicitly describe what they extract and from what

**2. Updated existing code to use shared utilities**:
- **ViolinPlotter**: `_create_proxy_artist_from_bodies()` reduced from 39 to 8 lines
- **plot_data_extractor**: `extract_colors()` now uses shared `extract_colors_from_polycollection()`

## Upfront Parameter Validation - REJECTED

### Decision: Let Matplotlib Handle Parameter Validation

**Why Manual Validation Was Rejected**:
1. **Matplotlib already validates**: `ax.scatter(s="invalid")` fails immediately with clear errors
2. **Redundant maintenance**: `NUMERIC_PARAMS`/`STRING_PARAMS` lists would grow huge and get out of sync with matplotlib
3. **Not adding value**: Matplotlib's error messages are already good: "could not convert string to float"
4. **Defensive programming**: Manual validation is just defensive programming at a different level

**The Real Solution**:
The original problem wasn't **lack of validation** - it was **buried fallback logic** that hid configuration issues:

```python
# BAD: Hidden fallback that masks real problems
base_size * size_mult if isinstance(base_size, (int, float)) else 50 * size_mult

# GOOD: Let matplotlib validate naturally  
base_size * size_mult  # Fails fast and clear if base_size is invalid
```

**Architectural Principle**: 
- **Eliminate defensive programming** patterns that hide issues
- **Let specialized libraries do what they do best** (matplotlib validates parameters)
- **Focus on real architectural improvements** like parameter flow via `_build_plot_args()`

**Result**: Cleaner code with natural fail-fast behavior and no maintenance overhead.

## Final Configuration System Design - FULLY IMPLEMENTED ✅

### Core Problem SOLVED
Current plotters had **four different configuration pathways** for the same initial kwargs:
1. `theme → _build_plot_args()` (inconsistently used)
2. `kwargs → _filtered_plot_kwargs` (over/under filtering issues)  
3. `kwargs → get_component_styles()` (grouped rendering)
4. `kwargs → direct processing` (bypasses theme integration)

**Result**: Theme values don't reach matplotlib, inconsistent precedence, parameter flow bugs.

### Minimal Solution Architecture - IMPLEMENTED

**Single Configuration Resolution Method:**
```python
def _resolve_phase_config(self, phase: str, **context: Any) -> dict[str, Any]:
    """Resolve configuration for a specific phase using component schema"""
    phase_params = self.component_schema.get("plot", {}).get(phase, set())
    config = {}
    
    for param in phase_params:
        # Clear precedence: Context → User → Theme
        value = (
            context.get(param) or
            self.kwargs.get(f"{phase}_{param}") or    # "scatter_alpha" 
            self.kwargs.get(param) or                 # "alpha"
            self.styler.get_style(f"{phase}_{param}") or  # theme: "scatter_alpha"
            self.styler.get_style(param)                   # theme: "alpha"
        )
        
        if value is not None:
            config[param] = value
    
    # Add computed parameters (size arrays, positioning, etc.)
    config.update(self._resolve_computed_parameters(phase, context))
    return config

def _resolve_computed_parameters(self, phase: str, context: dict) -> dict[str, Any]:
    """Handle data-dependent computation (plotter-specific override)"""
    return {}  # Base implementation - plotters override as needed
```

**Usage Pattern Examples:**
```python
# Simple single-phase (BarPlotter, ViolinPlotter)
def _draw(self, ax: Any, data: pd.DataFrame, **context: Any) -> None:
    config = self._resolve_phase_config("main", **context)
    patches = ax.bar(data[X], data[Y], **config)

# Multi-phase (ContourPlotter)  
def _draw(self, ax: Any, data: pd.DataFrame, **context: Any) -> None:
    contour_config = self._resolve_phase_config("contour", **context)
    scatter_config = self._resolve_phase_config("scatter", **context)
    
    contour = ax.contour(xx, yy, Z, **contour_config)
    ax.scatter(data[X], data[Y], **scatter_config)

# Multi-trajectory (BumpPlotter)
def _draw(self, ax: Any, data: pd.DataFrame, **context: Any) -> None:
    for trajectory in self.trajectory_data:
        traj_context = {**context, "trajectory_data": trajectory}
        config = self._resolve_phase_config("main", **traj_context)
        ax.plot(trajectory[time], trajectory[value], **config)
```

### Implementation Status - COMPLETE ✅

**✅ ViolinPlotter (COMPLETED)**
- Uses `_resolve_phase_config("main", **kwargs)` for all matplotlib parameters
- Theme values reach matplotlib correctly (e.g. `showmeans=True` from VIOLIN_THEME)
- User overrides work for all value types including `False` (critical falsy value fix)
- Conditional component collection based on configuration (cbars, cmeans, etc.)
- Violin showcase runs without errors, all tests pass

**✅ All Plotters Successfully Converted:**
- [x] ViolinPlotter (COMPLETED) - First plotter to use the new system
- [x] BarPlotter (COMPLETED) - Single phase implementation
- [x] ScatterPlotter (COMPLETED) - Using computed parameters for sizes
- [x] LinePlotter (COMPLETED) - Simple implementation
- [x] HistogramPlotter (COMPLETED) - Single phase, simple implementation
- [x] HeatmapPlotter (COMPLETED) - Single phase implementation with post-processing
- [x] BumpPlotter (COMPLETED) - Multi-trajectory implementation with trajectory-specific overrides
- [x] ContourPlotter (COMPLETED) - Multi-phase implementation for contour and scatter phases

**🎉 All Plotters Successfully Converted!**

### Final Implementation Pattern (PROVEN)

```python
# In BasePlotter - IMPLEMENTED ✅
def _resolve_phase_config(self, phase: str, **context: Any) -> dict[str, Any]:
    phase_params = self.component_schema.get("plot", {}).get(phase, set())
    config = {}
    
    for param in phase_params:
        sources = [
            lambda k: context.get(k),                           # Highest precedence
            lambda k: self.kwargs.get(f"{phase}_{k}"),         # Phase-specific user
            lambda k: self.kwargs.get(k),                      # General user
            lambda k: self.styler.get_style(f"{phase}_{k}"),   # Phase-specific theme  
            lambda k: self.styler.get_style(k),                # General theme (lowest)
        ]
        
        for source in sources:
            value = source(param)
            if value is not None:
                config[param] = value
                break
    
    config.update(self._resolve_computed_parameters(phase, context))
    return config

def _resolve_computed_parameters(self, phase: str, context: dict) -> dict[str, Any]:
    return {}  # Override in plotters that need computed parameters

# Usage in plotters - PROVEN ✅
def _draw(self, ax: Any, data: pd.DataFrame, **context: Any) -> None:
    config = self._resolve_phase_config("main", **context)
    parts = ax.violinplot(datasets, **config)  # Theme + user values reach matplotlib
```

### Success Criteria - ALL COMPLETED ✅
- [x] **ViolinPlotter converted** - using `_resolve_phase_config()` ✅
- [x] **Theme values reach matplotlib** - `showmeans=True` creates `cmeans` ✅  
- [x] **Falsy value handling fixed** - `showmeans=False` properly overrides theme ✅
- [x] **Single source of truth** - all parameters flow through one method ✅
- [x] **Defensive programming eliminated** - cbars handling based on config not existence ✅
- [x] **All plotters converted** - BarPlotter, ScatterPlotter, LinePlotter, HistogramPlotter, HeatmapPlotter, BumpPlotter, ContourPlotter now using new system ✅
- [x] **Multi-phase plotters** - ContourPlotter working cleanly with separate phases ✅
- [x] Remove deprecated `_build_plot_args()` method now that all plotters are converted ✅

## Summary

This comprehensive effort successfully resolved the core architectural issues around configuration and parameter flow in the dr_plotter system:

1. **Unified Configuration System**: All plotters now use the same `_resolve_phase_config()` method
2. **Theme Integration**: Theme values properly reach matplotlib functions  
3. **Parameter Precedence**: Clear, consistent precedence hierarchy across all plotters
4. **Defensive Programming Elimination**: Fail-fast approach surfaces real issues
5. **Code Consolidation**: Artist extraction utilities eliminate duplication
6. **Architectural Courage**: Rejected defensive validation in favor of clean, matplotlib-native approaches

**Result**: A dramatically more maintainable, consistent, and robust plotting system that properly integrates themes with matplotlib while maintaining clear separation of concerns.