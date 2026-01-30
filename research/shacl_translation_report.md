# SHACL Translation Report

**Generated:** 2026-01-29T19:36:39.802512
**Output:** ait_policy_shapes.ttl

## Statistics

| Type | Count |
|------|-------|
| Obligations | 65 |
| Permissions | 17 |
| Prohibitions | 14 |
| Skipped | 0 |
| **Total** | **96** |

## SHACL Features Used

- `sh:NodeShape` for class-level constraints
- `sh:property` for required properties
- `sh:severity` based on deontic type
- `deontic:type` custom property for rule classification

## Usage

```bash
# Validate RDF data against SHACL shapes
pip install pyshacl

# Python validation
from pyshacl import validate
conforms, results_graph, results_text = validate(
    data_graph='your_data.ttl',
    shacl_graph='ait_policy_shapes.ttl'
)
print(results_text)
```

## Next Steps

1. Create test RDF data for validation
2. Run SHACL validation
3. Report compliance results


## Validation Results

**Validated:** 2026-01-31 05:57
**Test Data:** comprehensive_test_data.ttl

### Metrics Summary

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Accuracy | 37.14% | ≥ 95% | ❌ |
| Precision | 20.83% | ≥ 90% | ❌ |
| Recall | 62.5% | ≥ 90% | ❌ |
| F1-Score | 31.25% | ≥ 90% | ❌ |
| False Positive Rate | 70.37% | ≤ 2% | ❌ |
| False Negative Rate | 37.5% | ≤ 1% | ❌ |

### Confusion Matrix

| | Predicted: Pass | Predicted: Violation |
|---|---|---|
| **Actual: Pass** | 8 (TN) | 19 (FP) |
| **Actual: Violation** | 3 (FN) | 5 (TP) |

### Test Entity Results

- **Total Entities Tested:** 35
- **Expected Violations:** 8
- **Detected Violations:** 24
- **Correctly Matched:** 5
