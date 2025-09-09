# Configuration System Consolidation - Phase 3B: Interface Consolidation

## Strategic Objective

Complete the interface consolidation by removing the fragmented FigureManager parameters (`figure`, `legend`, `theme`) and forcing all usage through the unified PlotConfig interface. This achieves the original strategic goal of "single source of truth" at the user interface level while preserving the valuable Theme architecture internally.

## Problem Context  

Phase 3A fixed precedence conflicts, but the fragmented interface remains. Users can still access the old multi-parameter interface:

**Current Fragmented Interface:**
```python
# Multiple ways to configure - cognitive overload
FigureManager(figure=FigureConfig(...), legend=LegendConfig(...), theme=LINE_THEME)
FigureManager(config=PlotConfig.from_preset("line"))  # Better but optional

# Users must learn both patterns
# Interface complexity persists
```

**Required Consolidated Interface:**
```python
# Single, clear configuration path
FigureManager(PlotConfig.from_preset("line").with_layout(2,3))  # Only way
# OR
FigureManager(config=PlotConfig(...))  # Explicit parameter name

# Users learn one pattern
# Interface simplicity achieved
```

The goal is **interface-level consolidation** without **architecture-level destruction** - users interact with unified PlotConfig while the system internally uses the proven Theme architecture.

## Requirements & Constraints

### Must Achieve
- **Single FigureManager interface** - only accept `config: PlotConfig` parameter
- **Clear migration path** - helpful error messages guide users to PlotConfig
- **Interface simplicity** - eliminate multi-parameter cognitive load
- **Force best practices** - users naturally use the superior PlotConfig approach

### Must Preserve  
- **All functionality** - every current capability accessible through PlotConfig
- **Theme system architecture** - no changes to theme.py or internal Theme usage
- **PlotConfig conversion** - existing `_to_legacy_configs()` method continues working
- **Visual output** - identical plots before and after interface changes

### Cannot Break
- **PlotConfig functionality** - preset system, iterative methods, conversion logic all preserved
- **Internal architecture** - Theme objects continue handling styling internally
- **Performance** - no degradation from interface consolidation
- **Examples functionality** - all examples must work after conversion to PlotConfig

## Decision Frameworks

### Interface Consolidation Strategy
**Chosen Approach**: Replace multiple parameters with single `config` parameter, provide clear migration guidance

**Interface Design:**
```python
# NEW: Single parameter interface
class FigureManager:
    def __init__(self, config: Optional[PlotConfig] = None) -> None:
        # Conversion logic: config -> figure, legend, theme (internal)
        # All existing functionality through unified interface
```

**Decision Criteria Applied**: Clear user interface, maximum functionality preservation, minimal architectural change

### Migration Strategy
**Approach**: Breaking change with helpful error messages and clear upgrade path

**Migration Support:**
- **Clear error messages** when old parameters used
- **Documentation examples** showing PlotConfig equivalents  
- **Preserve all functionality** through PlotConfig interface

## Success Criteria

### Interface Consolidation Success
- **Single parameter interface** - FigureManager accepts only `config: PlotConfig`
- **Clear error messages** - users get helpful guidance when using old interface
- **Functionality preservation** - all current capabilities accessible through PlotConfig
- **Usage simplification** - users learn one configuration pattern instead of multiple

### Migration Success
- **All examples converted** - every example uses PlotConfig interface
- **Clear conversion patterns** - obvious mapping from old to new interface
- **No functionality loss** - every old usage pattern has PlotConfig equivalent
- **Performance maintained** - no degradation from interface changes

### Architecture Preservation Success
- **Theme system untouched** - no changes to theme.py or Theme classes
- **Internal conversion works** - PlotConfig → (FigureConfig, LegendConfig, Theme) continues functioning
- **Visual equivalence** - converted examples produce identical plots
- **Styling architecture intact** - cycles, inheritance, plotter defaults preserved

## Quality Standards

**Reference**: Follow `docs/processes/design_philosophy.md` principles

**Key Principles Applied**:
- **Focus on Researcher's Workflow**: Single interface reduces cognitive load and learning curve
- **Clarity Through Structure**: Unified interface makes configuration approach obvious
- **Architectural Courage**: Bold interface simplification while preserving internal architecture
- **Self-Documenting**: Clear method signatures make usage patterns obvious

**Code Style Requirements**:
- **No comments or docstrings** - interface should be self-documenting
- **Complete type hints** - all parameters and return values properly typed
- **Clear error messages** - helpful guidance when users need to migrate
- **Consistent patterns** - PlotConfig used consistently throughout all examples

## Implementation Requirements

### FigureManager Interface Update

