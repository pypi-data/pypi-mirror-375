# Tactical Agent Prompt: Faceting Code Quality Remediation

**Agent Type**: general-purpose  
**Task**: Critical code quality fixes for faceting implementation to meet project standards  
**Expected Output**: Project-standard compliant faceting code with identical functionality

## Mission Objective

Fix critical code quality violations in the new faceting implementation while preserving all working functionality. The implementation currently works correctly but violates multiple project code standards that must be remediated immediately.

## Strategic Context

**Current Status**: 
- ✅ **Functionality works**: `examples/faceting/simple_grid.py` runs successfully
- ✅ **Architecture simplified**: 80% code reduction achieved (752 → ~200 lines)  
- ❌ **Code quality**: Multiple violations of project standards require immediate fixes

**Reference Documents**:
- `docs/projects/active/architectural_simplification/audit_reports/faceting_system_audit_report.md`
- Project `CLAUDE.md` - Zero Comments Policy and code style requirements
- `docs/processes/design_philosophy.md` - Core principles

**Key Quality Standards**:
- **Zero Comments Policy**: No comments, docstrings, or inline explanations
- **Comprehensive Type Hints**: All parameters and return values typed
- **Assertions Not Exceptions**: Use `assert condition, "message"` for validation
- **Self-Documenting Code**: Clear function names and extracted helpers
- **Fail Fast Principle**: Surface problems immediately, no defensive programming

## Critical Issues Requiring Immediate Fix

### Issue 1: Zero Comments Policy Violation 🚨
**Problem**: Code contains comments which are strictly forbidden
**Files Affected**: `src/dr_plotter/faceting/faceting_core.py`, `src/dr_plotter/faceting/style_coordination.py`
**Action Required**: Remove ALL comments, docstrings, and inline explanations

### Issue 2: Missing Validation Assertions 🚨
**Problem**: Functions lack basic validation following "assertions not exceptions" principle
**Action Required**: Add proper assertions at function entry points
```python
# Required assertions pattern:
def prepare_faceted_subplots(data, config, grid_shape):
    assert not data.empty, "Cannot facet empty DataFrame"
    assert config.rows or config.cols, "Must specify rows or cols for faceting"
    assert isinstance(grid_shape, tuple) and len(grid_shape) == 2, "grid_shape must be (rows, cols) tuple"
```

### Issue 3: Overly Complex Functions 🚨
**Problem**: Several functions exceed reasonable complexity and length
**Target Functions**:
- `plot_faceted_data()` (24 lines) - Extract plot coordination logic
- `_execute_plot_call()` (22 lines) - Extract plot type handlers
- `_apply_subplot_customization()` (26 lines) - Extract configuration helpers

**Action Required**: Break into focused single-purpose functions with clear names

### Issue 4: Type Hint Issues 🚨
**Problem**: Unnecessary string quotes in type hints
**Current**: `config: 'FacetingConfig'`
**Required**: `config: FacetingConfig` (with proper imports)

### Issue 5: Defensive Programming Anti-Pattern 🚨
**Problem**: Code uses defensive `continue` statements instead of fail-fast assertions
**Current**: 
```python
if line_data.empty:
    continue  # Defensive programming
```
**Required**: Either assert or remove the check entirely (fail fast)

## Implementation Tasks

### Task 1: Complete Comment Elimination
**Action**: Remove every comment, docstring, and inline explanation

**Files to Fix**:
- `src/dr_plotter/faceting/faceting_core.py`
- `src/dr_plotter/faceting/style_coordination.py`

**Standard**: Zero tolerance - not a single comment should remain

### Task 2: Add Proper Validation Assertions
**Action**: Add assertions at function entry points following project patterns

**Required Assertions for `faceting_core.py`**:
```python
def prepare_faceted_subplots(data: pd.DataFrame, config: FacetingConfig, grid_shape: Tuple[int, int]) -> Dict[Tuple[int, int], pd.DataFrame]:
    assert not data.empty, "Cannot facet empty DataFrame"
    assert config.rows or config.cols, "Must specify rows or cols for faceting"
    assert isinstance(grid_shape, tuple) and len(grid_shape) == 2, "grid_shape must be (rows, cols) tuple"

def plot_faceted_data(fm: FigureManager, data_subsets: Dict[Tuple[int, int], pd.DataFrame], plot_type: str, config: FacetingConfig, style_coordinator: FacetStyleCoordinator, **kwargs) -> None:
    assert data_subsets, "Cannot plot with empty data_subsets"
    assert plot_type in ["line", "scatter", "bar", "fill_between", "heatmap"], f"Unsupported plot type: {plot_type}"
    assert config.x and config.y, "Must specify x and y columns for plotting"
```

