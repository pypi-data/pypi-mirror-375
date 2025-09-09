# Problem Statement: Consolidate Error Handling

**Priority**: 2 (High Value)

## Strategic Objective

Establish a single, consistent error handling strategy across the entire codebase to replace the current mix of assertions, print statements, warnings, and silent failures. This creates predictable error behavior that aligns with DR methodology's "Fail Fast, Surface Problems" principle.

## Problem Context

The codebase has inconsistent error handling patterns that create unpredictable user experiences:

**Current Error Handling Chaos**:
```python
# From various files - inconsistent patterns
assert len(unsupported) == 0, f"Unsupported groupings: {unsupported}"  # Hard failure
print(f"Warning: DataFrame has only {len(data)} row(s)...")             # Console spam  
warnings.warn(f"Legend proxy creation failed: {e}")                     # Import warnings
if legend_creation_fails():
    return  # Silent failure - user never knows
```

**Inconsistency Problems**:
- **Unpredictable behavior**: Same type of problem handled differently in different places
- **Poor user experience**: Mix of crashes, warnings, and silent failures confuses users
- **Difficult debugging**: Problems surface at different points with different message formats
- **Hidden issues**: Silent failures and warnings let problems accumulate

**Evidence of Systematic Issue**:
- **validation.py**: Uses assertions for data validation
- **figure.py**: Uses try-catch with print statements for faceting errors
- **legend_manager.py**: Uses warnings for legend creation failures
- **plotters/**: Mix of all patterns depending on which developer wrote the code

## Requirements & Constraints

### Must Preserve
- **Current functionality** - no regression in successful operations
- **Error information** - users get same or better error information
- **Development debugging** - developers can still diagnose issues effectively
- **Integration behavior** - external systems continue working with error handling

### Must Achieve
- **Consistent error patterns** - same type of problem handled same way everywhere
- **Predictable user experience** - users know what to expect from error conditions
- **Clear error messages** - problems explained in actionable terms
- **Aligned with DR methodology** - fail fast, surface problems immediately

### Cannot Break
- **User workflows** - existing scripts continue working or fail with clear messages
- **Test suites** - existing tests continue passing or are updated consistently
- **External integrations** - matplotlib, pandas interactions handle errors appropriately

## Decision Frameworks

### Error Handling Strategy
**Option A**: Pure assertion approach - all validation through descriptive assertions
**Option B**: Exception hierarchy - custom exceptions for different error types
**Option C**: Error result pattern - return success/failure objects instead of raising
**Option D**: Hybrid approach - assertions for validation, exceptions for external failures

**Decision Criteria**:
- DR methodology strongly favors immediate failure over graceful degradation
- Development experience should provide clear, immediate feedback
- User experience should be predictable and helpful
- Performance should not be degraded by error handling overhead

**Recommended**: Option A with selective use of D - assertions for internal validation, exceptions only for external system failures

### Error Message Strategy
**Option A**: Structured error messages with consistent format
**Option B**: Simple descriptive messages focused on user actionability  
**Option C**: Technical error codes with detailed explanations
**Option D**: Context-aware messages that adapt to user's likely intent

**Decision Criteria**:
- Users should immediately understand what went wrong
- Messages should suggest corrective action when possible
- Technical detail should help debugging without overwhelming users
- Consistency should make error patterns learnable

**Recommended**: Option B - clear, actionable messages with consistent tone and format

### Validation Point Strategy
**Option A**: Validate inputs at every function boundary
**Option B**: Validate once at major component boundaries (constructors, public APIs)
**Option C**: Lazy validation - validate only when values are actually used
**Option D**: Eliminate most validation - trust inputs, let problems surface naturally

**Decision Criteria**:
- Early validation catches problems at their source
- Over-validation creates performance overhead and complexity
- Validation should align with natural component boundaries
- Users should get clear feedback about configuration mistakes

**Recommended**: Option B - validate at component boundaries, trust internal interfaces

## Success Criteria

### Consistency Success
- **Single error pattern** - all similar problems handled identically across codebase
- **Predictable behavior** - users know exactly what will happen when things go wrong
- **Uniform message format** - error messages follow consistent structure and tone
- **Clear escalation path** - users understand how to resolve or report issues

### User Experience Success
- **Immediate feedback** - problems detected and reported as early as possible
- **Actionable messages** - errors suggest specific steps to fix issues
- **No silent failures** - users always know when something goes wrong
- **Appropriate severity** - configuration mistakes don't crash, real failures do crash

### Developer Experience Success
- **Easy debugging** - error messages point to specific code locations and causes
- **Consistent patterns** - developers know how to handle errors when writing new code
- **Clear testing** - error conditions are easily testable with predictable outcomes
- **Maintenance simplicity** - error handling doesn't complicate code logic

## Quality Standards

**Reference**: Follow `docs/processes/design_philosophy.md` principles

**Key Principles Applied**:
- **Fail Fast, Surface Problems**: Problems should surface immediately rather than being hidden
- **Clarity Through Structure**: Error handling should be obvious and consistent
- **Focus on Researcher's Workflow**: Error messages should help users understand and fix issues quickly

**Consolidated Error Pattern**:
```python
# Consistent validation pattern
def create_figure(config: FigureConfig) -> Figure:
    assert config.rows > 0, f"Figure rows must be positive, got {config.rows}"
    assert config.cols > 0, f"Figure cols must be positive, got {config.cols}"
    assert len(config.x_labels) == config.rows, f"x_labels length {len(config.x_labels)} doesn't match rows {config.rows}"
    
    # Let external failures propagate naturally
    return plt.figure(figsize=config.figsize)

# Consistent error message format
"[Component] [Problem] [Expected] [Got] [Action]"
"FigureConfig: rows must be positive, got -1. Use rows > 0."
```

### Error Handling Standards
- **Assertions for validation** - check preconditions and configuration
- **Descriptive messages** - explain what's wrong and what's expected
- **Natural propagation** - let external system errors bubble up unchanged
- **No defensive programming** - trust internal interfaces after validation

## Adaptation Guidance

### Expected Discoveries
- **Hidden error cases** revealed when silent failures are eliminated
- **Performance impact** of consistent validation
- **User workflow disruptions** from stricter error handling
- **Integration issues** where external systems expect graceful degradation

### Handling Error Strategy Challenges
- **If assertions are too strict**: Examine whether conditions represent real invalid states
- **If performance suffers from validation**: Move expensive checks to development-time tools
- **If users complain about crashes**: Improve error messages rather than hiding failures
- **If external systems break**: Add specific exception handling only for external integration points

### Implementation Strategy
- **Start with most critical paths** - user-facing APIs and configuration validation
- **Work systematically through components** - ensure consistency within each component before moving to next
- **Test error conditions thoroughly** - verify that error handling provides good user experience
- **Monitor user feedback** - adjust message clarity based on real user confusion points

## Documentation Requirements

### Implementation Documentation
- **Error handling standards** for future development
- **Error message templates** showing consistent format and tone
- **Validation patterns** established at component boundaries
- **Testing approaches** for error conditions

### Strategic Insights
- **Common error patterns** identified across the codebase
- **User confusion points** revealed by error message analysis
- **Performance impact** of consolidated validation
- **Integration requirements** for external system error handling

### Future Reference
- **Error handling principles** for consistent application in new code
- **Message writing guidelines** for clear, actionable error communication
- **Validation design patterns** for component boundary protection

---

**Key Success Indicator**: When error handling is consolidated, users should never be surprised by how the system responds to problems, and developers should never need to guess how to handle errors when writing new code.