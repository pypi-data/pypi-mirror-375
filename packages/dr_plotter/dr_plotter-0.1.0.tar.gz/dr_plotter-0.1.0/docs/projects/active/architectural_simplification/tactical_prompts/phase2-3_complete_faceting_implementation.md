# Tactical Agent Prompt: Phase 2+3 Complete Faceting Implementation

**Agent Type**: general-purpose  
**Task**: Complete architectural replacement of faceting system in single atomic operation  
**Expected Output**: Working simplified faceting system with 80% code reduction

## Mission Objective

Execute complete immediate transition from over-engineered 6-module faceting system (750 lines) to simplified 2-module system (150 lines) while preserving all sophisticated functionality. This is an atomic replacement - delete old system and implement new system in single session with no intermediate broken states.

## Strategic Context

**Reference Documents**:
- `docs/projects/active/architectural_simplification/audit_reports/faceting_system_audit_report.md` - detailed implementation guidance
- `docs/projects/active/architectural_simplification/implementation_plans/faceting_system_complete_replacement.md` - strategic objectives

**Key Principles**:
- **Architectural Courage**: Complete elimination of old system, no compatibility layers
- **Leave No Trace**: Delete replaced code completely  
- **Preserve Sophisticated Value**: Multi-variable faceting, style coordination, advanced targeting
- **Direct Implementation**: Simple assertions, direct pandas/matplotlib operations

## Implementation Sequence

### Step 1: Preserve Current Integration Interface
**Action**: Document the exact external API that must be maintained
**Focus**:
- Read `src/dr_plotter/figure.py` to understand `plot_faceted()` method integration
- Document `FacetingConfig` parameters that must work identically
- Note any other external usage patterns found in audit

**Critical**: The replacement must maintain identical external interface behavior.

### Step 2: Complete Module Deletion
**Action**: Delete all 6 existing faceting modules atomically
**Files to Delete**:
```bash
rm src/dr_plotter/faceting/types.py                # 16 lines - unnecessary types
rm src/dr_plotter/faceting/data_analysis.py        # 71 lines - over-modularized  
rm src/dr_plotter/faceting/data_preparation.py     # 154 lines - over-abstracted
rm src/dr_plotter/faceting/grid_computation.py     # 131 lines - premature optimization
rm src/dr_plotter/faceting/validation.py           # 252 lines - defensive anti-pattern
rm src/dr_plotter/faceting/style_coordination.py   # 128 lines - will be replaced
```

**Result**: Completely empty `src/dr_plotter/faceting/` directory except `__init__.py`

### Step 3: Create Unified Core Module
**Action**: Create `src/dr_plotter/faceting/faceting_core.py` (~150-200 lines)

**Implementation Pattern** (from audit recommendations):
```python
from typing import Dict, Tuple, Optional, List, Any
import pandas as pd

def prepare_faceted_subplots(
    data: pd.DataFrame,
    config: 'FacetingConfig', 
    grid_shape: Tuple[int, int]
) -> Dict[Tuple[int, int], pd.DataFrame]:
    # REPLACE: data_analysis.py + data_preparation.py + grid_computation.py + types.py
    rows, cols = grid_shape
    
    # Direct dimension extraction (no analyze_data_dimensions)
    row_values = sorted(data[config.rows].unique()) if config.rows else [None]
    col_values = sorted(data[config.cols].unique()) if config.cols else [None]
    
    # Direct subsetting (no complex grid types)
    subsets = {}
    for r, row_val in enumerate(row_values):
        for c, col_val in enumerate(col_values):
            # Apply filters directly using pandas query
            filters = {}
            if row_val is not None: filters[config.rows] = row_val
            if col_val is not None: filters[config.cols] = col_val
            
            if filters:
                # Use pandas query for clean filtering
                query_parts = [f"`{k}` == @filters['{k}']" for k in filters]
                subset = data.query(' and '.join(query_parts))
            else:
                subset = data
                
            if not subset.empty:
                subsets[(r, c)] = subset
    
    return subsets

def plot_faceted_data(
    fm: 'FigureManager',
    data_subsets: Dict[Tuple[int, int], pd.DataFrame],
    plot_type: str, 
    config: 'FacetingConfig',
    style_coordinator: 'FacetStyleCoordinator',
    **kwargs
) -> None:
    # REPLACE: Complex plotting coordination logic
    # Direct matplotlib operations, no dual pipelines
    
    for (row, col), subplot_data in data_subsets.items():
        ax = fm.get_axes(row, col)
        
        # Get consistent styling if hue/lines dimension specified
        if config.lines:  # Will be renamed to 'hue' in interface
            for hue_value in subplot_data[config.lines].unique():
                hue_data = subplot_data[subplot_data[config.lines] == hue_value]
                plot_kwargs = style_coordinator.get_consistent_style(config.lines, hue_value)
                plot_kwargs.update(kwargs)
                
                # Direct plotting call
                getattr(ax, plot_type)(
                    hue_data[config.x], hue_data[config.y], 
                    **plot_kwargs
                )
        else:
            # Single series plotting
            getattr(ax, plot_type)(
                subplot_data[config.x], subplot_data[config.y], 
                **kwargs
            )
```

