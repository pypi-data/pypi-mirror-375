# Configuration System Consolidation - Phase 3C: Enhanced Iterative Methods

## Strategic Objective

Complete the iterative refinement workflow by implementing comprehensive `.with_*()` methods and workflow shortcuts that enable researchers to rapidly iterate through configuration refinements. This addresses the original core complaint: "changing colors or legend positioning requires reconstructing entire config objects."

## Problem Context  

With precedence conflicts fixed (Phase 3A) and interface consolidated (Phase 3B), the remaining workflow friction is **incomplete iterative capabilities**:

**Current Limited Iteration:**
```python
# Basic methods exist but workflow gaps remain
config = PlotConfig.from_preset("time_series")
config = config.with_colors(["#FF0000", "#00FF00"])    # ✅ Works
config = config.with_layout(2, 3)                     # ✅ Works  
config = config.with_legend(style="grouped")          # ✅ Works

# Missing workflow methods
config = config.with_theme("scatter")                 # ❌ Missing
config = config.with_fonts(size=14, weight="bold")    # ❌ Missing
config = config.with_figure_size(16, 10)             # ❌ Missing
config = config.with_presentation_style()             # ❌ Missing
```

**Required Complete Workflow:**
```python
# Comprehensive iterative refinement workflow
config = (PlotConfig.from_preset("time_series")
          .with_figure_size(16, 8)                    # Quick size adjustment
          .with_theme("scatter")                       # Switch visual theme
          .with_fonts(title=16, labels=12)            # Typography refinement
          .with_publication_style()                    # Context switch
          .with_transparency(0.8)                      # Alpha adjustment
          .with_accessibility())                       # Colorblind-safe conversion
```

## Requirements & Constraints

### Must Implement
- **Complete `.with_*()` method coverage** - every common configuration refinement has a method
- **Workflow-specific shortcuts** - `.with_publication_style()`, `.with_presentation_mode()`, `.with_accessibility()`
- **Intelligent parameter coordination** - changing one aspect appropriately adjusts related settings
- **Method chaining validation** - type safety and logical consistency in chained operations

### Must Preserve
- **Existing method functionality** - current `.with_colors()`, `.with_layout()`, `.with_legend()` unchanged
- **Immutable pattern** - all methods return new PlotConfig instances using `dataclasses.replace`
- **Type safety** - complete type hints throughout all new methods
- **PlotConfig architecture** - no changes to core data structure or conversion logic

### Cannot Break
- **Phase 1 & 2 functionality** - preset system and existing iterative methods preserved
- **Legacy conversion** - `_to_legacy_configs()` continues working with enhanced PlotConfig
- **Performance** - method chaining should remain fast
- **Integration** - enhanced methods work with FigureManager interface

## Decision Frameworks

### Method Coverage Strategy
**Chosen Approach**: Comprehensive coverage of common researcher refinement patterns

**Method Categories:**
- **Direct parameter methods** - `.with_theme()`, `.with_fonts()`, `.with_figure_size()`
- **Workflow shortcuts** - `.with_publication_style()`, `.with_presentation_mode()`
- **Context switches** - `.with_accessibility()`, `.with_high_contrast()`
- **Fine-tuning methods** - `.with_transparency()`, `.with_dpi()`, `.with_tight_layout()`

**Decision Criteria**: Cover 90%+ of common iteration patterns researchers use

### Implementation Strategy  
**Approach**: Build on existing immutable pattern with intelligent parameter handling

**Design Principles:**
- **Immutable updates** - all methods use `dataclasses.replace`
- **Smart defaults** - methods coordinate related parameters appropriately
- **Type safety** - complete type hints and validation
- **Composable design** - methods work together seamlessly

## Success Criteria

### Iterative Workflow Success
- **Comprehensive method coverage** - researchers can modify any aspect through `.with_*()` methods
- **Workflow shortcuts work** - context-specific methods (publication, presentation, accessibility) provide appropriate multi-parameter updates
- **Intelligent coordination** - changing figure size adjusts layout appropriately, switching to presentation mode updates fonts/dpi/colors together
- **Method chaining flows naturally** - common refinement sequences feel intuitive and efficient

