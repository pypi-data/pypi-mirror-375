# Task 2: Strip Validation Wrappers

## Strategic Objective
Eliminate catch-and-re-assert patterns in validation logic, allowing core validation assertions to bubble naturally without defensive wrapping that adds complexity and masks real problems.

## Problem Context
The `_plot_faceted_standard_pipeline` method in `src/dr_plotter/figure.py` contains try/catch wrappers around validation calls (lines 449-497) that catch AssertionError and re-raise with "enhanced" context. This defensive pattern violates DR methodology by adding complexity without architectural benefit.

## Requirements & Constraints

### Must Remove
- Try/catch wrappers around `validate_nested_list_dimensions` calls (4 instances: x_labels, y_labels, xlim, ylim)
- Custom error message formatting in catch blocks
- AssertionError catch-and-re-raise pattern

### Must Preserve
- All `validate_nested_list_dimensions` function calls
- Core validation logic and failure conditions
- Descriptive error messages from the validation functions themselves

### Cannot Break
- Any working faceting workflows
- Current validation behavior in success cases
- Integration with nested list validation system

## Decision Framework

**Validation Strategy**: Direct function calls without wrappers
- Keep `validate_nested_list_dimensions` calls as-is
- Remove try/catch blocks entirely
- Trust validation functions to provide clear error messages

**Code Organization**: Replace 4 similar patterns systematically
- Lines 449-460: x_labels validation wrapper → direct call
- Lines 462-473: y_labels validation wrapper → direct call  
- Lines 475-485: xlim validation wrapper → direct call
- Lines 487-497: ylim validation wrapper → direct call

## Success Criteria

### Behavioral Success
- Validation failures still produce clear, actionable error messages
- Invalid configurations still fail fast at validation points
- No silent failures or masked validation errors

### Code Quality Success
- All try/catch blocks around validation calls removed
- Direct calls to `validate_nested_list_dimensions` preserved
- Simplified, linear execution flow through validation logic

## Quality Standards
Reference `docs/processes/design_philosophy.md` for "Fail Fast, Surface Problems" and "Leave No Trace" principles.

**Specific Changes**:
1. Replace lines 449-460 with: `validate_nested_list_dimensions(config.x_labels, grid_rows, grid_cols, "x_labels")`
2. Replace lines 462-473 with: `validate_nested_list_dimensions(config.y_labels, grid_rows, grid_cols, "y_labels")`
3. Replace lines 475-485 with: `validate_nested_list_dimensions(config.xlim, grid_rows, grid_cols, "xlim")`
4. Replace lines 487-497 with: `validate_nested_list_dimensions(config.ylim, grid_rows, grid_cols, "ylim")`

## Adaptation Guidance

**If validation error messages are unclear**: Improve the `validate_nested_list_dimensions` function itself, don't add defensive wrapping

**If additional context is needed**: Consider whether the validation function should provide that context directly

## Documentation Requirements

**Implementation Notes**: Confirm that `validate_nested_list_dimensions` provides sufficiently clear error messages for users to understand validation failures without the wrapper context.