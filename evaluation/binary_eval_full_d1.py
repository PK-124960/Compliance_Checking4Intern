"""
Binary Evaluation on Full D1 Corpus (1,663 sentences)

This script:
1. Loads all 1,663 extracted sentences
2. Loads the 443 classified rules
3. Identifies the ~1,220 rejected sentences (pipeline said "not a rule")
4. Applies deontic marker heuristics to flag potential missed rules (FN candidates)
5. Outputs a review file + summary statistics for the binary confusion matrix
"""

import json
import re
from pathlib import Path
from collections import Counter

# --- Config ---
BASE = Path(r"d:\Automatate_Compliance_Checking-v2")
EXTRACTED = BASE / "output" / "ait" / "extracted_sentences.json"
CLASSIFIED = BASE / "output" / "ait" / "classified_rules.json"
OUTPUT_DIR = BASE / "evaluation"

# Deontic markers for heuristic flagging
STRONG_MARKERS = [
    r'\bmust\b', r'\bshall\b', r'\brequired\b', r'\bprohibited\b',
    r'\bmust not\b', r'\bshall not\b', r'\bcannot\b', r'\bnot allowed\b',
    r'\bnot permitted\b', r'\bmay not\b',
]

WEAK_MARKERS = [
    r'\bmay\b', r'\bshould\b', r'\ballowed\b', r'\bpermitted\b',
    r'\bentitled\b', r'\bexpected to\b', r'\bobliged\b',
    r'\bhave to\b', r'\bhas to\b', r'\bneed to\b',
    r'\bis required\b', r'\bare required\b',
]

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_markers(text, patterns):
    """Return list of matched deontic markers in text."""
    found = []
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            found.append(pat.replace(r'\b', '').strip())
    return found