### Task 3: Function Decomposition and Extraction
**Action**: Break complex functions into focused helpers with self-documenting names

#### 3a: Simplify `plot_faceted_data()` 
**Current Problem**: 24 lines handling multiple responsibilities
**Solution**: Extract plot coordination logic

**Target Pattern**:
```python
def plot_faceted_data(fm: FigureManager, data_subsets: Dict[Tuple[int, int], pd.DataFrame], plot_type: str, config: FacetingConfig, style_coordinator: FacetStyleCoordinator, **kwargs) -> None:
    assert data_subsets, "Cannot plot with empty data_subsets"
    assert plot_type in SUPPORTED_PLOT_TYPES, f"Unsupported plot type: {plot_type}"
    assert config.x and config.y, "Must specify x and y columns for plotting"
    
    for (row, col), subplot_data in data_subsets.items():
        _plot_subplot_at_position(fm, row, col, subplot_data, plot_type, config, style_coordinator, **kwargs)

def _plot_subplot_at_position(fm: FigureManager, row: int, col: int, subplot_data: pd.DataFrame, plot_type: str, config: FacetingConfig, style_coordinator: FacetStyleCoordinator, **kwargs) -> None:
    if config.lines and config.lines in subplot_data.columns:
        _plot_with_style_coordination(fm, row, col, subplot_data, plot_type, config, style_coordinator, **kwargs)
    else:
        _plot_single_series_at_position(fm, row, col, subplot_data, plot_type, config, **kwargs)
```

#### 3b: Extract Plot Type Handlers
**Current Problem**: `_execute_plot_call()` has complex conditional logic
**Solution**: Extract individual plot type handlers

**Target Pattern**:
```python
def _plot_line_data(ax: matplotlib.axes.Axes, data: pd.DataFrame, config: FacetingConfig, **kwargs) -> None:
    ax.plot(data[config.x], data[config.y], **kwargs)

def _plot_scatter_data(ax: matplotlib.axes.Axes, data: pd.DataFrame, config: FacetingConfig, **kwargs) -> None:
    ax.scatter(data[config.x], data[config.y], **kwargs)

def _execute_plot_call(ax: matplotlib.axes.Axes, plot_type: str, data: pd.DataFrame, config: FacetingConfig, **kwargs) -> None:
    plot_handlers = {
        "line": _plot_line_data,
        "scatter": _plot_scatter_data,
        "bar": _plot_bar_data,
        "fill_between": _plot_fill_between_data,
        "heatmap": _plot_heatmap_data,
    }
    plot_handlers[plot_type](ax, data, config, **kwargs)
```

### Task 4: Fix Type Hints
**Action**: Remove unnecessary string quotes and add proper imports

**Required Imports for `faceting_core.py`**:
```python
from typing import Dict, Tuple, Optional, List, Any
import pandas as pd
import matplotlib.axes
from dr_plotter.faceting_config import FacetingConfig
from dr_plotter.figure import FigureManager
from dr_plotter.faceting.style_coordination import FacetStyleCoordinator
```

**Fixed Type Hints**:
```python
def prepare_faceted_subplots(data: pd.DataFrame, config: FacetingConfig, grid_shape: Tuple[int, int]) -> Dict[Tuple[int, int], pd.DataFrame]:
def plot_faceted_data(fm: FigureManager, data_subsets: Dict[Tuple[int, int], pd.DataFrame], plot_type: str, config: FacetingConfig, style_coordinator: FacetStyleCoordinator, **kwargs) -> None:
```

### Task 5: Apply Fail-Fast Principle
**Action**: Replace defensive programming with fail-fast approach

**Current Defensive Pattern**:
```python
if line_data.empty:
    continue  # Skip empty data
```

**Fail-Fast Replacement Options**:
```python
# Option A: Assert non-empty (strict)
assert not line_data.empty, f"Line data for {line_value} is empty"

# Option B: Remove check entirely (let errors surface naturally)
# Just proceed with plotting - pandas/matplotlib will handle empty data appropriately
```

