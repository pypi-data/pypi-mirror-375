# Datadec Integration Assessment & Recommendations

## Executive Summary

Fresh eyes architectural assessment of dr_plotter's datadec integration patterns reveals significant opportunities for upstream consolidation. This analysis identifies **297 lines of datadec utilities** that could be moved upstream, **10+ files** with repeated patterns, and clear integration boundaries between core utilities and domain-specific functionality.

**Key Impact**: This integration effort could substantially reduce dr_plotter's complexity while making valuable utilities available to the broader datadec community.

## Comprehensive Usage Audit

### Current Integration Landscape

Based on systematic examination of the codebase, we identified **5 distinct categories** of datadec integration patterns:

#### 1. Core Integration Utilities (High Integration Potential)
**Location**: `src/dr_plotter/scripting/datadec_utils.py`

**Functionality**:
- Dynamic import management: `check_datadec_available()`, `get_datadec_functions()`, `get_datadec_constants()`
- Data preparation pipeline: `prepare_plot_data()` - comprehensive filtering, melting, categorization
- Metric builders: `build_olmes_metric_list()`, `all_metrics()`, `primary_metrics()`

**Assessment**: 🔥 High Priority - Generic utilities needed by any plotting library

#### 2. Domain-Specific Data Curation (Mixed Integration Potential)
**Location**: `src/dr_plotter/scripting/datadec_utils.py`

**Functionality**:
- Recipe collections: `BASE_RECIPES`, `BASE_AND_QC`, `RECIPES_WITHOUT_ABLATIONS`
- Performance groupings: `PPL_PERFORMANCE_RECIPE_CHUNKS`, `OLMES_PERFORMANCE_RECIPE_CHUNKS`
- Semantic families: `CUSTOM_RECIPE_FAMILIES`

**Assessment**: ⚠️ Medium Priority - Domain-specific but valuable for ML evaluation

#### 3. Model Utility Extensions (High Integration Potential)
**Location**: `src/dr_plotter/scripting/bump_utils.py`

**Functionality**:
- Model parameter sorting using `datadec.model_utils.param_to_numeric`
- Time series validation: `validate_bump_data_structure()`, `get_bump_data_summary()`
- Trajectory filtering: `apply_first_last_filter()`

**Assessment**: 🔥 High Priority - Parameter sorting broadly useful across contexts

#### 4. Systematic Plotting Patterns (High Integration Potential)
**Location**: Multiple scripts and examples

**Functionality**:
- Consistent data access: `DataDecide, select_params, select_data = get_datadec_functions()`
- Repeated filtering workflows: PPL vs OLMES metric separation
- Standard metric labeling: Consistent formatting across files
- Common grouping operations: params × data × metrics preparation

**Assessment**: 📈 High Value - Patterns repeated across 10+ files

#### 5. Specialized Analysis Functions (Medium Integration Potential)
**Location**: Various examples

**Functionality**:
- Data normalization: `normalize_df()` for ML curve analysis
- Complex filtering logic: Performance-based recipe selection
- Multi-metric orchestration: PPL and OLMES coordination

**Assessment**: 🔧 Medium Priority - Useful but specialized

## Architectural Health Assessment

### Positive Patterns
- **Clean abstraction**: `get_datadec_functions()` properly encapsulates import logic
- **Reusable utilities**: `prepare_plot_data()` consistently used across multiple scripts
- **Consistent naming**: Scripts follow similar patterns for data access

### Concerning Patterns
- **Massive data duplication**: Recipe lists duplicated across files
- **Scattered domain knowledge**: Recipe groupings in multiple locations without single source of truth
- **Mixed abstraction levels**: Low-level utilities alongside high-level data preparation

## Strategic Decision Framework

### Classification Matrix

**2x2 Framework for Integration Evaluation**:

**Generalizability** (How broadly useful?)
- **High**: Useful for any ML evaluation/visualization workflow
- **Low**: Specific to particular research domain

**Maintenance Burden** (Ongoing work required?)
- **High**: Frequent updates, domain knowledge, complex dependencies
- **Low**: Stable functionality, minimal dependencies

### Integration Strategy

**🔥 Move to Core Datadec** (High Generalizability + Low Maintenance):
- Generic data preparation utilities
- Import/dependency management helpers
- Standard metric access patterns
- Model parameter utilities

**📦 Create Datadec Extensions** (High Generalizability + High Maintenance):
- Domain-specific recipe collections
- Performance grouping logic
- Systematic plotting workflows

**🏠 Keep in dr_plotter** (Low Generalizability + Low Maintenance):
- Project-specific analysis functions
- Custom visualization workflows
- Local utility extensions

**🚫 Eliminate/Refactor** (Low Generalizability + High Maintenance):
- Duplicated data curation
- Inconsistent abstractions
- One-off helper functions

### Risk Assessment Criteria

For each integration candidate:

1. **API Stability Risk**: Breaking changes as datadec evolves?
2. **Dependency Risk**: Pulling visualization dependencies into data library?
3. **Maintenance Risk**: Long-term ownership clarity?
4. **Adoption Risk**: Will other projects use if moved upstream?

## Priority-Ordered Recommendations

