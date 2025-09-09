# Faceted Plotting: Comprehensive Design & Implementation Plan

## Project Overview

**Objective**: Transform complex multi-dimensional data visualization from brittle one-off solutions to reusable, intuitive patterns through native faceting support in dr_plotter.

**Current Status**: 
- ✅ Phase 1: Data analysis complete
- ✅ Phase 2: Working examples implemented
- ❌ Phase 3: API design (pending)
- ❌ Phase 4: Native implementation (pending)

**Strategic Goal**: Enable researchers to create publication-ready faceted visualizations with minimal boilerplate while maintaining fine-grained control when needed.

## Target Use Case: Multi-Dimensional ML Training Visualization

**Current Working Example**: 2×4 grid showing training curves across:
- **Rows**: Different metrics (pile-valppl, mmlu_average_correct_prob) 
- **Columns**: Different data recipes (C4, Dolma1.7, FineWeb-Edu, DCLM-Baseline)
- **Lines within each subplot**: Different model sizes (4M, 6M, 8M, 10M, 14M, etc.)

## Evidence-Based Findings

### Data Structure Insights
- **Perfect data density**: 100% coverage across 350 model_size × data_recipe combinations
- **Training progression**: 6-54 steps per combination, varied training lengths normal
- **Metric scale**: 1,913 total metrics provides rich subset selection options
- **Model size ordering**: Alphabetic sorting (10M, 14M, 150M) vs logical numeric ordering requires explicit handling

### Current Boilerplate Analysis

Users currently need **95+ lines** for faceted plots, broken down as:

1. **Data Preparation** (20+ lines):
   ```python
   # Filter DataFrame for target metrics/recipes/model sizes
   filtered_df = df[df["data"].isin(target_recipes) & df["params"].isin(model_sizes)].copy()
   # Set up categorical ordering for consistent plotting
   filtered_df["params"] = pd.Categorical(filtered_df["params"], categories=model_sizes, ordered=True)
   ```

2. **Manual Subplot Iteration** (30+ lines):
   ```python
   for col_idx, recipe in enumerate(target_recipes):
       recipe_data = df[df["data"] == recipe].copy()
       for row_idx, (metric, metric_label) in enumerate(zip(metrics, metric_labels)):
           fm.plot("line", row_idx, col_idx, metric_data, x="step", y=metric, hue_by="params")
           # Manual axis configuration per subplot
   ```

3. **Styling Coordination** (15+ lines):
   - Consistent colors/markers across subplots for same model size
   - Proper axis labels only on edges
   - Legend configuration for multi-dimensional data

4. **Theme Management** (themed variant adds 50+ lines):
   - Custom theme creation with color cycles
   - Scale coordination across subplots

### Key Friction Points Identified

1. **Repetitive subplot iteration**: Manual loops for each metric × recipe combination
2. **Styling consistency**: Ensuring the same model size gets same color/marker across all subplots  
3. **Label coordination**: Managing axis labels, titles, and legend across grid
4. **Data preparation**: Converting multi-dimensional data to per-subplot format
5. **Performance consideration**: 14 lines per subplot × 8 subplots = 112 total line objects to manage

## Architectural Insights from Implementation

### Natural Scope Boundaries
- **dr_plotter responsibility**: Generic plotting infrastructure (grids, styling coordination, legend management)
- **User code responsibility**: Domain-specific logic (data selection, metric interpretation, data preparation)

### Complexity Source
Multi-dimensional data visualization complexity comes from **coordination across dimensions**, not individual subplot complexity.

### Design Patterns Discovered
1. **Grid Layout Management**: Systematic separation of data preparation, grid creation, styling coordination
2. **Multi-Dimensional Styling**: Color/marker consistency across subplots requires centralized coordination
3. **Legend Strategy**: Multi-dimensional legends need careful positioning and grouping strategies

## Phase 3: API Design Requirements

**Complete Requirements**: See [`docs/plans/faceted_plotting_requirements.md`](./faceted_plotting_requirements.md) for comprehensive functional requirements.

**Complete Architecture Design**: See [`docs/plans/faceted_plotting_detailed_design.md`](./faceted_plotting_detailed_design.md) for full architectural specifications and implementation details.

### Design Questions Resolved

**Hybrid Architecture Selected**: Combination of simple method-based API for common cases with rich configuration objects for advanced scenarios.

**Key Decisions Made**:
1. **Parameter Resolution**: Direct parameters override FacetingConfig (config as defaults)
2. **File Structure**: New `faceting_config.py` file, remove unused `SubplotFacetingConfig`
3. **Grid Sizing**: Auto-calculate dimensions for wrapped layouts with validation
4. **Style Coordination**: Figure-level persistence across multiple faceting calls
5. **Validation**: Strict, eager validation with helpful error messages
6. **Empty Subplots**: Warning and continue with configurable behavior

### Final Architecture Summary

**Detailed Implementation Specification**: See [`docs/plans/faceted_plotting_detailed_design.md`](./faceted_plotting_detailed_design.md) for complete architecture, code examples, and implementation details.

