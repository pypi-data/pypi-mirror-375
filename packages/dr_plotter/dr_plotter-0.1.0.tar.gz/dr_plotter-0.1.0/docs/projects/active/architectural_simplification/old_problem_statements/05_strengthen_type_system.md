# Problem Statement: Strengthen Type System

**Priority**: 2 (High Value)

## Strategic Objective

Replace meaningless type aliases with meaningful types that provide actual type safety, catching common errors at development time rather than runtime. This addresses a systematic weakness that allows bugs to slip through that could be prevented by proper typing.

## Problem Context

The current type system provides the illusion of type safety without actual protection:

**Current Type System Weakness**:
```python
# From types.py - meaningless aliases
type BasePlotterParamName = str
type SubPlotterParamName = str  
type VisualChannel = str        # "hue_by" and "invalid_channel" are both valid
type ColName = str              # Any string accepted as column name
type StyleAttrName = str
```

**Real-World Impact**:
- **Parameter mistakes undetected**: `hue_by="colour"` (typo) passes type checking
- **Invalid channels accepted**: `style_by="nonexistent"` not caught until runtime
- **Column name errors**: `x="wrong_column"` fails silently in complex data pipelines
- **Configuration mistakes**: Theme keys like `"colour"` vs `"color"` not caught

**Evidence of Problems**:
```python
# These all pass type checking but fail at runtime
fm.plot("scatter", data, x="typo_column", hue_by="wrong_channel")
config = GroupingConfig(hue_by="bad_column", style_by="invalid") 
theme_override = {"colour": "red"}  # Should be "color"
```

## Requirements & Constraints

### Must Preserve
- **All current functionality** - no regression in plotting capabilities
- **Type hint completeness** - maintain 100% type coverage
- **Development workflow** - type checking remains fast and useful
- **IDE support** - autocomplete and error detection continue working

### Must Achieve
- **Meaningful type safety** - common mistakes caught at development time
- **Self-documenting types** - types communicate valid values/constraints
- **Runtime validation alignment** - type system matches actual validation
- **Developer confidence** - types help rather than hinder development

### Cannot Break
- **Existing code** - current user scripts continue working
- **Dynamic usage** - runtime flexibility preserved where needed
- **Performance** - no runtime overhead from stronger typing

## Decision Frameworks

### Type Strength Strategy
**Option A**: Literal types for finite sets (`VisualChannel = Literal["hue_by", "style_by", "size_by"]`)
**Option B**: Enum types for structured values (`class VisualChannel(Enum)`)
**Option C**: NewType wrappers for domain-specific strings (`ColName = NewType("ColName", str)`)
**Option D**: Protocol types for structural validation (`class DataColumn(Protocol)`)

**Decision Criteria**:
- Types should catch real mistakes developers make
- IDE support should be excellent (autocomplete, error highlighting)
- Runtime flexibility preserved for dynamic use cases
- Type checking performance remains acceptable

**Recommended**: Mixed approach - Option A for finite sets, Option C for domain strings, Option D for complex structures

### Column Name Validation Strategy
**Option A**: Validated column name type that checks against DataFrame at creation
**Option B**: Generic type that carries DataFrame schema information
**Option C**: Runtime validation with type hints for documentation
**Option D**: Keep string type but improve runtime validation

**Decision Criteria**:
- Balance between type safety and usability
- Performance impact of validation
- Complexity of implementation vs. benefit gained
- Integration with existing pandas patterns

**Recommended**: Option C - document expected types, improve runtime validation with clear errors

### Visual Channel Type Strategy  
**Option A**: Literal union of valid channel names
**Option B**: Enum with string values
**Option C**: Protocol defining channel interface
**Option D**: Class hierarchy for different channel types

**Decision Criteria**:
- Catch typos in common parameter names
- Enable IDE autocomplete for channel names
- Maintain flexibility for custom channels
- Align with how users think about channels

**Recommended**: Option A - `Literal["hue_by", "style_by", "size_by", ...]` for immediate typo detection

## Success Criteria

### Type Safety Success
- **Common mistakes caught** - typos in parameter names detected by type checker
- **Invalid values rejected** - type system prevents obviously wrong values
- **IDE support improved** - autocomplete works for parameter values, not just names
- **Documentation through types** - types communicate valid options to developers

### Developer Experience Success
- **Helpful error messages** - type errors point to specific problems
- **Reduced debugging time** - fewer runtime errors from simple mistakes
- **Better IDE integration** - intelligent suggestions and error highlighting
- **Self-documenting APIs** - function signatures communicate valid usage

### System Integration Success
- **Validation alignment** - type system matches runtime validation logic
- **Performance maintained** - no degradation in type checking or runtime performance
- **Migration simplicity** - existing code requires minimal changes
- **Future extensibility** - type system supports adding new plot types and channels

## Quality Standards

**Reference**: Follow `docs/processes/design_philosophy.md` principles

**Key Principles Applied**:
- **Fail Fast, Surface Problems**: Types catch problems at development time
- **Self-Documenting Code**: Types communicate valid usage patterns
- **Focus on Researcher's Workflow**: Types help rather than hinder common tasks

**Improved Type Patterns**:
```python
# Instead of meaningless aliases
type VisualChannel = Literal["hue_by", "style_by", "size_by", "alpha_by"]
type PlotType = Literal["scatter", "line", "bar", "histogram", "heatmap", "violin"]
type LegendPlacement = Literal["subplot", "figure", "none"]

# For column names - runtime validation with type hints
type ColumnName = Annotated[str, "DataFrame column name"]

# For configuration keys
type StyleKey = Literal["color", "alpha", "linewidth", "marker", "markersize"]
```

## Adaptation Guidance

### Expected Discoveries
- **Dynamic usage patterns** that require type flexibility
- **Performance bottlenecks** from type validation
- **Complex type relationships** between different components
- **IDE compatibility issues** with advanced type constructs

### Handling Type System Challenges
- **If types are too restrictive**: Add escape hatches for advanced usage while keeping safety for common cases
- **If performance suffers**: Move complex validation to development-time tools rather than runtime
- **If existing code breaks**: Provide gradual migration path with deprecation warnings
- **If IDE support is poor**: Prefer simpler types that work well over complex types that don't

### Implementation Strategy
- **Start with highest-impact types** - visual channels and plot types first
- **Gradual rollout** - introduce stronger types incrementally
- **Test with real codebases** - ensure types help rather than hinder actual development
- **Monitor performance** - ensure type checking remains fast

## Documentation Requirements

### Implementation Documentation
- **Type system architecture** showing new type hierarchy and relationships
- **Migration guide** for updating existing type annotations
- **IDE setup instructions** for optimal type checking experience
- **Performance benchmarks** comparing old vs new type checking speed

### Strategic Insights
- **Common error patterns** identified during type system analysis
- **Type safety vs flexibility trade-offs** discovered during implementation
- **Developer workflow impacts** of stronger typing
- **Integration points** where type system provides most value

### Future Reference
- **Type design principles** for consistent future type development
- **Type testing strategies** to ensure type safety without runtime overhead
- **Extension patterns** for adding new types as the system evolves

---

**Key Success Indicator**: When type system is strengthened, developers should experience fewer "it compiled but crashed at runtime" issues, and common mistakes like parameter typos should be caught immediately by their development environment.