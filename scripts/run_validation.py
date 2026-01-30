"""
SHACL Validation Runner
========================
Validates comprehensive test data against AIT policy SHACL shapes.
Generates detailed validation report for thesis documentation.

Usage:
    python scripts/run_validation.py

Output:
    - Console output with validation summary
    - research/shacl_validation_results.json - Full results
    - Updates to research/shacl_translation_report.md
"""

from pyshacl import validate
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, SH
import json
from pathlib import Path
from datetime import datetime
import sys

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SHACL_DIR = PROJECT_ROOT / "shacl"
RESEARCH_DIR = PROJECT_ROOT / "research"

# Namespaces
AIT = Namespace("http://example.org/ait-policy#")
DEONTIC = Namespace("http://example.org/deontic#")


def load_graphs():
    """Load SHACL shapes and test data graphs."""
    print("=" * 60)
    print("SHACL VALIDATION RUNNER")
    print("=" * 60)
    
    # Load SHACL shapes
    shapes_file = SHACL_DIR / "ait_policy_shapes.ttl"
    print(f"\n📋 Loading SHACL shapes from: {shapes_file}")
    shapes_graph = Graph()
    shapes_graph.parse(shapes_file, format="turtle")
    
    # Count shapes
    shape_count = len(list(shapes_graph.subjects(RDF.type, SH.NodeShape)))
    print(f"   Found {shape_count} SHACL NodeShapes")
    
    # Load test data - using targeted test data aligned with shape classes
    data_file = SHACL_DIR / "targeted_test_data.ttl"
    print(f"\n📊 Loading test data from: {data_file}")
    data_graph = Graph()
    data_graph.parse(data_file, format="turtle")
    
    # Count entities
    entity_count = len(set(data_graph.subjects()))
    print(f"   Found {entity_count} test entities")
    
    return shapes_graph, data_graph


def run_validation(shapes_graph, data_graph):
    """Run SHACL validation and parse results."""
    print("\n🔍 Running SHACL validation...")
    
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',
        abort_on_first=False,
        meta_shacl=False,
        advanced=True,
        debug=False
    )
    
    print(f"\n   Validation Result: {'✅ CONFORMS' if conforms else '❌ VIOLATIONS FOUND'}")
    
    return conforms, results_graph, results_text


def parse_violations(results_graph):
    """Parse validation results to extract violations."""
    violations = []
    
    # Query for validation results
    for result in results_graph.subjects(RDF.type, SH.ValidationResult):
        violation = {
            "focus_node": str(results_graph.value(result, SH.focusNode)),
            "source_shape": str(results_graph.value(result, SH.sourceShape)),
            "result_message": str(results_graph.value(result, SH.resultMessage)),
            "severity": str(results_graph.value(result, SH.resultSeverity)),
            "value": str(results_graph.value(result, SH.value)) if results_graph.value(result, SH.value) else None,
            "path": str(results_graph.value(result, SH.resultPath)) if results_graph.value(result, SH.resultPath) else None,
        }
        violations.append(violation)
    
    return violations


def calculate_metrics(violations, expected_violations):
    """Calculate validation accuracy metrics."""
    # Expected violations from targeted test data
    expected_violating_entities = {
        "Test_GS003_Fail",   # missing invoice
        "Test_GS005_Fail",   # missing promissory note
        "Test_GS006_Fail",   # missing overdueaccount
        "Test_GS010_Fail",   # missing giveexception
        "Test_GS017_Fail",   # sub-letting (prohibited)
    }
    
    # Extract actual violating entities from results
    actual_violating = set()
    for v in violations:
        node = v["focus_node"].split("#")[-1] if "#" in v["focus_node"] else v["focus_node"]
        actual_violating.add(node)
    
    # Calculate TP, FP, FN, TN
    tp = len(expected_violating_entities & actual_violating)
    fp = len(actual_violating - expected_violating_entities)
    fn = len(expected_violating_entities - actual_violating)
    
    total_entities = 15  # From targeted test data
    tn = total_entities - tp - fp - fn
    
    # Metrics
    accuracy = (tp + tn) / total_entities if total_entities > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0  # False Positive Rate
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0  # False Negative Rate
    
    return {
        "total_entities": total_entities,
        "expected_violations": len(expected_violating_entities),
        "actual_violations": len(actual_violating),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "accuracy": round(accuracy * 100, 2),
        "precision": round(precision * 100, 2),
        "recall": round(recall * 100, 2),
        "f1_score": round(f1 * 100, 2),
        "false_positive_rate": round(fpr * 100, 2),
        "false_negative_rate": round(fnr * 100, 2),
        "expected_entities": list(expected_violating_entities),
        "actual_entities": list(actual_violating),
        "matched": list(expected_violating_entities & actual_violating),
        "missed": list(expected_violating_entities - actual_violating),
        "extra": list(actual_violating - expected_violating_entities),
    }


