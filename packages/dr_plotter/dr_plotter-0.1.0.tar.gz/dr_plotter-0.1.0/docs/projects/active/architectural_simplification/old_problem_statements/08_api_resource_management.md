# Problem Statement: API Resource Management

**Priority**: 2 (High Value)

## Strategic Objective

Fix the resource management issues in the public API where each function creates unnecessary FigureManager instances, and improve the API design to better serve both simple and advanced use cases while eliminating resource waste.

## Problem Context

The public API in `api.py` has resource management and design issues that create inefficiency and missed opportunities:

**Current Resource Management Problems**:
```python
# From api.py - wasteful pattern repeated in every function
def scatter(data, x, y, ax=None, **kwargs):
    fm = FigureManager(external_ax=ax)  # New instance every time
    fm.plot("scatter", 0, 0, data, x=x, y=y, **kwargs)
    fm.finalize_layout()
    # FigureManager instance discarded - no cleanup, potential memory leaks
    return fm.fig, fm.get_axes(0, 0)
```

**API Design Issues**:
- **Resource waste**: New FigureManager for every API call instead of reuse
- **Missed opportunity**: API could be much simpler than current FigureManager interface
- **Inconsistent return types**: Some functions return Figure+Axes, others might return different things
- **Limited functionality**: API functions don't expose advanced features users might want

**Evidence of Problems**:
- **Memory inefficiency**: Creating and discarding complex objects for simple plots
- **Performance overhead**: Full FigureManager initialization for single-plot operations
- **API inconsistency**: `hist` uses `"histogram"` internally (line 64) - parameter/internal name mismatch
- **Limited extensibility**: Hard to add new API functions without duplicating resource management

## Requirements & Constraints

### Must Preserve
- **Function signatures** - existing user code continues working
- **Return value format** - `(Figure, Axes)` tuple maintained
- **Matplotlib integration** - external axes support preserved
- **All current functionality** - no regression in plotting capabilities

### Must Achieve
- **Resource efficiency** - eliminate unnecessary object creation
- **Consistent behavior** - all API functions follow same patterns
- **Clean resource management** - proper cleanup and memory management
- **Extensibility** - easy to add new API functions

### Cannot Break
- **User workflows** - existing scripts using API functions continue working
- **External axes integration** - `ax` parameter functionality preserved
- **Return value expectations** - users expecting Figure and Axes objects get them

## Decision Frameworks

### Resource Management Strategy
**Option A**: Shared FigureManager pool for API functions
**Option B**: Lightweight API-specific plotting class
**Option C**: Direct matplotlib calls with minimal wrapper
**Option D**: Stateless API functions that create optimized, minimal objects

**Decision Criteria**:
- Minimize resource overhead for simple operations
- Maintain consistency with full FigureManager behavior
- Enable future API extensions
- Preserve external axes integration

**Recommended**: Option B - lightweight class designed specifically for API use cases

### API Design Strategy
**Option A**: Keep current function-per-plot-type approach
**Option B**: Generic `plot(type, ...)` function with specific functions as convenience
**Option C**: Fluent interface - `api.plot(data).scatter(x, y)`
**Option D**: Class-based API - `Plotter(data).scatter(x, y)`

**Decision Criteria**:
- Align with user mental model for simple plotting
- Maintain backward compatibility
- Enable discovery of plot types and parameters
- Minimize cognitive load for common cases

**Recommended**: Option A with internal refactoring - preserve external interface, improve implementation

### External Axes Handling Strategy
**Option A**: Special-case external axes throughout API implementation
**Option B**: Normalize external axes into consistent internal format
**Option C**: Separate code paths for external vs internal axes
**Option D**: Abstract axes management behind clean interface

**Decision Criteria**:
- Eliminate code duplication across API functions
- Maintain matplotlib compatibility
- Clear separation of concerns
- Minimal complexity for common cases

**Recommended**: Option B - normalize early, handle consistently

## Success Criteria