### Task 6: Extract Constants and Configuration
**Action**: Remove magic strings and hard-coded values

**Extract Constants**:
```python
SUPPORTED_PLOT_TYPES = ["line", "scatter", "bar", "fill_between", "heatmap"]

def plot_faceted_data(...):
    assert plot_type in SUPPORTED_PLOT_TYPES, f"Unsupported plot type: {plot_type}"
```

### Task 7: File Formatting Fixes
**Action**: Fix formatting issues
- Add missing newline at end of `style_coordination.py`
- Ensure consistent spacing and formatting

## Code Quality Standards

### Mandatory Requirements
- **Zero Comments**: Not a single comment, docstring, or inline explanation
- **Comprehensive Type Hints**: Every parameter and return value must be typed
- **Self-Documenting Names**: Function and variable names must explain purpose clearly
- **Single Responsibility**: Each function should do one thing well
- **Fail Fast**: Use assertions to surface problems immediately
- **Direct Implementation**: No unnecessary abstraction layers

### Function Length Guidelines
- **Maximum 15 lines** per function (excluding assertions and type hints)
- **Single responsibility** per function
- **Clear, focused purpose** evident from function name

### Assertion Patterns
```python
# Entry validation
assert not data.empty, "Cannot process empty DataFrame"
assert config.required_field, "Missing required configuration field"

# Type validation  
assert isinstance(grid_shape, tuple), "grid_shape must be tuple"

# Value validation
assert plot_type in SUPPORTED_TYPES, f"Unsupported type: {plot_type}"
```

## Success Criteria

### Code Quality Success ✅
- [ ] **Zero comments**: No comments, docstrings, or explanations anywhere
- [ ] **Complete type hints**: All parameters and return values typed with proper imports
- [ ] **Function decomposition**: No function exceeds 15 lines or has multiple responsibilities  
- [ ] **Proper assertions**: Entry point validation following project patterns
- [ ] **Fail-fast implementation**: No defensive programming patterns
- [ ] **Constants extracted**: No magic strings or hard-coded values

### Functional Preservation ✅
- [ ] **Working functionality**: `examples/faceting/simple_grid.py` still runs successfully
- [ ] **Identical visual output**: No changes to plot appearance or behavior
- [ ] **Same API**: External interface unchanged
- [ ] **Performance maintained**: No degradation in execution speed

### Integration Success ✅
- [ ] **Import compatibility**: All imports work correctly with fixed type hints
- [ ] **FigureManager integration**: plot_faceted method works identically
- [ ] **Style coordination**: Consistent styling across subplots maintained

## Testing Requirements

### Functionality Testing
```bash
# Must pass - core functionality test
uv run python examples/faceting/simple_grid.py

# Expected: Successful execution with visual output identical to previous implementation
```

### Code Quality Verification
```bash
# Check for comments (should find nothing)
grep -r "^\s*#" src/dr_plotter/faceting/
grep -r '"""' src/dr_plotter/faceting/
grep -r "'''" src/dr_plotter/faceting/

# Expected: No output (no comments found)

# Type checking
mp src/dr_plotter/faceting/

# Expected: No type errors with proper imports
```

## Risk Mitigation

### Rollback Plan
- **Git checkpoint**: Current working state is preserved
- **Functionality verification**: Test after each major change  
- **Incremental fixes**: Apply fixes in small batches with testing

### Quality Assurance
- **Test-driven remediation**: Test functionality after each fix
- **Code review**: Verify each fix meets project standards
- **Integration testing**: Ensure fixes don't break other components

## Expected Deliverables

1. **Fixed `faceting_core.py`**:
   - Zero comments
   - Proper type hints with imports
   - Decomposed functions (max 15 lines each)
   - Entry point assertions
   - Constants extracted

2. **Fixed `style_coordination.py`**:
   - Zero comments
   - Proper type hints with imports  
   - File formatting fixed

3. **Functionality verification**:
   - Successful test runs
   - Identical visual output
   - No integration issues

4. **Quality report**:
   - Before/after code metrics
   - Confirmation of standards compliance
   - Any remaining technical debt identified

---

**Critical Success Factor**: The remediated code must meet all project quality standards while preserving 100% of current functionality. This is non-negotiable - both quality and functionality must be maintained.

**Key Implementation Principle**: Apply architectural courage to code quality - make bold improvements that eliminate complexity while maintaining clarity through structure and naming.