### Technical Implementation Success
- **Type safety maintained** - all methods have complete type hints and return correct types
- **Immutable pattern preserved** - no methods mutate existing PlotConfig instances
- **Performance optimized** - method chaining is fast, no unnecessary object creation
- **Integration verified** - enhanced PlotConfig works seamlessly with FigureManager

### User Experience Success
- **Workflow friction eliminated** - rapid configuration refinement without object reconstruction
- **Discoverable methods** - clear method names make functionality obvious
- **Consistent patterns** - all `.with_*()` methods follow same usage patterns
- **Complex configurations simplified** - common multi-parameter changes have single method shortcuts

## Quality Standards

**Reference**: Follow `docs/processes/design_philosophy.md` principles

**Key Principles Applied**:
- **Focus on Researcher's Workflow**: Methods address actual refinement patterns researchers need
- **Self-Documenting Code**: Method names clearly indicate their functionality
- **Minimalism**: No redundant methods, each serves distinct workflow need
- **Type Safety**: Complete type annotations throughout all new methods

**Code Style Requirements**:
- **No comments or docstrings** - method names and signatures should be self-documenting
- **Complete type hints** - every parameter and return value properly typed
- **Immutable patterns** - use `dataclasses.replace` for all updates
- **Consistent naming** - all methods follow `.with_*()` pattern

## Implementation Requirements

### Core Parameter Methods

1. **Theme Switching** in `src/dr_plotter/plot_config.py`:
   ```python
   def with_theme(self, theme_name: str) -> "PlotConfig":
       current_style = self._resolve_style_config()
       new_style = replace(current_style, theme=theme_name)
       return replace(self, style=new_style)
   ```

2. **Typography Control**:
   ```python
   def with_fonts(self, size: Optional[int] = None, weight: Optional[str] = None, 
                  title: Optional[int] = None, labels: Optional[int] = None) -> "PlotConfig":
       current_style = self._resolve_style_config()
       font_updates = {}
       if size is not None:
           font_updates["size"] = size
       if title is not None:
           font_updates["title_size"] = title
       if labels is not None:
           font_updates["label_size"] = labels
       if weight is not None:
           font_updates["weight"] = weight
       
       current_fonts = current_style.fonts or {}
       new_fonts = {**current_fonts, **font_updates}
       new_style = replace(current_style, fonts=new_fonts)
       return replace(self, style=new_style)
   ```

3. **Figure Size Adjustment**:
   ```python
   def with_figure_size(self, width: float, height: float) -> "PlotConfig":
       current_layout = self._resolve_layout_config()
       new_layout = replace(current_layout, figsize=(width, height))
       return replace(self, layout=new_layout)
   ```

4. **Transparency Control**:
   ```python
   def with_transparency(self, alpha: float) -> "PlotConfig":
       assert 0.0 <= alpha <= 1.0, f"Alpha must be between 0.0 and 1.0, got {alpha}"
       current_style = self._resolve_style_config()
       plot_styles = current_style.plot_styles or {}
       new_plot_styles = {**plot_styles, "alpha": alpha}
       new_style = replace(current_style, plot_styles=new_plot_styles)
       return replace(self, style=new_style)
   ```

5. **DPI Control**:
   ```python
   def with_dpi(self, dpi: int) -> "PlotConfig":
       current_style = self._resolve_style_config()
       figure_styles = current_style.figure_styles or {}
       new_figure_styles = {**figure_styles, "dpi": dpi}
       new_style = replace(current_style, figure_styles=new_figure_styles)
       return replace(self, style=new_style)
   ```

### Workflow Shortcut Methods

1. **Publication Style**:
   ```python
   def with_publication_style(self) -> "PlotConfig":
       return (self.with_fonts(title=14, labels=12)
                   .with_dpi(300)
                   .with_colors(PUBLICATION_COLORS)
                   .with_figure_size(8, 6))
   ```

