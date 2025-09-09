# Configuration System Consolidation - Phase 1: PlotConfig Foundation

## Strategic Objective

Create the PlotConfig foundation system that will replace the fragmented configuration architecture (FigureConfig, LegendConfig, Theme) with a unified interface supporting both simple string parameters and detailed config objects. This enables iterative workflow patterns while preserving fine-grained control for power users.

## Problem Context  

The current dr_plotter configuration system creates workflow friction through:
- **Multiple config objects** requiring manual coordination (FigureConfig + LegendConfig + Theme)
- **No preset system** for common patterns like bump plots or publication figures
- **No iterative interface** for rapid refinement of colors, layouts, legend positioning
- **Configuration precedence conflicts** between theme and explicit config settings

Analysis shows 36+ examples with repetitive configuration patterns that could be simplified through presets and unified interface.

## Requirements & Constraints

### Must Preserve
- **All current functionality** - no regression in plotting capabilities
- **Fine-grained control** - power users retain access to all matplotlib parameters through detailed config objects
- **Type safety** - maintain complete type hints throughout
- **Existing FigureManager interface** - current examples must continue working during transition

### Must Achieve  
- **PlotConfig unified interface** accepting both simple and detailed configurations
- **Domain-specific presets** for common patterns (bump_plot, publication, dashboard)
- **Internal config architecture** using new LayoutConfig and StyleConfig classes (not reusing existing FigureConfig)
- **Iterative workflow methods** - `.with_colors()`, `.with_layout()`, `.with_legend()` for rapid refinement
- **Backwards compatibility** - existing FigureManager calls work unchanged

### Cannot Break
- **Any existing functionality** - all current plotting capabilities preserved
- **Public APIs** - FigureManager interface maintained (can be extended)
- **Type checking** - no loss of type safety

## Decision Frameworks

### Internal Config Architecture Strategy
**Chosen Approach**: Create new internal config classes (LayoutConfig, StyleConfig) rather than reusing existing ones
- **LayoutConfig**: Handle rows/cols, figsize, spacing parameters (replaces FigureConfig role)
- **StyleConfig**: Handle colors, plot_styles, fonts, figure settings (replaces Theme role)  
- **PlotConfig**: Unified interface accepting both simple parameters and detailed config objects

**Decision Criteria Applied**: Clean architecture with single responsibility, no legacy baggage from existing config complexity

### Preset System Strategy
**Approach**: Built-in PLOT_CONFIGS dictionary with domain-specific presets
- **bump_plot**: Optimized colors and styling for bump chart visibility
- **publication**: Professional styling with appropriate fonts and DPI
- **dashboard**: Multi-subplot layout with grouped legends
- **faceted_analysis**: Optimized for complex multi-dimensional data

**Decision Criteria**: Cover most common use cases identified in existing examples

### Transition Strategy  
**Approach**: Additive interface during Phase 1 - FigureManager accepts optional PlotConfig alongside existing parameters
- Enables testing and validation without breaking existing code
- Internal conversion from PlotConfig to legacy configs maintains functionality
- Sets foundation for Phase 4 complete replacement

## Success Criteria

### Interface Creation Success
- **PlotConfig class** accepts both simple parameters (`layout=(2,2)`) and detailed objects (`layout=LayoutConfig(...)`)
- **Domain presets work** - `PlotConfig.from_preset("bump_plot")` produces appropriate styling
- **Iterative methods work** - `config.with_colors([...]).with_layout(3, 2)` enables rapid refinement
- **Type safety maintained** - all methods have complete type hints

### Integration Success  
- **FigureManager extended** to accept optional `config: PlotConfig` parameter
- **Backwards compatibility** - all existing FigureManager calls continue working unchanged
- **Internal conversion** - PlotConfig properly converts to existing config objects for rendering
- **No functionality regression** - all current plotting capabilities preserved

### Code Quality Success
- **Clean architecture** - new internal config classes follow single responsibility
- **Comprehensive type hints** - all classes and methods fully typed
- **Validation preserved** - configuration validation logic maintained
- **Documentation clarity** - code is self-documenting through clear naming

## Quality Standards

**Reference**: Follow `docs/processes/design_philosophy.md` principles

