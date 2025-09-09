# Phase 2C: Layout Hint System Implementation

## Strategic Objective

Replace hardcoded positioning calculations with semantic layout hint system that provides three-tier positioning: matplotlib defaults → layout hints → manual coordinates. This eliminates magic numbers while preserving all manual positioning control.

## Problem Context

Research identified 12+ hardcoded positioning values scattered across the legend system:
- `single_legend_x = 0.5`, `two_legend_left_x = 0.25`, etc.
- Complex conditional positioning logic based on legend count
- Users frequently override `layout_bottom_margin`, `layout_top_margin` manually
- No systematic approach to spacing, alignment, or responsive behavior

## Requirements & Constraints

**Must Implement**:
- `layout_hint` parameter accepting semantic positioning strings
- Three positioning tiers: "auto" (matplotlib) → hints ("below", "side", "compact") → manual coordinates
- Replace hardcoded values with calculated positioning based on hints
- Responsive behavior that adapts to figure size and content

**Must Preserve**:
- All current manual positioning parameters (single_legend_x, bbox_y_offset, etc.)
- Exact visual output when manual coordinates are specified
- Current positioning behavior as fallback when hints fail
- Backward compatibility with all existing configuration

**Cannot Break**:
- Any existing positioning overrides in examples or user code
- Visual quality of current legend layouts
- Integration with tight_layout system

## Decision Frameworks

**Layout Hint Vocabulary**:
- "below" - Smart bottom positioning with appropriate margin calculation
- "side" - Right-side positioning with space optimization
- "compact" - Minimize space usage while maintaining readability
- "spacious" - Extra spacing for maximum readability
- "auto" - Pure matplotlib positioning (no manual calculation)

**Implementation Strategy**:
- Add layout_hint processing to LegendConfig
- Create positioning calculation functions that replace hardcoded values
- Maintain current hardcoded system as fallback for compatibility
- Gradual migration path from hardcoded to calculated positioning

**Fallback Approach**:
- When layout_hint is provided, use calculated positioning
- When manual coordinates provided, use them exactly (highest priority)
- When neither provided, use current hardcoded behavior (backward compatibility)
- Clear precedence hierarchy: manual > hints > current defaults

## Success Criteria

**Layout Hint Functionality**:
- `layout_hint="below"` produces appropriate bottom positioning with calculated margins
- `layout_hint="side"` creates right-side positioning that adapts to figure width
- `layout_hint="compact"` minimizes space while maintaining visual quality
- `layout_hint="spacious"` provides generous spacing for complex legends

**Positioning Calculation Quality**:
- Calculated positions are visually equivalent or better than current hardcoded values
- Multi-legend layouts (GROUPED_BY_CHANNEL) have appropriate spacing and alignment
- Positioning adapts appropriately to figure dimensions and content size
- No overlap between legends or with subplot content

**Compatibility Preservation**:
- All existing manual positioning parameters continue working exactly as before
- Current hardcoded behavior maintained when no hints provided
- Visual output identical for any code not using new layout_hint parameter
- Graceful fallback if hint calculation fails

## Quality Standards

**Reference**: Follow `docs/processes/design_philosophy.md` principles

**Implementation Standards**:
- Positioning calculation functions separate from LegendManager core logic
- Clear semantic meaning for each layout hint
- Responsive calculations that consider figure and content dimensions
- Type hints for layout_hint parameter and calculation functions

**Layout Hint Processing Pattern**:
```python
def calculate_hint_positioning(self, hint: str, figure_size: Tuple[float, float], 
                             legend_count: int) -> Dict[str, float]:
    hint_calculators = {
        "below": self._calculate_below_positioning,
        "side": self._calculate_side_positioning, 
        "compact": self._calculate_compact_positioning,
        "spacious": self._calculate_spacious_positioning,
        "auto": lambda *args: {}  # No manual positioning
    }
    
    calculator = hint_calculators.get(hint)
    assert calculator, f"Unknown layout_hint '{hint}'. Valid options: {list(hint_calculators.keys())}"
    return calculator(figure_size, legend_count)
```

**Precedence Hierarchy**:
```python
def resolve_final_positioning(self) -> Dict[str, float]:
    positioning = {}
    
    # Layer 1: Current hardcoded defaults (fallback)
    positioning.update(self._get_hardcoded_defaults())
    
    # Layer 2: Layout hint calculations (if provided)
    if self.config.layout_hint:
        positioning.update(self._calculate_hint_positioning())
    
    # Layer 3: Manual overrides (highest priority)
    positioning.update(self._get_manual_overrides())
    
    return positioning
```

## Adaptation Guidance

**If Calculated Positions Don't Match Visual Quality**:
- Bias toward maintaining current visual quality over perfect calculation
- Document any positioning changes as intentional improvements
- Test with variety of figure sizes and legend complexities
- Adjust calculation algorithms based on visual output quality

**If Integration with Existing System is Complex**:
- Implement as additional layer over current positioning system
- Maintain current hardcoded values as fallback rather than replacing immediately
- Focus on most common layout scenarios first
- Progressive enhancement approach over wholesale replacement

**If Hint Vocabulary Proves Insufficient**:
- Start with core hints that cover 80% of use cases
- Add additional hints based on discovered needs during implementation
- Maintain extensible hint system for future additions
- Clear error messages for unsupported hints

## Documentation Requirements

**Implementation Documentation**:
- Layout hint vocabulary with visual examples of each positioning approach
- Positioning calculation algorithms and their responsive behavior
- Precedence hierarchy explanation (manual > hints > hardcoded defaults)
- Integration approach with existing positioning system

**Before/After Positioning Analysis**:
- Comparison of hardcoded vs calculated positioning for various scenarios
- Visual output quality assessment across different figure sizes
- Evidence of reduced need for manual positioning overrides
- Performance impact of positioning calculations

**Migration Strategy Documentation**:
- How existing code continues working unchanged
- Examples of converting manual positioning to layout hints
- Guidelines for when to use hints vs manual coordinates
- Troubleshooting guide for positioning issues with new system