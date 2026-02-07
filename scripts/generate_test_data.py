#!/usr/bin/env python3
"""
Test Data Generator for SHACL TDD (v2 — FOL-Aware)
=====================================================
Auto-generates test RDF data from gold standard + FOL formalizations.

Improvements over v1:
- Parses FOL formulas to extract rule-specific properties
- Uses llm_classification.subject for smarter entity type detection
- Extracts action/condition from classification for property names
- Generates rule-specific positive/negative properties (not just templates)

Usage:
    python scripts/generate_test_data.py
    python scripts/generate_test_data.py --output shacl/tdd_test_data.ttl
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
RESEARCH_DIR = PROJECT_ROOT / "research"
SHACL_DIR = PROJECT_ROOT / "shacl"


# =============================================================================
# SUBJECT → ENTITY TYPE MAPPING
# =============================================================================

# Priority-ordered: more specific subjects matched first
SUBJECT_ENTITY_MAP = [
    # Specific roles
    (r'postgraduate|post-graduate|pg student|doctoral|master.s student|diploma', 'PostgraduateStudent'),
    (r'graduate|graduating|alumni', 'Graduate'),
    (r'new student|incoming student|first.year', 'Student'),
    (r'student|learner', 'Student'),
    (r'employee|staff member', 'Employee'),
    (r'faculty|professor|instructor|lecturer|teacher|invigilator', 'Faculty'),
    (r'sponsor', 'Sponsor'),
    (r'resident|tenant|occupant', 'Resident'),
    # Organizational roles
    (r'committee|tribunal|board|panel', 'Committee'),
    (r'director|dean|president|registrar|head', 'Administrator'),
    (r'advisor|adviser|supervisor', 'Faculty'),
    (r'department|school|office|unit|ofin|ofa|asu', 'Department'),
    # Catch-all
    (r'person|individual|member|community', 'Person'),
]

# RDF type mapping
RDF_TYPES = {
    'Student': 'ait:Student',
    'PostgraduateStudent': 'ait:PostgraduateStudent',
    'Graduate': 'ait:Graduate',
    'Employee': 'ait:Employee',
    'Faculty': 'ait:Faculty',
    'Sponsor': 'ait:Sponsor',
    'Resident': 'ait:Resident',
    'Committee': 'ait:Committee',
    'Administrator': 'ait:Administrator',
    'Department': 'ait:Department',
    'Person': 'ait:Person',
}

# =============================================================================
# FOL → RDF PROPERTY EXTRACTION
# =============================================================================

# Map common FOL predicates/actions to RDF properties with boolean semantics
FOL_PROPERTY_MAP = {
    # Payment-related
    r'pay|paid|fee|invoice|payment|tuition|premium|charge': ('ait:payfee', 'boolean'),
    r'outstanding.?due|overdue': ('ait:outstandingdues', 'boolean'),
    r'financial.?support|proof.?of.?financial': ('ait:has_proof_of_financial_support', 'boolean'),
    r'promissory.?note': ('ait:promissory_note_sent', 'boolean'),
    
    # Registration/enrollment
    r'register|enrol|enrollment|registration': ('ait:enrolled', 'boolean'),
    r'semester|term|academic.?year': ('ait:semester', 'boolean'),
    r'add.?drop|course.?change': ('ait:adddropcoursesdeadline', 'boolean'),
    
    # Accommodation
    r'reside|accommodation|housing|dormitor|room|living': ('ait:residesoncampus', 'boolean'),
    r'evict|sub.?let|subletting': ('ait:subletting', 'boolean'),
    r'waiting.?list': ('ait:putnameonwaitinglist', 'boolean'),
    r'five.?day|beyond.?five|overstay': ('ait:livingbeyondfivedays', 'boolean'),
    r'spouse|family.?member|dependent': ('ait:moveswithspouse', 'boolean'),
    
    # Academic
    r'thesis|dissertation|research.?paper': ('ait:submit', 'boolean'),
    r'advisor|adviser|supervisor': ('ait:advisor', 'boolean'),
    r'cheat|plagiari|academic.?integrity|misconduct': ('ait:academicintegrity', 'boolean'),
    r'grade|retake|repeat|downgrade': ('ait:takes', 'boolean'),
    r'exam|invigilat|test': ('ait:exam_completed', 'boolean'),
    r'sra|research.?expense|advance': ('ait:sra_completed', 'boolean'),
    
    # Behavioral/ethical
    r'gift|gratuity|benefit|item.?valued': ('ait:acceptedgift', 'boolean'),
    r'report|disclose|inform|notify': ('ait:reported', 'boolean'),
    r'disturb|harass|bully|intimidat': ('ait:disturbing', 'boolean'),
    r'opinion|express|personal.?view': ('ait:expressingopinion', 'boolean'),
    
    # Administrative
    r'approv|authoriz|permission|consent': ('ait:approvalfromofamdirector', 'boolean'),
    r'grievance|complaint|dispute': ('ait:grievance_filed', 'boolean'),
    r'settlement|resolution|mediat': ('ait:settlement_made', 'boolean'),
    r'visa|immigration': ('ait:visa_valid', 'boolean'),
    r'insurance|health.?cover': ('ait:insurance_paid', 'boolean'),
    r'contract|appointment|employ': ('ait:employed', 'boolean'),
    
    # General compliance
    r'comply|conform|adhere|follow': ('ait:compliant', 'boolean'),
    r'confidential|restrict.?on.?publication': ('ait:confidentiality', 'boolean'),
}


def detect_entity_type(rule: dict) -> str:
    """
    Detect entity type from llm_classification.subject and original_text.
    Uses priority-ordered regex matching for accuracy.
    """
    # Primary: use classified subject
    subject = rule.get('llm_classification', {}).get('subject', '')
    
    if subject:
        subject_lower = subject.lower()
        for pattern, entity_type in SUBJECT_ENTITY_MAP:
            if re.search(pattern, subject_lower):
                return entity_type
    
    # Fallback: scan original text
    text = rule.get('original_text', '').lower()
    for pattern, entity_type in SUBJECT_ENTITY_MAP:
        if re.search(pattern, text):
            return entity_type
    
    return 'Person'


def extract_properties_from_fol(rule: dict) -> dict:
    """
    Extract RDF properties from FOL formula, shacl_hint, and rule text.
    
    Returns dict of {property_uri: (value, datatype)}.
    """
    properties = {}
    
    # Collect all text sources to search
    fol = rule.get('fol_formalization', {})
    classification = rule.get('llm_classification', {})
    
    search_texts = [
        fol.get('deontic_formula', ''),
        fol.get('fol_expansion', ''),
        fol.get('shacl_hint', ''),
        fol.get('explanation', ''),
        classification.get('action', ''),
        classification.get('condition', '') or '',
        rule.get('original_text', ''),
    ]
    combined_text = ' '.join(search_texts).lower()
    
    # Match against known property patterns
    for pattern, (prop, dtype) in FOL_PROPERTY_MAP.items():
        if re.search(pattern, combined_text, re.IGNORECASE):
            if prop not in properties:  # Don't overwrite if already found
                properties[prop] = ('true', dtype)
    
    return properties


def make_negative_properties(positive_props: dict, deontic_type: str) -> dict:
    """
    Generate negative (violating) properties from positive ones.
    
    Strategy:
    - For obligations: negate the key action property (true → false)
    - For prohibitions: assert the prohibited action happened (false → true)
    """
    negative = {}
    
    # Key properties that should be negated for violations
    KEY_NEGATE = {
        'ait:payfee', 'ait:enrolled', 'ait:residesoncampus',
        'ait:has_proof_of_financial_support', 'ait:reported',
        'ait:advisor', 'ait:submit', 'ait:sra_completed',
        'ait:compliant', 'ait:visa_valid', 'ait:insurance_paid',
        'ait:approvalfromofamdirector', 'ait:confidentiality',
        'ait:promissory_note_sent', 'ait:employed',
    }
    
    # Properties where "true" means violation (prohibitions)
    VIOLATION_TRUE = {
        'ait:disturbing', 'ait:subletting', 'ait:livingbeyondfivedays',
        'ait:acceptedgift', 'ait:outstandingdues',
    }
    
    for prop, (value, dtype) in positive_props.items():
        if prop in KEY_NEGATE:
            negative[prop] = ('false', dtype)
        elif prop in VIOLATION_TRUE:
            if deontic_type == 'prohibition':
                negative[prop] = ('true', dtype)
            else:
                negative[prop] = (value, dtype)
        else:
            negative[prop] = (value, dtype)
    
    # For prohibitions, also flip the "action happened" to true
    if deontic_type == 'prohibition':
        for prop in VIOLATION_TRUE:
            if prop in negative:
                negative[prop] = ('true', 'boolean')
    
    return negative


def format_entity_ttl(entity_id: str, rdf_type: str, label: str,
                      properties: dict) -> str:
    """Format a single entity as Turtle RDF."""
    lines = [f'ait:{entity_id} a {rdf_type} ;']
    lines.append(f'    rdfs:label "{label}" ;')
    
    prop_lines = []
    for prop, (value, dtype) in sorted(properties.items()):
        if dtype == 'boolean':
            prop_lines.append(f'    {prop} {value}')
        elif dtype == 'integer':
            prop_lines.append(f'    {prop} {value}')
        else:
            prop_lines.append(f'    {prop} "{value}"')
    
    if prop_lines:
        lines.append(' ;\n'.join(prop_lines) + ' .')
    else:
        # No properties — close with period
        lines[-1] = lines[-1].rstrip(' ;') + ' .'
    
    return '\n'.join(lines)


def generate_test_data(output_path: Path = None):
    """
    Generate TDD test data from gold standard + FOL formalizations.
    
    v2: Uses FOL formulas and classification metadata to generate
    rule-specific properties instead of fixed templates.
    """
    # Load FOL results
    fol_file = RESEARCH_DIR / "fol_formalization_v2_results.json"
    if not fol_file.exists():
        fol_file = RESEARCH_DIR / "fol_formalization_results.json"
    
    if not fol_file.exists():
        print(f"❌ FOL results not found: {fol_file}")
        return
    
    with open(fol_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    rules = data.get("formalized_rules", [])
    print(f"📋 Loaded {len(rules)} formalized rules")
    
    if output_path is None:
        output_path = SHACL_DIR / "tdd_test_data.ttl"
    
    # Turtle header
    ttl = f"""@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix ait: <http://example.org/ait-policy#> .
