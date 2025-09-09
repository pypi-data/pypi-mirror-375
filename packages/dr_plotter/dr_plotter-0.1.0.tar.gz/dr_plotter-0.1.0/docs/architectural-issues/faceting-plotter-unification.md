# Faceting-Plotter System Unification

## Problem Statement

The dr_plotter library has two separate plotting pathways that create inconsistencies and missing functionality:

1. **Normal plotting**: `fm.plot()` → `BasePlotter` → proper legend registration, styling, error handling
2. **Faceted plotting**: `fm.plot_faceted()` → direct `ax.plot()` → bypasses plotter infrastructure

This architectural split causes:
- **Missing legends in faceted plots** (current issue)
- **Potential styling inconsistencies** between pathways
- **Code duplication** and maintenance burden
- **Feature gaps** - new plotter improvements don't benefit faceting

## Root Cause Analysis

### Historical Context
The faceted plotting system was likely developed separately from the normal plotter system, creating parallel implementations. This mirrors the styling unification issue we recently solved in `styling_utils.py`.

### Current Faceted Flow
```python
fm.plot_faceted() 
  → plot_faceted_data()
    → _plot_with_style_coordination()
      → _execute_plot_call()
        → ax.plot()  # Direct matplotlib - no legend registration
```

### Normal Plotting Flow  
```python
fm.plot()
  → BasePlotter.get_plotter() 
    → plotter.render(ax)  # Automatic legend registration, styling
```

## Immediate Workaround Options

### Option 1: Manual Legend Registration in Faceting
**Approach**: Modify `_plot_line_data()` to register legend entries manually
**Pros**: Minimal code change, preserves existing architecture
**Cons**: Continues architectural duplication, requires legend system knowledge

### Option 2: Add Legend Support Flag
**Approach**: Add parameter to disable legend registration during refactor planning
**Pros**: Unblocks immediate usage
**Cons**: Temporary solution, doesn't address root cause

## Proposed Long-term Solution: Unified Architecture

### Strategy: Hybrid Approach
Replace direct matplotlib calls with normal plotter calls while preserving faceting-specific features.

### Key Components to Preserve
1. **FacetStyleCoordinator**: Cross-subplot color consistency
2. **Data pre-filtering**: Performance optimization  
3. **Faceting-specific config**: row_titles, col_titles, etc.

### Implementation Approach
```python
# Current (problematic):
ax.plot(data[config.x], data[config.y], **kwargs)

# Proposed (unified):
plot_kwargs = style_coordinator.get_consistent_style(config.lines, line_value)
plot_kwargs.update(kwargs)
plot_kwargs['label'] = str(line_value)
fm.plot(plot_type, row, col, line_data, x=config.x, y=config.y, **plot_kwargs)
```

## Critical Compatibility Questions

### 1. Data Flow Compatibility
**Question**: Can normal plotters handle pre-filtered DataFrames?
**Current**: Faceting pre-filters data by line value before plotting
**Normal**: Plotters expect full dataset, do internal grouping via `hue_by`
**Risk**: Plotters might not handle single-group datasets correctly

### 2. Style Coordination Integration
**Question**: How to maintain cross-subplot consistency?
**Current**: `FacetStyleCoordinator` ensures "seed=0" gets same color everywhere
**Challenge**: Multiple independent `fm.plot()` calls would get independent styling
**Need**: Way to pass coordinated styles as explicit kwargs

### 3. Legend Registration Logic
**Question**: Will multiple plot calls create duplicate entries?
**Current**: No entries registered (the bug)
**Risk**: Over-registration if not handled carefully
**Need**: Verify legend deduplication works correctly

### 4. Performance Impact
**Question**: Cost of multiple plotter instantiations?
**Current**: Direct matplotlib calls (fast)
**New**: Plotter creation overhead per line per subplot
**Need**: Performance benchmarking

## Testing Strategy (Before Implementation)

### Phase 1: Compatibility Verification
1. Test normal plotters with pre-filtered single-group DataFrames
2. Verify explicit x/y parameters work correctly  
3. Check style kwargs integration with plotter styling
4. Validate legend registration doesn't create duplicates

### Phase 2: Prototype Implementation
1. Create test branch with limited scope (line plots only)
2. Implement unified approach for single faceted example
3. Compare output: styling, legends, performance

### Phase 3: Full Migration
1. Extend to all plot types if prototype succeeds
2. Remove old direct-plotting code paths
3. Update tests to reflect unified behavior

## Decision Criteria

**Proceed with unification if**:
- ✅ Normal plotters handle pre-filtered data correctly
- ✅ Style coordination integrates cleanly
- ✅ Performance impact is acceptable (&lt;2x overhead)
- ✅ Legend behavior is correct and deduplicates properly

**Maintain separate systems if**:
- ❌ Fundamental incompatibilities discovered
- ❌ Performance degradation too severe
- ❌ Implementation complexity too high

## Alternative Approaches

### Option A: Extend Faceting System
Add legend registration directly to existing faceting code without unification.
**Pros**: Lower risk, faster implementation
**Cons**: Perpetuates architectural duplication

### Option B: Plotter Interface Adaptation  
Create faceting-specific plotter wrappers that handle the coordination.
**Pros**: Maintains separation while reusing components
**Cons**: Additional abstraction layer complexity

## Immediate Recommendation

**For current plotting needs**: Implement manual legend registration in faceting system as minimal viable fix.

**For architectural health**: Plan proper unification with thorough testing after immediate deadlines pass.

This follows the tactical execution principle of "unblock immediate work while planning strategic improvements."

---

**Status**: Analysis complete, awaiting decision on immediate vs. long-term approach
**Next Steps**: Choose approach based on timeline constraints and risk tolerance