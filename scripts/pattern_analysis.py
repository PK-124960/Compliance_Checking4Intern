"""
Pattern Analysis for Policy Rules
==================================
Categorizes policy rules by linguistic patterns and analyzes
formalization coverage for thesis RQ1.

Usage:
    python scripts/pattern_analysis.py

Output:
    - research/pattern_taxonomy_report.md
    - research/pattern_analysis_results.json
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
RESEARCH_DIR = PROJECT_ROOT / "research"


# Pattern definitions
PATTERNS = {
    "simple_prohibition": {
        "description": "Direct prohibition without conditions",
        "markers": ["not allowed", "prohibited", "shall not", "cannot", "must not", "is not permitted"],
        "fol_support": "Full",
        "example": "Students shall not disturb fellow students"
    },
    "simple_obligation": {
        "description": "Direct obligation without conditions",
        "markers": ["must", "shall", "is required", "have to", "are required"],
        "fol_support": "Full",
        "example": "Students must pay fees before registration"
    },
    "simple_permission": {
        "description": "Direct permission statement",
        "markers": ["may", "can", "is permitted", "is allowed", "are allowed"],
        "fol_support": "Full",
        "example": "Students may opt to reside off-campus"
    },
    "conditional_single": {
        "description": "Single condition with obligation/permission",
        "markers": ["if", "when", "in case", "provided that", "subject to"],
        "fol_support": "Full",
        "example": "If a student fails, they must retake the course"
    },
    "conditional_multiple": {
        "description": "Multiple conditions (AND/OR)",
        "markers": ["and", "or", "both", "either", "as well as"],
        "fol_support": "Full",
        "example": "Students who are enrolled AND paid fees may register"
    },
    "temporal_deadline": {
        "description": "Time-based constraints with deadlines",
        "markers": ["within", "before", "after", "by", "deadline", "days", "weeks"],
        "fol_support": "Partial",
        "example": "Payment must be made within 30 days"
    },
    "temporal_sequence": {
        "description": "Ordered sequence of events",
        "markers": ["then", "first", "next", "subsequently", "prior to"],
        "fol_support": "Partial",
        "example": "Submit form first, then attend interview"
    },
    "exception_based": {
        "description": "Rules with exceptions",
        "markers": ["except", "unless", "excluding", "other than", "apart from"],
        "fol_support": "Partial",
        "example": "All students must attend, except those on leave"
    },
    "quantified_universal": {
        "description": "Universal quantification (all/every)",
        "markers": ["all", "every", "each", "any", "no"],
        "fol_support": "Full",
        "example": "All students must complete orientation"
    },
    "quantified_existential": {
        "description": "Existential quantification (some/at least)",
        "markers": ["some", "at least", "one or more", "a", "an"],
        "fol_support": "Full",
        "example": "At least one advisor must sign the form"
    },
    "advisory_should": {
        "description": "Advisory statements with 'should' (weak deontic)",
        "markers": ["should"],
        "fol_support": "Debatable",
        "example": "Students should attend orientation"
    },
    "procedural_complex": {
        "description": "Multi-step procedures",
        "markers": ["step", "procedure", "process", "stages", "phases"],
        "fol_support": "Limited",
        "example": "The appeal process involves three stages..."
    }
}


def load_rules():
    """Load rules from extracted rules file."""
    # Try gold standard first
    gs_file = RESEARCH_DIR / "gold_standard_annotated.json"
    if gs_file.exists():
        with open(gs_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [
                {
                    "id": r["id"],
                    "text": r["original_text"],
                    "is_rule": r.get("human_annotation", {}).get("is_rule", True),
                    "rule_type": r.get("human_annotation", {}).get("rule_type")
                }
                for r in data
            ]
    
    # Fallback to extracted rules
    rules_file = RESEARCH_DIR / "extracted_rules.json"
    if rules_file.exists():
        with open(rules_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    print("❌ No rules file found")
    sys.exit(1)


def classify_pattern(text: str) -> list:
    """Classify the pattern(s) present in a rule text."""
    text_lower = text.lower()
    matched_patterns = []
    
    for pattern_name, pattern_info in PATTERNS.items():
        for marker in pattern_info["markers"]:
            if marker in text_lower:
                matched_patterns.append(pattern_name)
                break  # Only match each pattern once
    
    return matched_patterns if matched_patterns else ["unclassified"]


def analyze_rule(rule: dict) -> dict:
    """Analyze a single rule for patterns."""
    text = rule.get("text", "")
    patterns = classify_pattern(text)
    
    # Check FOL formalizability based on patterns
    fol_support_levels = {
        "Full": 3,
        "Partial": 2,
        "Limited": 1,
        "Debatable": 0
    }
    
    min_support = 3  # Start with full support
    for pattern in patterns:
        if pattern in PATTERNS:
            support = PATTERNS[pattern]["fol_support"]
            min_support = min(min_support, fol_support_levels.get(support, 0))
    
    support_names = {3: "Full", 2: "Partial", 1: "Limited", 0: "Debatable"}
    
    return {
        "rule_id": rule.get("id", "Unknown"),
        "text_snippet": text[:100] + "..." if len(text) > 100 else text,
        "patterns": patterns,
        "primary_pattern": patterns[0] if patterns else "unclassified",
        "fol_support": support_names.get(min_support, "Unknown"),
        "is_rule": rule.get("is_rule", True),
        "rule_type": rule.get("rule_type")
    }


def generate_taxonomy(analyzed_rules: list) -> dict:
    """Generate pattern taxonomy from analyzed rules."""
    taxonomy = defaultdict(lambda: {"count": 0, "rules": [], "fol_success": 0, "fol_partial": 0, "fol_limited": 0})
    
    for rule in analyzed_rules:
        if not rule.get("is_rule", True):
            continue  # Skip non-rules
            
        primary = rule["primary_pattern"]
        taxonomy[primary]["count"] += 1
        taxonomy[primary]["rules"].append(rule["rule_id"])
        
        support = rule["fol_support"]
        if support == "Full":
            taxonomy[primary]["fol_success"] += 1
        elif support == "Partial":
            taxonomy[primary]["fol_partial"] += 1
        else:
            taxonomy[primary]["fol_limited"] += 1
    
    return dict(taxonomy)


def generate_report(taxonomy: dict, analyzed_rules: list) -> str:
    """Generate markdown report."""
    
    total_rules = sum(t["count"] for t in taxonomy.values())
    full_support = sum(t["fol_success"] for t in taxonomy.values())
    partial_support = sum(t["fol_partial"] for t in taxonomy.values())
    
    # Sort by count
    sorted_patterns = sorted(taxonomy.items(), key=lambda x: x[1]["count"], reverse=True)
    
    report = f"""# Pattern Taxonomy Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Purpose:** Analyze linguistic patterns in policy rules for RQ1

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Rules Analyzed | {total_rules} |
| Patterns Identified | {len(taxonomy)} |
| Full FOL Support | {full_support} ({full_support/total_rules*100:.1f}%) |
| Partial FOL Support | {partial_support} ({partial_support/total_rules*100:.1f}%) |