@prefix deontic: <http://example.org/deontic#> .

# =============================================================================
# TDD Test Data v2 — FOL-Aware Generation
# =============================================================================
# Generated: {datetime.now().isoformat()}
# Source: {fol_file.name}
# Generator: generate_test_data.py v2 (FOL-aware property extraction)
#
# Each entity's properties are derived from:
#   1. FOL formula predicates → RDF property mappings
#   2. LLM classification subject/action analysis  
#   3. SHACL hints from formalization
#
# For obligations: positive = requirements met, negative = key requirement unmet
# For prohibitions: positive = prohibited action NOT done, negative = action done
# For permissions: positive only (permissions cannot be violated)
# =============================================================================

"""
    
    stats = {
        'positive': 0, 'negative': 0, 'skipped': 0,
        'entities_by_type': {}, 'properties_extracted': 0,
        'rules_with_properties': 0, 'empty_entities': 0,
    }
    
    for i, rule in enumerate(rules, 1):
        fol = rule.get('fol_formalization', {})
        classification = rule.get('llm_classification', {})
        
        if not fol or 'error' in str(fol).lower():
            stats['skipped'] += 1
            continue
        
        rule_id = rule.get('id', f'R{i:03d}')
        rule_id_clean = re.sub(r'[^A-Za-z0-9]', '', rule_id)
        dtype = fol.get('deontic_type', 'obligation')
        
        # Clean original text for comment (word-boundary truncation)
        original_text = rule.get('original_text', '').replace('\n', ' ').strip()
        if len(original_text) > 100:
            # Truncate at word boundary
            truncated = original_text[:100]
            last_space = truncated.rfind(' ')
            if last_space > 60:
                original_text = truncated[:last_space] + '...'
            else:
                original_text = truncated + '...'
        
        # Detect entity type
        entity_type = detect_entity_type(rule)
        rdf_type = RDF_TYPES.get(entity_type, 'ait:Person')
        stats['entities_by_type'][entity_type] = stats['entities_by_type'].get(entity_type, 0) + 1
        
        # Extract properties from FOL
        properties = extract_properties_from_fol(rule)
        
        if properties:
            stats['rules_with_properties'] += 1
            stats['properties_extracted'] += len(properties)
        else:
            stats['empty_entities'] += 1
        
        # Rule header comment
        subject = classification.get('subject', 'unspecified')
        action_text = classification.get('action', '').replace('\n', ' ')[:80]
        
        ttl += f"\n# {'='*65}\n"
        ttl += f"# {rule_id} | {dtype.upper()} | {entity_type}\n"
        ttl += f"# Subject: {subject}\n"
        if action_text:
            ttl += f"# Action: {action_text}\n"
        ttl += f"# Text: {original_text}\n"
        ttl += f"# Properties extracted: {len(properties)}\n"
        ttl += f"# {'='*65}\n\n"
        
        # --- Positive test entity ---
        pos_id = f"Pos_{rule_id_clean}"
        pos_label = f"Conforming {entity_type} for {rule_id} ({dtype})"
        ttl += format_entity_ttl(pos_id, rdf_type, pos_label, properties)
        ttl += '\n\n'
        stats['positive'] += 1
        
        # --- Negative test entity (obligations & prohibitions only) ---
        if dtype in ('obligation', 'prohibition') and properties:
            neg_properties = make_negative_properties(properties, dtype)
            neg_id = f"Neg_{rule_id_clean}"
            neg_label = f"Violating {entity_type} for {rule_id} ({dtype})"
            ttl += format_entity_ttl(neg_id, rdf_type, neg_label, neg_properties)
            ttl += '\n\n'
            stats['negative'] += 1
    
    # --- Summary footer ---
    total = stats['positive'] + stats['negative']
    ttl += f"""