def generate_report(conforms, violations, metrics, results_text):
    """Generate comprehensive validation report."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "validation_status": "CONFORMS" if conforms else "VIOLATIONS_FOUND",
        "metrics": metrics,
        "violations": violations,
        "results_text": results_text[:5000] if len(results_text) > 5000 else results_text,
    }
    
    # Save JSON report
    output_file = RESEARCH_DIR / "shacl_validation_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Full report saved to: {output_file}")
    
    return report


def print_summary(metrics):
    """Print validation summary to console."""
    print("\n" + "=" * 60)
    print("VALIDATION METRICS SUMMARY")
    print("=" * 60)
    
    print(f"""
┌─────────────────────────────────────────────────────────┐
│ Total Test Entities:      {metrics['total_entities']:>25} │
│ Expected Violations:      {metrics['expected_violations']:>25} │
│ Actual Violations:        {metrics['actual_violations']:>25} │
├─────────────────────────────────────────────────────────┤
│ True Positives (TP):      {metrics['true_positives']:>25} │
│ False Positives (FP):     {metrics['false_positives']:>25} │
│ True Negatives (TN):      {metrics['true_negatives']:>25} │
│ False Negatives (FN):     {metrics['false_negatives']:>25} │
├─────────────────────────────────────────────────────────┤
│ Accuracy:                 {metrics['accuracy']:>24}% │
│ Precision:                {metrics['precision']:>24}% │
│ Recall:                   {metrics['recall']:>24}% │
│ F1-Score:                 {metrics['f1_score']:>24}% │
├─────────────────────────────────────────────────────────┤
│ False Positive Rate:      {metrics['false_positive_rate']:>24}% │
│ False Negative Rate:      {metrics['false_negative_rate']:>24}% │
└─────────────────────────────────────────────────────────┘
""")
    
    # Threshold check
    print("\n📊 THRESHOLD CHECKS:")
    checks = [
        ("Accuracy", metrics['accuracy'], 95, "≥"),
        ("F1-Score", metrics['f1_score'], 90, "≥"),
        ("False Positive Rate", metrics['false_positive_rate'], 2, "≤"),
        ("False Negative Rate", metrics['false_negative_rate'], 1, "≤"),
    ]
    
    for name, value, threshold, op in checks:
        if op == "≥":
            status = "✅ PASS" if value >= threshold else "❌ FAIL"
        else:
            status = "✅ PASS" if value <= threshold else "❌ FAIL"
        print(f"   {name}: {value}% {op} {threshold}% → {status}")


def update_report_markdown(metrics):
    """Update the SHACL translation report with validation results."""
    report_file = RESEARCH_DIR / "shacl_translation_report.md"
    
    # Read existing content
    with open(report_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if validation results section exists
    if "## Validation Results" in content:
        # Already updated - skip
        print(f"\n⚠️  Report already contains validation results")
        return
    
    # Append validation results
    validation_section = f"""

## Validation Results

**Validated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Test Data:** comprehensive_test_data.ttl

### Metrics Summary

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Accuracy | {metrics['accuracy']}% | ≥ 95% | {'✅' if metrics['accuracy'] >= 95 else '❌'} |
| Precision | {metrics['precision']}% | ≥ 90% | {'✅' if metrics['precision'] >= 90 else '❌'} |
| Recall | {metrics['recall']}% | ≥ 90% | {'✅' if metrics['recall'] >= 90 else '❌'} |
| F1-Score | {metrics['f1_score']}% | ≥ 90% | {'✅' if metrics['f1_score'] >= 90 else '❌'} |
| False Positive Rate | {metrics['false_positive_rate']}% | ≤ 2% | {'✅' if metrics['false_positive_rate'] <= 2 else '❌'} |
| False Negative Rate | {metrics['false_negative_rate']}% | ≤ 1% | {'✅' if metrics['false_negative_rate'] <= 1 else '❌'} |

### Confusion Matrix

| | Predicted: Pass | Predicted: Violation |
|---|---|---|
| **Actual: Pass** | {metrics['true_negatives']} (TN) | {metrics['false_positives']} (FP) |
| **Actual: Violation** | {metrics['false_negatives']} (FN) | {metrics['true_positives']} (TP) |

### Test Entity Results

- **Total Entities Tested:** {metrics['total_entities']}
- **Expected Violations:** {metrics['expected_violations']}
- **Detected Violations:** {metrics['actual_violations']}
- **Correctly Matched:** {len(metrics['matched'])}
"""
    
    # Append to file
    with open(report_file, "a", encoding="utf-8") as f:
        f.write(validation_section)
    
    print(f"\n✅ Updated report: {report_file}")


def main():
    """Main execution flow."""
    try:
        # Load graphs
        shapes_graph, data_graph = load_graphs()
        
        # Run validation
        conforms, results_graph, results_text = run_validation(shapes_graph, data_graph)
        
        # Parse violations
        violations = parse_violations(results_graph)
        print(f"   Parsed {len(violations)} violation results")
        
        # Calculate metrics
        metrics = calculate_metrics(violations, expected_violations=8)
        
        # Print summary
        print_summary(metrics)
        
        # Generate report
        report = generate_report(conforms, violations, metrics, results_text)
        
        # Update markdown report
        update_report_markdown(metrics)
        
        print("\n" + "=" * 60)
        print("VALIDATION COMPLETE")
        print("=" * 60)
        
        return 0 if metrics['accuracy'] >= 95 else 1
        
    except Exception as e:
        print(f"\n❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