**Hybrid API Design**:
```python
# Simple API: Direct parameters for common cases
fm.plot_faceted(data=df, plot_type="line", rows="metric", cols="recipe", 
               lines="model_size", x="step", y="value")

# Advanced API: Rich configuration for complex scenarios
config = FacetingConfig(rows="metric", target_row=0, x_labels=[[...]])
fm.plot_faceted(data=df, plot_type="line", faceting=config, x="step", y="value")

# Mixed usage: Config + direct parameter overrides
fm.plot_faceted(data=df, faceting=complex_config, target_row=0)
```

### Implementation Deliverables (Phase 3)

**Reference**: Complete implementation specification in [`docs/plans/faceted_plotting_detailed_design.md`](./faceted_plotting_detailed_design.md)

**Summary**:
1. **New `faceting_config.py`** with comprehensive `FacetingConfig` class
2. **Enhanced `FigureManager.plot_faceted()`** with hybrid API pattern
3. **Decomposed helper methods** for validation, grid computation, data preparation, styling
4. **Figure-level style coordination** supporting layered faceting scenarios
5. **Strict validation system** with informative error messages

## Phase 4: Implementation Strategy

### Phase 4 Implementation Tasks

**Reference**: Complete technical specifications in [`docs/plans/faceted_plotting_detailed_design.md`](./faceted_plotting_detailed_design.md)

**Ready for Implementation**:
1. **File structure changes**: Create `faceting_config.py`, remove unused `SubplotFacetingConfig`
2. **Core `plot_faceted()` method** with all helper methods specified
3. **Configuration resolution system** with direct parameter override logic
4. **Comprehensive validation** for data, targeting, and configuration parameters
5. **Style coordination system** maintaining consistency across layered calls
6. **Example refactoring** demonstrating 95+ → <20 line reduction

### Success Criteria

- **Boilerplate reduction**: New API reduces example code by 60%+ lines
- **Functionality preservation**: All existing dr_plotter capabilities remain unchanged
- **Intuitive usage**: API feels natural for multi-dimensional visualization tasks
- **Performance maintenance**: No significant performance degradation for complex plots

## Key Technical Discoveries

### Model Size Ordering Challenge
- **Issue**: Alphabetic sorting (10M, 14M, 150M) vs logical numeric ordering (4M, 6M, 8M, 10M...)
- **Impact**: Affects line styling consistency and legend ordering
- **Solution**: API must provide explicit ordering control via `*_order` parameters (also serves as filtering)

### Metric Name Patterns
- **Discovery**: Actual metric names use underscores (pile_valppl) not hyphens (pile-valppl)
- **Impact**: API design must handle real-world naming conventions

### Theme Integration Complexity
- **Discovery**: Custom themes for faceted plots require 50+ additional lines
- **Opportunity**: Native faceting API could integrate theme management automatically

## Reusable Methodology

### Evidence-First Library Enhancement Pattern
1. **Phase 1**: Systematic data structure analysis
2. **Phase 2**: Working example implementation with current tools
3. **Phase 3**: API design based on friction point evidence  
4. **Phase 4**: Native implementation and validation

**Success Criteria**: Each phase provides concrete evidence for next phase design decisions.

### Multi-Dimensional Visualization Decomposition Pattern
1. **Data preparation**: Filter and structure multi-dimensional data
2. **Grid creation**: Establish subplot layout and coordination
3. **Styling coordination**: Ensure consistency across dimensions
4. **Legend management**: Handle multi-dimensional legend strategies

## Working Examples Status

### Current Implementation Files
- **`examples/06_faceted_training_curves.py`**: Main faceted plotting example (95+ lines)
- **`examples/06b_faceted_training_curves_themed.py`**: Themed variant (145+ lines)
- **`examples/plots/06_faceted_training_curves.png`**: Generated visualization
- **`examples/plots/06b_faceted_training_curves_themed.png`**: Themed visualization

### Integration Status
- **DataDecide integration**: Working with `uv add "dr_plotter[datadec]"`
- **CLI argument validation**: Complete with proper error handling
- **Theme system integration**: Demonstrated in themed variant

## Next Steps

### Immediate Phase 3 Tasks
1. **API specification design**: Define exact method signatures and parameters
2. **Configuration class design**: Create faceting configuration objects
3. **Data transformation design**: Define interface between user data and plotting system
4. **Styling coordination design**: Specify cross-subplot consistency mechanisms

### Phase 4 Implementation Tasks  
1. **Core faceting implementation**: Add `plot_faceted()` method to FigureManager
2. **Configuration system**: Implement faceting configuration classes
3. **Data utilities**: Build transformation functions for multi-dimensional data
4. **Example refactoring**: Convert current examples to use new API
5. **Testing and validation**: Comprehensive testing of new functionality

## Strategic Value

**Immediate**: Working visualization that meets complex multi-dimensional requirements
**Strategic**: Reusable patterns that handle entire classes of similar problems  
**Long-term**: Enhanced dr_plotter that makes complex visualizations significantly easier

**Key Architectural Insight**: Multi-dimensional visualization coordination patterns are applicable beyond ML evaluation data to scientific plotting generally.