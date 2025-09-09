# Configuration System Consolidation - Phase 2: Domain Presets Implementation

## Strategic Objective

Create comprehensive domain-specific presets that eliminate repetitive manual styling for specialized plots. This phase transforms the basic preset foundation from Phase 1 into a complete system that understands domain requirements (bump plots need high contrast, publication plots need specific typography) and provides excellent defaults while maintaining customization flexibility.

## Problem Context  

Analysis of the existing 36+ examples reveals repetitive configuration patterns that users must manually reconstruct:
- **Bump plots** require high-contrast colors, distinct line styles, and grouped legends for readability
- **Publication figures** need specific typography, DPI settings, and professional color palettes  
- **Dashboard layouts** require coordinated multi-subplot arrangements with appropriate legend positioning
- **Scientific plotting** needs consistent styling that works across different data types

Current system forces users to manually configure these common patterns every time, creating workflow friction and inconsistent visual quality.

## Requirements & Constraints

### Must Preserve
- **All Phase 1 functionality** - basic PlotConfig interface and existing FigureManager compatibility
- **Customization flexibility** - users can still override any preset parameter
- **Type safety** - complete type hints throughout preset system
- **Performance** - preset loading and application should be fast

### Must Achieve  
- **Domain intelligence** - presets that understand specific plot type requirements
- **Visual excellence** - each preset produces publication-quality output for its intended use case
- **Easy customization** - users can modify presets without starting from scratch
- **Comprehensive coverage** - presets address most common configuration patterns found in examples
- **Clear preset taxonomy** - logical organization and naming of available presets

### Cannot Break
- **Phase 1 interface** - existing PlotConfig functionality must continue working
- **Backwards compatibility** - FigureManager with PlotConfig parameter must work unchanged
- **Configuration validation** - all existing validation logic preserved

## Decision Frameworks

### Preset Architecture Strategy
**Chosen Approach**: Specialized preset categories with inheritance and composition
- **Base presets**: Core configurations (default, minimal, comprehensive)
- **Domain presets**: Plot-type-specific (bump_plot, scatter_matrix, time_series)  
- **Context presets**: Usage-specific (publication, presentation, dashboard, notebook)
- **Style presets**: Visual themes (high_contrast, colorblind_safe, grayscale)

**Decision Criteria Applied**: Cover real usage patterns while maintaining clear mental model

### Preset Customization Strategy
**Approach**: Layered override system with preset inheritance
- **Base + Override**: `PlotConfig.from_preset("publication", layout=(3, 2))`
- **Preset Composition**: `PlotConfig.from_presets(["publication", "high_contrast"])`
- **Iterative Refinement**: `preset.with_colors(custom_palette).with_layout(rows=4)`

**Decision Criteria**: Enable both quick customization and complex composition patterns

### Color Palette Strategy
**Approach**: Research-backed palettes optimized for specific use cases
- **Bump plots**: High contrast with sufficient visual separation for trend comparison
- **Publication**: Professional, print-safe colors that work in grayscale
- **Accessibility**: Colorblind-safe palettes for inclusive visualization
- **Data type specific**: Diverging, sequential, and categorical palettes

## Success Criteria

### Domain Intelligence Success
- **Bump plot excellence** - `PlotConfig.from_preset("bump_plot")` produces optimal styling for trend comparison
- **Publication quality** - `PlotConfig.from_preset("publication")` meets journal submission standards  
- **Dashboard coherence** - `PlotConfig.from_preset("dashboard")` creates visually cohesive multi-plot layouts
- **Scientific standards** - Domain presets follow established visualization best practices

### Preset System Success  
- **Complete coverage** - presets address 80%+ of configuration patterns found in existing examples
- **Easy discovery** - users can find appropriate presets through clear naming and documentation
- **Flexible customization** - common modifications (colors, layout) work smoothly with all presets
- **Composition patterns** - users can combine presets for complex requirements

### Implementation Success
- **Performance optimization** - preset loading adds minimal overhead
- **Validation integration** - preset configurations pass all existing validation
- **Type safety maintained** - complete type hints for all preset-related functionality
- **Clean architecture** - preset system integrates cleanly with Phase 1 foundation

## Quality Standards

**Reference**: Follow `docs/processes/design_philosophy.md` principles

**Key Principles Applied**:
- **Focus on Researcher's Workflow**: Presets eliminate repetitive configuration tasks
- **Clarity Through Structure**: Logical preset organization and naming
- **Evidence-Based Design**: Presets based on analysis of actual usage patterns
- **Zero Comments Policy**: Self-documenting through clear naming and structure

