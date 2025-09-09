# Configuration System Consolidation - Phase 2: Preset System Expansion

## Strategic Objective

Expand the existing basic preset system into a comprehensive domain-intelligent configuration library that eliminates repetitive manual styling for specialized research plots. Build on the solid PlotConfig foundation to create research-backed presets that understand visualization best practices and provide excellent defaults while maintaining full customization flexibility.

## Problem Context  

Phase 1 established a working preset foundation with basic presets (dashboard, publication, bump_plot, faceted_analysis), but analysis of existing examples reveals significant gaps in domain coverage:

**Current Preset Coverage Analysis:**
- ✅ **Dashboard layouts**: Basic 2x2 grid pattern covered
- ✅ **Publication styling**: Basic professional formatting covered  
- ✅ **Bump plots**: High-contrast colors for trend visibility covered
- ❌ **Time series analysis**: Missing optimized styling for temporal data
- ❌ **Distribution analysis**: Missing presets for histograms, boxplots, violin plots
- ❌ **Scatter matrix analysis**: Missing multi-dimensional correlation styling
- ❌ **Accessibility options**: No colorblind-safe or high-contrast alternatives
- ❌ **Presentation contexts**: Missing large-font, high-visibility options for slides

**Real User Pain Points from Examples:**
- Researchers manually configure time series plots with appropriate date formatting and trend emphasis
- Distribution analysis requires repeated setup of appropriate binning, colors, and statistical overlays
- Scatter matrices need distinct markers and colors for high-dimensional data readability
- Accessibility compliance requires manual color palette validation for each plot

## Requirements & Constraints

### Must Preserve
- **Existing preset functionality** - all current presets (dashboard, publication, bump_plot, faceted_analysis) continue working unchanged
- **Current PlotConfig API** - from_preset() method and .with_*() iterative patterns maintained
- **All customization capabilities** - users retain ability to override any preset parameter
- **Integration with examples** - current example usage patterns remain functional

### Must Achieve  
- **Complete domain coverage** - presets address 90%+ of common research visualization patterns
- **Research-backed design** - each preset based on established visualization best practices and accessibility standards
- **Visual excellence** - every preset produces publication-quality output for its intended domain
- **Accessibility compliance** - colorblind-safe and high-contrast options available
- **Clear taxonomy** - logical preset organization that researchers can easily discover and understand

### Cannot Break
- **Existing preset names** - dashboard, publication, bump_plot, faceted_analysis must maintain current functionality
- **PlotConfig interface** - no changes to from_preset() signature or .with_*() methods
- **Legacy config conversion** - all presets must convert properly to FigureConfig/LegendConfig/Theme
- **Performance** - preset loading should remain fast (<10ms per preset)

## Decision Frameworks

### Preset Expansion Strategy
**Chosen Approach**: Systematic domain analysis with research-backed implementations
- **Analyze existing examples** to identify most common unaddressed patterns
- **Research visualization best practices** for each domain (time series, distributions, correlations)
- **Validate with accessibility standards** ensuring colorblind compliance
- **Test with real data** to ensure visual quality and effectiveness

**Decision Criteria Applied**: Evidence-based design that addresses actual researcher needs while following established visualization guidelines

### Color Palette Research Strategy  
**Approach**: Scientific validation of color choices for each domain
- **Time Series**: Colors optimized for trend comparison and temporal pattern recognition
- **Distributions**: Colors that work for overlapping distributions and statistical emphasis  
- **Accessibility**: Validated colorblind-safe palettes using simulation tools
- **High Contrast**: Maximum readability for presentation and printed materials

**Decision Criteria**: Each palette tested for its specific use case with both normal and colorblind vision simulation

### Preset Organization Strategy
**Approach**: Clear taxonomic structure based on research workflows
- **Domain-specific**: time_series, distribution_analysis, scatter_matrix, correlation_analysis
- **Context-specific**: presentation (large fonts, high contrast), notebook (compact, clear), minimal (maximum data-ink ratio)  
- **Accessibility-focused**: colorblind_safe, high_contrast, grayscale_print
- **Style-focused**: vibrant (for engagement), professional (for reports), scientific (for journals)

## Success Criteria

### Domain Coverage Success
- **Time series excellence** - `PlotConfig.from_preset("time_series")` handles temporal data with appropriate date formatting and trend emphasis
- **Distribution quality** - `PlotConfig.from_preset("distribution_analysis")` optimizes histograms/boxplots with statistical overlays
- **Correlation clarity** - `PlotConfig.from_preset("scatter_matrix")` creates readable high-dimensional visualizations
- **Accessibility compliance** - `PlotConfig.from_preset("colorblind_safe")` passes accessibility validation tools

