# Compositional Architecture Plan: DataDecide Integration Phase 1

## Executive Summary

Following architectural analysis, we've identified that the core issue preventing effective datadec integration is **rigid single-transformation architecture**. Both `get_filtered_df()` and `easy_index_df()` can only operate on internal DataDecide data sources, making multi-step data processing pipelines impossible. This forces ~300+ lines of external post-processing utilities across repositories.

**Strategic Approach**: Enable compositional architecture using **existing functionality only**, then migrate external code to discover what additional features are actually needed, rather than guessing upfront.

## Core Architectural Problems Identified

### **Problem 1: No DataFrame Input Capability**
**Current Limitation**: Methods hardcoded to internal data sources
```python
# Impossible with current architecture
df = dd.get_filtered_df()  # Can ONLY work on dd.full_eval
df = dd.easy_index_df()    # Can ONLY work on dd.full_eval, can't accept df from previous step
```

**Required Fix**: Enable DataFrame input throughout
```python
# What should be possible
df = dd.full_eval
df = dd.get_filtered_df(input_df=df, filter_types=['max_steps'])
df = dd.easy_index_df(input_df=df, params=['7B'], data=['pile'])
```

### **Problem 2: Conflated Responsibilities**
**Current Confusion**:
- `get_filtered_df()`: Does filtering AND indexing AND aggregation
- `easy_index_df()`: Does selection AND column filtering

**Clear Separation Needed**:
- **Filtering**: Domain-specific data quality (remove NaNs, max_steps constraints)
- **Selection/Indexing**: Choose specific subsets (params, data, columns)
- **Aggregation**: Transform data structure (seed aggregation, means/stds)

## Implementation Strategy

### **Phase 1: Pure Architecture Enhancement (2-3 weeks)**
**Objective**: Enable compositional workflows using existing functionality only

#### **1A: Enable DataFrame Input**
```python
def get_filtered_df(
    self,
    input_df: Optional[pd.DataFrame] = None,  # CRITICAL addition
    filter_types: List[str] = ["max_steps"],
    return_means: bool = True,
    min_params: str = "10M",
    verbose: bool = False,
) -> pd.DataFrame:
    # Use input_df if provided, otherwise default to self.full_eval
    base_df = input_df.copy() if input_df is not None else self.full_eval.copy()
    # ... rest of existing logic unchanged
```

```python
def easy_index_df(
    self,
    input_df: Optional[pd.DataFrame] = None,  # CRITICAL addition
    df_name: str = "full_eval",  # Keep for backward compatibility
    data: Optional[Union[str, List[str]]] = None,
    params: Optional[Union[str, List[str]]] = None,
    # ... rest of existing parameters
) -> pd.DataFrame:
    # Use input_df if provided, otherwise load by name
    if input_df is not None:
        df = input_df.copy()
    else:
        df = self.load_dataframe(df_name)
    # ... rest of existing logic unchanged
```

#### **1B: Extract Atomic Utilities**
Create composable functions from existing `get_filtered_df()` logic:

```python
def filter_data_quality(
    self,
    input_df: pd.DataFrame,
    filter_types: List[str] = ["max_steps"],
    min_params: str = "10M",
    verbose: bool = False,
) -> pd.DataFrame:
    # Extract filtering logic from current get_filtered_df()
    # Pure data quality operations only
    
def aggregate_by_seeds(
    self, 
    input_df: pd.DataFrame,
    verbose: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # Extract aggregation logic from current get_filtered_df()
    # Return (mean_df, std_df)
    
def select_subset(
    self,
    input_df: pd.DataFrame, 
    data: Optional[Union[str, List[str]]] = None,
    params: Optional[Union[str, List[str]]] = None,
    columns: Optional[List[str]] = None,
) -> pd.DataFrame:
    # Extract selection logic from current easy_index_df()
    # Pure selection operations only
```