**Target Usage Patterns**:
```python
# Domain-specific excellence
with FigureManager(PlotConfig.from_preset("bump_plot")) as fm:
    fm.plot("bump", data, ...)  # Automatically optimized styling

# Context-aware configuration
config = PlotConfig.from_preset("publication", layout=(2, 3))
with FigureManager(config) as fm: ...

# Preset composition and customization  
config = (PlotConfig.from_preset("dashboard")
          .with_colors(BRAND_PALETTE)
          .with_legend(position="outside_bottom"))
```

## Implementation Requirements

### Enhanced Preset System
1. **Expand `src/dr_plotter/plot_presets.py`**:
   - **Domain-specific presets**: bump_plot, scatter_matrix, time_series, distribution_analysis
   - **Context presets**: publication, presentation, dashboard, notebook, minimal
   - **Style presets**: high_contrast, colorblind_safe, grayscale, vibrant
   - **Research-backed color palettes** for each domain with documented rationale

2. **Color Palette Research and Implementation**:
   - **BUMP_OPTIMIZED_PALETTE**: High contrast colors tested for trend line visibility
   - **PUBLICATION_PALETTE**: Print-safe colors that work in grayscale conversion
   - **ACCESSIBILITY_PALETTE**: Colorblind-safe options validated with simulation tools
   - **SCIENTIFIC_PALETTE**: Colors following established scientific visualization guidelines

3. **Preset Validation System**:
   - Validation that each preset produces appropriate output for its intended use case
   - Integration with existing configuration validation
   - Error handling for invalid preset names or combinations

### Enhanced PlotConfig Capabilities  
1. **Extend `src/dr_plotter/plot_config.py`**:
   - **Multi-preset composition**: `from_presets(["base", "style"])` method
   - **Smart override handling**: Intelligent parameter merging when combining presets
   - **Preset introspection**: Methods to query available presets and their characteristics
   - **Enhanced .with_*() methods**: Better integration with preset-based configurations

2. **Advanced Customization Patterns**:
   - **Preset inheritance**: Ability to create custom presets based on existing ones
   - **Conditional overrides**: Context-aware parameter adjustment
   - **Validation integration**: Ensure preset + override combinations remain valid

### Integration with Existing Examples
1. **Example Analysis and Preset Mapping**:
   - Analyze existing 36+ examples to identify common configuration patterns
   - Map existing manual configurations to appropriate preset + override combinations
   - Validate that presets + minimal overrides can replicate all existing functionality

2. **Preset Coverage Validation**:
   - Ensure each identified pattern has an appropriate preset
   - Test that preset-based configurations produce visually equivalent output
   - Document any configuration patterns that require manual setup (should be minimal)

## Adaptation Guidance

### Expected Discoveries
- **Complex parameter interdependencies** in existing examples that affect preset design
- **Visual quality trade-offs** between preset simplicity and fine-grained control
- **Performance implications** of complex preset composition and override logic
- **Domain knowledge gaps** where research is needed to create optimal presets

### Handling Preset Design Challenges
- **If color research is complex**: Focus on established visualization guidelines and accessibility standards
- **If preset composition is difficult**: Simplify to basic override patterns initially, add composition later
- **If performance is impacted**: Profile preset loading and optimize bottlenecks
- **If domain expertise is needed**: Research established best practices in scientific visualization

### Implementation Strategy  
- **Research first**: Understand domain requirements before implementing presets
- **Validate visually**: Test each preset with real data to ensure quality
- **Start simple**: Basic preset + override patterns before complex composition
- **Document rationale**: Capture why specific preset choices were made for future reference

## Documentation Requirements

### Implementation Documentation
- **Preset taxonomy** - complete catalog of available presets with use cases
- **Color palette research** - rationale and testing methodology for palette choices  
- **Domain requirements** - visualization best practices research that informed preset design
- **Performance analysis** - impact of preset system on configuration loading time

### Strategic Insights  
- **Configuration pattern analysis** - common patterns discovered in existing examples
- **Preset usage prediction** - which presets likely to be most/least used and why
- **Customization patterns** - how users are likely to modify presets based on workflow analysis
- **Domain knowledge capture** - visualization expertise encoded in preset designs

### Future Reference
- **Preset extension methodology** - how to research and create new domain-specific presets
- **Color palette validation** - testing approaches for accessibility and print compatibility
- **Performance optimization patterns** - lessons for efficient preset composition systems
- **Usage analytics framework** - how to measure preset adoption and effectiveness

---

**Key Success Indicator**: When Phase 2 is complete, a researcher should be able to create a publication-quality bump plot with `FigureManager(PlotConfig.from_preset("bump_plot"))` that looks better than manually configured alternatives, while retaining the ability to customize any aspect through `.with_*()` methods or detailed config objects.