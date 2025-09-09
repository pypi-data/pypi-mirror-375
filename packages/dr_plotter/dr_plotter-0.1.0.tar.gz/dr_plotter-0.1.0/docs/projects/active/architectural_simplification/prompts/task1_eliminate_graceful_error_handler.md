# Task 1: Eliminate Graceful Error Handler

## Strategic Objective
Remove defensive error handling that masks real problems, allowing actual issues to surface immediately as per DR methodology's "Fail Fast, Surface Problems" principle.

## Problem Context
The `_handle_faceting_errors_gracefully` method in `src/dr_plotter/figure.py` (lines 732-776) provides complex error recovery and user guidance instead of failing fast. This masks underlying validation issues and prevents users from understanding real problems.

## Requirements & Constraints

### Must Remove
- `_handle_faceting_errors_gracefully` method entirely (lines 732-776)
- Try/catch block in `plot_faceted` method (lines 392-424)
- Call to graceful handler at line 424

### Must Preserve
- All current functionality in success cases
- Existing assertion at line 394 for empty DataFrame validation
- All method signatures and public API contracts

### Cannot Break
- Any working plot generation workflows
- Integration with existing FigureManager patterns

## Decision Framework

**Error Handling Strategy**: Let assertions bubble naturally
- Original assertion at line 394 already provides clear message
- Remove try/catch wrapper that calls graceful handler
- Trust existing validation to surface real problems immediately

**Code Organization**: Minimal surgical changes
- Delete entire graceful handler method
- Remove try/catch block around existing logic
- Keep all other logic exactly as-is

## Success Criteria

### Behavioral Success
- Empty DataFrame scenarios still fail with clear assertion message
- All other faceting operations work identically to before
- No silent failures or masked errors

### Code Quality Success
- `_handle_faceting_errors_gracefully` method completely removed
- Try/catch block in `plot_faceted` eliminated
- Clean, direct execution path from validation to failure

## Quality Standards
Reference `docs/processes/design_philosophy.md` for "Fail Fast, Surface Problems" principle.

**Specific Changes**:
1. Delete lines 732-776 (`_handle_faceting_errors_gracefully` method)
2. Replace try/catch block (lines 392-424) with direct execution
3. Keep assertion at line 394 unchanged

## Adaptation Guidance

**If other code depends on graceful handler**: This is defensive programming that should be eliminated - update callers to handle failure appropriately

**If assertions need improvement**: Focus on making assertion messages clearer, not adding defensive handling

## Documentation Requirements

**Implementation Notes**: List the specific lines removed and confirm that existing assertion messages remain descriptive for users.