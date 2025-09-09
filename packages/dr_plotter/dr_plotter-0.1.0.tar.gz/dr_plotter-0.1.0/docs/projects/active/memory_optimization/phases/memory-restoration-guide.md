# Memory Restoration Guide: FigureManager Parameter Organization Project

## Current Project Status: Phase 2 Complete, Ready for Phase 3 Decision

### What We're Working On
**Goal**: Systematic reorganization of FigureManager parameter architecture to resolve parameter chaos, fix theme integration conflicts, and establish clean foundation for advanced features.

**Root Problem**: FigureManager had grown organically with unorganized parameters, broken controls (margin parameters didn't work), and poor parameter routing.

## Major Accomplishments ✅

### Phase 1: Architecture Analysis (COMPLETE)
- **Phase 1a**: Architecture inventory revealed rich config infrastructure already exists (80% complete)
- **Discovery**: SubplotFacetingConfig exists but unused - ready for future faceted plotting
- **Finding**: Legacy bridge methods handle parameter conversion but create chaos

### Phase 2: Clean Slate Implementation (COMPLETE) 
- **Legacy bridge removal**: Deleted `_convert_legacy_*()` methods (~100 lines)
- **Config-first constructor**: FigureManager now accepts only config objects
- **FigureConfig consolidation**: Eliminated artificial SubplotLayoutConfig separation
- **Examples updated**: Both faceted plotting examples now use clean consolidated architecture

## Current Architecture (Successfully Implemented)

### Clean FigureManager Constructor:
```python
FigureManager(
    figure=FigureConfig(
        rows=2, cols=4, figsize=(16, 9), tight_layout_pad=0.3,
        subplot_kwargs={"sharey": "row"}
    ),
    legend=LegendConfig(...),
    theme=Theme(...)
)
```

### Parameter Classification Principle:
- **Explicit parameters**: Common structural params (rows, cols, figsize) + non-matplotlib function params (tight_layout_pad)
- **Kwargs dictionaries**: Direct matplotlib function parameters (figure_kwargs → plt.figure(), subplot_kwargs → plt.subplots())

## Issues We've Identified & Documented

### Parameter Routing Problems:
1. **Data ordering override**: Internal pandas.pivot() destroys user data ordering
2. **Stranded plotter parameters**: HeatmapPlotter format='int', xlabel_pos='bottom' exist in code but no API route
3. **Theme-behavior misalignment**: GROUPED_BAR_THEME doesn't control grouping (themes = styling only)
4. **Manual axes access**: Users must call ax.set_xlim(), ax.set_yscale() manually

### Architecture Audit Results:
- **Current parameter flow works well** for most cases (fm.plot kwargs → plotter)
- **Specific gaps**: Heatmap stranded parameters, manual axes configuration
- **Theme system**: Excellent but doesn't cover all parameter types

## Strategic Decision Point: What's Next?

### Option 1: Current Architecture Is Sufficient
- Consolidated FigureConfig solved major architectural problems
- Most parameter routing works well through existing kwargs flow
- Manual axes access acceptable for advanced use cases

### Option 2: Add Systematic Parameter Routing
- `axes_kwargs` in FigureManager constructor for ax.set_*() parameters
- `plotter_kwargs` in FigureManager constructor for stranded plotter parameters
- Provides systematic routing vs manual post-plot configuration

## Key Documents & Context

### Essential Reading:
- `docs/plans/2025-08-26-figuremanager-parameter-organization.md` - Complete project plan
- `docs/architecture-inventory.md` - Config infrastructure analysis
- `docs/axes-plotter-parameter-routing-audit.md` - Current parameter routing analysis
- `docs/reports/2025-08-26_figuremanager_parameter_organization/` - Lab notes and strategic report

### Working Files:
- `examples/06_faceted_training_curves.py` - Updated with consolidated architecture
- `examples/06b_faceted_training_curves_themed.py` - Themed version with consolidated architecture

## User Collaboration Style

### Your Approach (Critical for Continuity):
- **Strategic thinking partner**: Analysis → Options → Recommendation structure
- **Evidence-based decisions**: No assumptions, always validate with concrete data
- **Systematic architectural work**: Build on established patterns, create reusable processes
- **Quality standards**: No comments, assertions over exceptions, complete type hints, fail fast/loud

### Decision Philosophy:
- **No backward compatibility**: Clean slate approach, breaking changes acceptable
- **Build on existing**: 80% of config infrastructure already exists, extend rather than replace
- **User mental model**: Match how researchers actually think about plot configuration
- **Organized flexibility**: Explicit params for common cases, kwargs for power users

## Immediate Next Decision

**Question to resolve**: Do we need `axes_kwargs` and `plotter_kwargs` in FigureManager constructor, or is the current consolidated architecture sufficient?

**Context for decision**: 
- Examples now use clean consolidated FigureConfig (much simpler)
- Still have stranded heatmap parameters and manual axes access
- Need to balance systematic architecture vs practical sufficiency

**Evidence needed**: Test current consolidated architecture against real use cases to see if additional parameter routing justified.

## Key Principle: Minimize Friction Between Idea and Visualization
Every design choice should reduce friction for researchers. The consolidated FigureConfig achieved this - question is whether additional parameter routing enhancements provide enough friction reduction to justify architectural complexity.