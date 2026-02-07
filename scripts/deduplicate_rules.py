#!/usr/bin/env python3
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
"""
Rule Deduplication Script
=========================
Removes duplicate/near-duplicate rules from extracted_rules.json based on
text similarity (Jaccard similarity on word n-grams).

Usage:
    python scripts/deduplicate_rules.py [--threshold 0.8] [--dry-run]

Output:
    - research/extracted_rules_deduplicated.json
    - Console report of duplicates found
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
RESEARCH_DIR = PROJECT_ROOT / "research"


def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    import re
    # Remove newlines, extra spaces, page markers
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'Page \d+/\d+', '', text)
    text = re.sub(r'FB-\d+-\d+-\d+:\s*\w+\s*POLICY', '', text)
    return text.strip().lower()


def word_ngrams(text: str, n: int = 3) -> set:
    """Generate word n-grams from text."""
    words = text.split()
    if len(words) < n:
        return {text}
    return {' '.join(words[i:i+n]) for i in range(len(words) - n + 1)}


def jaccard_similarity(text1: str, text2: str) -> float:
    """Calculate Jaccard similarity between two texts using word trigrams."""
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    
    ngrams1 = word_ngrams(norm1)
    ngrams2 = word_ngrams(norm2)
    
    if not ngrams1 or not ngrams2:
        return 0.0
    
    intersection = ngrams1 & ngrams2
    union = ngrams1 | ngrams2
    
    return len(intersection) / len(union) if union else 0.0


def containment_similarity(text1: str, text2: str) -> float:
    """Check if one text is contained within another (substring check)."""
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    
    shorter = norm1 if len(norm1) <= len(norm2) else norm2
    longer = norm1 if len(norm1) > len(norm2) else norm2
    
    if shorter in longer:
        return 1.0
    
    # Also check word-level containment
    words_short = set(shorter.split())
    words_long = set(longer.split())
    
    if not words_short:
        return 0.0
    
    return len(words_short & words_long) / len(words_short)


def deduplicate_rules(rules: list, threshold: float = 0.8) -> tuple:
    """
    Remove duplicate rules based on text similarity.
    
    Returns:
        (unique_rules, duplicate_groups, stats)
    """
    # Group by source document first for efficiency
    by_doc = defaultdict(list)
    for rule in rules:
        by_doc[rule.get("source_document", "unknown")].append(rule)
    
    # Track which rules to keep
    kept = []
    duplicates = []  # list of (kept_rule, duplicate_rule, similarity)
    seen_indices = set()
    
    all_rules = list(enumerate(rules))
    
    for i, rule_a in all_rules:
        if i in seen_indices:
            continue
        
        text_a = rule_a.get("original_text", "")
        if not text_a.strip():
            seen_indices.add(i)
            continue
        
        group = [rule_a]
        
        for j, rule_b in all_rules:
            if j <= i or j in seen_indices:
                continue
            
            text_b = rule_b.get("original_text", "")
            if not text_b.strip():
                continue
            
            # Quick length check - skip if very different lengths
            len_ratio = min(len(text_a), len(text_b)) / max(len(text_a), len(text_b))
            if len_ratio < 0.3:
                continue
            
            # Check similarity
            sim = jaccard_similarity(text_a, text_b)
            containment = containment_similarity(text_a, text_b)
            
            effective_sim = max(sim, containment * 0.9)
            
            if effective_sim >= threshold:
                seen_indices.add(j)
                group.append(rule_b)
                duplicates.append((rule_a["rule_id"], rule_b["rule_id"], round(effective_sim, 3)))
        
        # Keep the longest (most complete) version
        best = max(group, key=lambda r: len(r.get("original_text", "")))
        if len(group) > 1:
            best["merged_from"] = [r["rule_id"] for r in group]
            best["merge_count"] = len(group)
        kept.append(best)
        seen_indices.add(i)
    
    stats = {
        "original_count": len(rules),
        "deduplicated_count": len(kept),
        "removed_count": len(rules) - len(kept),
        "reduction_pct": round((1 - len(kept) / len(rules)) * 100, 1) if rules else 0,
        "duplicate_pairs": len(duplicates),
        "by_document": {}
    }
    
    # Per-document stats
    for doc, doc_rules in by_doc.items():
        doc_kept = [r for r in kept if r.get("source_document") == doc]
        stats["by_document"][doc] = {
            "original": len(doc_rules),
            "kept": len(doc_kept),
            "removed": len(doc_rules) - len(doc_kept)
        }
    
    return kept, duplicates, stats


def main():
    parser = argparse.ArgumentParser(description="Deduplicate extracted rules")
    parser.add_argument("--threshold", type=float, default=0.8,
                        help="Similarity threshold (0.0-1.0, default: 0.8)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show duplicates without saving")
    parser.add_argument("--input", type=str, default=None,
                        help="Input file (default: research/extracted_rules.json)")
    args = parser.parse_args()
    
    # Load rules
    input_file = Path(args.input) if args.input else RESEARCH_DIR / "extracted_rules.json"
    if not input_file.exists():
        print(f"[ERROR] Input file not found: {input_file}")
        return 1
    
    with open(input_file, "r", encoding="utf-8") as f:
        rules = json.load(f)
    
    print("=" * 60)
    print("RULE DEDUPLICATION")
    print("=" * 60)
    print(f"Input: {input_file}")
    print(f"Total rules: {len(rules)}")
    print(f"Similarity threshold: {args.threshold}")
    print("=" * 60)
    
    # Deduplicate
    unique_rules, duplicates, stats = deduplicate_rules(rules, args.threshold)
    
    # Report
    print(f"\n[RESULTS]")
    print(f"   Original:      {stats['original_count']}")
    print(f"   Deduplicated:  {stats['deduplicated_count']}")
    print(f"   Removed:       {stats['removed_count']} ({stats['reduction_pct']}%)")
    print(f"   Duplicate pairs found: {stats['duplicate_pairs']}")
    
    if duplicates:
        print(f"\nSample duplicate pairs (first 20):")
        for kept_id, dup_id, sim in duplicates[:20]:
            print(f"   {kept_id} ↔ {dup_id} (similarity: {sim})")
    
    print(f"\nPer-document breakdown:")
    for doc, doc_stats in sorted(stats["by_document"].items()):
        print(f"   {doc[:50]:50s}  {doc_stats['original']:3d} → {doc_stats['kept']:3d} (-{doc_stats['removed']})")
    
    if not args.dry_run:
        # Save deduplicated rules
        output_file = RESEARCH_DIR / "extracted_rules_deduplicated.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(unique_rules, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] Saved deduplicated rules: {output_file}")
        
        # Save stats
        stats_file = RESEARCH_DIR / "deduplication_stats.json"
        stats["timestamp"] = datetime.now().isoformat()
        stats["threshold"] = args.threshold
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        print(f"[OK] Saved stats: {stats_file}")
    else:
        print("\n[DRY RUN] No files saved")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