#### **1C: Maintain Backward Compatibility**
- All existing method calls work exactly as before
- New functionality available through optional parameters
- Comprehensive test coverage to ensure no regressions

**Success Criteria**:
- ✅ All existing tests pass unchanged
- ✅ New compositional workflows possible
- ✅ Zero new features added (pure architectural improvement)

### **Phase 2: Single Repository Migration (1-2 weeks)**
**Objective**: Validate compositional architecture with dr_plotter integration

#### **Target**: `prepare_plot_data()` Migration
**Current External Logic** (~50 lines in dr_plotter):
```python
def prepare_plot_data(dd, params, data, metrics, aggregate_seeds=False):
    # Complex logic mixing filtering, selection, aggregation, melting
    df = dd.get_filtered_df(filter_types=smart_filter_logic, return_means=False)
    df = manual_pandas_filtering(df, params, data)
    df = manual_aggregation_logic(df, aggregate_seeds)
    df = manual_melting_logic(df, metrics)
    return df
```

**New Compositional Approach**:
```python
def prepare_plot_data(dd, params, data, metrics, aggregate_seeds=False):
    # Use datadec compositional utilities throughout
    df = dd.filter_data_quality(dd.full_eval, filter_types=smart_filter_logic)
    df = dd.select_subset(df, params=params, data=data, columns=needed_columns)
    if aggregate_seeds:
        df, _ = dd.aggregate_by_seeds(df)
    df = melt_for_plotting(df, metrics)  # Only plotting-specific logic remains external
    return df
```

**Success Criteria**:
- ✅ Identical output to current implementation
- ✅ Reduced code complexity in dr_plotter
- ✅ Demonstrates compositional approach works
- ✅ Identifies what plotting-specific logic still needs external handling

### **Phase 3: Cross-Repository Validation (1-2 weeks)**
**Objective**: Test compositional architecture with ddpred's more complex patterns

#### **Target**: `get_filtered_data()` Migration
**Current External Logic** (~80 lines in ddpred):
```python
def get_filtered_data(dd, param_size, data_recipe, metric, exclude_data, exclude_params):
    # Complex validation, filtering, selection, metric-specific processing
    validated_params = select_params(param_size, exclude=exclude_params)
    validated_data = select_data(data_recipe, exclude=exclude_data)
    df = dd.get_filtered_df(filter_types=["max_steps", metric_type], return_means=True)
    df = better_easy_index_df(df, validated_data, validated_params)
    df = filter_to_specific_metrics(df, metric)
    return df, validated_params, validated_data
```

**New Compositional Approach**:
```python
def get_filtered_data(dd, param_size, data_recipe, metric, exclude_data, exclude_params):
    # Use datadec compositional utilities for core operations
    validated_params = select_params(param_size, exclude=exclude_params)  # Keep external
    validated_data = select_data(data_recipe, exclude=exclude_data)       # Keep external
    df = dd.filter_data_quality(dd.full_eval, filter_types=["max_steps", metric_type])
    df, _ = dd.aggregate_by_seeds(df)  # replace return_means=True
    df = dd.select_subset(df, data=validated_data, params=validated_params)
    df = filter_to_specific_metrics(df, metric)  # Keep external for now
    return df, validated_params, validated_data
```

**Discovery Opportunity**: 
- Which validation patterns are ddpred-specific vs. broadly useful?
- What metric filtering logic could benefit other repositories?
- Are there selection patterns that should be enhanced in datadec?

**Success Criteria**:
- ✅ Identical functionality to current ddpred implementation
- ✅ Reduced external utility code
- ✅ Clear evidence of which patterns are reused vs. repository-specific

### **Phase 4: Evidence-Based Integration (Timeline TBD)**
**Objective**: Move only validated, reused patterns upstream

#### **Integration Candidates** (Based on Phase 2-3 Discovery):
**Only move upstream patterns that**:
- Are used by both repositories in their migrations
- Provide clear value over external implementation
- Fit cleanly within established compositional architecture

