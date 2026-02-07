#!/usr/bin/env python3
"""
TDD Test Data Quality Fix Script
=================================
Fixes quality issues in tdd_test_data.ttl:
1. Empty entities (no properties) - adds meaningful properties from rule text
2. Neg = Pos entities - ensures violation entities differ from conforming ones
3. Missing negative entities - generates violating instances

Usage:
    python scripts/fix_tdd_test_data.py [--dry-run]

Output:
    - shacl/tdd_test_data_fixed.ttl
    - Console report of fixes applied
"""

import sys
import io
import re
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SHACL_DIR = PROJECT_ROOT / "shacl"
RESEARCH_DIR = PROJECT_ROOT / "research"


# Map rule text keywords to relevant properties
RULE_PROPERTY_MAP = {
    # Payment/Financial
    "pay": "ait:payfee",
    "fee": "ait:payfee",
    "invoice": "ait:payfee",
    "deposit": "ait:payfee",
    "fine": "ait:payfee",
    # Enrollment
    "enrol": "ait:enrolled",
    "register": "ait:enrolled",
    "admission": "ait:enrolled",
    # Accommodation
    "accommodation": "ait:residesoncampus",
    "dormitory": "ait:residesoncampus",
    "campus": "ait:residesoncampus",
    "housing": "ait:residesoncampus",
    "vacate": "ait:residesoncampus",
    # Reporting
    "report": "ait:reported",
    "submit": "ait:submit",
    "notify": "ait:reported",
    # Employment
    "employ": "ait:employed",
    "assistant": "ait:employed",
    "staff": "ait:employed",
    # Academic
    "exam": "ait:exam_completed",
    "test": "ait:exam_completed",
    "course": "ait:enrolled",
    "credit": "ait:enrolled",
    # Approval
    "approval": "ait:approvalfromofamdirector",
    "permission": "ait:approvalfromofamdirector",
    "authorized": "ait:approvalfromofamdirector",
    # Compliance
    "comply": "ait:compliant",
    "compli": "ait:compliant",
    "proper": "ait:compliant",
    "attire": "ait:compliant",
    "wear": "ait:compliant",
}


