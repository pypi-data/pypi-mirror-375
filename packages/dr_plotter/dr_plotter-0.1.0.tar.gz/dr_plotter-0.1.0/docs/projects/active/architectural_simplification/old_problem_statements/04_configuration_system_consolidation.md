# Problem Statement: Configuration System Consolidation

## Strategic Objective

Replace the fragmented configuration system with a single PlotConfig interface that provides domain-specific intelligence, supports iterative refinement workflows, and eliminates configuration complexity while preserving fine-grained control. This addresses the core workflow needs of rapid iteration and domain-specific styling (like bump plots) that require precise formatting.

## Problem Context

The current configuration system creates cognitive overload and impedes the iterative plotting workflow that is essential for research:

**Workflow Friction Issues**:
- **Complex configuration for common tasks** - creating a 2x2 grid with grouped legends requires understanding 3+ config objects
- **Poor iterative refinement** - changing colors or legend positioning requires reconstructing entire config objects  
- **No domain-specific intelligence** - specialized plots like bump plots need manual styling configuration every time
- **Precedence conflicts** - theme.legend_config can override LegendConfig at runtime, creating unpredictable behavior

**Evidence of Workflow Problems**:
```python
# Current - complex setup for simple 2x2 grid with grouped legends
with FigureManager(
    figure=FigureConfig(rows=2, cols=2, figsize=(12,10), tight_layout_pad=0.3),
    legend=LegendConfig(strategy=LegendStrategy.GROUPED_BY_CHANNEL, channel_titles={...}),
    theme=custom_theme
) as fm:
    # Iterative changes require reconstructing configs
    
# What's needed for bump plots - complex manual styling every time
bump_theme = Theme(colors=high_contrast_palette, line_styles=distinct_patterns, ...)
with FigureManager(figure=..., legend=..., theme=bump_theme) as fm:
    fm.plot("bump", ...)  # Still needs manual styling parameters
```

**Core Workflow Requirements Not Met**:
- **Iterative refinement** - quickly changing specific aspects (colors, legend position, layout) 
- **Domain-specific presets** - bump plots, scatter matrices need specialized styling to be readable
- **Fine-grained control** - ability to override any aspect without modifying library code
- **Zero-config common cases** - simple plots should work great with minimal configuration

## Requirements & Constraints

### Must Preserve
- **All current functionality** - no regression in plotting capabilities
- **Fine-grained control** - ability to customize any aspect without modifying library code
- **Type safety** - maintain complete type hints
- **Configuration expressiveness** - preserve all current customization capabilities

### Must Achieve  
- **Iterative workflow support** - quick modification of specific aspects (colors, legend, layout)
- **Domain-specific intelligence** - plot-type-aware presets (bump plots, scatter matrices, etc.)
- **Zero-config excellence** - simple plots work great with minimal configuration
- **Single source of truth** - eliminate configuration precedence conflicts
- **Immediate validation failure** - clear error messages, no auto-correction

### Cannot Break
- **Public API** - FigureManager interface preserved (implementation can change)
- **Advanced customization** - power users retain access to all matplotlib parameters
- **Plot quality** - specialized plots like bump plots maintain visual excellence

### Design Principles
- **Breaking changes acceptable** - optimize for best user experience, not backward compatibility
- **Clean presets + granular override** - simple cases simple, complex cases possible
- **Auto-calculate missing dimensions** - sensible defaults where appropriate

## Decision Frameworks

### PlotConfig Architecture Strategy
**Option A**: Single PlotConfig with domain-specific presets and iterative methods
**Option B**: Hierarchical config objects organized by concern (LayoutConfig, StyleConfig, LegendConfig)
**Option C**: Functional builder pattern with method chaining
**Option D**: Multiple specialized config classes for different use cases

**Decision Criteria**:
- Support iterative workflow (change specific aspects quickly)
- Provide domain-specific intelligence (bump plot presets)
- Maintain fine-grained control without library modification
- Clear mental model for users

**Recommended**: Option A - single PlotConfig with smart presets and `.with_*()` methods for iteration

### Domain-Specific Intelligence Strategy
**Option A**: Plot-type-aware presets with automatic styling
**Option B**: User-defined custom presets stored in configuration files
**Option C**: Dynamic preset generation based on data analysis
**Option D**: Manual configuration only, no preset intelligence

**Decision Criteria**:
- Eliminate repetitive manual styling for specialized plots like bump plots
- Provide excellent defaults for common plot types
- Enable easy customization of presets
- Maintain predictable behavior