**Potential Candidates** (to be validated):
```python
# If both repos need exclusion patterns
def select_subset(
    self, input_df, 
    params=None, data=None, 
    exclude_params=None, exclude_data=None  # Add if proven valuable
)

# If both repos need metric-specific filtering
def filter_by_metrics(
    self, input_df,
    metrics: List[str],
    metric_type: Optional[str] = None  # Add if proven valuable
)

# If both repos need melting capabilities  
def melt_for_analysis(
    self, input_df,
    metrics: List[str],
    id_columns: Optional[List[str]] = None  # Add if proven valuable
)
```

#### **Explicit Non-Integration** (Repository-Specific):
- Complex validation logic specific to ddpred workflows
- Plotting-specific transformations specific to dr_plotter  
- Domain knowledge that doesn't generalize

**Success Criteria**:
- ✅ Clear evidence each new feature is used by multiple repositories
- ✅ Features fit naturally within compositional architecture
- ✅ No feature creep or speculative additions

## Risk Management

### **Technical Risks**
**Backward Compatibility**: Changes to core methods could break existing code
- *Mitigation*: Comprehensive test coverage, optional parameter approach

**Performance Impact**: DataFrame copying could introduce overhead
- *Mitigation*: Performance benchmarking, optimize only if needed

### **Strategic Risks**
**Scope Creep**: Could expand beyond manageable architectural changes
- *Mitigation*: Strict adherence to phased approach with explicit validation checkpoints

**Over-Engineering**: Could create complex abstractions before proving value
- *Mitigation*: Start with existing functionality only, evidence-based feature addition

### **Validation Checkpoints**
- **Phase 1 Gate**: All existing tests pass, compositional workflows demonstrable
- **Phase 2 Gate**: dr_plotter migration successful with code reduction
- **Phase 3 Gate**: ddpred migration successful with clear pattern discovery
- **Phase 4 Gate**: Clear evidence for each proposed upstream integration

## Expected Outcomes

### **Immediate Benefits** (Phase 1)
- **Compositional Architecture**: Multi-step data processing using datadec utilities
- **No Functionality Risk**: Pure architectural improvement with full backward compatibility
- **Foundation for Integration**: Enables evidence-based discovery of integration opportunities

### **Medium-Term Benefits** (Phase 2-3)
- **Code Reduction**: Elimination of external post-processing utilities where datadec can handle natively
- **Standardization**: Common patterns for data processing across repositories
- **Evidence Generation**: Clear data on which external patterns are actually reused vs. repository-specific

### **Long-Term Benefits** (Phase 4+)
- **Selective Integration**: Only proven-valuable patterns moved upstream
- **Solid Architecture**: Compositional foundation that supports future enhancements
- **Community Value**: Reusable utilities available to broader datadec ecosystem

## Success Metrics

### **Quantitative Targets**
- **Phase 1**: Zero test regressions, compositional workflows demonstrable
- **Phase 2**: 30-50% reduction in dr_plotter's datadec utility code  
- **Phase 3**: Similar code reduction in ddpred with maintained functionality
- **Phase 4**: Clear usage evidence for each proposed integration

### **Qualitative Indicators**
- **Developer Experience**: Simpler multi-step data processing workflows
- **Architecture Quality**: Clear separation of concerns with composable utilities
- **Integration Success**: External repositories can leverage datadec utilities throughout their pipelines

## Conclusion

This plan provides a **foundation-first, evidence-based approach** to datadec integration that avoids common architectural pitfalls. By starting with compositional architecture using existing functionality, then validating through real repository migrations, we ensure that any upstream integrations are proven valuable rather than speculative.

The approach aligns perfectly with DR methodology principles: **architectural courage** through bold structural improvement, **fail fast** through early validation, and **minimalism** through evidence-based feature addition only.

**Next Step**: Begin Phase 1 implementation with DataFrame input capability and atomic utility extraction from existing `get_filtered_df()` and `easy_index_df()` methods.