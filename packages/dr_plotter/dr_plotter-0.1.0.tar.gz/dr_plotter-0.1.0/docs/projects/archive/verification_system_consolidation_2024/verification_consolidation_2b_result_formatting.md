# Tactical Prompt: Consolidate Verification Result Formatting

## Strategic Objective
Create a unified, consistent output formatting system for all verification functions. This eliminates the scattered print statements and inconsistent messaging across verification files, providing a clean, predictable user experience for debugging plot verification.

## Problem Context
The verification system currently has inconsistent output formatting scattered across all verification functions:
- **Different emoji/symbol usage** (✅❌🔴 vs checkmarks) across files
- **Inconsistent indentation and message formats** making output hard to parse
- **Mixed responsibilities**: Some functions print directly, others return structured data
- **Scattered print statements** throughout verification logic instead of centralized formatting

This creates cognitive overhead when debugging and makes the verification output unpredictable.

## Requirements & Constraints
**Must Create**:
- Single formatting module (`verification_formatter.py`) that handles all verification output
- Standardized message templates for common verification scenarios (success, failure, warnings)
- Consistent emoji/symbol usage (✅ for success, 🔴 for failure, ⚠️ for warnings)
- Unified indentation system for nested information (main messages, details, suggestions)

**Must Preserve**:
- All current information content in verification output
- Ability to distinguish between different types of verification results
- Debug information and detailed failure explanations
- Integration with existing verification function return formats

**Files to Modify**:
- Create new: `src/dr_plotter/scripting/verification_formatter.py`
- Update: All verification functions in `verification.py`, `plot_verification.py`, `verif_decorators.py`
- Update: Remove all direct print statements from verification logic

## Decision Frameworks
**Output Structure Design**:
- **Centralized vs Distributed**: All formatting logic in single module vs scattered formatting helpers
- **Template vs Dynamic**: Pre-defined message templates vs dynamic message building
- **Verbosity Control**: Single output level vs multiple verbosity options (choose single level for simplicity)

**Message Format Standards**:
- **Symbol Usage**: Consistent emoji set (✅🔴⚠️) for all success/failure/warning indicators
- **Indentation Pattern**: 2-space or 4-space indentation for nested content (choose 4-space for readability)
- **Section Headers**: Clear section separation with consistent formatting

**Data Flow Design**:
- **Return vs Print**: Verification functions return structured data, formatter handles display
- **Immediate vs Batched**: Format and display immediately vs collect and batch format
- **Error Integration**: How to handle formatting errors without breaking verification

## Success Criteria
**Unified Output Format**:
- [ ] All verification output uses consistent emoji symbols (✅🔴⚠️)
- [ ] Consistent 4-space indentation for nested information
- [ ] Standardized message templates for common verification scenarios
- [ ] Clean section separation between different types of verification results

**Code Organization**:
- [ ] All print statements removed from verification logic files
- [ ] Single `verification_formatter.py` module handles all output formatting
- [ ] Verification functions return only structured data
- [ ] Clear separation between verification logic and presentation

**Functional Preservation**:
- [ ] All current verification information preserved in output
- [ ] Debug information and detailed explanations maintained
- [ ] Error messages remain clear and actionable
- [ ] Output remains useful for debugging plot issues

## Quality Standards
**Consistent User Experience**: All verification output follows same visual patterns and information hierarchy
**Clean Code Separation**: Verification logic completely separate from presentation concerns
**Maintainable Templates**: Message formats easy to modify and extend
**Performance**: Formatting adds minimal overhead to verification process

## Adaptation Guidance
**If verification functions have complex output**: Create structured data format that captures all information, then format in presentation layer
**If current messages are unclear**: Improve message clarity while maintaining information content
**If indentation is inconsistent**: Standardize on 4-space indentation throughout
**If emoji usage varies**: Choose single consistent set and apply everywhere

## Documentation Requirements
**Create implementation document** showing:
- New message template system and formatting standards
- Migration guide from old scattered printing to new centralized formatting
- Before/after examples of verification output formatting
- List of all functions modified and their new output contracts

**Implementation Approach**:
1. **Analyze current output patterns** across all verification functions
2. **Create unified formatting module** with standard templates and helper functions
3. **Remove all print statements** from verification logic
4. **Update verification functions** to use centralized formatter
5. **Test output consistency** across all verification scenarios

This consolidation creates a much cleaner debugging experience with predictable, well-formatted verification output.