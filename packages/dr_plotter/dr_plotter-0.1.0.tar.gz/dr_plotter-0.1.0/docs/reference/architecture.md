# DR_Plotter Architecture Reference

**Last Updated**: 2025-08-29  
**Purpose**: Comprehensive architectural reference consolidating analysis from multiple sources

## Table of Contents
- [Configuration Infrastructure](#configuration-infrastructure)
- [Style System](#style-system) 
- [Parameter Routing](#parameter-routing)
- [Plot Architecture](#plot-architecture)
- [Theme System](#theme-system)
- [Legend Management](#legend-management)

## Configuration Infrastructure

### Core Configuration Classes

#### LegendConfig
**Location**: `src/dr_plotter/legend_manager.py:62`
- **Purpose**: Comprehensive legend configuration including strategy, positioning, layout margins, and multi-legend coordination
- **Key Parameters**: `strategy`, `position`, `deduplication`, `ncol`, layout margins, positioning coordinates
- **Usage**: Accepted by FigureManager constructor, processed via `_convert_legacy_legend_params()`

#### SubplotLayoutConfig  
**Location**: `src/dr_plotter/figure_config.py:13`
- **Purpose**: Controls subplot grid layout and spacing
- **Parameters**: `rows`, `cols`, `layout_rect`, `layout_pad`
- **Usage**: Created internally by FigureManager from individual parameters

#### SubplotFacetingConfig
**Location**: `src/dr_plotter/figure_config.py:35`
- **Purpose**: Configuration for faceted plotting functionality
- **Parameters**: `facet_by`, `group_by`, `x_col`, `y_col`, `facet_rows`, `facet_cols`, `wrap_facets`
- **Status**: Infrastructure ready, enables native faceting API

#### FigureCoordinationConfig
**Location**: `src/dr_plotter/figure_config.py:57`
- **Purpose**: Figure-level coordination and matplotlib integration
- **Parameters**: `theme`, `shared_styling`, `external_ax`, `fig_kwargs`
- **Usage**: Created internally by FigureManager for matplotlib integration

#### GroupingConfig
**Location**: `src/dr_plotter/grouping_config.py:8`
- **Purpose**: Maps visual channels to data columns for aesthetic grouping
- **Parameters**: `hue`, `style`, `size`, `marker`, `alpha`
- **Usage**: Used by plotting system for visual channel management

### Configuration Pattern Analysis

**Architectural Strengths**:
- Rich configuration infrastructure with dataclass-based objects
- Sophisticated theme system with proper inheritance  
- Legacy compatibility through parameter conversion
- Built-in validation methods in config objects

**Current Integration State**:
- Partial migration: FigureManager uses config objects internally but accepts individual parameters
- Theme-first design with mature integration
- Faceting infrastructure ready for advanced features

## Style System

### Theme Architecture

#### Core Components
```python
class Theme:
    parent: Optional["Theme"]    # Inheritance chain
    plot_styles: PlotStyles     # Plot-phase styling
    post_styles: PostStyles     # Post-plot styling  
    axes_styles: AxesStyles     # Axes configuration
    figure_styles: FigureStyles # Figure-level settings
    **styles: Any              # General styles (cycles, colors)
```

#### Style Categories
- **PlotStyles**: `linewidth`, `alpha`, `marker`, `s` (size)
- **AxesStyles**: `grid_alpha`, `label_fontsize`, `legend_fontsize`, `cmap`
- **FigureStyles**: `title_fontsize`, figure-level formatting
- **General Styles**: Color cycles, theme-wide defaults, custom cycles

#### Style Resolution Order
1. **Kwargs** (highest priority) - Direct parameters to `fm.plot()`
2. **Theme styles** (medium priority) - Custom theme values
3. **Base theme** (lowest priority) - BASE_THEME defaults

### StyleApplicator System

**Precedence Hierarchy**:
```python
component_kwargs > group_styles > plot_styles > base_styles
```

**Components**:
- **component_kwargs**: Direct parameters from plot() call
- **group_styles**: Visual channel styling (hue, size, marker)
- **plot_styles**: Plot-specific theme styling
- **base_styles**: BASE_THEME defaults

### Color Management

#### Cycle Configuration
```python
from dr_plotter import consts
**{
    consts.get_cycle_key("hue"): itertools.cycle(custom_colors),
    consts.get_cycle_key("style"): itertools.cycle(["-", "--", ":"]),
    consts.get_cycle_key("marker"): itertools.cycle(["o", "s", "^"]),
}
```

**Features**:
- Custom color cycles per visual channel
- Consistent color mapping across subplots
- Theme-based default colors
- Automatic color coordination in multi-subplot layouts

## Parameter Routing

### Current Flow Architecture

**Parameter Path**: `FigureManager.plot()` → `_add_plot()` → `BasePlotter.__init__()` → `StyleApplicator` → Individual plotters

#### Parameter Categories
1. **Reserved Parameters**: Data mapping (`x`, `y`), visual channels (`hue_by`, `style_by`), system (`theme`, `legend`)
2. **Base Plotter Parameters**: `["x", "y", "colorbar_label", "_figure_manager", "_shared_hue_styles"]`
3. **Plotter-Specific Parameters**: Defined per plotter (mostly empty arrays currently)
4. **Component Schema Parameters**: Defined per plotter per styling phase
5. **Filtered Parameters**: Remaining kwargs passed to matplotlib after filtering

### Routing Analysis

**Well-Routed Parameters**:
- Standard matplotlib parameters (colors, line styles, markers)
- Theme-based styling (fonts, grid, transparency)
- Visual channel mappings (hue, size, style)

**Stranded Parameters** (exist in code but not user-accessible):
- `format` parameter in HeatmapPlotter (cell text formatting)
- `xlabel_pos` parameter (top/bottom positioning)
- Advanced axes configuration parameters

### Current Gaps

**Missing Integration**:
- Layout parameters still require manual post-plot configuration
- Axis scaling (`xscale="log"`) stored in theme but needs manual application
- Scientific notation formatting not systematically handled

## Plot Architecture

### BasePlotter Inheritance

**Structure**: All 8 plotters inherit from BasePlotter with consistent lifecycle:
- `prepare_data()`: Data preprocessing and column renaming
- `render()`: Main plotting logic with GroupingConfig handling
- `_draw()`: Individual plot rendering

**Features**:
- Consistent data preparation patterns (`x_col → X_COL_NAME`)
- Unified grouped vs individual rendering through single `render()` method
- Component schema standardization for styling integration

### Plotter Types

#### LinePlotter
- **Parameter routing**: Excellent - all matplotlib line parameters accessible
- **Features**: Full theme integration, visual channel support
- **Status**: Complete implementation

#### ScatterPlotter  
- **Parameter routing**: Excellent - includes continuous size mapping
- **Features**: Multi-dimensional parameter mapping, size channels
- **Status**: Complete implementation

#### HeatmapPlotter
- **Parameter routing**: Good for standard parameters, gaps in cell formatting
- **Stranded features**: `format='int'` for cell text, `xlabel_pos` positioning
- **Status**: Core complete, advanced features need API exposure

#### BarPlotter, ViolinPlotter, HistogramPlotter, StripPlotter, BumpPlotter
- **Parameter routing**: Standard matplotlib parameters well-integrated
- **Features**: Theme system integration, visual channel support
- **Status**: Complete core implementations

## Theme System

### Capabilities Assessment

#### What Themes Handle Well
- **Plot Appearance**: Line styles, colors, transparency, markers
- **Text Formatting**: Font sizes for labels, legends, titles
- **Grid and Visual Styling**: Alpha, color, style coordination
- **Color Management**: Custom cycles, consistent multi-subplot coloring

#### Current Limitations
- **Layout Parameters**: Cannot theme `figsize`, subplot spacing, legend positioning
- **Axis Formatting**: Scientific notation, tick formatting require manual handling  
- **Configuration Conflicts**: Theme vs FigureManager parameter conflicts exist
- **Limited Style Coverage**: Missing categories for layout and advanced formatting

### Theme Integration Success

**Successful Configurations** (~60% of styling parameters):
- All plot appearance (colors, lines, transparency)
- All text formatting (fonts, sizes)
- Grid and visual styling
- Custom color palettes and cycles

**Requires Enhancement**:
- Layout and positioning parameters
- Axis formatting and scientific notation
- Legend configuration (conflicts with FigureManager)
- Layout margins and spacing

## Legend Management

### Strategy-Based System

#### Four Legend Strategies
1. **PER_AXES**: Individual legends per subplot
2. **FIGURE_BELOW**: Single legend below figure
3. **GROUPED_BY_CHANNEL**: Separate legends per visual channel ("split")
4. **NONE**: No legend display

#### Deduplication Logic
- **Shared strategies** (split, figure_below): Deduplicate by visual channel value
- **Per-axes strategies**: Deduplicate by axis scope
- **Centralized coordination**: All entries through `FigureManager.register_legend_entry()`

#### Legend vs Colorbar Separation
- **Text/marker legends**: Handled by legend system
- **Continuous color mapping**: Separate colorbar components
- **Rationale**: Different visual encoding types require different implementations

### Integration Architecture

**Components**:
- **LegendConfig**: Configuration object with positioning and styling
- **LegendRegistry**: Manages deduplication and coordination
- **LegendStrategy**: Enum defining behavior types

**Coordination**: Single point through FigureManager prevents inconsistent behavior across plot types

## Key Architectural Principles

### Design Philosophy Alignment
- **Assertions Over Exceptions**: Performance-critical validation using assertions
- **Complete Type Coverage**: All functions have explicit type hints
- **No Code Comments**: Self-documenting through clear naming and structure
- **Breaking Changes Acceptable**: Research library prioritizes optimal design

### Evidence-Based Architecture
- **Validation Requirements**: All architectural claims verified with concrete evidence
- **Multi-Agent Coordination**: Complex tasks use specialized agents with systematic handoffs
- **Systematic Process Design**: Reusable multi-stage processes for architectural challenges
- **Iterative Refinement**: Continuous improvement based on empirical results

## Implementation Status

### Completed Systems
- ✅ Core plotting architecture with 8 plotter types
- ✅ Sophisticated theme system with inheritance
- ✅ Legend management with multiple strategies
- ✅ Parameter routing for common use cases
- ✅ Faceting infrastructure (SubplotFacetingConfig ready)

### Enhancement Opportunities
- **Theme system expansion**: Layout and formatting parameter coverage
- **Parameter routing completion**: Expose stranded advanced parameters
- **Configuration conflict resolution**: Clear separation between theme and manager parameters
- **Debugging and validation tools**: Better developer experience for theme development

### Strategic Assessment
The architecture demonstrates sophisticated design with strong foundations in configuration management, theming, and plotting coordination. The system is production-ready for core functionality with clear paths for expanding advanced features.