**Recommended**: Option A - built-in plot-type presets with clear override paths

### Iterative Workflow Support Strategy
**Option A**: Immutable config objects with `.with_*()` methods returning new configs
**Option B**: Mutable config objects with `.update()` methods
**Option C**: Builder pattern with fluent interface
**Option D**: Configuration templates with parameter substitution

**Decision Criteria**:
- Enable rapid iteration on specific aspects (colors, positioning, layout)
- Clear, discoverable methods for common modifications
- Type safety and predictable behavior
- Align with functional programming best practices

**Recommended**: Option A - immutable configs with explicit `.with_*()` methods

## Success Criteria

### Workflow Support Success
- **Iterative refinement** - users can quickly modify colors, legend position, layout without reconstructing configs
- **Domain intelligence** - `PlotConfig.from_preset("bump_plot")` produces excellent styling automatically
- **Zero-config excellence** - simple plots look great with `FigureManager()` default
- **Fine-grained control** - users can override any matplotlib parameter through config

### Interface Simplification Success  
- **Single configuration object** - PlotConfig replaces FigureConfig, LegendConfig, Theme complexity
- **Clear precedence** - no configuration conflicts or mysterious override behavior
- **Progressive disclosure** - simple string parameters for common cases, full config objects for power users
- **Discoverable features** - domain presets and iterative methods are obvious

### Implementation Success
- **Code consolidation** - configuration logic centralized in PlotConfig system
- **Validation clarity** - immediate failure with clear error messages
- **Type safety** - complete type hints with meaningful type checking
- **Clean architecture** - configuration concerns separated from rendering logic

## Quality Standards

**Reference**: Follow `docs/processes/design_philosophy.md` principles

**Key Principles Applied**:
- **Focus on Researcher's Workflow**: Support iterative refinement and domain-specific styling needs
- **Clarity Through Structure**: Single configuration object with obvious organization
- **Architectural Courage**: Bold replacement of fragmented system rather than incremental patches
- **Succinct and Self-Documenting**: Configuration interface supports rapid iteration

**Proposed PlotConfig Design Pattern**:
```python
# Zero-config excellence
with FigureManager() as fm:
    fm.plot("scatter", data, x="time", y="accuracy", hue_by="model")

# Domain-specific intelligence  
with FigureManager(PlotConfig.from_preset("bump_plot", layout=(2, 2))) as fm:
    fm.plot("bump", data, ...)  # Automatically gets optimal bump plot styling

# Iterative workflow support
config = PlotConfig.from_preset("bump_plot")
config = config.with_layout((2, 3))
config = config.with_colors(["#FF6B6B", "#4ECDC4", "#45B7D1"])
config = config.with_legend(style="grouped", position="outside_right")

# Fine-grained control when needed
with FigureManager(PlotConfig(
    layout=LayoutConfig(rows=2, cols=3, figsize=(16, 12), spacing={"wspace": 0.3}),
    style=StyleConfig(plot_styles={"bump": {"linewidth": 4, "alpha": 0.8}}),
    legend=LegendConfig(style="grouped", position=(0.95, 0.8), ncol=2)
)) as fm:
    # Complete control available
```

## Implementation Strategy

### Phase 1: PlotConfig Foundation (Week 1-2)
**Objective**: Build PlotConfig alongside current system without breaking changes

**Key Components**:
- `PlotConfig` class with simple interface and internal conversion to current config objects
- Domain-specific presets (`PLOT_CONFIGS` dictionary with bump_plot, publication, etc.)
- FigureManager support for PlotConfig parameter alongside existing parameters

**Implementation**:
```python
# New: src/dr_plotter/plot_config.py
@dataclass
class PlotConfig:
    layout: Union[tuple, "LayoutConfig"] = (1, 1)
    style: Union[str, "StyleConfig"] = "default" 
    legend: Union[str, "LegendConfig"] = "subplot"
    
    @classmethod
    def from_preset(cls, preset_name: str, **overrides) -> "PlotConfig":
        base = PLOT_CONFIGS[preset_name]
        return base.with_overrides(**overrides)
        
    def with_layout(self, layout) -> "PlotConfig": ...
    def with_colors(self, colors) -> "PlotConfig": ...
    def with_legend(self, **kwargs) -> "PlotConfig": ...

# Updated: FigureManager.__init__ accepts PlotConfig
class FigureManager:
    def __init__(
        self,
        config: Optional[PlotConfig] = None,  # New unified parameter
        # Keep existing parameters for transition
        figure: Optional[FigureConfig] = None,
        legend: Optional[LegendConfig] = None,
        theme: Optional[Any] = None,
    ): ...
```

