# Faceted Plotting: Complete Requirements Specification

## Overview

This document specifies all requirements for native faceting support in dr_plotter, enabling researchers to create publication-ready multi-dimensional visualizations with minimal boilerplate while maintaining fine-grained control.

**Target**: Transform 95+ lines of manual subplot management into intuitive high-level API calls that compose naturally with dr_plotter's existing functionality.

## Core Requirements

### 1. Core Faceting API

**Requirement**: Add `plot_faceted()` method to FigureManager with intuitive dimension mapping.

**Specifications**:
- Support `rows`, `cols`, and `lines` dimension parameters for semantic mapping
- Integration with all existing dr_plotter plot types: line, scatter, bar, heatmap, fill_between, etc.
- Maintain existing plot method signature compatibility (same parameters work)
- Return same plot objects and axes access patterns as current API

**Example**:
```python
fm.plot_faceted(
    data=df,
    plot_type="line",
    rows="metric",      # Map to subplot rows  
    cols="data_recipe", # Map to subplot columns
    lines="model_size", # Map to line series within subplots
    x="step", y="value"
)
```

### 2. Flexible Layout System

**Requirement**: Support both explicit grid layouts and wrapped single-dimension layouts.

**Specifications**:

#### Full Grid Layout
- Both `rows` and `cols` specified creates explicit grid (e.g., 2×4)
- Grid dimensions determined by unique values in row/col columns

#### Wrapped Layout  
- Single dimension (`rows` OR `cols`) + `ncols`/`nrows` for automatic wrapping
- Fill order: index 0 filled first, then index 1, etc.
- Example: `rows="data_recipe"` with `ncols=2` arranges 4 recipes in 2×2 grid

**Example**:
```python
# Explicit grid
fm.plot_faceted(rows="metric", cols="data_recipe", ...)  # 2×4 grid

# Wrapped layout  
fm.plot_faceted(rows="data_recipe", ncols=2, ...)        # 2×2 grid (4 recipes wrapped)
```

### 3. Ordering and Filtering Control

**Requirement**: Explicit control over element ordering and subset selection.

**Specifications**:
- `row_order`, `col_order`, `lines_order` parameters with dual functionality:
  - **Ordering**: Specify exact sequence (solves alphabetic vs numeric sorting issues)
  - **Filtering**: Only elements listed are included (implicit filtering)
- If order parameter not specified, use natural data order
- Empty order list means skip that dimension entirely

**Example**:
```python
fm.plot_faceted(
    # ...
    row_order=["pile-valppl", "mmlu_average_correct_prob"],  # Explicit ordering
    col_order=["C4", "Dolma1.7", "FineWeb-Edu"],            # Also filters out other recipes  
    lines_order=["4M", "6M", "8M", "10M", "14M", "16M"]     # Numeric logical order
)
```

### 4. Per-Subplot Fine Control

**Requirement**: Preserve and extend FigureConfig nested list patterns for individual subplot control.

**Specifications**:

#### Label Control (Preserve Existing)
- `x_labels`: Nested list `[[row0_labels], [row1_labels]]` where each inner list has `cols` elements
- `y_labels`: Same pattern for Y-axis labels
- `None` values skip specific subplots

#### Axis Limits Control (New Extension)
- `xlim`: Nested list `[[(min, max), None, (min, max)], [...]]` for X-axis limits
- `ylim`: Same pattern for Y-axis limits  
- `None` values use automatic limits for those subplots

**Example**:
```python
fm.plot_faceted(
    # ...
    x_labels=[["Steps", "Steps", "Training Steps", "Steps"],    # Row 0
              ["Steps", "Steps", "Steps", "Steps"]],            # Row 1
    xlim=[[(0, 50000), None, None, (0, 30000)],                # Row 0 limits
          [None, (1000, 60000), None, None]]                   # Row 1 limits
)
```

### 5. Layered Faceting

**Requirement**: Enable multiple `plot_faceted()` calls on same FigureManager for composite visualizations.

**Specifications**:

#### Multiple Call Support
- Successive calls compose correctly on same axes
- Each call can use different plot types, data, styling
- Maintain legend and styling coordination across layers

#### Selective Subplot Targeting
- `target_row`: Apply to specific row index only
- `target_col`: Apply to specific column index only  
- `target_rows`: Apply to list of row indices (e.g., `[0, 2]`)
- `target_cols`: Apply to list of column indices (e.g., `[1, 3]`)

**Example**:
```python
with FigureManager(figure=FigureConfig(rows=2, cols=4)) as fm:
    # Layer 1: Base scatter plots
    fm.plot_faceted(data=scatter_data, plot_type="scatter", rows="metric", cols="recipe", ...)
    
    # Layer 2: Trend lines only on first row
    fm.plot_faceted(data=trend_data, plot_type="line", target_row=0, ...)
    
    # Layer 3: Confidence intervals on specific columns  
    fm.plot_faceted(data=ci_data, plot_type="fill_between", target_cols=[0, 2], ...)
```

### 6. Styling Coordination

**Requirement**: Maintain consistent styling across subplots for same logical data values.

**Specifications**:

#### Cross-Subplot Consistency
- Same `lines` dimension values get identical colors/markers across all subplots
- Color cycles and marker cycles coordinate globally, not per-subplot
- Legend shows each unique value once, not repeated per subplot

#### Theme Integration
- Custom themes work seamlessly with faceted plots
- Theme color cycles apply consistently across subplot grid
- Automatic legend positioning and sizing for multi-dimensional data

**Example**: Model size "10M" gets same color in every subplot where it appears.

### 7. Data Integration

**Requirement**: Handle multi-dimensional pandas DataFrame data preparation automatically.

**Specifications**:
- Accept pandas DataFrames with dimension columns (rows, cols, lines values)
- Automatic data subsetting per subplot based on row/col dimension values
- Handle missing combinations gracefully (empty subplots)
- Support null values in metric columns (standard ML evaluation pattern)
- Preserve categorical data types and ordering

## Extended Requirements

### 8. Subplot Title Management

**Requirement**: Flexible automatic and manual subplot title control.

**Specifications**:
- `subplot_titles="auto"`: Use dimension values as titles
- `subplot_titles=[[title_matrix]]`: Manual nested list pattern
- `title_template="{col} - {row}"`: Template for automatic title generation
- `None` in title matrix skips titles for specific subplots

### 9. Shared Axes Control  

**Requirement**: Granular control over axis sharing patterns.

**Specifications**:
- `shared_x="all"`: Share X-axis across entire grid
- `shared_x="row"`: Share X-axis within each row
- `shared_x="col"`: Share X-axis within each column  
- `shared_x=False`: No X-axis sharing (default)
- Same pattern for `shared_y`
- Integration with existing FigureConfig `subplot_kwargs={"sharey": "row"}` patterns

### 10. Error Handling and Validation

**Requirement**: Comprehensive validation with informative error messages.

**Specifications**:

#### Data Validation
- Check that dimension columns exist in DataFrame
- Validate that dimension values exist in data
- Check that x/y columns exist and contain plottable data

#### Configuration Validation  
- Ensure nested list dimensions match computed grid size
- Validate target_row/target_col indices are within grid bounds
- Check that order parameters contain valid dimension values

#### Graceful Degradation
- Handle empty subplots when data combinations are missing
- Continue plotting other subplots if individual subplots fail
- Provide clear warnings about skipped subplots

### 11. Performance Optimization

**Requirement**: Efficient handling of large datasets and complex grids.

**Specifications**:
- Minimize DataFrame copying and subsetting operations
- Vectorized data preparation where possible
- Efficient memory usage for large subplot counts
- Lazy evaluation of data subsets until plotting

### 12. Advanced Styling Options

**Requirement**: Additional styling control for complex scenarios.

**Specifications**:
- `color_wrap=True/False`: Whether to wrap color cycle vs maintain consistent mapping
- `subplot_spacing`: Control spacing between subplots beyond FigureConfig
- `edge_labels_only=True`: Axis labels only on grid edges (default for multi-subplot)
- Integration with existing theme system styling parameters

### 13. Data Aggregation Support

**Requirement**: Handle multiple observations per (x, hue) combination.

**Specifications**:
- `agg_func="mean"`: Aggregate function for multiple values  
- `error_bars="std"`: Error bar type when aggregating
- `ci=95`: Confidence interval percentage
- Support for common aggregation patterns in ML evaluation data

### 14. Debug and Inspection Tools

**Requirement**: Development and debugging support for complex faceted plots.

**Specifications**:
- `debug=True`: Print data subsetting and grid computation info
- `dry_run=True`: Validate all parameters without actually plotting
- `fm.get_facet_info()`: Return computed grid layout and data subsets
- `fm.get_subplot_data(row, col)`: Access data used for specific subplot

## Priority Classification

### Critical (Phase 3/4 Implementation)
- Core Faceting API (Requirement 1)
- Flexible Layout System (Requirement 2)  
- Ordering and Filtering Control (Requirement 3)
- Layered Faceting (Requirement 5)

### High Priority (Phase 4 Implementation)
- Per-Subplot Fine Control (Requirement 4)
- Styling Coordination (Requirement 6)
- Data Integration (Requirement 7)
- Shared Axes Control (Requirement 9)
- Error Handling and Validation (Requirement 10)

### Medium Priority (Future Phases)
- Subplot Title Management (Requirement 8)
- Performance Optimization (Requirement 11)
- Advanced Styling Options (Requirement 12)
- Data Aggregation Support (Requirement 13)

### Nice to Have (Future)
- Debug and Inspection Tools (Requirement 14)
- Export and save integration enhancements

## Success Criteria

**Functional**:
- Reduce 95+ line faceted plot examples to <20 lines with new API
- All existing dr_plotter functionality remains unchanged (backward compatibility)
- Complex layered visualizations possible with intuitive API calls

**Quality**:
- Publication-ready output quality matches or exceeds current examples
- Performance comparable to manual subplot management
- Comprehensive error messages guide users through common mistakes

**Usability**:
- API feels natural to ML researchers familiar with faceted plotting concepts
- Fine-grained control available when needed without breaking high-level convenience
- Clear mental model for dimension mapping and subplot targeting