### Phase 1: Core Utilities Integration (Immediate - High Impact)

**🔥 Priority 1A: Data Pipeline Utilities**
- **Action**: Move `prepare_plot_data()` function to datadec
- **Rationale**: Used in 6+ files, pure data transformation, no visualization dependencies
- **API Proposal**: `datadec.plotting.prepare_plot_data(dd, params, data, metrics, aggregate_seeds=False)`
- **Impact**: Eliminates 50+ lines of repeated functionality

**🔥 Priority 1B: Import Management**
- **Action**: Move import checking and function access utilities to datadec
- **Rationale**: Every external integration needs this, eliminates boilerplate
- **API Proposal**: `datadec.utils.get_plotting_interface()` or similar
- **Impact**: Standardizes datadec integration pattern

**🔥 Priority 1C: Parameter Utilities**
- **Action**: Extend datadec to make `param_to_numeric` more discoverable, add sorting helpers
- **Rationale**: Used for consistent parameter ordering across plotting contexts
- **API Proposal**: `datadec.model_utils.sort_parameters(param_list)`
- **Impact**: Eliminates repeated sorting logic

### Phase 2: Domain Knowledge Integration (Medium-term - High Value)

**📦 Priority 2A: Recipe Collections**
- **Action**: Create `datadec-recipes` or `datadec.recipes` subpackage
- **Content**: All recipe groupings, performance chunks, semantic families
- **Rationale**: High value for ML evaluation, but needs active curation
- **Impact**: Single source of truth for recipe organization

**📦 Priority 2B: Metric Builders**
- **Action**: Move `build_olmes_metric_list()`, `all_metrics()`, `primary_metrics()` to datadec
- **Rationale**: Generic enough for reuse, ties to datadec constants
- **Impact**: Standardizes metric access patterns

### Phase 3: Pattern Standardization (Long-term - Architectural)

**🏗️ Priority 3A: Systematic Plotting Interface**
- **Action**: Design standard interface for common ML plotting workflows
- **Rationale**: Eliminate repeated patterns across 10+ files
- **Consider**: `datadec.plotting` module or separate `datadec-plotting` package
- **Impact**: Dramatically simplifies plotting integration

**🏗️ Priority 3B: Analysis Function Standardization**
- **Action**: Evaluate functions like `normalize_df()` for broader applicability
- **Rationale**: Common ML analysis patterns could benefit broader community
- **Impact**: Reduces custom analysis code

### Phase 4: Cleanup & Simplification (Ongoing)

**🔧 Eliminate Duplication**
- Remove recipe lists from example files once moved upstream
- Consolidate scattered domain knowledge into single source of truth
- Simplify import patterns throughout dr_plotter

**🔧 Refactor Dependencies**
- Remove dr_plotter's custom datadec utilities once upstream versions exist
- Update all scripts to use new upstream APIs
- Document migration path for external users

## Implementation Strategy

### Suggested Approach

1. **Start with Phase 1A**: Move `prepare_plot_data()` to prove integration pattern works
2. **Validate adoption**: Ensure dr_plotter successfully uses upstream version
3. **Iterate rapidly**: Move remaining Phase 1 items based on learning
4. **Community feedback**: Get input on Phase 2 items before building
5. **Long-term planning**: Phase 3 items require broader architectural decisions

### Success Metrics

- **Code reduction**: Decrease in dr_plotter's datadec_utils.py file size
- **Elimination of duplication**: Remove repeated patterns across example files
- **External adoption**: Other projects using moved functionality
- **Maintainability**: Cleaner, more maintainable integration patterns

## File Impact Analysis

### Files Currently Using Datadec Integration

**Heavy Integration** (Priority for cleanup):
- `src/dr_plotter/scripting/datadec_utils.py` (297 lines)
- `scripts/plot_bump_timesteps.py` (1079 lines, imports datadec utilities)
- `examples/28_systematic_ml_plotting.py` (1035 lines, duplicates recipe data)

**Medium Integration**:
- `scripts/plot_bump.py`
- `scripts/plot_means.py`
- `scripts/plot_seeds.py`
- `examples/MI_lines.py`

**Light Integration**:
- Various other examples using `get_datadec_functions()`

### Migration Impact

**Immediate Benefits**:
- ~300 lines of utility code moved upstream
- Elimination of data duplication across files
- Standardized datadec integration pattern

**Long-term Benefits**:
- Community access to ML evaluation utilities
- Reduced maintenance burden for dr_plotter
- Better separation of concerns between visualization and data access

## Next Steps

1. **Create proof-of-concept**: Implement `prepare_plot_data()` in datadec
2. **Test integration**: Update one dr_plotter script to use upstream version
3. **Establish process**: Create guidelines for future integration decisions
4. **Plan systematically**: Use this framework to evaluate remaining utilities
5. **Document migration**: Provide clear upgrade path for external users

## Conclusion

This integration represents a significant opportunity to improve both dr_plotter's maintainability and the broader datadec ecosystem. The clear patterns identified provide a roadmap for systematic consolidation that benefits the entire ML evaluation community.

**Recommendation**: Proceed with Phase 1A implementation as proof-of-concept, then systematically work through remaining priorities based on validation and community feedback.