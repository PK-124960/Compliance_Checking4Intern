# SHACL Validation Findings Report

**Generated:** 2026-01-31
**Purpose:** Document SHACL validation results and findings for thesis

---

## Executive Summary

The SHACL validation testing revealed important findings about the automated FOL-to-SHACL translation process:

1. **SHACL shapes are syntactically valid** - All 96 shapes parse correctly
2. **Constraint detection works** - Missing properties are correctly flagged as violations
3. **Key finding**: Auto-generated shapes require refinement for production deployment

---

## Validation Configuration

| Parameter | Value |
|-----------|-------|
| SHACL Shapes File | `shacl/ait_policy_shapes.ttl` |
| Test Data File | `shacl/targeted_test_data.ttl` |
| Total Shapes | 96 |
| Total Test Entities | 15 (targeted) |
| Validation Engine | pyshacl 0.31.0 |

---

## Validation Results

### Metrics Summary

| Metric | Value | Target | Analysis |
|--------|-------|--------|----------|
| Matched Violations | 4/5 | 5/5 | 80% recall on expected failures |
| False Positives | 4 | 0 | Due to broad target classes |
| Accuracy | 66.67% | ≥95% | Below target - see analysis |

### Correctly Detected Violations

| Test Case | Rule ID | Violation Type | Status |
|-----------|---------|----------------|--------|
| Test_GS003_Fail | GS-003 | Missing invoice | ✅ Detected |
| Test_GS005_Fail | GS-005 | Missing promissory note | ✅ Detected |
| Test_GS006_Fail | GS-006 | Missing overdue account link | ✅ Detected |
| Test_GS010_Fail | GS-010 | Missing exception flag | ✅ Detected |

### Missed Violation

| Test Case | Rule ID | Reason |
|-----------|---------|--------|
| Test_GS017_Fail | GS-017 | No mandatory property requirement in shape |

---

## Key Finding: Target Class Granularity

### Issue Identified

The automated FOL-to-SHACL translation creates shapes with broad target classes that match more entities than intended.

**Example:**

```turtle
# Generated shape targets all Students
ait:Gs014Shape a sh:NodeShape ;
    sh:targetClass ait:Student ;  # Matches ALL students
    sh:property [ sh:path ait:putnameonwaitinglist ; sh:minCount 1 ] .
```

This causes the shape to require `putnameonwaitinglist` for ALL students, not just those relevant to the waiting list rule.

### Recommended Solution

Use more specific target classes or add `sh:targetNode` for explicit entity targeting:

```turtle
# Improved: Target only waiting list applicants
ait:Gs014Shape a sh:NodeShape ;
    sh:targetClass ait:WaitingListApplicant ;  # Specific class
    sh:property [ sh:path ait:putnameonwaitinglist ; sh:minCount 1 ] .
```

---

## Thesis Implications

### What This Demonstrates

1. **RQ3 Answer**: FOL CAN be translated to SHACL (✅ 100% syntactic success)
2. **Limitation Found**: Automated translation produces shapes that require semantic review
3. **Value Added**: Identifies specific improvement needed for production deployment

### Contribution

This finding contributes to the thesis by:

- Quantifying the gap between automated and production-ready shapes
- Identifying specific patterns that cause false positives
- Proposing refinement strategies for shape target classes

---

## Technical Details

### Validation Command

```bash
python scripts/run_validation.py
```

### Output Files

- `research/shacl_validation_results.json` - Full JSON results
- `research/shacl_translation_report.md` - Updated with findings

### Test Data Structure

- 10 expected PASS entities (aligned with shape target classes)
- 5 expected VIOLATE entities (intentionally missing properties)

---

## Recommendations for Future Work

1. **Ontology Design**: Create more granular class hierarchy for policy entities
2. **Shape Refinement**: Review auto-generated shapes and adjust target classes
3. **Closed World Assumption**: Consider using `sh:closed true` for stricter validation
4. **SHACL-SPARQL Rules**: Use `sh:sparql` for complex conditional constraints

---

## Conclusion

The SHACL validation testing successfully demonstrates that:

- ✅ The translation pipeline produces syntactically valid SHACL shapes
- ✅ The shapes correctly detect constraint violations
- ⚠️ Automated shapes need human review for optimal target class specificity
- ✅ This finding is valuable for the thesis methodology discussion