### Resource Efficiency Success
- **Memory usage reduction** - API functions use significantly less memory per call
- **Performance improvement** - faster execution for simple plots
- **Proper cleanup** - no resource leaks from API function calls
- **Scalability** - API functions perform well with repeated calls

### Code Quality Success
- **Duplication elimination** - shared resource management code across API functions
- **Consistent patterns** - all API functions follow identical internal structure
- **Clear separation** - API concerns separated from full FigureManager concerns
- **Easy extension** - adding new API functions requires minimal boilerplate

### User Experience Success
- **No behavior changes** - existing user code works identically
- **Better performance** - users notice faster simple plotting operations
- **Consistent interface** - all API functions behave predictably
- **Clear documentation** - API function purpose and usage obvious

## Quality Standards

**Reference**: Follow `docs/processes/design_philosophy.md` principles

**Key Principles Applied**:
- **Focus on Researcher's Workflow**: Simple plots should be as frictionless as possible
- **Succinct and Self-Documenting**: API code should be minimal and obvious
- **Architectural Courage**: Fix resource issues boldly rather than working around them

**Improved API Pattern**:
```python
# Proposed efficient pattern
class _APIPlotter:
    """Lightweight plotter optimized for single-plot API functions"""
    def __init__(self, external_ax: Optional[plt.Axes] = None):
        self.external_ax = external_ax
        self.fig, self.ax = self._setup_axes()
        
    def _setup_axes(self) -> Tuple[plt.Figure, plt.Axes]:
        if self.external_ax:
            return self.external_ax.get_figure(), self.external_ax
        return plt.subplots(1, 1)
        
    def plot(self, plot_type: str, data: DataFrame, **kwargs) -> None:
        plotter = BasePlotter.get_plotter(plot_type)
        # Minimal setup, direct plotting
        
    def finalize(self) -> Tuple[plt.Figure, plt.Axes]:
        # Minimal finalization, return resources
        return self.fig, self.ax

# API functions become simple
def scatter(data, x, y, ax=None, **kwargs):
    plotter = _APIPlotter(ax)
    plotter.plot("scatter", data, x=x, y=y, **kwargs)
    return plotter.finalize()
```

### API Implementation Standards
- **Minimal object creation** - only create what's actually needed
- **Consistent resource lifecycle** - setup, use, cleanup pattern for all functions
- **Shared code paths** - common operations factored into reusable components
- **Clear separation** - API concerns don't leak into core plotting logic

## Adaptation Guidance

### Expected Discoveries
- **Hidden dependencies** on full FigureManager functionality in API use cases
- **Performance bottlenecks** in current FigureManager initialization
- **Edge cases** in external axes handling across different plot types
- **User workflows** that depend on current resource management behavior

### Handling Resource Management Challenges
- **If lightweight approach breaks functionality**: Identify minimal FigureManager features needed for API
- **If external axes integration is complex**: Consider separate optimized path for external axes
- **If performance doesn't improve**: Profile to identify actual bottlenecks
- **If memory usage doesn't decrease**: Examine what resources are actually being held

### Implementation Strategy
- **Benchmark current performance** - establish baseline for improvement measurement
- **Implement lightweight plotter** - focus on API use cases specifically
- **Test with existing examples** - ensure no behavior changes
- **Monitor resource usage** - verify improvements are real

## Documentation Requirements

### Implementation Documentation
- **Resource management architecture** showing new API implementation approach
- **Performance benchmarks** comparing old vs new resource usage
- **API implementation patterns** for consistent future development
- **External axes handling** documentation for maintainers

### Strategic Insights
- **Resource waste patterns** identified in original API design
- **Performance characteristics** of different resource management approaches
- **User workflow analysis** informing optimal API design
- **Extension patterns** for adding new API functions efficiently

### Future Reference
- **API design principles** for consistent future development
- **Resource management patterns** for other components
- **Performance optimization techniques** applied to API functions

---

**Key Success Indicator**: When API resource management is fixed, users should experience noticeably faster performance for simple plots, and the API implementation should be clean enough that adding new plot types requires only a few lines of boilerplate code.