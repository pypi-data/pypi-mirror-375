# Problem Statement: Decompose FigureManager

## Strategic Objective

Break up the monolithic 876-line FigureManager class into focused components with clear, single responsibilities that align with the DR methodology's "Atomicity" principle. This decomposition will reveal natural architectural boundaries and simplify state management.

## Problem Context  

The FigureManager class violates multiple DR methodology principles by handling too many responsibilities:

**Current Responsibility Overload**:
- **Figure/subplot creation and management** (lines 92-140)
- **Plot coordination and rendering** (lines 200-350)
- **Faceting pipeline orchestration** (lines 400-600)
- **Legend system coordination** (lines 150-199)
- **Style system integration** (lines 76, 95-96)
- **Layout finalization and cleanup** (lines 800-876)

**Architectural Issues**:
- **Mixed abstraction levels**: High-level coordination mixed with implementation details
- **Complex state management**: Multiple interdependent instance variables that must stay synchronized
- **Unclear boundaries**: No clear separation between figure-level concerns and plot-level concerns
- **Testing difficulty**: Single class requires complex setup for any unit test

**Evidence of Problems**:
```python
# From figure.py - single class handling everything
class FigureManager:
    def __init__(self, figure, legend, theme):  # Configuration coordination
        # ... 50 lines of initialization
        
    def plot(self, plot_type, row, col, data, **kwargs):  # Plot rendering
        # ... 80 lines mixing coordination and implementation
        
    def _setup_faceting_pipeline(self, ...):  # Faceting orchestration  
        # ... 100+ lines of complex pipeline logic
        
    def finalize_layout(self):  # Layout and cleanup
        # ... 40 lines of figure finalization
```

## Requirements & Constraints

### Must Preserve
- **Public API compatibility** - `FigureManager` interface remains unchanged for users
- **Context manager behavior** - `with FigureManager() as fm:` pattern continues working
- **All plotting functionality** - no regression in plot types or features
- **Integration points** - matplotlib, pandas, style systems

### Must Achieve
- **Clear separation of concerns** - each component has single, well-defined purpose
- **Simplified state management** - minimal shared state between components
- **Natural architectural boundaries** - boundaries that reflect conceptual model
- **Improved testability** - components can be unit tested independently

### Cannot Break
- **User code** - existing examples and user scripts continue working
- **Configuration system** - config objects work with new architecture
- **External integrations** - no changes to matplotlib or pandas interactions

## Decision Frameworks

### Component Decomposition Strategy
**Option A**: Horizontal split by functionality (PlotManager, LayoutManager, StyleManager)
**Option B**: Vertical split by concern level (Coordinator, Orchestrator, Renderer)
**Option C**: Domain split by plotting concepts (FigureBuilder, PlotRenderer, LayoutFinalizer)

**Decision Criteria**:
- Components should align with natural conceptual boundaries
- Each component should have clear, single responsibility
- Dependencies should flow in one direction
- Testing should be straightforward for each component

**Recommended**: Option C (domain split) - aligns with how users think about plotting process

### State Management Approach
**Option A**: Shared state object passed between components
**Option B**: Immutable state with explicit state transitions
**Option C**: Message passing between independent components

**Decision Criteria**:
- Minimize coupling between components
- Make state changes explicit and traceable
- Maintain performance for plotting operations
- Keep complexity manageable

**Recommended**: Option A with clear ownership - simple and performant

### FigureManager Role After Decomposition
**Option A**: Thin facade that delegates to specialist components
**Option B**: Coordinator that orchestrates but doesn't implement
**Option C**: Eliminate entirely, expose components directly

**Decision Criteria**:
- Preserve user API compatibility
- Maintain single entry point for common workflows
- Enable advanced users to access components directly
- Keep coordination logic clear and minimal

**Recommended**: Option B (coordinator pattern) - maintains compatibility while enabling flexibility

## Success Criteria

### Architectural Success
- **Single responsibility components** - each class has one clear purpose
- **Clear dependency direction** - no circular dependencies between components
- **Natural boundaries** - component splits align with user mental model
- **Reduced complexity** - individual components are easier to understand

### Code Quality Success
- **Line count reduction** - largest component significantly smaller than current FigureManager
- **Improved testability** - components can be tested in isolation
- **Clear interfaces** - component boundaries have obvious, clean APIs
- **Elimination of mixed concerns** - no component handles multiple abstraction levels

### User Experience Success
- **No API changes** - existing user code continues working unchanged
- **Better error messages** - problems traced to specific components
- **Performance maintained** - no regression in plotting performance
- **Extension points** - advanced users can customize individual components

## Quality Standards

**Reference**: Follow `docs/processes/design_philosophy.md` principles

**Key Principles Applied**:
- **Atomicity**: Each component has single, well-defined purpose
- **Clarity Through Structure**: Code organization reflects conceptual model
- **Architectural Courage**: Bold restructuring rather than incremental complexity addition

**Component Design Patterns**:
```python
# Clear component boundaries
class FigureBuilder:
    """Handles figure and subplot creation"""
    def create_figure_with_subplots(self, config: FigureConfig) -> FigureState
    
class PlotRenderer:  
    """Handles individual plot rendering"""
    def render_plot(self, plot_type: str, subplot: SubplotRef, data: DataFrame) -> PlotState
    
class LayoutFinalizer:
    """Handles layout, legends, and figure finalization"""  
    def finalize_figure(self, figure_state: FigureState, plot_states: List[PlotState]) -> None
```

### State Management Standards
- **Explicit ownership** - clear which component owns which state
- **Minimal sharing** - only essential state shared between components  
- **Immutable where possible** - reduce risk of accidental state corruption
- **Clear lifecycle** - state creation, modification, and cleanup well-defined

## Adaptation Guidance

### Expected Discoveries
- **Hidden dependencies** between current mixed responsibilities
- **State synchronization issues** that weren't obvious in monolithic design
- **Performance bottlenecks** from excessive state passing
- **Testing gaps** revealed by component isolation

### Handling Component Boundary Questions
- **If responsibility is unclear**: Assign to component closest to user's mental model
- **If multiple components need same data**: Consider if it belongs in shared state or if design needs refinement
- **If performance suffers**: Evaluate whether boundary is in wrong place or state sharing is too heavy

### Integration Strategy
- **Preserve existing tests** - run full test suite against new architecture
- **Phase introduction** - implement components one at a time with existing code as fallback
- **Monitor complexity** - ensure decomposition reduces rather than increases cognitive load

## Documentation Requirements

### Implementation Documentation
- **Component architecture diagram** showing responsibilities and dependencies
- **State flow documentation** describing how state moves through components
- **Migration notes** for any internal API changes (not user-facing)

### Strategic Insights
- **Natural boundaries discovered** during decomposition
- **Hidden complexity revealed** by separating concerns
- **Performance implications** of the new architecture
- **Testing improvements** gained from component isolation

### Future Reference
- **Component design patterns** established for consistent future development
- **Extension points** for advanced customization
- **Refactoring approach** that can be applied to other monolithic classes

---

**Key Success Indicator**: When FigureManager is decomposed, each component should be easily explainable to a new developer, and the overall system should be more testable and maintainable while preserving all user-facing functionality.