**Key Principles Applied**:
- **Focus on Researcher's Workflow**: Enable rapid iteration and domain-specific presets
- **Clarity Through Structure**: Unified interface with obvious organization
- **Zero Comments Policy**: Code self-documenting through clear naming and type hints
- **Comprehensive Typing**: All function signatures with complete type hints

**Implementation Pattern Example**:
```python
# Target usage after implementation
config = (PlotConfig.from_preset("publication")
          .with_layout(2, 3)  
          .with_colors(CUSTOM_PALETTE)
          .with_legend(style="grouped", position="outside_right"))

with FigureManager(config) as fm:
    fm.plot("scatter", data, x="time", y="accuracy", hue_by="model")
```

## Implementation Requirements

### File Creation Required
1. **`src/dr_plotter/plot_config.py`**:
   - `LayoutConfig` dataclass with rows, cols, figsize, spacing parameters
   - `StyleConfig` dataclass with colors, plot_styles, fonts, figure parameters
   - `PlotConfig` dataclass accepting Union types for simple/detailed configs
   - `.from_preset()` classmethod loading from PLOT_CONFIGS
   - `.with_layout()`, `.with_colors()`, `.with_legend()` iterative methods
   - `._to_legacy_configs()` method converting to existing config objects

2. **`src/dr_plotter/plot_presets.py`**:
   - PLOT_CONFIGS dictionary with domain-specific presets
   - Color palettes: PUBLICATION_COLORS, BUMP_OPTIMIZED_PALETTE
   - Presets: "default", "bump_plot", "publication", "dashboard", "faceted_analysis"

3. **Update `src/dr_plotter/figure.py`**:
   - Add PlotConfig import
   - Extend FigureManager.__init__ to accept optional `config: PlotConfig`
   - Add conversion logic: if config provided, convert to legacy configs
   - Preserve all existing initialization logic

### Integration Points
- **FigureManager constructor** must handle both old and new interfaces seamlessly
- **Type imports** - ensure all typing imports available (Union, Optional, etc.)
- **Legacy conversion** - PlotConfig must convert properly to FigureConfig/LegendConfig/Theme
- **Validation** - preserve all existing validation logic through conversion layer

### Code Style Requirements
- **No comments or docstrings** - code must be self-documenting
- **Complete type hints** - every parameter and return value typed
- **Dataclass pattern** - use @dataclass for config classes
- **Immutable updates** - .with_*() methods return new instances using dataclasses.replace

## Adaptation Guidance

### Expected Discoveries
- **Complex parameter mapping** between new internal configs and existing ones
- **Validation interdependencies** between current config objects that affect conversion
- **Type resolution challenges** with Union types accepting both simple and complex configs
- **Import dependency cycles** between new and existing config modules

### Handling Implementation Challenges
- **If parameter mapping is complex**: Document the mapping clearly and ensure no functionality loss
- **If validation fails**: Examine whether validation is actually needed or can be simplified
- **If type resolution is difficult**: Use forward references and ensure imports are properly ordered  
- **If dependencies are circular**: Consider extracting common types to separate module

### Implementation Strategy
- **Build incrementally** - start with basic classes, add methods progressively
- **Test conversion thoroughly** - ensure PlotConfig -> legacy config conversion preserves all settings
- **Validate with existing examples** - spot-check that key examples would work through conversion
- **Handle edge cases** - ensure robust handling of None values and missing parameters

## Documentation Requirements

### Implementation Documentation
- **Architecture decisions** - why new internal configs vs reusing existing ones
- **Conversion logic** - how PlotConfig parameters map to legacy config objects  
- **Preset rationale** - why specific presets chosen and how they address common use cases
- **Type safety approach** - how Union types enable both simple and complex usage

### Strategic Insights  
- **Configuration complexity patterns** discovered during implementation
- **Parameter interdependencies** found between existing config objects
- **Simplification opportunities** identified through unified interface design
- **Workflow patterns** that inform iterative method design

### Future Reference
- **Extension patterns** - how to add new presets and iterative methods
- **Integration approach** - lessons for Phase 4 complete replacement strategy
- **Validation consolidation** - opportunities to simplify validation logic in future phases

---

**Key Success Indicator**: When Phase 1 is complete, users should be able to write `FigureManager(PlotConfig.from_preset("bump_plot").with_layout(2,3))` and get identical output to manually configuring the equivalent FigureConfig/LegendConfig combination, while all existing FigureManager usage continues working unchanged.