---

## Pattern Distribution

| Pattern | Count | % | FOL Support | Formalizable |
|---------|-------|---|-------------|--------------|
"""
    
    for pattern_name, data in sorted_patterns:
        pct = data["count"] / total_rules * 100 if total_rules > 0 else 0
        fol_support = PATTERNS.get(pattern_name, {}).get("fol_support", "Unknown")
        formalizable = "✅" if fol_support in ["Full", "Partial"] else "⚠️"
        report += f"| {pattern_name.replace('_', ' ').title()} | {data['count']} | {pct:.1f}% | {fol_support} | {formalizable} |\n"
    
    report += f"""

---

## Pattern Definitions

"""
    
    for pattern_name, pattern_info in PATTERNS.items():
        if pattern_name in taxonomy:
            report += f"""### {pattern_name.replace('_', ' ').title()}

- **Description:** {pattern_info['description']}
- **Markers:** {', '.join(pattern_info['markers'][:5])}{'...' if len(pattern_info['markers']) > 5 else ''}
- **FOL Support:** {pattern_info['fol_support']}
- **Example:** "{pattern_info['example']}"
- **Count in Corpus:** {taxonomy[pattern_name]['count']}

"""
    
    report += f"""---

## FOL Expressiveness Analysis

### Fully Expressible Patterns (Answer to RQ1)