def parse_tdd_file(filepath: Path) -> str:
    """Read the TDD test data file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def extract_entities(content: str) -> list:
    """Parse test entities from the TTL content."""
    entities = []
    
    # Match entity blocks with their headers
    pattern = re.compile(
        r'# =+\n'
        r'# (GS-\d+) \| (\w+) \| (\w+)\n'
        r'# Subject: (.+?)\n'
        r'# Action: (.+?)\n'
        r'# Text: (.+?)\n'
        r'# Properties extracted: (\d+)\n'
        r'# =+\n'
        r'(.*?)(?=# =|$)',
        re.DOTALL
    )
    
    for match in pattern.finditer(content):
        rule_id = match.group(1)
        deontic_type = match.group(2).lower()
        target_class = match.group(3)
        subject = match.group(4)
        action = match.group(5)
        text = match.group(6)
        prop_count = int(match.group(7))
        entity_block = match.group(8).strip()
        
        # Check for Pos and Neg entities
        has_pos = f"Pos_{rule_id.replace('-', '')}" in entity_block or f"Pos_{rule_id}" in entity_block
        has_neg = f"Neg_{rule_id.replace('-', '')}" in entity_block or f"Neg_{rule_id}" in entity_block
        
        # Count actual properties in Pos entity  
        pos_props = re.findall(r'ait:\w+\s+(true|false|"[^"]*"|\d+)', entity_block.split("Neg_")[0] if "Neg_" in entity_block else entity_block)
        
        entities.append({
            "rule_id": rule_id,
            "deontic_type": deontic_type,
            "target_class": target_class,
            "subject": subject,
            "action": action,
            "text": text,
            "prop_count": prop_count,
            "has_pos": has_pos,
            "has_neg": has_neg,
            "actual_pos_props": len(pos_props),
            "entity_block": entity_block,
            "full_match": match.group(0)
        })
    
    return entities


def infer_properties(text: str, action: str, max_props: int = 2) -> list:
    """Infer suitable properties from rule text and action."""
    combined = (text + " " + action).lower()
    found = set()
    
    for keyword, prop in RULE_PROPERTY_MAP.items():
        if keyword in combined and prop not in found:
            found.add(prop)
            if len(found) >= max_props:
                break
    
    # If nothing found, add a generic compliant property
    if not found:
        found.add("ait:compliant")
    
    return sorted(found)


def fix_empty_entity(entity: dict) -> str:
    """Generate a fixed entity block with at least 1 property."""
    rule_id = entity["rule_id"]
    rule_id_clean = rule_id.replace("-", "")
    target_class = entity["target_class"]
    deontic_type = entity["deontic_type"]
    
    props = infer_properties(entity["text"], entity["action"])
    
    # Build Pos entity
    pos_lines = [
        f'ait:Pos_{rule_id_clean} a ait:{target_class} ;',
        f'    rdfs:label "Conforming {target_class} for {rule_id} ({deontic_type})" ;'
    ]
    for i, prop in enumerate(props):
        separator = " ." if i == len(props) - 1 else " ;"
        pos_lines.append(f'    {prop} true{separator}')
    
    result = '\n'.join(pos_lines) + '\n'
    
    # Build Neg entity (with at least one property flipped)
    neg_lines = [
        f'',
        f'ait:Neg_{rule_id_clean} a ait:{target_class} ;',
        f'    rdfs:label "Violating {target_class} for {rule_id} ({deontic_type})" ;'
    ]
    for i, prop in enumerate(props):
        separator = " ." if i == len(props) - 1 else " ;"
        neg_lines.append(f'    {prop} false{separator}')
    
    result += '\n'.join(neg_lines) + '\n'
    
    return result


def fix_identical_neg_pos(entity: dict) -> str:
    """Fix cases where Neg entity has same values as Pos entity."""
    block = entity["entity_block"]
    
    # Find properties in Neg entity and flip at least the first boolean to false
    neg_start = block.find("Neg_")
    if neg_start == -1:
        return block
    
    neg_section = block[neg_start:]
    
    # Replace first "true" in Neg entity with "false"
    fixed_neg = re.sub(r'(ait:\w+)\s+true', r'\1 false', neg_section, count=1)
    
    if fixed_neg != neg_section:
        return block[:neg_start] + fixed_neg
    
    return block


def apply_fixes(content: str, entities: list, dry_run: bool = False) -> tuple:
    """Apply all fixes to the TDD test data."""
    fixed_content = content
    fixes = {
        "empty_filled": 0,
        "neg_fixed": 0,
        "neg_added": 0,
        "total_fixes": 0
    }
    
    for entity in entities:
        # Fix 1: Empty entities (no properties)
        if entity["actual_pos_props"] == 0:
            new_block = fix_empty_entity(entity)
            old_block = entity["entity_block"]
            if old_block.strip():
                fixed_content = fixed_content.replace(old_block, new_block)
            fixes["empty_filled"] += 1
            fixes["total_fixes"] += 1
        
        # Fix 2: Identical Neg/Pos (check if Neg has same property values as Pos)
        elif entity["has_neg"] and entity["has_pos"]:
            block = entity["entity_block"]
            pos_end = block.find("ait:Neg_")
            if pos_end > 0:
                pos_section = block[:pos_end]
                neg_section = block[pos_end:]
                
                # Extract property values
                pos_values = re.findall(r'(ait:\w+)\s+(true|false)', pos_section)
                neg_values = re.findall(r'(ait:\w+)\s+(true|false)', neg_section)
                
                if pos_values and neg_values:
                    pos_dict = dict(pos_values)
                    neg_dict = dict(neg_values)
                    
                    # Check if all values are identical
                    if pos_dict == neg_dict:
                        fixed_block = fix_identical_neg_pos(entity)
                        if fixed_block != block:
                            fixed_content = fixed_content.replace(block, fixed_block)
                            fixes["neg_fixed"] += 1
                            fixes["total_fixes"] += 1
        
        # Fix 3: Missing Neg entity for obligations/prohibitions
        elif not entity["has_neg"] and entity["deontic_type"] in ["obligation", "prohibition"]:
            if entity["actual_pos_props"] > 0:
                # Generate a Neg entity with flipped properties
                rule_id_clean = entity["rule_id"].replace("-", "")
                target_class = entity["target_class"]
                deontic_type = entity["deontic_type"]
                
                # Extract Pos properties
                pos_props = re.findall(r'(ait:\w+)\s+(true|false)', entity["entity_block"])
                
                if pos_props:
                    neg_lines = [
                        f'',
                        f'ait:Neg_{rule_id_clean} a ait:{target_class} ;',
                        f'    rdfs:label "Violating {target_class} for {entity["rule_id"]} ({deontic_type})" ;'
                    ]
                    for i, (prop, val) in enumerate(pos_props):
                        flipped = "false" if val == "true" else "true"
                        separator = " ." if i == len(pos_props) - 1 else " ;"
                        neg_lines.append(f'    {prop} {flipped}{separator}')
                    
                    neg_block = '\n'.join(neg_lines) + '\n'
                    
                    # Insert after the Pos entity
                    old_block = entity["entity_block"]
                    new_block = old_block.rstrip() + '\n' + neg_block
                    fixed_content = fixed_content.replace(old_block, new_block)
                    fixes["neg_added"] += 1
                    fixes["total_fixes"] += 1
    
    return fixed_content, fixes


def main():
    parser = argparse.ArgumentParser(description="Fix TDD test data quality issues")
    parser.add_argument("--dry-run", action="store_true", help="Report issues without saving")
    args = parser.parse_args()
    
    tdd_file = SHACL_DIR / "tdd_test_data.ttl"
    if not tdd_file.exists():
        print(f"[ERROR] TDD file not found: {tdd_file}")
        return 1
    
    print("=" * 60)
    print("TDD TEST DATA QUALITY FIX")
    print("=" * 60)
    
    content = parse_tdd_file(tdd_file)
    entities = extract_entities(content)
    
    print(f"Total entities parsed: {len(entities)}")
    
    # Analyze issues
    empty = [e for e in entities if e["actual_pos_props"] == 0]
    no_neg = [e for e in entities if not e["has_neg"] and e["deontic_type"] in ["obligation", "prohibition"]]
    
    print(f"Empty entities (no properties): {len(empty)}")
    if empty:
        for e in empty[:10]:
            print(f"  {e['rule_id']} ({e['deontic_type']}) - {e['text'][:60]}...")
    
    print(f"Missing negatives (obligation/prohibition): {len(no_neg)}")
    
    # Apply fixes
    fixed_content, fixes = apply_fixes(content, entities, args.dry_run)
    
    print(f"\nFixes applied:")
    print(f"  Empty entities filled:       {fixes['empty_filled']}")
    print(f"  Identical Neg/Pos fixed:     {fixes['neg_fixed']}")
    print(f"  Missing Neg entities added:  {fixes['neg_added']}")
    print(f"  Total fixes:                 {fixes['total_fixes']}")
    
    if not args.dry_run and fixes['total_fixes'] > 0:
        output_file = SHACL_DIR / "tdd_test_data_fixed.ttl"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(fixed_content)
        print(f"\n[OK] Saved fixed TDD data: {output_file}")
    elif args.dry_run:
        print("\n[DRY RUN] No files saved")
    else:
        print("\nNo fixes needed!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
