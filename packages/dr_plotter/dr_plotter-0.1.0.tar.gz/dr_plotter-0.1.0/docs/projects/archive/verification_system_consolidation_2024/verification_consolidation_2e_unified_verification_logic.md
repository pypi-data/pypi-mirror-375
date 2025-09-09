# Tactical Prompt: Consolidate Verification Logic Functions

## Strategic Objective
Create a unified, pluggable verification engine that eliminates the remaining duplication in verification logic functions. This completes the foundation consolidation by creating a single, extensible system for all verification operations while maintaining all current functionality.

## Problem Context
Despite the progress in consolidating data extraction and formatting, the verification system still has scattered verification logic with similar patterns:
- **Multiple `verify_*_consistency()` functions** (color, marker, size, alpha, style) with nearly identical logic structures
- **Multiple `verify_*_strategy()` functions** (unified, split figure strategies) with similar validation patterns
- **Duplicate parameter processing and result formatting** across verification functions
- **Similar verification workflows** that could be generalized into pluggable rules

This remaining duplication makes the system harder to maintain and extend.

## Requirements & Constraints
**Must Create**:
- Unified verification engine that can execute different types of verification rules
- Pluggable verification rule system where specific checks become configurable rules
- Single entry point for all verification operations with consistent interfaces
- Generic verification workflows that work for consistency checks, strategy checks, etc.

**Must Preserve**:
- All current verification capabilities and accuracy
- Existing parameter interfaces during transition
- All current return value structures and error information
- Integration with existing decorator and formatting systems

**Files to Modify**:
- Create new: `src/dr_plotter/scripting/unified_verification_engine.py`
- Update: `plot_verification.py` (replace scattered verification functions)
- Update: All verification callers to use unified verification engine
- Update: Import statements throughout verification system

## Decision Frameworks
**Verification Engine Architecture**:
- **Rule-based vs Function-based**: Create pluggable verification rules vs keep separate functions with shared utilities
- **Generic vs Specific**: Single generic verification engine vs specialized engines for different verification types
- **Configuration-driven vs Code-driven**: Rules configured through parameters vs rules implemented as code

**Rule System Design**:
- **Rule Registration**: How verification rules are registered and discovered by the engine
- **Parameter Standardization**: Common parameter interface across all verification rule types
- **Result Format**: Unified result format that works for all verification rule outputs
- **Error Handling**: How verification rules report errors and failures consistently

**Migration Strategy**:
- **Backward Compatibility**: Maintain existing function signatures vs clean break to new interface
- **Rule Conversion**: Convert existing verification functions to rules vs create new rule implementations
- **Integration Points**: How unified engine integrates with decorators and formatting system

## Success Criteria
**Unified Verification System**:
- [ ] Single verification engine handles all verification types (consistency, strategy, channel variation)
- [ ] Pluggable rule system allows easy addition of new verification types
- [ ] All `verify_*_consistency()` functions eliminated and replaced with unified consistency rule
- [ ] All `verify_*_strategy()` functions consolidated into unified strategy verification

**Code Consolidation**:
- [ ] Eliminate duplicate parameter processing across verification functions
- [ ] Single result format and error handling across all verification operations
- [ ] Generic verification workflows that work for all verification rule types
- [ ] Clean separation between verification logic and rule-specific implementations

**Functional Preservation**:
- [ ] All existing verification capabilities maintained with identical accuracy
- [ ] Existing verification behavior unchanged from user perspective
- [ ] All current parameter interfaces continue to work during transition
- [ ] Performance maintained or improved through consolidated implementation

## Quality Standards
**Extensibility**: New verification types can be added through pluggable rule system without modifying core engine
**Consistency**: All verification operations follow same patterns and interfaces
**Maintainability**: Single verification engine is easier to understand, test, and debug than scattered functions
**Performance**: Unified system should perform at least as well as current scattered implementation

## Adaptation Guidance
**If verification logic differs subtly**: Identify the core pattern and create configurable rule parameters to handle variations
**If parameter interfaces are inconsistent**: Design unified parameter interface that can accommodate all current usage patterns
**If some verification logic is complex**: Create specialized rule types within the pluggable system
**If performance is affected**: Profile verification engine and optimize common verification workflows

## Documentation Requirements
**Create implementation document** showing:
- Unified verification engine architecture and pluggable rule system design
- Mapping from old scattered verification functions to new unified rules
- Rule creation guide for adding new verification types
- Performance characteristics and any behavior changes from consolidation

**Implementation Approach**:
1. **Design unified verification engine** with pluggable rule architecture
2. **Convert existing verification functions** to use unified engine with appropriate rules
3. **Update all callers** to use unified verification interface
4. **Remove old scattered verification functions** completely
5. **Test verification consistency** across all scenarios to ensure identical behavior

This consolidation creates a clean, extensible verification foundation that eliminates the remaining duplication while making it easy to add new verification capabilities in the future.