### Research Integration Success  
- **Evidence-based design** - each preset backed by published visualization research or accessibility standards
- **Visual validation** - every preset tested with real research data to ensure quality
- **Performance optimization** - all presets load quickly and render efficiently
- **Clear documentation** - preset choices and customization options are obvious to researchers

### Workflow Enhancement Success
- **Reduced configuration time** - common research plots require minimal manual configuration
- **Consistent visual quality** - presets produce publication-ready output without manual styling  
- **Easy customization** - researchers can modify presets through familiar .with_*() patterns
- **Discoverable options** - clear preset names and organization guide appropriate selection

## Quality Standards

**Reference**: Follow `docs/processes/design_philosophy.md` principles

**Key Principles Applied**:
- **Focus on Researcher's Workflow**: Each preset addresses specific research visualization needs
- **Evidence-Based Design**: Presets based on visualization research and accessibility standards
- **Self-Documenting Code**: Preset names and color palette names clearly indicate their purpose
- **Zero Comments Policy**: Implementation self-documenting through structure and naming

**Research Validation Requirements**:
- **Color palette research** documented with accessibility testing methodology
- **Domain best practices** referenced from established visualization guidelines  
- **Real data testing** with examples from each target domain
- **Performance benchmarking** to ensure preset loading remains fast

## Implementation Requirements

### Domain-Specific Preset Expansion

1. **Time Series Analysis Presets** - Add to `src/dr_plotter/plot_presets.py`:
   ```python
   "time_series": {
       "style": {
           "colors": TEMPORAL_OPTIMIZED_PALETTE,  # Research-backed temporal colors
           "plot_styles": {"linewidth": 2, "alpha": 0.8, "marker": None},
           "theme": "line"
       },
       "legend": {"style": "figure"},
       "layout": {"figsize": (14, 6)}  # Wide format optimal for temporal data
   }
   ```

2. **Distribution Analysis Presets**:
   ```python
   "distribution_analysis": {
       "style": {
           "colors": DISTRIBUTION_PALETTE,  # Colors for overlapping distributions  
           "plot_styles": {"alpha": 0.7, "edgecolor": "black", "linewidth": 0.5},
           "theme": "base"
       },
       "legend": {"style": "subplot"},
       "layout": {"figsize": (12, 8)}
   }
   ```

3. **Correlation/Scatter Matrix Presets**:
   ```python
   "scatter_matrix": {
       "style": {
           "colors": HIGH_DIMENSIONAL_PALETTE,  # Distinct colors for many categories
           "plot_styles": {"s": 30, "alpha": 0.6, "edgecolors": "none"},
           "theme": "scatter"
       },
       "legend": {"style": "grouped"},
       "layout": {"figsize": (16, 16), "tight_layout_pad": 0.4}
   }
   ```

### Context-Specific Preset Expansion

1. **Presentation Context**:
   ```python
   "presentation": {
       "style": {
           "colors": HIGH_VISIBILITY_PALETTE,
           "fonts": {"size": 16, "weight": "bold"},
           "plot_styles": {"linewidth": 4, "markersize": 8},
           "figure_styles": {"dpi": 150}
       },
       "legend": {"style": "figure"},
       "layout": {"figsize": (16, 9)}  # Widescreen ratio
   }
   ```

2. **Notebook Context** (compact, clear):
   ```python
   "notebook": {
       "style": {
           "colors": NOTEBOOK_PALETTE,
           "fonts": {"size": 10},
           "plot_styles": {"linewidth": 1.5, "markersize": 4}
       },
       "legend": {"style": "subplot"},
       "layout": {"figsize": (10, 6), "tight_layout_pad": 0.2}
   }
   ```

### Accessibility-Focused Preset Expansion

1. **Colorblind-Safe Options**:
   ```python
   "colorblind_safe": {
       "style": {
           "colors": COLORBLIND_SAFE_PALETTE,  # Validated with simulation tools
           "plot_styles": {"linewidth": 2, "linestyle": "solid"}
       }
   }
   ```

2. **High Contrast Options**:
   ```python
   "high_contrast": {
       "style": {
           "colors": HIGH_CONTRAST_PALETTE,  # Maximum distinguishability
           "plot_styles": {"linewidth": 3, "edgecolor": "black", "linewidth": 1}
       }
   }
   ```

### Research-Backed Color Palette Development