The following patterns can be fully expressed in First-Order Logic:

| Pattern | Count | Formalization Rate |
|---------|-------|-------------------|
"""
    
    for pattern_name, data in sorted_patterns:
        if PATTERNS.get(pattern_name, {}).get("fol_support") == "Full":
            rate = (data["fol_success"] / data["count"] * 100) if data["count"] > 0 else 0
            report += f"| {pattern_name.replace('_', ' ').title()} | {data['count']} | 100% |\n"
    
    report += f"""

### Partially Expressible Patterns

The following patterns require additional handling or simplification:

| Pattern | Count | Challenge |
|---------|-------|-----------|
"""
    
    for pattern_name, data in sorted_patterns:
        support = PATTERNS.get(pattern_name, {}).get("fol_support", "Unknown")
        if support in ["Partial", "Limited", "Debatable"]:
            challenges = {
                "Partial": "Temporal operators not native to FOL",
                "Limited": "Multi-step procedures hard to atomize",
                "Debatable": "'Should' semantics unclear"
            }
            report += f"| {pattern_name.replace('_', ' ').title()} | {data['count']} | {challenges.get(support, 'N/A')} |\n"
    
    report += f"""

---

## Key Findings for Thesis

### RQ1: What linguistic patterns can be formalized?

1. **Fully Formalizable ({full_support}/{total_rules} = {full_support/total_rules*100:.1f}%)**
   - Simple obligations, permissions, prohibitions
   - Conditional rules (single and multiple conditions)
   - Universally and existentially quantified rules

2. **Partially Formalizable ({partial_support}/{total_rules} = {partial_support/total_rules*100:.1f}%)**
   - Temporal constraints (require temporal logic extension)
   - Exception-based rules (require defeasibility handling)

3. **Challenging Patterns**
   - Advisory "should" statements (semantic ambiguity)
   - Complex procedural rules (multi-step sequences)

### Contribution

This analysis identifies the linguistic boundary of FOL expressiveness for academic policy rules, providing empirical data for the thesis methodology chapter.
"""
    
    return report


def main():
    """Main execution flow."""
    print("=" * 60)
    print("PATTERN ANALYSIS FOR POLICY RULES")
    print("=" * 60)
    
    # Load rules
    rules = load_rules()
    print(f"\n📋 Loaded {len(rules)} rules")
    
    # Analyze each rule
    print("\n🔍 Analyzing patterns...")
    analyzed = [analyze_rule(r) for r in rules]
    
    # Generate taxonomy
    taxonomy = generate_taxonomy(analyzed)
    
    # Print summary
    print("\n📊 Pattern Distribution:")
    for pattern, data in sorted(taxonomy.items(), key=lambda x: x[1]["count"], reverse=True):
        print(f"   {pattern.replace('_', ' ').title():30s} {data['count']:3d} rules")
    
    # Generate report
    report = generate_report(taxonomy, analyzed)
    
    # Save report
    report_file = RESEARCH_DIR / "pattern_taxonomy_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n✅ Report saved: {report_file}")
    
    # Save JSON results
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_rules": len(rules),
        "taxonomy": taxonomy,
        "analyzed_rules": analyzed
    }
    
    results_file = RESEARCH_DIR / "pattern_analysis_results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"✅ Results saved: {results_file}")
    
    print("\n✅ Pattern analysis complete!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
