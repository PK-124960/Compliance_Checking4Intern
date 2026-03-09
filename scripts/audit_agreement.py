#!/usr/bin/env python3
"""
Audit & Fix human_llm_agreement Field
======================================
Checks gold_standard_annotated_v4.json for mismatches between
human_annotation and llm_annotation and reports/fixes the agreement field.

Usage:
    python scripts/audit_agreement.py           # Report only
    python scripts/audit_agreement.py --fix     # Fix and save
"""

import json
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
RESEARCH_DIR = PROJECT_ROOT / "research"
GOLD_FILE = RESEARCH_DIR / "gold_standard_annotated_v4.json"


def audit_agreement(fix: bool = False):
    """Audit the human_llm_agreement field for consistency."""
    with open(GOLD_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    total = len(data)
    issues = []
    stats = {
        "total": total,
        "detection_agree": 0,      # is_rule matches
        "detection_disagree": 0,   # is_rule differs
        "type_agree": 0,           # rule_type matches (among detection agreements)
        "type_disagree": 0,        # rule_type differs (among detection agreements)
        "field_incorrect": 0,      # human_llm_agreement field is wrong
        "field_inflated": 0,       # agreement=True but types differ
    }
    
    type_confusions = []  # (id, human_type, llm_type)
    
    for entry in data:
        entry_id = entry["id"]
        human = entry.get("human_annotation", {})
        llm = entry.get("llm_annotation", {})
        recorded_agreement = entry.get("human_llm_agreement")
        
        human_is_rule = human.get("is_rule")
        llm_is_rule = llm.get("is_rule")
        human_type = human.get("rule_type")
        llm_type = llm.get("rule_type")
        
        # Check detection agreement
        detection_match = (human_is_rule == llm_is_rule)
        if detection_match:
            stats["detection_agree"] += 1
        else:
            stats["detection_disagree"] += 1
        
        # Check type agreement (only if both say it's a rule)
        type_match = None
        if human_is_rule and llm_is_rule:
            type_match = (human_type == llm_type)
            if type_match:
                stats["type_agree"] += 1
            else:
                stats["type_disagree"] += 1
                type_confusions.append({
                    "id": entry_id,
                    "text": entry.get("original_text", "")[:80],
                    "human_type": human_type,
                    "llm_type": llm_type,
                    "human_marker": human.get("deontic_marker", ""),
                    "llm_marker": llm.get("deontic_marker", ""),
                })
        
        # Check if recorded agreement is correct
        # "Agreement" should mean BOTH detection AND type match
        full_agreement = detection_match and (type_match is True or type_match is None)
        
        if recorded_agreement and not full_agreement:
            stats["field_inflated"] += 1
            issues.append({
                "id": entry_id,
                "text": entry.get("original_text", "")[:80],
                "human_is_rule": human_is_rule,
                "llm_is_rule": llm_is_rule,
                "human_type": human_type,
                "llm_type": llm_type,
                "recorded": recorded_agreement,
                "computed_detection": detection_match,
                "computed_type": type_match,
            })
        
        if recorded_agreement != detection_match:
            stats["field_incorrect"] += 1
    
    # Print report
    print("=" * 70)
    print("AGREEMENT FIELD AUDIT REPORT")
    print("=" * 70)
    print(f"\nDataset: {GOLD_FILE.name}")
    print(f"Total entries: {stats['total']}")
    print(f"\n--- Detection Agreement (is_rule match) ---")
    print(f"  Agree:    {stats['detection_agree']}")
    print(f"  Disagree: {stats['detection_disagree']}")
    print(f"  Rate:     {stats['detection_agree']/stats['total']*100:.1f}%")
    
    both_rules = stats['type_agree'] + stats['type_disagree']
    print(f"\n--- Type Classification Agreement (among {both_rules} shared rules) ---")
    print(f"  Agree:    {stats['type_agree']}")
    print(f"  Disagree: {stats['type_disagree']}")
    if both_rules > 0:
        print(f"  Rate:     {stats['type_agree']/both_rules*100:.1f}%")
    
    print(f"\n--- Agreement Field Issues ---")
    print(f"  Field = True but types differ (INFLATED): {stats['field_inflated']}")
    print(f"  Field != detection match:                  {stats['field_incorrect']}")
    
    if type_confusions:
        print(f"\n--- Type Classification Disagreements ({len(type_confusions)} total) ---")
        
        # Summarize by confusion pair
        confusion_pairs = Counter()
        for tc in type_confusions:
            pair = f"{tc['human_type']} → {tc['llm_type']}"
            confusion_pairs[pair] += 1
        
        print("\n  Confusion summary:")
        for pair, count in confusion_pairs.most_common():
            print(f"    {pair}: {count}")
        
        print("\n  Detailed disagreements:")
        for tc in type_confusions:
            print(f"    {tc['id']}: human={tc['human_type']}, llm={tc['llm_type']}")
            print(f"      markers: human='{tc['human_marker']}', llm='{tc['llm_marker']}'")
            print(f"      text: \"{tc['text']}...\"")
            print()
    
    if issues:
        print(f"\n--- Entries with INFLATED agreement (True but types differ) ---")
        for iss in issues[:10]:  # Show first 10
            print(f"  {iss['id']}: human={iss['human_type']}, llm={iss['llm_type']}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")
    
    # Compute corrected metrics
    print(f"\n{'=' * 70}")
    print("CORRECTED METRICS")
    print(f"{'=' * 70}")
    print(f"  Detection Accuracy (is_rule):    {stats['detection_agree']}/{stats['total']} = {stats['detection_agree']/stats['total']*100:.2f}%")
    if both_rules > 0:
        print(f"  Type Classification Accuracy:    {stats['type_agree']}/{both_rules} = {stats['type_agree']/both_rules*100:.2f}%")
    print(f"  Overall (detection + type):      {stats['type_agree'] + (stats['total'] - both_rules)}/{stats['total']} (need separate computation)")
    
    # Fix if requested
    if fix and issues:
        print(f"\n--- Fixing {len(issues)} inflated agreement entries ---")
        
        fixed_data = json.loads(json.dumps(data))  # deep copy
        fixes_made = 0
        
        for entry in fixed_data:
            human = entry.get("human_annotation", {})
            llm = entry.get("llm_annotation", {})
            
            human_is_rule = human.get("is_rule")
            llm_is_rule = llm.get("is_rule")
            human_type = human.get("rule_type")
            llm_type = llm.get("rule_type")
            
            detection_match = (human_is_rule == llm_is_rule)
            type_match = None
            if human_is_rule and llm_is_rule:
                type_match = (human_type == llm_type)
            
            # Add detailed agreement fields
            entry["human_llm_agreement_detection"] = detection_match
            entry["human_llm_agreement_type"] = type_match if type_match is not None else "N/A"
            
            # Keep original for reference
            entry["human_llm_agreement_original"] = entry.get("human_llm_agreement")
            
            # Update to reflect detection-only agreement (what it was measuring)
            # This preserves backward compatibility while clarifying semantics
            entry["human_llm_agreement"] = detection_match
            
            if entry["human_llm_agreement_original"] != detection_match:
                fixes_made += 1
        
        # Save backup first
        backup_path = GOLD_FILE.with_name(f"{GOLD_FILE.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  Backup saved: {backup_path.name}")
        
        # Save fixed version
        with open(GOLD_FILE, "w", encoding="utf-8") as f:
            json.dump(fixed_data, f, indent=2, ensure_ascii=False)
        print(f"  Fixed file saved: {GOLD_FILE.name}")
        print(f"  Fixes applied: {fixes_made}")
        print(f"  New fields added: human_llm_agreement_detection, human_llm_agreement_type")
    
    return stats, issues, type_confusions


if __name__ == "__main__":
    fix_mode = "--fix" in sys.argv
    stats, issues, confusions = audit_agreement(fix=fix_mode)
    
    if issues and not fix_mode:
        print(f"\nRun with --fix to correct {len(issues)} inflated agreement entries.")
