#!/usr/bin/env python3
"""
FOL to SHACL Translation Script
Converts FOL formalizations to SHACL shapes for RDF validation.

Usage:
    python scripts/fol_to_shacl.py
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
RESEARCH_DIR = PROJECT_ROOT / "research"
SHACL_DIR = PROJECT_ROOT / "shacl"

# SHACL Prefixes
PREFIXES = """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix ait: <http://example.org/ait-policy#> .
@prefix deontic: <http://example.org/deontic#> .
"""

# Deontic to SHACL mapping
DEONTIC_SEVERITY = {
    "obligation": "sh:Violation",
    "prohibition": "sh:Violation", 
    "permission": "sh:Info"
}


def normalize_predicate(pred: str) -> str:
    """Convert FOL predicate to valid SHACL identifier."""
    # Remove special characters
    pred = re.sub(r'[\\(){}[\],;:\"\'<>]', '', pred)
    # Convert to CamelCase
    words = re.split(r'[\s_-]+', pred)
    return ''.join(word.capitalize() for word in words if word)


def extract_predicates(formula: str) -> List[str]:
    """Extract predicate names from FOL formula."""
    # Match CamelCase or snake_case identifiers followed by (
    pattern = r'([A-Za-z][A-Za-z0-9_]*)\s*\('
    matches = re.findall(pattern, formula)
    # Filter out FOL operators
    operators = {'forall', 'exists', 'O', 'P', 'F', 'implies', 'and', 'or', 'not', 'if', 'then', 'Within', 'Before'}
    return list(set(m for m in matches if m not in operators))


def fol_to_shacl_shape(rule: Dict, index: int) -> str:
    """Convert a single FOL rule to SHACL shape."""
    rule_id = rule.get('id', f'Rule{index}')
    fol = rule.get('fol_formalization', {})
    
    if not fol or 'error' in fol:
        return f"# {rule_id}: Skipped (error in FOL)\n"
    
    deontic_type = fol.get('deontic_type', 'obligation')
    formula = fol.get('deontic_formula', '')
    expansion = fol.get('fol_expansion', '')
    original_text = rule.get('original_text', '')[:100]
    
    # Extract main subject/class
    predicates = extract_predicates(formula + ' ' + expansion)
    main_class = predicates[0] if predicates else 'Thing'
    
    # Get severity based on deontic type
    severity = DEONTIC_SEVERITY.get(deontic_type, 'sh:Warning')
    
    # Build SHACL shape
    shape_name = f"ait:{normalize_predicate(rule_id)}Shape"
    
    shape = f"""
# ===========================================
# {rule_id}: {deontic_type.upper()}
# Original: "{original_text}..."
# FOL: {formula[:80]}...
# ===========================================
{shape_name} a sh:NodeShape ;
    sh:targetClass ait:{normalize_predicate(main_class)} ;
    rdfs:label "{rule_id}" ;
    rdfs:comment "{original_text.replace('"', "'")}" ;
    deontic:type deontic:{deontic_type} ;
    sh:severity {severity} ;
"""
    
    # Add property constraints based on predicates
    for i, pred in enumerate(predicates[1:4], 1):  # Limit to first 3 predicates
        normalized = normalize_predicate(pred)
        shape += f"""    sh:property [
        sh:path ait:{normalized.lower()} ;
        sh:name "{pred}" ;
        sh:minCount 1 ;
    ] """
        if i < min(len(predicates) - 1, 3):
            shape += ";\n"
        else:
            shape += ".\n"
    
    if not predicates[1:4]:
        shape = shape.rstrip(' ;\n') + ".\n"
    
    return shape


def generate_shacl_shapes(results_file: Path) -> str:
    """Generate SHACL shapes from FOL results."""
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    shapes = PREFIXES + "\n"
    shapes += f"# Generated: {datetime.now().isoformat()}\n"
    shapes += f"# Source: {results_file.name}\n"
    shapes += f"# Total Rules: {len(results['formalized_rules'])}\n\n"
    
    # Add ontology header
    shapes += """
# ===========================================
# AIT Policy Ontology
# ===========================================
ait:PolicyOntology a owl:Ontology ;
    rdfs:label "AIT Policy Rules as SHACL" ;
    rdfs:comment "SHACL shapes generated from FOL formalizations" .

# Deontic Types
deontic:obligation a rdfs:Class .
deontic:permission a rdfs:Class .
deontic:prohibition a rdfs:Class .

"""
    
    # Statistics
    stats = {"obligation": 0, "permission": 0, "prohibition": 0, "skipped": 0}
    
    for i, rule in enumerate(results['formalized_rules'], 1):
        fol = rule.get('fol_formalization', {})
        if 'error' in fol:
            stats['skipped'] += 1
            continue
        
        dtype = fol.get('deontic_type', 'obligation')
        if dtype in stats:
            stats[dtype] += 1
        
        shapes += fol_to_shacl_shape(rule, i)
    
    # Add summary at end
    shapes += f"""
# ===========================================
# SUMMARY
# ===========================================
# Obligations: {stats['obligation']}
# Permissions: {stats['permission']}
# Prohibitions: {stats['prohibition']}
# Skipped: {stats['skipped']}
# ===========================================
"""
    
    return shapes, stats


def generate_shacl_report(stats: Dict, output_file: Path) -> str:
    """Generate markdown report for SHACL translation."""
    report = f"""# SHACL Translation Report

**Generated:** {datetime.now().isoformat()}
**Output:** {output_file.name}

## Statistics

| Type | Count |
|------|-------|
| Obligations | {stats['obligation']} |
| Permissions | {stats['permission']} |
| Prohibitions | {stats['prohibition']} |
| Skipped | {stats['skipped']} |
| **Total** | **{sum(stats.values())}** |

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
"""
    return report


def main():
    print("=" * 60)
    print("FOL TO SHACL TRANSLATION")
    print("=" * 60)
    
    # Create SHACL directory
    SHACL_DIR.mkdir(exist_ok=True)
    
    # Find FOL results file
    results_file = RESEARCH_DIR / "fol_formalization_v2_results.json"
    if not results_file.exists():
        results_file = RESEARCH_DIR / "fol_formalization_results.json"
    
    if not results_file.exists():
        print(f"Error: No FOL results found in {RESEARCH_DIR}")
        return
    
    print(f"Reading: {results_file}")
    
    # Generate SHACL shapes
    shapes, stats = generate_shacl_shapes(results_file)
    
    # Save SHACL file
    output_file = SHACL_DIR / "ait_policy_shapes.ttl"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(shapes)
    print(f"✅ SHACL shapes saved: {output_file}")
    
    # Generate report
    report = generate_shacl_report(stats, output_file)
    report_file = RESEARCH_DIR / "shacl_translation_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"📝 Report saved: {report_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for dtype, count in stats.items():
        print(f"  {dtype.title()}: {count}")
    print("=" * 60)


if __name__ == "__main__":
    main()
