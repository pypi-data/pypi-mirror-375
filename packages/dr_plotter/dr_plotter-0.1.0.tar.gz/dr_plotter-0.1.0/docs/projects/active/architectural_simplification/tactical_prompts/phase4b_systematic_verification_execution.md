# Tactical Agent Prompt: Phase 4B - Systematic Verification Execution

**Agent Type**: general-purpose  
**Task**: Execute systematic faceting verification testing with objective measurement  
**Expected Output**: Complete verification of simplified faceting system with documented results

## Mission Objective

Execute the comprehensive verification test plan systematically, using verification decorators to provide **objective measurement** rather than subjective visual assessment. Verify that the simplified faceting system (80% code reduction) preserves all sophisticated functionality while maintaining professional output quality.

## Strategic Context

**Current Status**:
- ✅ **Faceting system simplified**: From 6 modules/752 lines → 2 modules/380 lines  
- ✅ **Code quality achieved**: Zero comments, proper assertions, excellent architecture
- ✅ **Test plan designed**: 35 systematic test cases with objective verification criteria
- 🎯 **Critical Phase**: Prove the simplified system works correctly across ALL use cases

**Key Principle**: **Confidence through objective measurement**, not hope through visual inspection.

**Reference Documents**:
- `docs/projects/active/architectural_simplification/test_plans/faceting_verification_test_plan.md` - **PRIMARY SPECIFICATION**
- `src/dr_plotter/scripting/verif_decorators.py` - Verification decorator capabilities
- Examples in `examples/faceting/` and `examples/` - Reference implementations

## Implementation Strategy

### **Test-Driven Systematic Execution**
- **One test at a time** - Complete each test fully before proceeding
- **Objective verification** - Every test uses verification decorators for measurable results
- **Immediate debugging** - Fix issues as they're discovered with detailed diagnostic output
- **Documentation required** - Record results, evidence, and insights for each test

### **Priority-Based Implementation Order**
Follow the **exact priority order** from the test plan:

#### **Priority 1: Core Functionality** (Must complete first)
1. **Basic 2D Faceting** - Foundation test ensuring grid creation and color coordination
2. **Single Dimension Faceting** - Edge case verification for rows-only/cols-only  
3. **All Plot Types Integration** - Critical for ensuring no functionality loss
4. **Color Consistency Regression** - Verification that simplification preserves behavior

#### **Priority 2: Advanced Features** (After Priority 1 complete)
5. **Selective Targeting - Single Position** - Advanced targeting verification
6. **Multiple Position Targeting** - Complex targeting scenarios
7. **FigureManager Legend Integration** - Integration with legend system
8. **Existing Example Compatibility** - Regression prevention for real usage

*Continue through all 35 test cases as specified in the test plan*

## Test Infrastructure Setup

### Task 1: Create Verification Test Framework
**Action**: Set up systematic testing infrastructure
**Requirements**:

#### 1a: Test Data Generation Utilities
```python
# Create: tests/verification/data_generators.py
def create_synthetic_faceting_data(
    n_points: int,
    metrics: List[str],
    datasets: List[str], 
    models: List[str],
    seed: int = 42
) -> pd.DataFrame:
    # Generate controlled synthetic data for systematic testing
    # Must produce predictable, consistent results for verification
```

#### 1b: Verification Decorator Integration
```python
# Create: tests/verification/test_core_functionality.py
import sys
sys.path.append('src/dr_plotter/scripting')
from verif_decorators import verify_plot, inspect_plot_properties, verify_figure_legends

# Import all verification capabilities as specified in test plan
```

#### 1c: Reference Implementation Validation
```python
# Validate that existing examples work correctly before using as reference
def validate_reference_examples():
    # Run examples/faceting/simple_grid.py and capture output
    # Run key examples from faceted_plotting_guide.py
    # Ensure reference implementations are correct before comparison testing
```

#### 1d: Performance Benchmarking Setup
```python
# Create: tests/verification/performance_baseline.py  
def establish_performance_baseline():
    # Measure execution time for standard test cases
    # Create reference timing data for regression detection
    # Set up memory usage monitoring
```

**Deliverable**: Working test infrastructure that enables systematic execution

### Task 2: Priority 1 Test Implementation

