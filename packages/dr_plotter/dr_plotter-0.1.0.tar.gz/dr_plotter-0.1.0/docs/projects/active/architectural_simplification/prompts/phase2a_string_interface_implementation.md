# Phase 2A: String Interface Implementation

## Strategic Objective

Add simple string interface to FigureManager that makes GROUPED_BY_CHANNEL functionality discoverable while preserving all existing LegendConfig functionality. This is a pure addition with zero breaking changes that immediately solves the discoverability problem.

## Problem Context  

Research shows GROUPED_BY_CHANNEL is used in only 2/15+ examples despite being the most advanced feature. The barrier is complex configuration: `LegendConfig(strategy=LegendStrategy.GROUPED_BY_CHANNEL)` vs simple `legend="grouped"`.

## Requirements & Constraints

**Must Implement**:
- String parsing in FigureManager constructor accepting `legend` parameter
- `resolve_legend_config()` function mapping strings to LegendConfig objects
- Support for: `"grouped"`, `"subplot"`, `"figure"`, `"none"` string values
- Backward compatibility - all existing LegendConfig usage continues working unchanged

**Must Preserve**:
- All current LegendConfig functionality and parameters
- All existing example scripts continue working without changes
- Current legend behavior for any code not using new string interface

**Cannot Break**:
- Any existing FigureManager constructor calls
- Any existing LegendConfig usage patterns
- Visual output of current examples

## Decision Frameworks

**Implementation Location**:
- Add string processing to FigureManager.__init__ before LegendManager creation
- Create resolve_legend_config() as module-level utility function
- Maintain clean separation between string parsing and legend logic

**String Mapping Strategy**:
- Use research findings for smart defaults per strategy
- "grouped" gets extra bottom margin for multi-legend layouts  
- "figure" and "subplot" use current proven defaults
- "none" maps directly to NONE strategy

**Error Handling Approach**:
- Invalid strings should raise clear ValueError with helpful message
- List valid options in error message for discoverability
- No silent fallbacks that could hide configuration mistakes

## Success Criteria

**Interface Functionality**:
- `FigureManager(legend="grouped")` creates GROUPED_BY_CHANNEL legend
- `FigureManager(legend="figure")` creates FIGURE_BELOW legend  
- `FigureManager(legend="subplot")` creates PER_AXES legend
- `FigureManager(legend="none")` disables legends
- Invalid strings raise helpful error messages

**Backward Compatibility**:
- All existing FigureManager(legend=LegendConfig(...)) calls work unchanged
- All current examples produce identical visual output
- No changes to LegendConfig class or LegendManager behavior

**Code Quality**:
- Clean string parsing logic separate from legend implementation
- Type hints for new string parameter
- Integration follows existing FigureManager patterns

## Quality Standards

**Reference**: Follow `docs/processes/design_philosophy.md` principles

**Implementation Standards**:
- Use assertions for validation, not try-catch blocks
- No comments in code - self-documenting through clear naming
- Complete type hints for all parameters and return values
- Import typing modules at top of files

**String Mapping Implementation**:
```python
def resolve_legend_config(legend_input: Union[str, LegendConfig]) -> LegendConfig:
    if isinstance(legend_input, str):
        string_mappings = {
            "grouped": LegendConfig(
                strategy=LegendStrategy.GROUPED_BY_CHANNEL,
                layout_bottom_margin=0.2  # Extra space for multi-legends
            ),
            "subplot": LegendConfig(strategy=LegendStrategy.PER_AXES),
            "figure": LegendConfig(strategy=LegendStrategy.FIGURE_BELOW), 
            "none": LegendConfig(strategy=LegendStrategy.NONE)
        }
        assert legend_input in string_mappings, f"Invalid legend string '{legend_input}'. Valid options: {list(string_mappings.keys())}"
        return string_mappings[legend_input]
    return legend_input
```

## Adaptation Guidance

**If FigureManager Constructor is More Complex Than Expected**:
- Add string processing as first step before existing legend logic
- Maintain all current parameter validation and processing
- Ensure legend parameter accepts Union[str, LegendConfig] type

**If LegendConfig Integration Requires Changes**:
- Avoid modifying LegendConfig class itself
- Keep all logic in resolve_legend_config() function
- Maintain LegendConfig as final configuration object

**If Testing Reveals Issues**:
- Test with variety of existing examples to ensure no regressions
- Verify string interface works with all current visual encoding patterns
- Confirm GROUPED functionality works correctly with simple string activation

## Documentation Requirements

**Implementation Documentation**:
- File locations modified with specific functions added
- String mapping logic explanation
- Integration approach with existing legend system
- Type signature changes to FigureManager constructor

**Testing Results**:
- Confirmation that all existing examples continue working
- New string interface functionality demonstrated
- GROUPED_BY_CHANNEL accessibility improvement validated
- Performance impact assessment (should be minimal)

**User Impact**:
- Clear before/after comparison of GROUPED_BY_CHANNEL activation
- Examples of new string interface usage
- Confirmation of zero breaking changes