2. **Presentation Mode**:
   ```python
   def with_presentation_mode(self) -> "PlotConfig":
       return (self.with_fonts(size=16, weight="bold")
                   .with_dpi(150)
                   .with_colors(HIGH_VISIBILITY_PALETTE)
                   .with_transparency(0.9)
                   .with_figure_size(16, 9))
   ```

3. **Accessibility Conversion**:
   ```python
   def with_accessibility(self) -> "PlotConfig":
       return (self.with_colors(COLORBLIND_SAFE_PALETTE)
                   .with_fonts(size=12, weight="normal")
                   .with_transparency(0.8))
   ```

4. **High Contrast Mode**:
   ```python
   def with_high_contrast(self) -> "PlotConfig":
       return (self.with_colors(HIGH_CONTRAST_PALETTE)
                   .with_fonts(weight="bold")
                   .with_transparency(1.0))
   ```

### Context-Aware Methods

1. **Smart Layout Adjustment**:
   ```python
   def with_tight_layout(self, pad: Optional[float] = None) -> "PlotConfig":
       current_layout = self._resolve_layout_config()
       new_pad = pad if pad is not None else 0.3
       new_layout = replace(current_layout, tight_layout_pad=new_pad)
       return replace(self, layout=new_layout)
   ```

2. **Preset Override**:
   ```python
   def with_preset_override(self, preset_name: str, **overrides) -> "PlotConfig":
       base_preset = PlotConfig.from_preset(preset_name)
       # Apply overrides to base preset
       result = base_preset
       for key, value in overrides.items():
           if hasattr(result, f"with_{key}"):
               result = getattr(result, f"with_{key}")(value)
       return result
   ```

### Method Chaining Validation

1. **Type Safety Validation**:
   - All methods return `PlotConfig` type
   - Parameter types validated with assertions
   - Union types handled appropriately

2. **Logical Consistency**:
   ```python
   def _validate_chaining_consistency(self) -> None:
       # Optional validation for complex chaining scenarios
       # Could check for conflicting settings
       pass
   ```

## Adaptation Guidance

### Expected Implementation Challenges
- **Parameter coordination complexity** - ensuring methods that affect related settings coordinate appropriately
- **Type hint complexity** - handling Optional parameters and Union types in method signatures
- **Performance optimization** - ensuring method chaining doesn't create excessive object creation
- **Testing thoroughness** - validating all method combinations work correctly

### Handling Method Implementation Complications
- **If parameter coordination is complex**: Start with simple independent methods, add coordination incrementally
- **If type hints become unwieldy**: Use type aliases for complex Union types
- **If performance degrades**: Profile method chaining, optimize object creation patterns
- **If testing becomes overwhelming**: Focus on common usage patterns first, edge cases later

### Implementation Strategy
- **Start with high-value methods** - implement methods for most common refinement patterns first
- **Test method combinations** - ensure chaining works smoothly for typical workflows
- **Validate with real usage** - test methods with actual research plotting scenarios
- **Document method patterns** - create clear examples of effective method chaining

## Documentation Requirements

### Method Documentation
- **Complete method reference** - documentation of all `.with_*()` methods with parameters and examples
- **Workflow pattern examples** - common method chaining sequences for typical research tasks
- **Context method guides** - when to use publication vs presentation vs accessibility methods
- **Type reference** - clear documentation of parameter types and validation rules

### Implementation Documentation
- **Method implementation patterns** - consistent approaches used across all `.with_*()` methods
- **Parameter coordination logic** - how methods coordinate related settings intelligently
- **Performance optimization** - techniques used to ensure efficient method chaining
- **Testing approach** - methodology for validating method functionality and combinations

### Strategic Insights
- **Workflow pattern analysis** - which method combinations are most commonly used
- **User experience validation** - confirmation that iterative workflow friction is eliminated
- **Method design principles** - guidelines for creating effective configuration methods
- **Extension framework** - patterns for adding new `.with_*()` methods as needs arise

---

**Key Success Indicator**: When Phase 3C is complete, researchers should be able to start with any preset and rapidly refine it to meet their exact needs through intuitive method chaining, eliminating the need to reconstruct configuration objects for common plotting refinement workflows.