# =============================================================================
# GENERATION SUMMARY
# =============================================================================
# Positive test entities (conforming):  {stats['positive']}
# Negative test entities (violating):   {stats['negative']}
# Skipped (no formalization):           {stats['skipped']}
# Total entities generated:             {total}
#
# Rules with extracted properties:      {stats['rules_with_properties']}/{len(rules)}
# Total properties extracted:           {stats['properties_extracted']}
# Empty entities (no properties found): {stats['empty_entities']}
#
# Entity type distribution:
"""
    for etype, count in sorted(stats['entities_by_type'].items(), key=lambda x: -x[1]):
        ttl += f"#   {etype}: {count}\n"
    
    ttl += "# =============================================================================\n"
    
    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(ttl)
    
    print(f"\n✅ Generated TDD test data v2: {output_path}")
    print(f"   Positive entities:  {stats['positive']}")
    print(f"   Negative entities:  {stats['negative']}")
    print(f"   Skipped:            {stats['skipped']}")
    print(f"   Total:              {total}")
    print(f"\n   Rules with properties: {stats['rules_with_properties']}/{len(rules)}")
    print(f"   Properties extracted:  {stats['properties_extracted']}")
    print(f"   Empty entities:        {stats['empty_entities']}")
    print(f"\n   Entity types:")
    for etype, count in sorted(stats['entities_by_type'].items(), key=lambda x: -x[1]):
        print(f"     {etype}: {count}")
    
    return stats


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate TDD test data (v2 FOL-aware)")
    parser.add_argument("--output", "-o", type=Path, default=None,
                       help="Output path (default: shacl/tdd_test_data.ttl)")
    args = parser.parse_args()
    
    generate_test_data(args.output)