1. **Update Constructor Signature** in `src/dr_plotter/figure.py`:
   ```python
   # CURRENT
   def __init__(
       self,
       config: Optional[PlotConfig] = None,
       figure: Optional["FigureConfig"] = None,
       legend: Optional[Union[str, LegendConfig]] = None,
       theme: Optional[Any] = None,
   ) -> None:
   
   # REQUIRED CHANGE
   def __init__(self, config: Optional[PlotConfig] = None) -> None:
       # Add validation for removed parameters
       # Provide helpful error messages
       # Use existing conversion logic
   ```

2. **Add Migration Error Messages**:
   ```python
   def __init__(self, config: Optional[PlotConfig] = None, **kwargs) -> None:
       # Detect old parameter usage
       old_params = {"figure", "legend", "theme"}
       used_old_params = old_params.intersection(kwargs.keys())
       
       if used_old_params:
           assert False, (
               f"FigureManager no longer accepts {used_old_params} parameters. "
               f"Use PlotConfig instead: "
               f"FigureManager(PlotConfig(layout=..., legend=..., style=...))"
           )
   ```

3. **Preserve All Conversion Logic**:
   - Keep existing `_to_legacy_configs()` method in PlotConfig
   - Maintain internal usage of FigureConfig, LegendConfig, Theme
   - No changes to Theme system or plotter integration

### Example Conversion Requirements

1. **Systematic Example Updates**:
   - Convert ALL examples to use PlotConfig interface
   - Create clear before/after conversion patterns
   - Validate visual output remains identical

2. **Conversion Pattern Documentation**:
   ```python
   # BEFORE (old fragmented interface)
   with FigureManager(
       figure=FigureConfig(rows=2, cols=2, figsize=(16, 12)),
       legend=LegendConfig(strategy="grouped"),
       theme=LINE_THEME
   ) as fm:
   
   # AFTER (unified PlotConfig interface) 
   with FigureManager(PlotConfig(
       layout={"rows": 2, "cols": 2, "figsize": (16, 12)},
       legend={"style": "grouped"},
       style={"theme": "line"}
   )) as fm:
   
   # OR using presets + iteration (preferred)
   with FigureManager(
       PlotConfig.from_preset("line")
       .with_layout(2, 2, figsize=(16, 12))
       .with_legend(style="grouped")
   ) as fm:
   ```

### API Surface Updates

1. **Update Import Guidance**:
   - Examples should import PlotConfig alongside FigureManager
   - Remove usage of FigureConfig, LegendConfig in examples
   - Theme objects only used internally through PlotConfig

2. **Preset System Integration**:
   - Ensure all current presets work with new interface
   - Validate preset → legacy config conversion continues working
   - Test iterative methods work with consolidated interface

## Adaptation Guidance

### Expected Implementation Challenges
- **Example conversion scope** - systematically updating all examples without missing any
- **Complex configurations** - ensuring all current FigureConfig/LegendConfig capabilities are accessible through PlotConfig
- **Error message clarity** - providing helpful migration guidance without overwhelming users

### Handling Consolidation Complications
- **If examples conversion is complex**: Focus on common patterns first, handle edge cases incrementally
- **If functionality gaps discovered**: Extend PlotConfig interface rather than keeping old parameters
- **If performance degrades**: Profile conversion overhead, optimize PlotConfig → legacy conversion

### Implementation Strategy
- **Audit all examples first** - understand current usage patterns before conversion
- **Create conversion patterns** - document common before/after transformations
- **Test incrementally** - convert and validate examples in small batches
- **Validate visual equivalence** - ensure converted examples produce identical plots

## Documentation Requirements

### Interface Documentation
- **Single interface guide** - clear documentation of PlotConfig-only usage
- **Conversion examples** - before/after patterns for common configurations
- **Error message reference** - what users see when using old interface and how to fix
- **Functionality mapping** - how every old capability is accessible through PlotConfig

### Implementation Documentation
- **Example conversion catalog** - complete list of updated examples with conversion patterns
- **Testing methodology** - approach for validating visual equivalence after conversion
- **Performance impact** - measurement of any overhead from interface consolidation
- **Architecture preservation verification** - confirmation that Theme system remains intact

### Strategic Insights
- **Interface vs architecture distinction** - lessons about consolidating user interfaces while preserving internal architecture
- **Migration strategy effectiveness** - assessment of breaking change approach with helpful error messages
- **User experience improvement** - validation that single interface reduces cognitive load

---

**Key Success Indicator**: When Phase 3B is complete, users should only be able to configure FigureManager through PlotConfig, with all current functionality accessible through the unified interface, while the internal Theme architecture continues to handle styling complexity without any user-visible changes in visual output.