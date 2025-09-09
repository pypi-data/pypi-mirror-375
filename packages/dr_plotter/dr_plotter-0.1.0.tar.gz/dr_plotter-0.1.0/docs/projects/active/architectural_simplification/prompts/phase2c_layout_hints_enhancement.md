# Phase 2C: Layout Hints Enhancement

## Strategic Objective

Add semantic layout hint system to the existing PositioningCalculator, providing user-friendly positioning vocabulary (`layout_hint="below"`, `"side"`, `"compact"`, `"spacious"`) while preserving all current systematic positioning functionality.

## Problem Context

The PositioningCalculator successfully implements systematic positioning that eliminates hardcoded magic numbers and provides figure-width responsive behavior. However, it lacks the semantic layout hint interface that was designed in Phase 2C to give users intuitive positioning control.

Current system provides excellent systematic calculation but requires users to understand positioning parameters. Layout hints would provide semantic vocabulary that translates to appropriate positioning calculations.

## Requirements & Constraints

**Must Implement**:
- `layout_hint` parameter in LegendConfig with semantic positioning vocabulary
- Integration with existing PositioningCalculator without breaking current functionality
- Four core layout hints: `"below"`, `"side"`, `"compact"`, `"spacious"`
- Layout hint processing that produces appropriate positioning calculations
- Clear precedence hierarchy: manual overrides > layout hints > systematic defaults

**Must Preserve**:
- All current PositioningCalculator functionality and systematic positioning
- Existing figure-width responsive behavior and multi-legend positioning
- All manual positioning overrides (bbox_to_anchor, positioning coordinates)
- Current visual output quality and positioning accuracy
- Integration with FigureManager layout system

**Cannot Break**:
- Any existing positioning behavior or visual output
- Current PositioningCalculator API or systematic calculations
- Integration with legend creation and layout processes
- Performance characteristics of positioning system

## Decision Frameworks

**Layout Hint Vocabulary Design**:
- `"below"` - Optimized bottom positioning with appropriate margin calculation
- `"side"` - Right-side positioning that adapts to figure dimensions
- `"compact"` - Minimize space usage while maintaining readability
- `"spacious"` - Extra generous spacing for maximum readability and visual separation

**Implementation Architecture**:
- Add `layout_hint: Optional[str] = None` to LegendConfig
- Extend PositioningCalculator to process layout hints into positioning parameters
- Maintain existing systematic calculation as foundation, with hints as modifiers
- Create hint-to-positioning translation functions within PositioningCalculator

**Integration Strategy**:
- Layout hints should modify existing PositioningConfig parameters, not replace systematic calculations
- Use current figure-width responsive logic as foundation, with hints adjusting spacing and alignment
- Preserve all current manual override capabilities with highest precedence
- Fallback gracefully to systematic defaults if hint processing fails

## Success Criteria

**Layout Hint Functionality**:
- `layout_hint="below"` produces appropriate bottom positioning with calculated margins
- `layout_hint="side"` creates right-side positioning that adapts to figure width
- `layout_hint="compact"` minimizes space while maintaining visual quality and readability
- `layout_hint="spacious"` provides generous spacing for complex multi-legend layouts

**Integration Quality**:
- Layout hints work seamlessly with existing PositioningCalculator systematic calculations
- Figure-width responsive behavior maintained and enhanced by hint modifiers
- Multi-legend positioning (2, 3+ legends) works correctly with all layout hints
- Performance impact minimal - hints should be lightweight parameter modifications

**Precedence Hierarchy**:
- Manual positioning overrides (bbox_to_anchor, coordinates) take highest precedence
- Layout hints applied as second priority, modifying systematic calculations
- Systematic defaults (current behavior) serve as foundation when no hints provided
- Clear, predictable behavior when multiple positioning approaches specified

## Quality Standards

**Reference**: Follow `docs/processes/design_philosophy.md` principles and existing PositioningCalculator patterns

**Implementation Standards**:
- Type hints for layout_hint parameter and hint processing functions
- Use assertions for validation, not try-catch blocks
- Clean separation between hint processing and systematic calculation logic
- Integration follows existing PositioningCalculator architecture patterns

**Layout Hint Processing Pattern**:
```python
def process_layout_hint(self, hint: str, figure_dimensions: FigureDimensions, 
                       legend_metadata: LegendMetadata) -> Dict[str, Any]:
    hint_modifiers = {
        "below": self._calculate_below_hint_modifiers,
        "side": self._calculate_side_hint_modifiers,
        "compact": self._calculate_compact_hint_modifiers,
        "spacious": self._calculate_spacious_hint_modifiers,
    }
    
    assert hint in hint_modifiers, f"Invalid layout_hint '{hint}'. Valid options: {list(hint_modifiers.keys())}"
    
    modifier_func = hint_modifiers[hint]
    return modifier_func(figure_dimensions, legend_metadata)
```

**Positioning Hierarchy Integration**:
```python
def calculate_positions(self, figure_dimensions: FigureDimensions, 
                       legend_metadata: LegendMetadata, 
                       manual_overrides: Optional[Dict[str, Any]] = None) -> PositioningResult:
    
    # Layer 1: Systematic defaults (foundation)
    base_result = self._calculate_systematic_positioning(figure_dimensions, legend_metadata)
    
    # Layer 2: Layout hint modifiers (if provided)
    if hasattr(self.config, 'layout_hint') and self.config.layout_hint:
        hint_modifiers = self.process_layout_hint(
            self.config.layout_hint, figure_dimensions, legend_metadata
        )
        base_result = self._apply_hint_modifiers(base_result, hint_modifiers)
    
    # Layer 3: Manual overrides (highest precedence)
    if manual_overrides:
        base_result = self._apply_manual_overrides(base_result, manual_overrides)
    
    return base_result
```

## Adaptation Guidance

**If Layout Hint Integration is Complex**:
- Start with simple hint-to-parameter mapping rather than sophisticated calculation
- Focus on most common hints ("below", "compact") before implementing full vocabulary
- Ensure fallback to current systematic behavior if hint processing encounters issues
- Document any discovered integration complexity for future enhancement

**If Visual Output Changes with Hints**:
- Prioritize maintaining current visual quality as baseline
- Test hints across different figure sizes and legend counts to ensure quality
- Adjust hint calculations based on visual output assessment
- Document any positioning improvements as intentional enhancements

**If Performance Impact is Significant**:
- Profile hint processing to identify performance bottlenecks
- Cache hint calculations when figure dimensions and metadata unchanged
- Optimize hint processing for common usage patterns
- Consider lazy evaluation approaches for complex hint scenarios

## Documentation Requirements

**Implementation Documentation**:
- Layout hint vocabulary with clear descriptions and visual examples
- Integration approach with existing PositioningCalculator architecture
- Precedence hierarchy explanation (manual > hints > systematic defaults)
- Performance characteristics and hint processing approach

**Layout Hint Specification**:
- Complete description of each hint's positioning behavior and calculations
- Visual examples showing hint effects across different figure configurations
- Guidelines for when to use each hint type based on layout requirements
- Error handling and validation approach for invalid hint values

**Integration Validation**:
- Testing results showing hint functionality across different scenarios
- Evidence that existing positioning behavior preserved
- Performance impact assessment of hint processing
- Visual quality comparison with and without layout hints

**User Experience Documentation**:
- Clear examples of layout hint usage in realistic scenarios
- Migration guide for users wanting to adopt layout hints
- Best practices for choosing appropriate hints for different use cases
- Troubleshooting guide for hint-related positioning issues