Execute **each test exactly as specified** in the test plan. For each test:

#### **Required Implementation Pattern**:

```python
# Test Case: [Name from test plan]
@verify_plot(
    # EXACT decorator configuration from test plan
    expected_legends=N,
    expected_channels={...},  # Copy exact specification  
    verify_legend_consistency=True/False,
    min_unique_threshold=N,
    subplot_descriptions={...}
)
def test_[name]():
    # 1. Create test data as specified
    data = create_synthetic_faceting_data(...)
    
    # 2. Configure faceting exactly as specified  
    config = FacetingConfig(...)  # Copy exact config from test plan
    
    # 3. Execute faceting
    with FigureManager(figure=FigureConfig(rows=N, cols=M)) as fm:
        fm.plot_faceted(data=data, plot_type="...", faceting=config, **kwargs)
        fig = fm.fig
    
    # 4. Return figure for verification decorator analysis
    return fig

# Execute and document results
def execute_test_with_documentation():
    try:
        result_fig = test_[name]()
        # SUCCESS: Document what passed
        record_test_success(test_name, verification_details)
    except AssertionError as e:
        # FAILURE: Document specific failure and debug
        record_test_failure(test_name, str(e), debug_info)
        # DO NOT CONTINUE until this test passes
```

#### **Test Case 1: Basic 2D Faceting**
**Implementation Requirements** (from test plan):

```python
@verify_plot(
    expected_legends=0,  # Using figure legend, not subplot legends
    expected_channels={
        (0,0): ["color"], (0,1): ["color"], (0,2): ["color"],
        (1,0): ["color"], (1,1): ["color"], (1,2): ["color"]
    },
    verify_legend_consistency=False,
    min_unique_threshold=4,  # 4 models should produce 4 colors
    subplot_descriptions={
        0: "Loss metric across 3 datasets with 4 model colors",
        1: "Accuracy metric across 3 datasets with same 4 model colors"
    }
)
def test_basic_2d_faceting():
    # Create synthetic data: 2 metrics × 3 datasets × 4 models
    data = create_synthetic_faceting_data(
        n_points=100,
        metrics=["loss", "accuracy"],
        datasets=["train", "val", "test"], 
        models=["A", "B", "C", "D"]
    )
    
    config = FacetingConfig(
        rows="metric",    # 2 metrics: loss, accuracy
        cols="dataset",   # 3 datasets: train, val, test
        lines="model",    # 4 models: A, B, C, D
        x="step", y="value"
    )
    
    with FigureManager(figure=FigureConfig(rows=2, cols=3)) as fm:
        fm.plot_faceted(data=data, plot_type="line", faceting=config)
        return fm.fig
```

**Expected Success**: Verification decorator confirms:
- 2×3 subplot grid created correctly
- 4 distinct colors for 4 models
- Same model = same color across all 6 subplots
- Each subplot contains only relevant metric×dataset data

**If Test Fails**: 
- **Analyze verification decorator output** for specific failure details
- **Debug using `@inspect_plot_properties`** to see actual vs expected properties
- **Fix underlying issue** in faceting implementation
- **Re-run until test passes** before proceeding

#### **Test Case 2: Single Dimension Faceting**
**Implementation**: Follow exact specification from test plan for rows-only and cols-only scenarios

#### **Test Case 3: All Plot Types Integration**  
**Implementation**: Test line, scatter, bar, fill_between, heatmap with faceting

#### **Test Case 4: Color Consistency Regression**
**Implementation**: Compare color assignments to reference implementation

**Critical Requirement**: **ALL Priority 1 tests must pass** before proceeding to Priority 2

## Systematic Execution Requirements

### **Individual Test Execution Protocol**

#### **For Each Test Case**:

1. **Read Test Specification** - Study exact requirements from test plan
2. **Implement Test Code** - Following exact decorator configuration
3. **Execute Test** - Run with verification decorator analysis
4. **Analyze Results** - Review verification output for pass/fail
5. **Debug If Failed** - Use diagnostic output to identify and fix issues
6. **Document Results** - Record success/failure with evidence
7. **Proceed Only On Success** - Do not advance until test passes