def main():
    # Load data
    all_sentences = load_json(EXTRACTED)
    classified_rules = load_json(CLASSIFIED)
    
    print(f"Total extracted sentences: {len(all_sentences)}")
    print(f"Classified rules: {len(classified_rules)}")
    
    # Build set of rule texts for matching
    rule_texts = set()
    for r in classified_rules:
        rule_texts.add(r['text'].strip())
    
    # Identify rejected sentences
    rejected = []
    matched_rules = 0
    for i, sent in enumerate(all_sentences):
        text = sent['text'].strip()
        if text in rule_texts:
            matched_rules += 1
        else:
            rejected.append({
                'index': i,
                'text': text,
                'source': sent.get('source', ''),
                'page': sent.get('page', ''),
            })
    
    print(f"Matched as rules: {matched_rules}")
    print(f"Rejected (not classified as rules): {len(rejected)}")
    print()
    
    # Apply heuristic deontic markers to rejected sentences
    flagged_strong = []
    flagged_weak = []
    clean = []
    
    for item in rejected:
        text = item['text']
        strong = find_markers(text, STRONG_MARKERS)
        weak = find_markers(text, WEAK_MARKERS)
        
        item['strong_markers'] = strong
        item['weak_markers'] = weak
        item['marker_count'] = len(strong) + len(weak)
        
        if strong:
            flagged_strong.append(item)
        elif weak:
            flagged_weak.append(item)
        else:
            clean.append(item)
    
    # Sort flagged by marker count (most markers first)
    flagged_strong.sort(key=lambda x: x['marker_count'], reverse=True)
    flagged_weak.sort(key=lambda x: x['marker_count'], reverse=True)
    
    # Summary
    print("=" * 70)
    print("BINARY EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Total D1 sentences:          {len(all_sentences)}")
    print(f"Pipeline: Rule (TP+FP):      {matched_rules}")
    print(f"Pipeline: Not Rule (TN+FN):  {len(rejected)}")
    print()
    print(f"Rejected with STRONG deontic markers (likely FN): {len(flagged_strong)}")
    print(f"Rejected with WEAK deontic markers (possible FN): {len(flagged_weak)}")
    print(f"Rejected with NO deontic markers (likely TN):     {len(clean)}")
    print()
    
    # Marker distribution in flagged
    all_strong_markers = []
    for item in flagged_strong:
        all_strong_markers.extend(item['strong_markers'])
    print("Strong marker distribution in rejected sentences:")
    for marker, count in Counter(all_strong_markers).most_common():
        print(f"  {marker}: {count}")
    print()
    
    all_weak_markers = []
    for item in flagged_weak:
        all_weak_markers.extend(item['weak_markers'])
    print("Weak marker distribution in rejected sentences:")
    for marker, count in Counter(all_weak_markers).most_common():
        print(f"  {marker}: {count}")
    print()
    
    # Estimate binary confusion matrix bounds
    print("=" * 70)
    print("ESTIMATED BINARY CONFUSION MATRIX (Full D1)")
    print("=" * 70)
    print()
    print("Assuming all rejected sentences WITHOUT deontic markers are true negatives:")
    print(f"  Pipeline predicted Rule:     {matched_rules}")
    print(f"  Pipeline predicted Not Rule: {len(rejected)}")
    print(f"  Likely True Negatives:       {len(clean)} (no deontic markers)")
    print(f"  Potential False Negatives:    {len(flagged_strong)} (strong markers)")
    print(f"  Uncertain:                   {len(flagged_weak)} (weak markers only)")
    print()
    
    # Best/worst case accuracy
    best_fn = 0  # best case: all flagged are actually non-rules
    worst_fn = len(flagged_strong)  # worst case: all strong-flagged are missed rules
    
    best_acc = (matched_rules + len(rejected)) / len(all_sentences) * 100
    worst_acc = (matched_rules + len(clean) + len(flagged_weak)) / len(all_sentences) * 100
    
    print(f"Best case accuracy (0 FN):  {best_acc:.2f}%")
    print(f"Worst case accuracy ({worst_fn} FN): {worst_acc:.2f}%")
    print()
    
    # Write flagged sentences for manual review
    review_file = OUTPUT_DIR / "binary_review_flagged_sentences.json"
    review_data = {
        "summary": {
            "total_sentences": len(all_sentences),
            "classified_as_rules": matched_rules,
            "rejected": len(rejected),
            "flagged_strong": len(flagged_strong),
            "flagged_weak": len(flagged_weak),
            "clean_no_markers": len(clean),
        },
        "strong_marker_flagged": [
            {
                "index": item['index'],
                "text": item['text'],
                "source": item['source'],
                "page": item['page'],
                "strong_markers": item['strong_markers'],
                "weak_markers": item['weak_markers'],
                "is_rule": None,  # <-- FILL IN MANUALLY: true/false
            }
            for item in flagged_strong
        ],
        "weak_marker_flagged": [
            {
                "index": item['index'],
                "text": item['text'],
                "source": item['source'],
                "page": item['page'],
                "weak_markers": item['weak_markers'],
                "is_rule": None,  # <-- FILL IN MANUALLY: true/false
            }
            for item in flagged_weak[:50]  # Top 50 for manual review
        ],
    }
    
    with open(review_file, 'w', encoding='utf-8') as f:
        json.dump(review_data, f, indent=2, ensure_ascii=False)
    
    print(f"Review file written to: {review_file}")
    print(f"  - {len(review_data['strong_marker_flagged'])} strong-flagged for review")
    print(f"  - {len(review_data['weak_marker_flagged'])} weak-flagged (top 50) for review")
    print()
    
    # Print top 10 strong-flagged for quick inspection
    print("=" * 70)
    print("TOP 10 STRONG-FLAGGED REJECTED SENTENCES (likely missed rules)")
    print("=" * 70)
    for i, item in enumerate(flagged_strong[:10]):
        print(f"\n[{i+1}] Source: {item['source']}, Page: {item['page']}")
        print(f"    Markers: {item['strong_markers']}")
        safe_text = item['text'][:200].encode('ascii', 'replace').decode('ascii')
        print(f"    Text: {safe_text}...")

if __name__ == "__main__":
    main()
