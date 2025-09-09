# Memory Restoration Guide: Phase 2 FigureManager Parameter Organization Project

## Current State: Phase 2 Step 2 COMPLETED + Step 3 IN PROGRESS

**CRITICAL**: You were in the middle of conducting a FigureConfig Architecture Audit when memory compaction occurred.

## What We Just Completed: Legacy Bridge Removal ✅

### Major Achievement: Clean Config-First FigureManager
Just successfully completed **Phase 2 Step 2: Legacy Bridge Removal** with these results:

**Removed (~100 lines of legacy code)**:
- ✅ `_convert_legacy_legend_params()` method - completely deleted
- ✅ `_build_legend_config()` method - completely deleted  
- ✅ All individual parameters from constructor (rows, cols, legend_strategy, plot_margin_bottom, etc.)

**Created Clean New Architecture**:
```python
# NEW FigureManager constructor (config-only)
def __init__(
    self,
    layout: Optional[SubplotLayoutConfig] = None,
    legend: Optional[LegendConfig] = None, 
    figure: Optional[FigureConfig] = None,
    theme: Optional[Any] = None,
    faceting: Optional[SubplotFacetingConfig] = None,
) -> None:

# NEW FigureConfig class created
@dataclass
class FigureConfig:
    figsize: Tuple[int, int] = (12, 8)
    plot_margin_top: float = 0.1
    plot_margin_bottom: float = 0.1
    plot_margin_left: float = 0.1
    plot_margin_right: float = 0.1
    
    figure_kwargs: Dict[str, Any] = field(default_factory=dict)
    subplot_kwargs: Dict[str, Any] = field(default_factory=dict)
    axes_kwargs: Dict[str, Any] = field(default_factory=dict)
    plotter_kwargs: Dict[str, Any] = field(default_factory=dict)
    
    external_ax: Optional[plt.Axes] = None
    shared_styling: Optional[bool] = None
```

**Status Verified**:
- ✅ Legacy methods completely gone (grep confirmed)
- ✅ Old parameters rejected with TypeError 
- ✅ New config-first API works perfectly
- ✅ Figsize routing fixed and working
- ✅ All examples now break (as expected - no backwards compatibility)

## Current Task: FigureConfig Architecture Audit 🔍

**YOU WERE INTERRUPTED** while executing: `@docs/plans/figureconfig-architecture-audit-prompt.md`

### The Question We're Investigating
**Our Parameter Classification Rule**:
- **Explicit parameters**: Only for parameters that DON'T map directly to single matplotlib function call
- **Kwargs dictionaries**: Only for direct matplotlib function parameters

**Key Concern**: Should `nrows`, `ncols`, `figsize` be explicit parameters or in `subplot_kwargs`?

### What You Had Started
**TodoWrite shows**: "Execute FigureConfig Architecture Audit - validating parameter classification and identifying side effects" - **IN PROGRESS**

**Your Investigation Progress**:
- ✅ Started matplotlib function call analysis
- ✅ Found `plt.subplots()` usage in figure.py:102-103
- ✅ Found multiple `tight_layout()` calls with `rect` and `pad` parameters
- ✅ Identified that `figsize` is currently explicit (not in kwargs) in our implementation
- 🚧 **INTERRUPTED** during comprehensive side effects analysis

### Critical Findings So Far
**Matplotlib Function Calls Found**:
1. `plt.subplots(layout.rows, layout.cols, constrained_layout=False, **combined_kwargs)` 
2. Multiple `fig.tight_layout(rect=..., pad=self._layout_pad)` calls
3. `figsize` handling: Currently explicit but gets merged into combined_kwargs

**Key Architecture Question**: 
- Current impl: `figsize` is explicit parameter passed separately to `_create_figure_axes()`
- Proposed audit: Should `figsize`, `nrows`, `ncols` be in `subplot_kwargs` instead?

## What You Need to Continue

### Resume Investigation Points
1. **Parameter extraction side effects**: How does FigureManager use `self.rows` and `self.cols`?
2. **Integration impact**: Do themes, legends, plotters need explicit access to grid dimensions?
3. **Usability assessment**: Is `subplot_kwargs={'nrows': 2, 'ncols': 4}` intuitive vs explicit params?

### Files to Examine
- `src/dr_plotter/figure.py` - FigureManager matplotlib integration
- `src/dr_plotter/plotters/base.py` - Plotter grid dimension usage
- Examples that use grid dimensions for validation

### Expected Output
Create `/docs/figureconfig-architecture-audit.md` with:
- Complete matplotlib function call inventory
- Missing explicit parameters analysis  
- Side effects assessment of kwargs extraction approach
- Final recommendation on architecture validation

## Strategic Context
This audit will determine if our current FigureConfig architecture is sound or needs modification before we migrate all 20+ examples to the new API. **The decision affects the entire parameter organization foundation.**

## Command to Resume
Pick up exactly where you left off with the comprehensive audit investigation, focusing on parameter extraction complexity and integration impact analysis.