#### **Success Documentation Format**:
```markdown
### Test: [Name]
**Status**: ✅ PASSED
**Duration**: X.X seconds
**Key Verification Results**:
- Subplot grid: X×Y confirmed
- Color consistency: N distinct colors verified across all subplots
- Legend verification: Expected count confirmed
- Channel analysis: All specified channels verified

**Evidence**:
- Verification decorator output: [Paste key success messages]
- Visual properties extracted: [Summary of color/marker analysis]
```

#### **Failure Documentation Format**:
```markdown
### Test: [Name] 
**Status**: ❌ FAILED
**Failure Details**: [Exact error message from verification decorator]
**Root Cause**: [Analysis of why the test failed]
**Expected**: [What the test expected to see]
**Actual**: [What was actually observed]
**Fix Applied**: [Specific changes made to resolve issue]
**Retry Result**: [Success/failure after fix]
```

### **Debugging and Issue Resolution**

#### **When Tests Fail**:

1. **Use Verification Decorator Diagnostics**:
   ```python
   @inspect_plot_properties()  # Add this to failing test for detailed analysis
   def debug_failing_test():
       # Same test code - decorator will output comprehensive analysis
   ```

2. **Common Failure Patterns and Solutions**:

   **Color Inconsistency**:
   ```
   Failure: "Expected 4 unique colors, found 2"
   Debug: Check FacetStyleCoordinator registration
   Fix: Ensure all dimension values registered before plotting
   ```

   **Missing Subplots**:
   ```
   Failure: "Expected subplot at (1,2) not found" 
   Debug: Check data filtering and subplot creation logic
   Fix: Verify data subsetting creates expected combinations
   ```

   **Legend Issues**:
   ```
   Failure: "Expected 1 legend, found 0"
   Debug: Check FigureManager legend configuration
   Fix: Ensure legend strategy properly configured
   ```

3. **Issue Resolution Process**:
   - **Identify root cause** using verification decorator diagnostic output
   - **Fix underlying implementation** in faceting system
   - **Re-run test** to confirm fix resolves issue
   - **Document fix** for future reference
   - **Proceed only after test passes**

## Advanced Testing Scenarios

### **Performance Testing Implementation**

#### **Large Dataset Performance Test**:
```python
@verify_plot(
    expected_legends=0,
    expected_channels="sparse_check",  # Sample subset for efficiency
    tolerance=0.1
)
def test_large_dataset_performance():
    import time
    
    # Generate large dataset as specified in test plan
    large_data = create_synthetic_faceting_data(
        n_points=100000,
        metrics=["loss", "acc", "f1", "precision"],
        datasets=["train", "val", "test"] * 10,  # 30 datasets  
        models=["A", "B", "C", "D", "E"]
    )
    
    # Measure performance
    start_time = time.time()
    
    config = FacetingConfig(rows="metric", cols="dataset", lines="model", x="step", y="value")
    with FigureManager(figure=FigureConfig(rows=4, cols=30)) as fm:
        fm.plot_faceted(data=large_data, plot_type="line", faceting=config)
        result = fm.fig
    
    execution_time = time.time() - start_time
    
    # Performance requirement: < 30 seconds (from test plan)
    assert execution_time < 30.0, f"Performance regression: {execution_time}s > 30s"
    
    return result
```

### **Regression Testing Implementation**

#### **Color Consistency Regression Test**:
```python
def test_color_consistency_regression():
    # Create identical test data
    data = create_reference_dataset()  # Exactly reproducible data
    config = FacetingConfig(rows="metric", cols="dataset", lines="model", x="step", y="value")
    
    # Extract colors from simplified implementation
    with FigureManager(figure=FigureConfig(rows=2, cols=3)) as fm:
        fm.plot_faceted(data=data, plot_type="line", faceting=config)
        current_colors = extract_all_subplot_colors(fm.fig)
    
    # Compare to reference colors (captured separately)
    reference_colors = load_reference_color_data()  # From baseline measurement
    
    # Verify exact match (tolerance=0.0 for regression)
    assert current_colors == reference_colors, "Color assignments changed after simplification"
```

## Quality Assurance and Evidence Requirements

### **Evidence Documentation Standards**

