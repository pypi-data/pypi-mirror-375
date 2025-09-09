# Phase 2B: Smart GROUPED Defaults

## Strategic Objective

Improve GROUPED_BY_CHANNEL strategy with smart defaults for channel titles, column calculations, and positioning to create a polished experience that encourages adoption of this sophisticated functionality.

## Problem Context

Research shows GROUPED_BY_CHANNEL has sophisticated functionality but poor defaults:
- Generic channel titles ("Hue" instead of context-aware names)
- Simple `min(len(items), 4)` ncol calculation repeated across examples  
- Users frequently override positioning parameters manually
- Better defaults will increase adoption from current 2/15+ examples

## Requirements & Constraints

**Must Improve**:
- Auto-generated channel titles with sensible context-aware defaults
- Smart ncol calculation based on legend content and figure dimensions
- Better default positioning for multi-legend layouts (build on Phase 2A's `layout_bottom_margin=0.2`)
- Responsive behavior that adapts to content

**Must Preserve**:
- All manual override capabilities - users can still specify exact channel_titles, ncol, positioning
- Existing LegendConfig parameters and functionality
- Current behavior when users provide explicit configuration
- Backward compatibility with existing GROUPED_BY_CHANNEL usage

**Cannot Break**:
- Any existing LegendConfig usage patterns
- Manual positioning overrides
- Current visual output when explicit parameters are provided

## Decision Frameworks

**Channel Title Intelligence**:
- Use column names from visual encoding as context clues
- "model_size" → "Model Size", "dataset_type" → "Dataset Type"
- "hue_by" parameter → remove "_by" suffix, title case result
- Fallback to current simple title() behavior for unrecognizable patterns

**Smart Column Calculation**:
- Consider figure width, legend content length, readability
- Account for multi-legend layouts (GROUPED creates multiple legends)
- Balance between horizontal space usage and readability
- Adaptive algorithm that works for 1-20 legend entries

**Positioning Intelligence**:  
- Multi-legend spacing that adapts to legend count and content
- Consider overlap prevention between multiple channel legends
- Responsive positioning based on figure dimensions
- Smart defaults that reduce need for manual margin adjustments

## Success Criteria

**Channel Title Improvements**:
- Context-aware titles generated from visual encoding column names
- "hue_by='model_size'" generates "Model Size" title instead of "Hue"
- "marker_by='dataset'" generates "Dataset" title instead of "Marker"
- Manual channel_titles parameter still overrides auto-generated titles

**Smart Column Calculation**:
- ncol adapts to legend content and available space
- Multi-legend layouts use appropriate column counts per legend
- No more repetitive `min(len(items), 4)` patterns in user code
- Readable legends across variety of content sizes

**Enhanced Default Positioning**:
- Multi-legend layouts have appropriate spacing and positioning
- Reduced need for manual layout_bottom_margin overrides
- Good default behavior across different figure sizes
- Professional appearance without manual tuning

## Quality Standards

**Reference**: Follow `docs/processes/design_philosophy.md` principles

**Implementation Standards**:
- Smart defaults as methods on LegendManager class
- Clear separation between automatic and manual configuration
- Fallback gracefully to current behavior if smart calculation fails

**Context-Aware Title Generation**:
```python
def generate_channel_title(self, channel: str, source_column: Optional[str]) -> str:
    if channel in self.config.channel_titles:
        return self.config.channel_titles[channel]
    
    if source_column:
        # Smart processing: "model_size" -> "Model Size", "hue_by" -> "Hue"
        return self._contextualize_column_name(source_column)
    
    return channel.title()  # Current fallback behavior
```

**Smart Column Calculation**:
```python
def calculate_optimal_ncol(self, legend_entries: List[LegendEntry], available_width: float) -> int:
    if self.config.ncol is not None:
        return self.config.ncol  # Manual override takes precedence
    
    # Smart calculation based on content and space
    return self._compute_adaptive_ncol(legend_entries, available_width)
```

## Adaptation Guidance

**If Context Detection is Difficult**:
- Focus on common patterns first ("_by" suffix removal, underscore_to_title)
- Maintain simple title() fallback for unrecognized patterns
- Document what patterns are recognized for user awareness

**If Smart Calculations Are Complex**:
- Start with improved heuristics over current simple approach
- Focus on most common usage patterns (2-6 legend entries)
- Graceful fallback to current calculation if smart approach fails

**If Positioning Changes Affect Visual Output**:
- Bias toward conservative improvements that maintain current quality
- Test with existing GROUPED examples to ensure no degradation
- Document any visual changes as improvements rather than breaking changes

## Documentation Requirements

**Implementation Documentation**:
- Smart algorithms added with clear logic explanation
- Integration points with existing legend creation process
- Fallback behavior when automatic approaches fail
- Examples of improved titles and column calculations

**Before/After Comparison**:
- Visual examples showing improved channel titles
- Demonstration of smart column calculation improvements
- Evidence of reduced need for manual configuration overrides
- User experience improvements for common scenarios

**User Impact Assessment**:
- Quantification of configuration reduction in existing examples
- New capabilities unlocked by smart defaults
- Preserved manual override capabilities demonstrated
- Performance impact of smart calculation algorithms