**Key Requirements**:
- **Direct pandas operations**: No `analyze_data_dimensions()` abstraction
- **Simple assertions**: Replace 252 lines of validation.py with basic asserts
- **Unified data preparation**: Single function replaces 4 modules
- **No performance optimization complexity**: Remove caching, thresholds, dual pipelines

### Step 4: Create Simplified Style Coordination
**Action**: Create `src/dr_plotter/faceting/style_coordination.py` (~80-100 lines)

**Implementation Pattern**:
```python
from typing import Dict, Any
import matplotlib.pyplot as plt

class FacetStyleCoordinator:
    # PRESERVE: Genuine value for professional output
    # SIMPLIFY: Remove LRU caching and complex coordination layers
    
    def __init__(self, theme: Optional[str] = None) -> None:
        self._style_assignments: Dict[str, Dict[Any, Dict[str, Any]]] = {}
        self._color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
        self._color_index = 0
        
    def get_consistent_style(self, dimension: str, value: Any) -> Dict[str, Any]:
        # Ensure same dimension value gets same style across all subplots
        if dimension not in self._style_assignments:
            self._style_assignments[dimension] = {}
            
        if value not in self._style_assignments[dimension]:
            # Assign next style in cycle
            color = self._color_cycle[self._color_index % len(self._color_cycle)]
            self._color_index += 1
            self._style_assignments[dimension][value] = {'color': color}
            
        return self._style_assignments[dimension][value].copy()
```

**Key Requirements**:
- **Preserve style coordination value**: Consistent colors across subplots
- **Remove caching complexity**: No LRU eviction logic
- **Direct matplotlib integration**: Use plt.rcParams directly
- **Professional output**: Maintain publication-ready visual consistency

### Step 5: Update Integration Points
**Action**: Modify `src/dr_plotter/figure.py` plot_faceted method

**Implementation Pattern**:
```python
def plot_faceted(
    self,
    data: pd.DataFrame,
    plot_type: str,
    faceting: Optional[FacetingConfig] = None, 
    **kwargs,
) -> None:
    # REPLACE: Complex dual pipeline with simple single path
    
    # Simple assertions replace 252 lines of validation.py
    assert not data.empty, "Cannot facet empty DataFrame"
    
    config = faceting or FacetingConfig()
    assert config.rows or config.cols, "Must specify rows or cols for faceting"
    
    # Direct grid calculation (no compute_grid_layout_metadata)
    n_rows = len(data[config.rows].unique()) if config.rows else 1
    n_cols = len(data[config.cols].unique()) if config.cols else 1
    
    # Prepare data subsets 
    from .faceting.faceting_core import prepare_faceted_subplots, plot_faceted_data
    from .faceting.style_coordination import FacetStyleCoordinator
    
    data_subsets = prepare_faceted_subplots(data, config, (n_rows, n_cols))
    
    # Style coordination for consistent appearance
    style_coordinator = FacetStyleCoordinator()
    if config.lines:  # Register dimension values for consistency
        all_values = data[config.lines].unique()
        for value in all_values:
            style_coordinator.get_consistent_style(config.lines, value)
    
    # Execute plotting
    plot_faceted_data(self, data_subsets, plot_type, config, style_coordinator, **kwargs)
```

**Key Requirements**:
- **Preserve external interface**: `plot_faceted(data, plot_type, faceting, **kwargs)` unchanged
- **Single execution path**: Remove dual pipeline complexity  
- **Direct assertions**: Replace defensive validation with fail-fast approach
- **Clean integration**: Import from new modules

### Step 6: Update Module Exports
**Action**: Rewrite `src/dr_plotter/faceting/__init__.py`

**New Exports**:
```python
from .faceting_core import prepare_faceted_subplots, plot_faceted_data
from .style_coordination import FacetStyleCoordinator

__all__ = [
    "prepare_faceted_subplots",
    "plot_faceted_data", 
    "FacetStyleCoordinator",
]
```

**Key Requirements**:
- **Minimal exports**: Only functions actually needed by figure.py
- **No legacy functions**: Complete elimination of old abstractions
- **Clean interface**: Clear separation of concerns