1. **Create New Palette Constants**:
   ```python
   # Temporal data optimized colors - based on ColorBrewer temporal schemes
   TEMPORAL_OPTIMIZED_PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
   
   # Distribution analysis - colors that work for overlapping histograms
   DISTRIBUTION_PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
   
   # High-dimensional data - maximum distinctiveness for scatter matrices
   HIGH_DIMENSIONAL_PALETTE = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33", "#a65628", "#f781bf"]
   
   # Colorblind-safe palette validated with Coblis simulator
   COLORBLIND_SAFE_PALETTE = ["#0173b2", "#de8f05", "#029e73", "#cc78bc", "#ca9161", "#fbafe4", "#949494", "#ece133"]
   
   # High contrast for presentations and accessibility
   HIGH_CONTRAST_PALETTE = ["#000000", "#e69f00", "#56b4e9", "#009e73", "#f0e442", "#0072b2", "#d55e00", "#cc79a7"]
   
   # Professional presentation colors - high visibility
   HIGH_VISIBILITY_PALETTE = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#5D2E8B", "#228B22"]
   
   # Compact notebook colors - subtle but clear
   NOTEBOOK_PALETTE = ["#4472C4", "#E70200", "#70AD47", "#7030A0", "#FF6600", "#264478"]
   ```

2. **Document Color Research**:
   - Each palette tested with real data examples
   - Accessibility validation using colorblind simulation tools
   - Performance in grayscale conversion for print compatibility
   - Rationale documented for each palette choice

### Enhanced Preset Validation

1. **Add Preset Testing Framework**:
   ```python
   def validate_preset_completeness():
       """Ensure all presets have required components and convert properly to legacy configs"""
       for preset_name, preset_config in PLOT_CONFIGS.items():
           config = PlotConfig.from_preset(preset_name)
           figure_config, legend_config, theme = config._to_legacy_configs()
           assert figure_config is not None
           assert legend_config is not None
   ```

2. **Visual Quality Validation**:
   - Create test plots with each preset using real research data
   - Validate color distinguishability and readability
   - Test preset combinations with .with_*() methods

### Example Integration Analysis

1. **Analyze Current Examples** for preset opportunities:
   - Identify manual configurations that could be replaced with presets
   - Document configuration patterns that suggest new preset needs
   - Test that new presets would simplify existing example code

2. **Create Preset Usage Examples**:
   - Demonstrate each new preset with appropriate research data
   - Show customization patterns through .with_*() methods
   - Validate visual quality and researcher workflow improvement

## Adaptation Guidance

### Expected Implementation Challenges
- **Color palette research complexity** requiring visualization expertise and accessibility testing
- **Domain knowledge gaps** needing research into time series, distribution, and correlation visualization best practices
- **Performance optimization** ensuring new presets don't slow down configuration loading
- **Preset naming conventions** that are discoverable and memorable for researchers

### Handling Research and Design Challenges  
- **If visualization research is complex**: Focus on established guidelines from sources like ColorBrewer, Matplotlib documentation, and accessibility standards
- **If accessibility testing is difficult**: Use online colorblind simulators and high-contrast validation tools
- **If performance degrades**: Profile preset loading and optimize color palette storage and lookup
- **If preset names are unclear**: Test with real researchers or use established naming conventions from other visualization tools

### Implementation Strategy
- **Research first, implement second**: Understand each domain's visualization needs before creating presets
- **Test incrementally**: Validate each preset with real data before moving to next domain
- **Document decisions**: Capture rationale for color choices and configuration parameters
- **Validate accessibility**: Test each preset with colorblind simulation and high-contrast requirements

## Documentation Requirements

### Research Documentation
- **Color palette validation methodology** - how each palette was tested for accessibility and effectiveness
- **Domain best practices research** - visualization guidelines and standards informing each preset
- **Performance impact analysis** - measurement of preset loading time and memory usage
- **Visual quality validation** - examples of each preset with real research data

### Implementation Documentation  
- **Preset taxonomy and usage guide** - clear documentation of when to use each preset
- **Customization patterns** - common .with_*() modifications for each preset type
- **Integration examples** - before/after comparisons showing preset benefits
- **Accessibility compliance** - documentation of colorblind-safe and high-contrast validation

### Strategic Insights
- **Usage pattern prediction** - analysis of which presets likely to be most valuable based on example analysis
- **Extension framework** - methodology for researchers to create custom presets based on their specific domains
- **Quality metrics** - measures of preset effectiveness in reducing configuration time and improving visual quality

---

**Key Success Indicator**: When Phase 2 expansion is complete, a researcher analyzing time series data should be able to create an excellent visualization with `FigureManager(PlotConfig.from_preset("time_series"))` that requires no manual styling, while researchers with accessibility needs can use `PlotConfig.from_preset("colorblind_safe")` to ensure their visualizations are inclusive, and all presets maintain the ability to be customized through `.with_colors()`, `.with_layout()`, and other iterative methods.