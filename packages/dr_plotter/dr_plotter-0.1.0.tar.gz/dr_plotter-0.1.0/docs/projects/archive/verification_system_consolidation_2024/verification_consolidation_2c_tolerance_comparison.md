# Tactical Prompt: Unify Tolerance-Based Comparison Logic

## Strategic Objective
Create a unified comparison system for all tolerance-based verification logic. This eliminates duplicate comparison functions scattered across files and ensures consistent, reliable comparison behavior throughout the verification system.

## Problem Context  
The verification system currently has tolerance comparison logic duplicated with subtle variations:
- **`_count_unique_floats()` and `_count_unique_colors()`** in plot_verification.py with similar but different implementations
- **Similar tolerance logic scattered** across size, alpha, color comparisons with inconsistent approaches
- **Different default tolerances** used across different verification types without clear rationale
- **Inconsistent tolerance handling** making verification results unpredictable

This duplication creates subtle bugs and makes verification behavior hard to predict.

## Requirements & Constraints
**Must Create**:
- Single comparison utilities module (`comparison_utils.py`) with unified tolerance-based comparison functions
- Universal `values_are_equal(a, b, tolerance)` function that handles floats, colors, and other numeric types automatically
- Universal `count_unique_values(values, tolerance)` function that replaces all scattered unique-counting logic
- Type-aware tolerance handling with appropriate defaults for different data types

**Must Preserve**:
- All current verification accuracy and behavior
- Ability to configure tolerances for specific verification scenarios
- Support for different data types (floats, RGBA tuples, sizes, alphas)
- Integration with existing verification function interfaces

**Files to Modify**:
- Create new: `src/dr_plotter/scripting/comparison_utils.py`
- Update: `plot_verification.py` (remove `_count_unique_floats`, `_count_unique_colors`)
- Update: All verification functions that use tolerance-based comparison
- Update: Import statements throughout verification system

## Decision Frameworks
**Comparison Function Design**:
- **Single Universal vs Type-Specific**: One `values_are_equal()` function vs separate functions for different types
- **Automatic Type Detection vs Explicit**: Detect value types automatically vs require explicit type specification
- **Tolerance Defaults**: Hard-coded vs configurable vs adaptive tolerances based on data type

**Unique Value Counting**:
- **Algorithm Choice**: Distance-based clustering vs simple tolerance comparison for uniqueness
- **Performance vs Accuracy**: O(n²) accurate comparison vs faster approximate methods
- **Memory Usage**: In-place comparison vs building intermediate data structures

**Integration Strategy**:
- **Backward Compatibility**: Maintain existing function signatures vs clean break to new interface
- **Error Handling**: How to handle comparison errors and edge cases consistently
- **Configuration**: How to expose tolerance configuration to verification functions

## Success Criteria
**Unified Comparison System**:
- [ ] Single `values_are_equal(a, b, tolerance=None)` function handles all value types automatically
- [ ] Single `count_unique_values(values, tolerance=None)` function replaces all scattered unique-counting logic
- [ ] Consistent default tolerances for different data types (colors, sizes, alphas, floats)
- [ ] Type-aware comparison that automatically handles RGBA tuples, floats, etc.

**Code Consolidation**:
- [ ] All duplicate comparison logic eliminated from verification files
- [ ] Single source of truth for tolerance-based comparison throughout system
- [ ] Consistent comparison behavior across all verification types
- [ ] Clean import structure with single comparison utilities module

**Functional Reliability**:
- [ ] All existing verification tests continue to pass with identical results
- [ ] Consistent uniqueness detection across different data types
- [ ] Reliable comparison behavior for edge cases (NaN, infinity, very small differences)
- [ ] Configurable tolerances for special verification scenarios

## Quality Standards
**Mathematical Correctness**: Comparison logic handles floating point precision and edge cases properly
**Performance Efficiency**: Comparison functions are optimized for typical verification data sizes
**Type Safety**: Automatic type detection is robust and handles unexpected input gracefully
**Configuration Clarity**: Tolerance settings are clearly documented and easy to understand

## Adaptation Guidance
**If existing tolerances differ**: Document the differences and choose the most conservative/accurate approach
**If comparison algorithms vary**: Standardize on the most robust mathematical approach
**If performance is a concern**: Profile comparison functions and optimize common cases
**If type detection is complex**: Start with explicit type handling, add automation incrementally

## Documentation Requirements
**Create implementation document** showing:
- New unified comparison function interfaces and usage patterns
- Mapping from old scattered comparison functions to new unified system
- Default tolerance values for different data types and rationale
- Performance characteristics and any behavior changes from consolidation

**Implementation Approach**:
1. **Audit all tolerance-based comparison logic** across verification files
2. **Create unified comparison utilities** with automatic type detection and appropriate defaults
3. **Replace all scattered comparison logic** with calls to unified functions
4. **Test comparison consistency** across all verification scenarios
5. **Validate identical verification behavior** after consolidation

This consolidation ensures reliable, consistent comparison behavior throughout the verification system while eliminating duplicate logic.