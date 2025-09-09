# Problem Statement: Validation Centralization

**Priority**: 3 (Technical Debt)

## Strategic Objective

Replace the scattered validation logic with a single, consistent validation framework that provides clear error messages, eliminates defensive programming patterns, and aligns with DR methodology's "Fail Fast, Surface Problems" principle.

## Problem Context

Validation is currently scattered across multiple components with inconsistent patterns, timing, and error handling:

**Current Validation Scatter**:
```python
# From various files - inconsistent validation patterns
# FigureConfig.validate(): 35 lines of matrix validation with assertions
assert len(self.x_labels) == self.rows, f"x_labels length {len(self.x_labels)} doesn't match rows {self.rows}"

# GroupingConfig.validate_against_enabled(): Channel validation  
assert len(unsupported) == 0, f"Unsupported groupings: {unsupported}"

# validate_faceting_data_requirements(): 40+ lines with difflib integration
if missing_columns:
    suggestion = difflib.get_close_matches(missing[0], available, n=1)
    # Complex error recovery logic...

# BasePlotter validation: Mixed with business logic
if not hasattr(data, column):
    print(f"Warning: Column {column} not found")  # Inconsistent error handling
```

**Validation Problems**:
- **Inconsistent timing**: Some validation at object creation, some during operations
- **Mixed error patterns**: Assertions, exceptions, print statements, warnings
- **Scattered logic**: Validation rules spread across 10+ files
- **Defensive complexity**: Complex error recovery instead of clear failure

**Evidence of Validation Drift**:
- Different components use different assertion patterns
- Error messages have inconsistent format and tone
- Some validation is defensive (tries to continue), some is strict
- Validation logic mixed with business logic throughout codebase

## Requirements & Constraints

### Must Preserve
- **All current validation logic** - same inputs rejected, same inputs accepted
- **Error information quality** - users get same or better error information
- **Validation timing** - critical validations still happen early
- **Integration behavior** - components continue validating appropriately

### Must Achieve
- **Consistent validation patterns** - same type of problem handled same way everywhere
- **Clear error messages** - consistent format, tone, and actionable information
- **Centralized validation logic** - validation rules in single, discoverable location
- **Fail-fast behavior** - alignment with DR methodology principles

### Cannot Break
- **User workflows** - existing scripts continue working or fail with clear messages
- **Component interfaces** - validation doesn't change public APIs
- **Performance** - validation overhead remains minimal

## Decision Frameworks

### Validation Architecture Strategy
**Option A**: Central ValidationService used by all components
**Option B**: Validation mixins/decorators applied to component methods
**Option C**: Schema-based validation with declarative rules
**Option D**: Component-boundary validation with shared validation utilities

**Decision Criteria**:
- Eliminate validation code duplication
- Provide consistent error experience
- Align with DR methodology's fail-fast principle
- Maintain component autonomy and testability

**Recommended**: Option D - validation at component boundaries using shared utilities

### Error Message Strategy
**Option A**: Structured error messages with consistent template
**Option B**: Context-aware messages that adapt to user's likely intent
**Option C**: Simple, actionable messages with consistent tone
**Option D**: Technical error codes with detailed explanations

**Decision Criteria**:
- Users should immediately understand what went wrong
- Messages should suggest corrective action when possible
- Consistency should make error patterns learnable
- Technical detail should help debugging without overwhelming

**Recommended**: Option C - simple, consistent messages with clear actions

### Validation Timing Strategy
**Option A**: Eager validation at object creation
**Option B**: Lazy validation when values are first used
**Option C**: Just-in-time validation at operation boundaries
**Option D**: Mixed approach based on validation type

**Decision Criteria**:
- Early validation catches configuration problems immediately
- Performance impact should be minimal
- Error location should be obvious to users
- Validation should align with natural component lifecycles

**Recommended**: Option A with Option C elements - validate configuration early, validate data just-in-time

## Success Criteria

### Centralization Success
- **Shared validation utilities** - common validation patterns factored into reusable functions
- **Consistent error format** - all validation errors follow same message template
- **Elimination of scattered logic** - validation rules discoverable in central location
- **Pattern consistency** - same validation approach used across all components

