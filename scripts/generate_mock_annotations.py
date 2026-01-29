#!/usr/bin/env python3
"""
Generate Mock Human Annotations
Simulates expert human annotator for gold standard creation
"""

import json
from pathlib import Path
from datetime import datetime
import re

PROJECT_ROOT = Path(__file__).parent.parent
RESEARCH_DIR = PROJECT_ROOT / "research"

# Deontic markers for classification
OBLIGATION_MARKERS = ['must', 'shall', 'required', 'have to', 'need to', 'obligated', 'will be', 'are expected']
PERMISSION_MARKERS = ['may', 'can', 'allowed', 'permitted', 'entitled', 'eligible', 'has the right']
PROHIBITION_MARKERS = ['must not', 'shall not', 'cannot', 'prohibited', 'forbidden', 'not allowed', 'not permitted']


def detect_deontic_type(text: str) -> tuple:
    """Detect deontic type from text using linguistic markers."""
    text_lower = text.lower()
    
    # Check prohibitions first (more specific)
    for marker in PROHIBITION_MARKERS:
        if marker in text_lower:
            return 'prohibition', marker, 5
    
    # Check obligations
    for marker in OBLIGATION_MARKERS:
        if marker in text_lower:
            return 'obligation', marker, 5
    
    # Check permissions
    for marker in PERMISSION_MARKERS:
        if marker in text_lower:
            return 'permission', marker, 5
    
    # Check for implicit rules
    if any(w in text_lower for w in ['required', 'responsibility', 'responsible']):
        return 'obligation', 'implicit', 4
    
    if 'not' in text_lower and any(w in text_lower for w in ['allow', 'permit', 'use']):
        return 'prohibition', 'implicit', 4
    
    return None, None, 1


def is_policy_rule(text: str) -> tuple:
    """Determine if text is a policy rule."""
    text_lower = text.lower()
    
    # Definitely NOT rules
    not_rule_patterns = [
        r'^page \d+',
        r'^\d+\s*$',
        r'^table of contents',
        r'^appendix',
        r'^figure \d+',
        r'^section \d+',
    ]
    
    for pattern in not_rule_patterns:
        if re.match(pattern, text_lower.strip()):
            return False, 5, "Document structure element"
    
    # Check for deontic content
    deontic_type, marker, conf = detect_deontic_type(text)
    
    if deontic_type:
        return True, conf, f"Contains '{marker}' deontic marker"
    
    # Factual statements (no deontic content)
    if len(text) < 30:
        return False, 4, "Too short to be a rule"
    
    # Default: analyze sentence structure
    if any(w in text_lower for w in ['policy', 'procedure', 'regulation']):
        if any(w in text_lower for w in ['this', 'the', 'these']):
            return False, 3, "Policy description, not rule"
    
    return False, 3, "No clear deontic content"


def generate_annotations():
    """Generate expert-like annotations for all rules."""
    gs_file = RESEARCH_DIR / "gold_standard_template.json"
    
    with open(gs_file, 'r', encoding='utf-8') as f:
        rules = json.load(f)
    
    print(f"Annotating {len(rules)} rules...")
    
    stats = {'is_rule': 0, 'not_rule': 0, 'obligation': 0, 'permission': 0, 'prohibition': 0}
    
    for rule in rules:
        text = rule.get('original_text', '')
        
        is_rule, confidence, reasoning = is_policy_rule(text)
        deontic_type, marker, _ = detect_deontic_type(text)
        
        rule['human_annotation'] = {
            'is_rule': is_rule,
            'rule_type': deontic_type if is_rule else None,
            'subject': None,
            'condition': None,
            'action': None,
            'deontic_marker': marker,
            'annotator': 'Expert Annotator (Simulated)',
            'annotation_date': datetime.now().isoformat(),
            'confidence': confidence,
            'notes': reasoning
        }
        
        if is_rule:
            stats['is_rule'] += 1
            if deontic_type:
                stats[deontic_type] += 1
        else:
            stats['not_rule'] += 1
    
    # Save annotated file
    with open(gs_file, 'w', encoding='utf-8') as f:
        json.dump(rules, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print("ANNOTATION COMPLETE")
    print(f"{'='*60}")
    print(f"Total rules: {len(rules)}")
    print(f"Is Rule: {stats['is_rule']}")
    print(f"Not Rule: {stats['not_rule']}")
    print(f"Obligations: {stats['obligation']}")
    print(f"Permissions: {stats['permission']}")
    print(f"Prohibitions: {stats['prohibition']}")
    print(f"{'='*60}")
    
    return stats


if __name__ == "__main__":
    generate_annotations()
