# DataDecide Integration Implementation Plan

## Executive Summary

This document outlines the concrete implementation plan for integrating datadec's new helper methods and plotting utilities with dr_plotter. The plan leverages datadec's newly unified API to dramatically simplify dr_plotter's integration patterns while providing a clear migration path.

**Key Changes in DataDecide (Branch: 09-07-helpers)**:
- ✅ Added helper methods: `aggregate_results()`, `filter_data_quality()`, `select_subset()`
- ✅ Unified validation patterns in `validation.py`
- ✅ Eliminated `script_utils.py` (breaking change for dr_plotter)
- 🚧 Adding plotting preparation methods: `prepare_plot_data()`, `melt_for_plotting()`
- 🚧 Adding convenience wrappers: `dd.select_params()`, `dd.select_data()`

## Implementation Strategy

### Phase 1: DataDecide API Completion (Current Sprint)

**🚧 In Progress - Plotting Preparation Methods**

Add to `src/datadec/data.py`:
```python
def select_params(self, params="all", exclude=None) -> List[str]:
    """Select and validate model parameter sizes via dd instance."""
    return validation.select_params(params, exclude)

def select_data(self, data="all", exclude=None) -> List[str]:
    """Select and validate data recipe names via dd instance."""
    return validation.select_data(data, exclude)

def melt_for_plotting(self, df, metrics=None, include_seeds=True, drop_na=True):
    """Convert DataFrame to long format for plotting libraries."""
    # Smart ID column selection based on include_seeds
    # Automatic metric detection if not provided
    # Standard melt + NaN cleanup

def prepare_plot_data(self, params=None, data=None, metrics=None, 
                     aggregate_seeds=False, input_df=None, auto_filter=True, 
                     verbose=False, **select_subset_kwargs):
    """One-stop method for preparing data for plotting libraries."""
    # Uses smart filter determination
    # Orchestrates filter_data_quality + select_subset + aggregate_results + melt_for_plotting
```

Add to `src/datadec/validation.py`:
```python
def determine_filter_types(metrics: List[str]) -> List[str]:
    """Determine optimal filter types based on metrics being used."""
    # Smart filtering logic from dr_plotter's prepare_plot_data
```

### Phase 2: Dr_plotter Dependency Update (Next Sprint)

**🔥 Critical Breaking Change Fix**

Current dr_plotter code:
```python
# BROKEN - script_utils no longer exists
from datadec.script_utils import select_params, select_data
```

**Immediate Fix Required**:
```python
# Update dr_plotter imports
from datadec.validation import select_params, select_data
```

**Better Long-term Solution**:
```python  
# Use new unified API
from datadec import DataDecide

dd = DataDecide()
params = dd.select_params(["150M", "1B"])
data = dd.select_data(["C4", "Dolma1.7"])
```

### Phase 3: Dr_plotter Integration Simplification (Following Sprint)

**🎯 Target: Replace `prepare_plot_data()` with upstream version**

Current implementation in `src/dr_plotter/scripting/datadec_utils.py` (47 lines):
```python
def prepare_plot_data(dd, params, data, metrics, aggregate_seeds=False):
    # Complex manual implementation with filter logic
    # Manual parameter filtering 
    # Manual aggregation handling
    # Manual melting logic
```

**New simplified version** (5 lines):
```python
def prepare_plot_data(dd, params, data, metrics, aggregate_seeds=False):
    """Prepare plotting data using datadec's unified API."""
    return dd.prepare_plot_data(
        params=params, data=data, metrics=metrics, 
        aggregate_seeds=aggregate_seeds
    )
```

**Even better - eliminate wrapper entirely**:
```python
# Direct usage in plotting scripts
plot_df = dd.prepare_plot_data(
    params=["150M", "1B", "7B"], 
    data=["C4", "Dolma1.7"],
    metrics=["dolma_books-valppl", "arc_easy_acc_raw"]
)
```

### Phase 4: Function Consolidation (Future Sprint)

**🚀 Upstream Move Candidates**

After validation, move these dr_plotter utilities to datadec core:

1. **Metric Builders** → `datadec.metrics` module:
   - `build_olmes_metric_list()` 
   - `all_metrics()`
   - `primary_metrics()`

2. **Recipe Collections** → `datadec.recipes` module:
   - `BASE_RECIPES`, `BASE_AND_QC`, etc.
   - Performance groupings
   - Semantic families

3. **Import Utilities** → Enhanced datadec core:
   - Better integration helpers for external libraries

## Migration Impact Analysis

### Files Requiring Updates in Dr_plotter

**High Priority (Breaking Change)**:
- `src/dr_plotter/scripting/datadec_utils.py` - Fix import, simplify prepare_plot_data
- Any scripts importing from `datadec.script_utils` - Update import path

**Medium Priority (Optimization)**:
- All scripts using `get_datadec_functions()` - Can switch to unified `dd` API
- Example files with repeated recipe data - Use upstream constants

**Low Priority (Future)**:
- Scripts with manual data preparation - Can use `dd.prepare_plot_data()`

### API Compatibility Strategy

**Backward Compatibility Approach**:
1. Keep existing dr_plotter functions working during transition
2. Gradually migrate to upstream versions
3. Deprecate local utilities after upstream adoption

**Breaking Changes**:
- ❌ `datadec.script_utils` import paths (immediate fix required)
- ⚠️ Some function signatures may change (document migration)

## Implementation Timeline

### Week 1: DataDecide API Completion
- [ ] Add plotting preparation methods to datadec
- [ ] Add convenience wrapper methods  
- [ ] Comprehensive testing of new methods
- [ ] Update datadec documentation

### Week 2: Dr_plotter Emergency Fix  
- [ ] Fix broken `script_utils` imports
- [ ] Test dr_plotter functionality restored
- [ ] Update dr_plotter dependency to latest datadec

### Week 3: Dr_plotter Optimization
- [ ] Simplify `prepare_plot_data()` using upstream version
- [ ] Migrate key scripts to unified API
- [ ] Performance validation

### Week 4: Documentation & Rollout
- [ ] Update dr_plotter integration documentation  
- [ ] Create migration guide for external users
- [ ] Plan Phase 4 upstream moves

## Success Metrics

**Quantitative Goals**:
- Reduce dr_plotter's `datadec_utils.py` from 297 → ~50 lines
- Eliminate data duplication across 10+ files
- Single-import API pattern for researchers

**Qualitative Goals**:
- Simplified researcher workflow (everything via `dd` instance)
- Clear separation between data access and visualization
- Reusable plotting preparation pipeline for other libraries

## Risk Mitigation

**Import Path Breaking Changes**:
- Document migration clearly
- Provide exact find/replace commands  
- Test against dr_plotter's test suite

**API Surface Expansion**:
- Keep new methods focused and well-documented
- Follow established datadec patterns
- Plan for future refactoring if needed

**Integration Complexity**:
- Implement incrementally with validation at each step
- Maintain dr_plotter functionality throughout transition
- Clear rollback plan if issues arise

## Next Steps

1. **Immediate**: Complete datadec plotting preparation methods
2. **Critical**: Fix dr_plotter's broken imports 
3. **Strategic**: Begin systematic migration to unified API
4. **Future**: Plan upstream consolidation of domain-specific utilities

This plan transforms the integration challenge into a systematic upgrade that benefits both projects and the broader ML evaluation ecosystem.