### User Experience Success
- **Predictable error behavior** - users know what to expect from validation failures
- **Clear error messages** - problems explained in actionable terms
- **Immediate feedback** - validation problems detected as early as practical
- **Helpful suggestions** - error messages guide users toward solutions

### Developer Experience Success
- **Easy validation testing** - validation behavior easily verifiable in tests
- **Simple validation addition** - adding new validation rules straightforward
- **Clear validation location** - obvious where to find and modify validation logic
- **Debugging simplicity** - validation errors easy to trace to source

## Quality Standards

**Reference**: Follow `docs/processes/design_philosophy.md` principles

**Key Principles Applied**:
- **Fail Fast, Surface Problems**: Validation should detect problems immediately and clearly
- **Clarity Through Structure**: Validation logic should be obviously organized and discoverable
- **Succinct and Self-Documenting**: Validation code should be minimal and self-explanatory

**Centralized Validation Pattern**:
```python
# Shared validation utilities
class ValidationUtils:
    @staticmethod
    def validate_matrix_dimensions(matrix: List[List], expected_rows: int, expected_cols: int, name: str) -> None:
        assert len(matrix) == expected_rows, f"{name} has {len(matrix)} rows, expected {expected_rows}"
        for i, row in enumerate(matrix):
            assert len(row) == expected_cols, f"{name} row {i} has {len(row)} columns, expected {expected_cols}"
    
    @staticmethod
    def validate_columns_exist(data: DataFrame, columns: List[str], context: str) -> None:
        missing = [col for col in columns if col not in data.columns]
        assert not missing, f"{context}: columns {missing} not found in data. Available: {list(data.columns)}"

# Component boundary validation
class FigureConfig:
    def __post_init__(self) -> None:  # Validate at creation
        assert self.rows > 0, f"Figure rows must be positive, got {self.rows}"
        assert self.cols > 0, f"Figure cols must be positive, got {self.cols}"
        if self.x_labels:
            ValidationUtils.validate_matrix_dimensions(self.x_labels, self.rows, self.cols, "x_labels")
```

### Validation Standards
- **Consistent message format**: "[Context]: [Problem]. [Expected]. [Action]."
- **Early detection**: Validate configuration at creation, validate data at usage
- **Clear assertions**: Descriptive assertion messages that explain the problem
- **No defensive programming**: Validation failures should stop execution, not continue with degraded behavior

## Adaptation Guidance

### Expected Discoveries
- **Hidden validation dependencies** between components
- **Complex validation cases** that resist simple centralization
- **Performance impact** of centralized validation
- **Legacy validation patterns** that are difficult to migrate

### Handling Validation Challenges
- **If validation is too complex to centralize**: Create validation utilities for common patterns, keep complex logic local
- **If performance suffers**: Move expensive validation to development-time tools
- **If error messages become too verbose**: Balance information with usability
- **If migration breaks existing behavior**: Preserve behavior while improving consistency

### Implementation Strategy
- **Start with most common patterns** - centralize validation that appears in multiple places
- **Implement shared utilities first** - build foundation before migrating existing validation
- **Test error message quality** - ensure consolidated messages are as helpful as originals
- **Monitor validation performance** - ensure centralization doesn't create bottlenecks

## Documentation Requirements

### Implementation Documentation
- **Validation architecture** showing centralized utilities and component boundary patterns
- **Error message guidelines** for consistent validation message creation
- **Validation testing patterns** for verifying validation behavior
- **Migration notes** documenting changes to validation timing or behavior

### Strategic Insights
- **Common validation patterns** identified across the codebase
- **Validation complexity sources** discovered during centralization
- **Error message effectiveness** analysis comparing old vs new messages
- **Performance characteristics** of centralized vs scattered validation

### Future Reference
- **Validation design principles** for consistent future development
- **Error message templates** for creating helpful validation messages
- **Validation testing strategies** for comprehensive validation coverage

---

**Key Success Indicator**: When validation is centralized, adding validation to a new component should be straightforward using established patterns, and all validation errors should provide clear, consistent guidance that helps users fix their configuration or data problems immediately.