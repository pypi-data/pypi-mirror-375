# Tactical Agent Prompt: Phase 4A - Verification Test Case Design

**Agent Type**: general-purpose  
**Task**: Comprehensive analysis and test case design for faceting system verification  
**Expected Output**: Detailed test plan with verification decorator specifications

## Mission Objective

Analyze the current faceting implementation and existing examples to design a comprehensive verification testing strategy using the project's verification decorators. Create systematic test cases that provide objective, detailed analysis of faceting functionality rather than subjective visual assessment.

## Strategic Context

**Current Status**:
- ✅ **Faceting system simplified**: 80% code reduction with excellent quality standards
- ✅ **Functionality preserved**: Multi-variable faceting, style coordination, advanced targeting all working
- 🎯 **Next Challenge**: Systematic verification that ALL capabilities work correctly across ALL use cases

**Key Problem**: Agents cannot reliably assess plot quality through visual inspection alone. The verification decorators in `src/dr_plotter/scripting/` provide objective analysis capabilities that solve this problem.

**Reference Documents**:
- `docs/projects/active/architectural_simplification/audit_reports/faceting_system_audit_report.md` - functionality requirements
- `src/dr_plotter/scripting/verif_decorators.py` - verification capabilities available
- `src/dr_plotter/scripting/plot_data_extractor.py` - detailed plot property extraction
- Existing faceting examples in `examples/` directory

## Research and Analysis Tasks

### Task 1: Analyze Current Faceting Capabilities
**Action**: Comprehensive analysis of implemented faceting functionality
**Focus**:
- Read the new `src/dr_plotter/faceting/faceting_core.py` completely
- Read the new `src/dr_plotter/faceting/style_coordination.py` completely  
- Understand `FacetingConfig` parameters and their effects
- Map out all supported plot types and configuration options
- Document integration points with `FigureManager`

**Deliverable**: **Functionality Map** documenting:
- All faceting capabilities (rows, cols, lines, targeting, etc.)
- Supported plot types and their behavior
- Style coordination features and expected visual consistency
- Configuration parameters and their effects
- Integration points and dependencies

### Task 2: Inventory Existing Examples and Use Cases
**Action**: Comprehensive survey of current faceting usage
**Focus**:
- Find ALL files in `examples/` directory that use faceting
- Analyze each example's specific faceting configuration
- Document the expected visual behavior for each example
- Identify patterns and common use cases
- Note any advanced or edge case scenarios

**Deliverable**: **Example Inventory** documenting:
- Complete list of faceting examples with descriptions
- Specific `FacetingConfig` parameters used in each
- Expected visual outcomes for each example
- Complexity level (basic, intermediate, advanced)
- Coverage gaps where additional test cases are needed

### Task 3: Master Verification Decorator Capabilities
**Action**: Deep analysis of verification system capabilities
**Focus**:
- Study `verif_decorators.py` completely - understand all decorator types and parameters
- Study `plot_data_extractor.py` - understand what plot properties can be extracted
- Study `unified_verification_engine.py` - understand verification logic
- Map decorator capabilities to faceting verification needs
- Understand how to specify expected plot properties

**Deliverable**: **Verification Capabilities Map** documenting:
- Available decorators and their specific capabilities
- How to specify expected legends, channels, consistency checks
- Property extraction capabilities (colors, markers, positions, etc.)
- Error detection and diagnostic capabilities
- How to create comprehensive test specifications

### Task 4: Gap Analysis and Edge Case Identification
**Action**: Identify testing gaps and challenging scenarios
**Focus**:
- Compare faceting capabilities against current example coverage
- Identify sophisticated features that aren't currently tested
- Find edge cases and error conditions that need verification
- Consider integration scenarios and boundary conditions
- Document potential failure modes and how to test for them

**Deliverable**: **Gap Analysis Report** documenting:
- Untested faceting capabilities requiring coverage
- Edge cases and error conditions to verify
- Integration scenarios needing systematic testing
- Potential failure modes and detection strategies
- Priority levels for different test categories

## Test Case Design Requirements

### Test Category 1: Core Functionality Verification
**Design Requirements**:
- **Multi-variable faceting**: Verify correct data partitioning across rows/cols
- **Style coordination**: Verify consistent colors/markers across subplots
- **Plot type support**: Verify all plot types work with faceting
- **Basic integration**: Verify FigureManager integration works correctly

**Specification Format**:
```python
# Example specification format
@verify_plot(
    expected_legends=1,
    expected_channels={(0,0): ["color"], (0,1): ["color"], (1,0): ["color"], (1,1): ["color"]},
    verify_legend_consistency=True,
    subplot_descriptions={...}
)
def test_basic_multi_variable_faceting():
    # Clear test description
    # Expected behavior specification
    # Implementation approach
```

### Test Category 2: Advanced Feature Verification  
**Design Requirements**:
- **Advanced targeting**: Verify selective subplot population
- **Custom ordering**: Verify row_order, col_order, lines_order parameters
- **Empty subplot handling**: Verify strategies (error, warn, silent)
- **Complex configurations**: Verify sophisticated FacetingConfig combinations

### Test Category 3: Integration and Compatibility Verification
**Design Requirements**:
- **FigureManager integration**: Verify plot_faceted method works with all configurations
- **Theme integration**: Verify consistent styling with different themes
- **Legend management**: Verify legend placement and coordination
- **Existing example compatibility**: Verify all existing examples still work identically