### Step 7: Functionality Verification  
**Action**: Test with real examples to ensure working functionality

**Test Cases**:
```bash
# Test basic functionality
cd /Users/daniellerothermel/drotherm/repos/dr_plotter
uv run python examples/faceting/simple_grid.py

# Should produce:
# - Correct 2×2 grid layout (data recipes × model sizes)  
# - Consistent seed coloring across all subplots
# - Professional visual output with proper axis labels
# - No errors or exceptions
```

**Success Criteria**:
- ✅ Example runs without errors
- ✅ Visual output matches expected professional quality
- ✅ Multi-variable faceting works: rows="data", cols="params", lines="seed"
- ✅ Style coordination preserves consistent colors
- ✅ Integration with FigureManager works seamlessly

### Step 8: Cleanup and Documentation
**Action**: Remove any remaining legacy references

**Tasks**:
- Search codebase for any remaining imports of deleted functions
- Update any other examples that might import old faceting functions  
- Verify no broken imports anywhere in codebase
- Document the new simplified architecture

## Implementation Standards

### Code Quality Requirements
- **Follow project code style**: No comments, comprehensive type hints, assertions not exceptions
- **Direct implementation**: Use pandas and matplotlib APIs directly, no unnecessary abstractions
- **Single responsibility**: Each function has clear, focused purpose
- **Self-documenting**: Clear names that explain intent without comments

### Architectural Standards  
- **Atomicity**: Complete replacement in single session, no intermediate broken states
- **Minimalism**: Preserve only essential functionality, eliminate all unnecessary complexity
- **Direct operations**: `data[col].unique()` instead of `analyze_data_dimensions()`
- **Fail fast**: Simple assertions with clear messages instead of defensive validation

### Preservation Requirements
- **Sophisticated functionality**: Multi-variable faceting, style coordination, advanced targeting must work identically
- **External interface**: `FigureManager.plot_faceted()` behavior unchanged for users
- **Professional output**: Visual quality maintained across all subplot configurations
- **FacetingConfig compatibility**: Core parameters (rows, cols, lines, x, y) work identically

## Success Criteria

### Functional Success ✅
- [ ] `examples/faceting/simple_grid.py` runs successfully and produces expected output
- [ ] Multi-variable faceting works: `rows="data", cols="params", lines="seed"`  
- [ ] Style coordination maintained: consistent colors across subplots
- [ ] Advanced targeting functional: selective subplot population
- [ ] Professional visual output: publication-ready appearance

### Architectural Success ✅
- [ ] 80% code reduction: 750 lines → ~150 lines
- [ ] Module consolidation: 6 modules → 2 focused modules  
- [ ] Complexity elimination: No validation.py, types.py, data_analysis.py, grid_computation.py
- [ ] Direct implementation: No unnecessary abstraction layers
- [ ] Single execution path: No dual pipelines or performance optimization complexity

### Integration Success ✅
- [ ] `FigureManager.plot_faceted()` interface preserved exactly
- [ ] All imports work correctly after replacement
- [ ] No broken dependencies anywhere in codebase
- [ ] Clean module exports with minimal API surface

## Risk Mitigation

### Rollback Plan
- **Git checkpoint**: Commit current state before starting implementation
- **Atomic replacement**: If any step fails, complete rollback possible
- **Test-driven**: Functionality verification before declaring success

### Quality Assurance
- **Comprehensive testing**: Run all faceting examples, not just simple_grid.py
- **Integration verification**: Ensure figure.py integration works correctly
- **Code review**: Verify new implementation follows project standards
- **Performance check**: Ensure simplified system performs adequately

## Expected Deliverables

1. **Two new focused modules**:
   - `src/dr_plotter/faceting/faceting_core.py` (~150-200 lines)
   - `src/dr_plotter/faceting/style_coordination.py` (~80-100 lines)

2. **Updated integration**:
   - Modified `src/dr_plotter/figure.py` plot_faceted method
   - Rewritten `src/dr_plotter/faceting/__init__.py`

3. **Verification results**:
   - Successful run of `examples/faceting/simple_grid.py`
   - Documentation of any discovered issues or improvements

4. **Implementation report**:
   - Code reduction metrics (before/after line counts)
   - Functionality preservation verification
   - Any deviations from audit recommendations and reasons

---

**Critical Success Factor**: This implementation must achieve complete architectural simplification while maintaining identical user-facing functionality. The replacement system should feel simpler to maintain while providing the same sophisticated faceting capabilities to users.

**Key Implementation Insight**: Trust the audit findings - the sophisticated value lies in style coordination and multi-dimensional positioning, not in elaborate validation and optimization systems. Implement with architectural courage.