### Phase 2: Domain Presets Implementation (Week 2-3)
**Objective**: Create plot-type-aware configurations that eliminate manual styling

**Key Components**:
- Bump plot preset with optimized colors, line styles, and legend configuration
- Publication preset with appropriate fonts, colors, and DPI settings
- Scatter matrix preset with distinct markers and appropriate layout

**Implementation**:
```python
# New: src/dr_plotter/plot_presets.py
PLOT_CONFIGS = {
    "bump_plot": PlotConfig(
        style=StyleConfig(
            colors=BUMP_OPTIMIZED_PALETTE,  # High contrast for line visibility
            plot_styles={"bump": {"linewidth": 3, "marker": "o", "alpha": 0.8}},
        ),
        legend="grouped"  # Channel grouping optimal for bump plots
    ),
    "publication": PlotConfig(
        style=StyleConfig(
            colors=PUBLICATION_PALETTE,
            fonts={"title": 14, "labels": 12, "ticks": 10},
            figure={"dpi": 300}
        ),
        legend="figure"
    )
}
```

### Phase 3: Iterative Interface (Week 3-4)
**Objective**: Enable rapid iteration workflow with immutable config updates

**Key Components**:
- `.with_*()` methods for common iteration patterns (colors, legend, layout)
- Type-safe immutable updates using `dataclasses.replace`
- Clear error messages for invalid configurations

**Implementation**:
```python
class PlotConfig:
    def with_colors(self, colors) -> "PlotConfig":
        new_style = self._style_config.with_colors(colors)
        return replace(self, style=new_style, _style_config=new_style)
        
    def with_legend(self, style=None, position=None, **kwargs) -> "PlotConfig":
        updates = {k: v for k, v in {"style": style, "position": position, **kwargs}.items() if v is not None}
        new_legend = self._legend_config.update(**updates)
        return replace(self, legend=new_legend, _legend_config=new_legend)

# Real workflow becomes:
config = PlotConfig.from_preset("bump_plot").with_layout((2, 3)).with_colors(custom_palette)
```

### Phase 4: Clean Implementation (Week 4-5)
**Objective**: Replace old configuration system with PlotConfig as primary interface

**Key Components**:
- Remove complex FigureConfig, LegendConfig, Theme interdependencies
- Update all examples to use PlotConfig interface
- Comprehensive testing of domain presets and iterative workflows

**Breaking Change Strategy**:
- Replace all example configurations with PlotConfig equivalents
- Remove old configuration object creation from public APIs
- Focus on optimal user experience rather than backward compatibility

## Adaptation Guidance

### Expected Discoveries
- **Hidden configuration dependencies** between currently separate config objects
- **Validation complexity** that can't be easily consolidated
- **User workflow patterns** that inform optimal configuration interface
- **Backward compatibility challenges** with existing user code

### Handling Consolidation Challenges
- **If dependencies are complex**: Consider if they indicate fundamental architectural problems
- **If validation can't be simplified**: Examine whether validation is actually needed or defensive
- **If backward compatibility is difficult**: Prioritize future clarity over short-term compatibility
- **If user workflows don't match design**: Adapt design to actual usage patterns discovered

### Implementation Strategy
- **Build new system alongside old** - avoid big-bang replacement
- **Test with real examples** - ensure new system handles actual user needs
- **Gradual migration path** - deprecate old configs while supporting transition
- **Document clearly** - users need clear guidance on migration and new patterns

## Documentation Requirements

### Implementation Documentation
- **Configuration architecture** showing consolidated system structure
- **Migration guide** for users moving from old config objects to new interface
- **Before/after examples** demonstrating complexity reduction
- **Performance impact** of consolidation (should be positive)

### Strategic Insights
- **Root causes of configuration complexity** identified during consolidation
- **User workflow patterns** discovered through real usage analysis
- **Validation simplifications** achieved by eliminating defensive programming
- **Integration improvements** gained from single configuration source

### Future Reference
- **Configuration design principles** for consistent future development
- **Consolidation methodology** that can be applied to other fragmented systems
- **User experience patterns** that minimize cognitive load while maintaining flexibility

---

**Key Success Indicator**: When configuration system is consolidated, researchers should be able to iterate rapidly on plot refinements (`config.with_colors(...).with_legend(position=...)`) and specialized plots like bump plots should look excellent with minimal configuration (`PlotConfig.from_preset("bump_plot")`), while power users retain complete control over all matplotlib parameters through fine-grained config objects.