### Test Category 4: Edge Cases and Error Conditions
**Design Requirements**:
- **Single subplot scenarios**: When only one row or column specified
- **Missing data scenarios**: How empty data subsets are handled
- **Invalid configurations**: How errors are detected and reported
- **Boundary conditions**: Large grids, many series, complex targeting

### Test Category 5: Regression and Consistency
**Design Requirements**:
- **Visual consistency**: Colors, markers, legends consistent across subplots
- **Output quality**: Professional publication-ready appearance
- **Performance consistency**: No degradation with complex configurations
- **API compatibility**: Existing code continues working unchanged

## Documentation Requirements

### Primary Deliverable: Comprehensive Test Plan Document
**File**: `docs/projects/active/architectural_simplification/test_plans/faceting_verification_test_plan.md`

**Required Sections**:

#### 1. **Executive Summary**
- Overview of testing strategy and approach
- Key objectives and success criteria
- Summary of test categories and coverage

#### 2. **Functionality Analysis**  
- Complete map of faceting capabilities
- Integration points and dependencies
- Supported configurations and behaviors

#### 3. **Existing Example Analysis**
- Inventory of current examples with descriptions
- Coverage analysis - what's tested vs. what needs testing
- Complexity assessment and gaps identified

#### 4. **Verification Strategy**
- How verification decorators will be used
- Mapping of test categories to decorator capabilities
- Expected property specifications and success criteria

#### 5. **Test Case Specifications**
**Format for each test case**:
```markdown
### Test Case: [Name]
**Objective**: Clear description of what this test verifies
**Category**: Core/Advanced/Integration/Edge Cases/Regression
**Priority**: High/Medium/Low
**Complexity**: Basic/Intermediate/Advanced

**Faceting Configuration**:
- Specific FacetingConfig parameters
- Expected data requirements
- Plot type and styling

**Expected Visual Properties**:
- Legend specifications (count, entries, positioning)
- Channel specifications (color consistency, marker usage)
- Subplot layout and content expectations
- Style coordination requirements

**Verification Decorator Specification**:
```python
@verify_plot(
    expected_legends=N,
    expected_channels={...},
    verify_legend_consistency=True/False,
    subplot_descriptions={...}
)
```

**Implementation Notes**:
- Data setup requirements
- Potential challenges or complexity
- Dependencies on other tests
```

#### 6. **Implementation Roadmap**
- Test case priority order for Phase 4B implementation
- Dependencies between test cases
- Expected implementation effort and timeline
- Risk assessment and mitigation strategies

#### 7. **Success Criteria and Verification Standards**
- What constitutes successful test completion
- Acceptable tolerance levels for visual consistency
- Error detection and diagnostic requirements
- Documentation standards for test results

## Quality Standards

### Analysis Quality Requirements
- **Comprehensive coverage**: Every faceting capability must be analyzed and planned for testing
- **Evidence-based design**: All test cases must be based on actual functionality analysis
- **Specific verification criteria**: Each test must have clear, objective success criteria
- **Implementation readiness**: Test specifications must be detailed enough for direct implementation

### Documentation Quality Requirements
- **Self-contained specifications**: Each test case specification should be implementable without additional research
- **Clear success criteria**: Objective, measurable outcomes for each test
- **Practical implementation guidance**: Specific decorator configurations and expected behaviors
- **Comprehensive coverage justification**: Rationale for why these test cases provide complete verification

## Expected Timeline and Effort

### Research Phase (60% of effort)
- Functionality analysis and mapping
- Example inventory and gap analysis  
- Verification capability mastery
- Edge case identification

### Design Phase (40% of effort)
- Test case specification creation
- Verification decorator configuration
- Implementation roadmap development
- Documentation completion

## Success Criteria

### Analysis Completeness ✅
- [ ] All faceting capabilities documented and understood
- [ ] All existing examples analyzed and categorized
- [ ] All verification decorator capabilities mapped to testing needs
- [ ] Comprehensive gap analysis identifying untested scenarios

### Test Design Quality ✅
- [ ] Test cases provide comprehensive coverage of all faceting functionality
- [ ] Each test case has specific, objective verification criteria
- [ ] Verification decorators are properly specified for each test
- [ ] Implementation approach is clear and actionable

### Documentation Excellence ✅
- [ ] Test plan document is comprehensive and self-contained
- [ ] Each test case specification is implementable without additional research
- [ ] Success criteria are clear and measurable
- [ ] Implementation roadmap provides clear guidance for Phase 4B

## Critical Success Factors

**Systematic Coverage**: The test plan must cover ALL faceting capabilities, not just the obvious ones. Edge cases and integration scenarios are critical for complete verification.

**Objective Verification**: Every test must use verification decorators to provide specific, measurable success criteria rather than subjective visual assessment.

**Implementation Readiness**: The test specifications must be detailed enough that Phase 4B can implement and execute them systematically without additional design work.

**Quality Assurance**: The verification approach must be capable of detecting subtle issues like color consistency problems, legend coordination failures, or data partitioning errors.

---

**Key Implementation Principle**: Design tests that provide **confidence through objective measurement** rather than **hope through visual inspection**. The verification decorators are the key to transforming subjective "it looks right" into objective "it meets specification".