#### **For Each Successful Test**:
1. **Verification decorator output** - Full success messages
2. **Property extraction results** - Color, marker, legend analysis
3. **Performance metrics** - Execution time, memory usage if applicable
4. **Visual evidence** - Screenshots or saved plots for complex tests

#### **For Overall Test Suite**:
1. **Test execution summary** - Pass/fail counts, total duration
2. **Coverage analysis** - Which faceting capabilities were verified
3. **Performance comparison** - Simplified vs. reference benchmarks
4. **Issue resolution log** - Problems found and solutions applied

### **Final Verification Report Format**

**Create**: `docs/projects/active/architectural_simplification/verification_results/phase4b_execution_report.md`

**Required Sections**:
```markdown
# Phase 4B Verification Execution Report

## Executive Summary
- **Total Tests**: X/35 passed
- **Execution Time**: X hours over Y days  
- **Performance**: Simplified system X% faster than baseline
- **Issues Found**: N issues identified and resolved

## Test Category Results
### Core Functionality (Priority 1)
- Basic 2D Faceting: ✅ PASSED - [evidence summary]
- Single Dimension Faceting: ✅ PASSED - [evidence summary]  
- All Plot Types Integration: ✅ PASSED - [evidence summary]
- Color Consistency Regression: ✅ PASSED - [evidence summary]

### [Continue for all categories...]

## Performance Analysis
- **Baseline Execution**: Reference time measurements
- **Simplified Performance**: Current implementation measurements  
- **Performance Improvement**: X% faster due to simplification
- **Memory Usage**: Y% reduction in memory consumption

## Issues Discovered and Resolved
### Issue 1: [Description]
- **Test**: Which test discovered the issue
- **Symptom**: Verification decorator error message
- **Root Cause**: Technical analysis of the problem
- **Solution**: Code changes made to fix issue
- **Resolution**: Test now passes with evidence

## Quality Assurance Summary
- **Objective Verification**: All tests use verification decorators
- **No Subjective Assessment**: Every result measured objectively
- **Comprehensive Coverage**: All faceting capabilities verified
- **Regression Prevention**: Simplified system maintains all functionality

## Conclusion and Recommendations
- **System Status**: Simplified faceting system fully verified
- **Confidence Level**: High - objective measurement confirms functionality
- **Next Steps**: System ready for production use
- **Future Testing**: Recommendations for ongoing verification
```

## Success Criteria

### **Phase 4B Completion Requirements**

#### **All Tests Must Pass** ✅
- **35/35 test cases** execute successfully with verification decorator confirmation
- **No subjective "looks good"** assessments - only objective measurement results
- **All sophisticated functionality** (multi-variable faceting, style coordination, advanced targeting) verified working
- **Performance maintained or improved** compared to pre-simplification baseline

#### **Documentation Complete** ✅  
- **Individual test results** documented with evidence
- **Overall execution report** completed with analysis and insights
- **Issue resolution log** shows problems found and fixed
- **Performance benchmarks** demonstrate improvement from simplification

#### **System Integration Verified** ✅
- **All existing examples** work identically after simplification
- **FigureManager integration** preserved and functional
- **Legend system coordination** maintained
- **Theme integration** consistent across different visual styles

## Critical Success Factors

### **Systematic Execution Discipline**
- **One test at a time** - complete each fully before advancing
- **Fix issues immediately** - do not accumulate technical debt
- **Document everything** - evidence and insights for each test
- **Objective measurement only** - no subjective visual assessment

### **Quality Through Verification**
- **Trust verification decorators** - they provide objective measurement
- **Use diagnostic output** - detailed failure analysis guides debugging  
- **Demand passing tests** - do not proceed on failing tests
- **Maintain evidence** - documentation proves system works correctly

### **Performance-Aware Verification**
- **Measure execution time** for performance regression detection
- **Monitor memory usage** for resource efficiency verification
- **Compare to baselines** for improvement confirmation
- **Document improvements** achieved through simplification

---

**Key Implementation Principle**: Execute the test plan **exactly as specified** using verification decorators for **objective measurement**. The simplified faceting system must **prove its correctness** through systematic verification, not hope through visual inspection.

**Critical Success Factor**: This phase transforms the faceting system from "probably works" to "proven to work correctly" through comprehensive objective verification.