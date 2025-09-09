# DR_PLOTTER DESIGN DECISIONS

**Last Updated**: 2025-08-29  
**Enhanced**: Consolidated with architectural insights from comprehensive audit and analysis work

## General Architecture

### **Assertions Over Exceptions**
**What**: Use Python assertions for validation instead of try-catch exception handling
**Rationale**: Performance critical for ML code; fail-fast philosophy makes bugs obvious; reduces defensive programming that masks real issues

### **Complete Type Coverage** 
**What**: Every function parameter and return value must have explicit type hints
**Rationale**: Enables static analysis, improves code clarity, prevents type-related bugs; specific patterns like `-> None` for `__init__` methods ensure consistency

### **No Code Comments Policy**
**What**: Zero tolerance for comments, docstrings, or inline documentation in code
**Rationale**: Forces self-documenting code through clear naming and structure; aligns with minimalism principle; prevents documentation drift

### **FigureManager Primary Interface**
**What**: FigureManager is the main user-facing API, with direct plotting API as secondary
**Rationale**: Tests complete architectural stack integration; provides systematic multi-subplot coordination; enables figure-level styling coordination

### **Breaking Changes Acceptable**
**What**: Backward compatibility is not a constraint for design improvements
**Rationale**: Research library philosophy prioritizes optimal design over stable APIs; enables systematic architectural improvements

## Style System

### **Theme Hierarchy Resolution**
**What**: Style resolution follows: user kwargs → group styles → plot theme → base theme → hardcoded fallback
**Rationale**: Provides predictable override behavior; enables systematic theming while allowing granular control; ensures fallback behavior is always defined

### **Component-Based Styling**
**What**: All styling operations organized by components (main, title, xlabel, grid, etc.) with phase-based execution
**Rationale**: Enables granular theming control; separates concerns clearly; allows systematic styling across different plot types

### **Shared Cycle Configuration**
**What**: Plots within a figure can share style cycles for coordinated visual encoding
**Rationale**: Prevents duplicate colors/markers in multi-plot figures with shared legends; enables systematic progression through style cycles

### **Error Color Recovery**
**What**: Failed styling operations fall back to bright red (#FF0000) with console warnings
**Rationale**: Makes styling failures immediately obvious for debugging; prevents silent failures that hide configuration issues

## Legend Management

### **Strategy-Based Legend System**
**What**: Four legend strategies - PER_AXES, FIGURE_BELOW, GROUPED_BY_CHANNEL ("split"), NONE - with different coordination behavior
**Rationale**: Different use cases require different legend approaches; systematic approach prevents inconsistent legend behavior across plot types

### **Channel-Based Deduplication**
**What**: Shared legend strategies (split, figure_below) deduplicate by visual channel value; per-axes strategies deduplicate by axis scope
**Rationale**: Shared legends should show unique values regardless of source plot; per-axes legends need axis-specific entries for same values

### **Centralized Legend Registration**
**What**: All legend entries go through FigureManager.register_legend_entry() with LegendRegistry managing deduplication
**Rationale**: Single coordination point prevents inconsistent legend behavior; enables systematic deduplication and positioning

### **Legend vs Colorbar Separation**
**What**: Text/marker legends handled by legend system; continuous color mapping handled by separate colorbar components
**Rationale**: Different visual encoding types require different implementation approaches; prevents feature mixing that complicates both systems

## Plot Architecture

### **BasePlotter Inheritance**
**What**: All 8 plotters inherit from BasePlotter with consistent lifecycle methods (prepare_data, render, _draw)
**Rationale**: Ensures systematic behavior across plot types; enables consistent styling integration; reduces code duplication

### **Component Schema Standardization**
**What**: Each plotter defines component schemas specifying styleable attributes by phase (plot, axes)
**Rationale**: Systematic styling requires explicit attribute definitions; enables StyleApplicator to work consistently across plot types

### **Data Preparation Consistency**
**What**: Consistent column renaming (x_col → X_COL_NAME) and melting patterns across plotters
**Rationale**: Systematic data handling reduces plotter-specific logic; enables consistent downstream processing

### **Grouped vs Individual Rendering**
**What**: Single render() method handles both individual and grouped plotting through GroupingConfig
**Rationale**: Eliminates code duplication between plotting modes; systematic approach to visual encoding channels

## Process Architecture

### **Evidence-Based Validation**
**What**: All architectural claims must be verified with concrete evidence (file/line references, pattern counts)
**Rationale**: Prevents implementation of solutions to non-existent problems; ensures recommendations are grounded in reality

### **Multi-Agent Coordination**
**What**: Complex tasks use specialized agents with systematic handoffs and conflict resolution
**Rationale**: Enables parallel work while maintaining quality; systematic approach to handling agent disagreements and validation

### **Systematic Process Design**
**What**: Create reusable multi-stage processes (audit → synthesis → verification) rather than ad-hoc solutions
**Rationale**: Scales coordination effort; creates repeatable approaches to complex architectural challenges; maintains quality standards

### **Iterative Process Refinement**
**What**: Processes are designed, tested, and refined based on empirical results
**Rationale**: Enables continuous improvement of coordination effectiveness; prevents process rigidity that reduces adaptability