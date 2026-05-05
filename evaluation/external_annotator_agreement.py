"""
External Annotator Agreement Study (D3-grounded)
==================================================
Computes inter-annotator reliability on a 50-item stratified sample
drawn from the D3 Full AIT Corpus.

Four annotators:
  1. author_gold   — author's majority-vote-reconciled gold labels
  2. kittipat      — external annotator 1
  3. mayuree       — external annotator 2
  4. llm           — pipeline LLM (Mistral) classification

Outputs:
  - Fleiss' Kappa (3 human annotators: author, kittipat, mayuree)
  - Pairwise Cohen's Kappa (all pairs including LLM)
  - LLM classification accuracy vs human gold
  - Per-class precision/recall/F1 for LLM
  - Saved JSON: output/ait/external_annotator_agreement.json

Usage:
    python -m evaluation.external_annotator_agreement
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


# ── Label normalisation ──────────────────────────────────────────────────

def normalise_label(raw: str) -> str:
    """Map raw classification to canonical 5-class label."""
    raw = raw.strip().lower()
    if raw == "obligation":
        return "obligation"
    if raw == "permission":
        return "permission"
    if raw == "prohibition":
        return "prohibition"
    if "non-deontic" in raw or "constitutive" in raw or "epistemic" in raw:
        return "non-deontic"
    if "unclear" in raw or "truncated" in raw:
        return "non-deontic"   # collapse unclear → non-deontic
    return raw


def to_binary(label: str) -> str:
    """Collapse to binary: deontic vs. non-deontic."""
    return "non-deontic" if label == "non-deontic" else "deontic"


# ── Data loading ─────────────────────────────────────────────────────────

def load_data(output_dir: Path):
    """Load all annotator data and return aligned label lists."""
    answer_key = json.loads(
        (output_dir / "reannotation_answer_key.json").read_text(encoding="utf-8")
    )
    kittipat = json.loads(
        (output_dir / "questionnaire_kittipat.json").read_text(encoding="utf-8")
    )
    mayuree = json.loads(
        (output_dir / "questionnaire_mayuree.json").read_text(encoding="utf-8")
    )
    llm = json.loads(
        (output_dir / "questionnaire_LLM.json").read_text(encoding="utf-8")
    )

    # Build lookup by item_id
    ak_map = {a["item_id"]: normalise_label(a["original_type"]) for a in answer_key}
    ki_map = {k["item_id"]: normalise_label(k["classification"]) for k in kittipat}
    ma_map = {m["item_id"]: normalise_label(m["classification"]) for m in mayuree}
    llm_map = {l["item_id"]: normalise_label(l["reannotation"]) for l in llm
               if l.get("reannotation", "").strip()}

    # Align on common item_ids across all four sources
    common_ids = sorted(set(ak_map) & set(ki_map) & set(ma_map) & set(llm_map))

    return {
        "item_ids":  common_ids,
        "gold":      [ak_map[i]  for i in common_ids],
        "kittipat":  [ki_map[i]  for i in common_ids],
        "mayuree":   [ma_map[i]  for i in common_ids],
        "llm":       [llm_map[i] for i in common_ids],
        # raw references
        "answer_key_raw": answer_key,
        "kittipat_raw":   kittipat,
        "mayuree_raw":    mayuree,
        "llm_raw":        llm,
    }


# ── Cohen's Kappa ────────────────────────────────────────────────────────

def cohens_kappa(labels1: list[str], labels2: list[str]) -> float:
    """Compute Cohen's Kappa coefficient."""
    n = len(labels1)
    if n == 0:
        return 0.0
    categories = sorted(set(labels1) | set(labels2))
    matrix = {(c1, c2): 0 for c1 in categories for c2 in categories}
    for a, b in zip(labels1, labels2):
        matrix[(a, b)] += 1
    p_o = sum(matrix[(c, c)] for c in categories) / n
    p_e = sum(
        (sum(matrix[(c, c2)] for c2 in categories) / n)
        * (sum(matrix[(c1, c)] for c1 in categories) / n)
        for c in categories
    )
    if p_e >= 1.0:
        return 1.0 if p_o >= 1.0 else 0.0
    return (p_o - p_e) / (1 - p_e)


# ── Fleiss' Kappa ────────────────────────────────────────────────────────

def fleiss_kappa(ratings: list[list[str]]) -> float:
    """
    Compute Fleiss' Kappa for multiple annotators.
    ratings: list of [annotator1_label, annotator2_label, ...] per item.
    """
    n_items  = len(ratings)
    n_raters = len(ratings[0])
    categories = sorted(set(label for item in ratings for label in item))
    n_cats = len(categories)
    cat_idx = {c: i for i, c in enumerate(categories)}

    counts = []
    for item in ratings:
        row = [0] * n_cats
        for label in item:
            row[cat_idx[label]] += 1
        counts.append(row)

    p_items = [
        (sum(r * r for r in row) - n_raters) / (n_raters * (n_raters - 1))
        for row in counts
    ]
    P_bar = sum(p_items) / n_items

    p_cats = [
        sum(counts[i][j] for i in range(n_items)) / (n_items * n_raters)
        for j in range(n_cats)
    ]
    P_e = sum(p * p for p in p_cats)

    if P_e >= 1.0:
        return 1.0 if P_bar >= 1.0 else 0.0
    return (P_bar - P_e) / (1 - P_e)


# ── Per-class metrics ────────────────────────────────────────────────────

def per_class_metrics(labels_true: list[str], labels_pred: list[str]) -> dict:
    """Compute per-class precision, recall, F1 and overall accuracy."""
    categories = sorted(set(labels_true) | set(labels_pred))
    n = len(labels_true)
    agree = sum(1 for a, b in zip(labels_true, labels_pred) if a == b)

    per_class = {}
    for c in categories:
        tp = sum(1 for a, b in zip(labels_true, labels_pred) if a == c and b == c)
        fp = sum(1 for a, b in zip(labels_true, labels_pred) if a != c and b == c)
        fn = sum(1 for a, b in zip(labels_true, labels_pred) if a == c and b != c)
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec  = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1   = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        per_class[c] = {
            "precision": round(prec, 4),
            "recall":    round(rec,  4),
            "f1":        round(f1,   4),
            "support":   tp + fn,
        }

    # Macro averages
    macro_p = sum(v["precision"] for v in per_class.values()) / len(per_class) if per_class else 0
    macro_r = sum(v["recall"]    for v in per_class.values()) / len(per_class) if per_class else 0
    macro_f1= sum(v["f1"]        for v in per_class.values()) / len(per_class) if per_class else 0

    return {
        "n":              n,
        "accuracy":       round(agree / n, 4) if n else 0,
        "macro_precision":round(macro_p, 4),
        "macro_recall":   round(macro_r, 4),
        "macro_f1":       round(macro_f1, 4),
        "per_class":      per_class,
        "categories":     categories,
    }


# ── Disagreement analysis ────────────────────────────────────────────────

def find_disagreements(data: dict) -> list[dict]:
    """Find items where annotators disagree and report details."""
    disagreements = []
    for idx, item_id in enumerate(data["item_ids"]):
        gold = data["gold"][idx]
        ki   = data["kittipat"][idx]
        ma   = data["mayuree"][idx]
        llm  = data["llm"][idx]

        labels_humans = {gold, ki, ma}
        if len(labels_humans) > 1 or llm != gold:
            gs_id = None
            for ak in data["answer_key_raw"]:
                if ak["item_id"] == item_id:
                    gs_id = ak["gs_id"]
                    break
            disagreements.append({
                "item_id":      item_id,
                "gs_id":        gs_id,
                "gold":         gold,
                "kittipat":     ki,
                "mayuree":      ma,
                "llm":          llm,
                "llm_correct":  llm == gold,
                "human_agree":  len(labels_humans) == 1,
            })
    return disagreements


# ── Interpretation ───────────────────────────────────────────────────────

def interpret_kappa(k: float) -> str:
    if k >= 0.81: return "Almost perfect"
    if k >= 0.61: return "Substantial"
    if k >= 0.41: return "Moderate"
    if k >= 0.21: return "Fair"
    return "Slight"


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    output_dir = PROJECT_ROOT / "output" / "ait"
    data = load_data(output_dir)
    n = len(data["item_ids"])

    print(f"\n{'='*70}")
    print(f"  D3-GROUNDED ANNOTATOR AGREEMENT STUDY (N={n})")
    print(f"  Annotators: author_gold (majority-vote), kittipat, mayuree, llm")
    print(f"{'='*70}")

    # ── Section 1: 3-Human IRR (Gold Standard) ───────────────────────────
    print(f"\n{'-'*70}")
    print("  SECTION 1 — HUMAN INTER-RATER RELIABILITY (author, kittipat, mayuree)")
    print(f"{'-'*70}")

    # Fleiss' Kappa — 3 human annotators (the IRR gold)
    ratings_3human = [[g, k, m] for g, k, m in
                      zip(data["gold"], data["kittipat"], data["mayuree"])]
    fk_3human = fleiss_kappa(ratings_3human)
    print(f"\n  Fleiss' Kappa (3 humans, multi-class): {fk_3human:.4f}  [{interpret_kappa(fk_3human)}]")

    # Binary Fleiss'
    gold_bin = [to_binary(l) for l in data["gold"]]
    ki_bin   = [to_binary(l) for l in data["kittipat"]]
    ma_bin   = [to_binary(l) for l in data["mayuree"]]
    ratings_bin = [[g, k, m] for g, k, m in zip(gold_bin, ki_bin, ma_bin)]
    fk_bin = fleiss_kappa(ratings_bin)
    print(f"  Fleiss' Kappa (3 humans, binary deontic/non): {fk_bin:.4f}  [{interpret_kappa(fk_bin)}]")

    # Pairwise Cohen's κ among humans
    ck_gold_ki = cohens_kappa(data["gold"], data["kittipat"])
    ck_gold_ma = cohens_kappa(data["gold"], data["mayuree"])
    ck_ki_ma   = cohens_kappa(data["kittipat"], data["mayuree"])
    print(f"\n  Pairwise Cohen's Kappa (multi-class):")
    print(f"    Gold vs Kittipat  : {ck_gold_ki:.4f}  [{interpret_kappa(ck_gold_ki)}]")
    print(f"    Gold vs Mayuree   : {ck_gold_ma:.4f}  [{interpret_kappa(ck_gold_ma)}]")
    print(f"    Kittipat vs Mayuree: {ck_ki_ma:.4f}  [{interpret_kappa(ck_ki_ma)}]")

    # Agreement rates
    for name, l1, l2 in [
        ("Gold vs Kittipat",   data["gold"],     data["kittipat"]),
        ("Gold vs Mayuree",    data["gold"],     data["mayuree"]),
        ("Kittipat vs Mayuree",data["kittipat"], data["mayuree"]),
    ]:
        agree = sum(1 for a, b in zip(l1, l2) if a == b)
        print(f"    {name:22s}: {agree}/{n} = {agree/n:.1%} raw agreement")

    # ── Section 2: LLM Classification Accuracy ───────────────────────────
    print(f"\n{'-'*70}")
    print("  SECTION 2 — LLM CLASSIFICATION ACCURACY vs HUMAN GOLD")
    print(f"{'-'*70}")

    llm_metrics = per_class_metrics(data["gold"], data["llm"])
    ck_llm_gold = cohens_kappa(data["gold"], data["llm"])
    ck_llm_ki   = cohens_kappa(data["kittipat"], data["llm"])
    ck_llm_ma   = cohens_kappa(data["mayuree"],  data["llm"])

    print(f"\n  LLM Accuracy (vs majority-vote gold)    : {llm_metrics['accuracy']:.4f}  ({llm_metrics['accuracy']*n:.0f}/{n})")
    print(f"  LLM Macro F1 (vs majority-vote gold)    : {llm_metrics['macro_f1']:.4f}")
    print(f"  LLM Cohen kappa (vs gold)               : {ck_llm_gold:.4f}  [{interpret_kappa(ck_llm_gold)}]")
    print(f"  LLM Cohen kappa (vs Kittipat)           : {ck_llm_ki:.4f}  [{interpret_kappa(ck_llm_ki)}]")
    print(f"  LLM Cohen kappa (vs Mayuree)            : {ck_llm_ma:.4f}  [{interpret_kappa(ck_llm_ma)}]")

    print(f"\n  Per-class breakdown (LLM vs Gold):")
    print(f"    {'Class':<15} {'Precision':>10} {'Recall':>8} {'F1':>8} {'Support':>8}")
    for cls, m in llm_metrics["per_class"].items():
        print(f"    {cls:<15} {m['precision']:>10.4f} {m['recall']:>8.4f} {m['f1']:>8.4f} {m['support']:>8}")

    # Also include LLM in 4-annotator Fleiss'
    ratings_4 = [[g, k, m, l] for g, k, m, l in
                 zip(data["gold"], data["kittipat"], data["mayuree"], data["llm"])]
    fk_4annotators = fleiss_kappa(ratings_4)
    print(f"\n  Fleiss Kappa (4 annotators incl. LLM)  : {fk_4annotators:.4f}  [{interpret_kappa(fk_4annotators)}]")

    # ── Section 3: Disagreement Analysis ────────────────────────────────
    disagreements = find_disagreements(data)
    llm_errors = [d for d in disagreements if not d["llm_correct"]]
    print(f"\n{'-'*70}")
    print(f"  SECTION 3 — DISAGREEMENTS")
    print(f"{'-'*70}")
    print(f"  Human disagreements  : {sum(1 for d in disagreements if not d['human_agree'])}/{n}")
    print(f"  LLM errors vs gold   : {len(llm_errors)}/{n}  (accuracy = {(n - len(llm_errors))/n:.1%})")

    if llm_errors:
        print(f"\n  LLM errors:")
        for d in llm_errors:
            print(f"    {d['gs_id']:8s}  Gold={d['gold']:12s}  LLM={d['llm']:12s}  "
                  f"Ki={d['kittipat']:12s}  Ma={d['mayuree']:12s}")

    # ── Label distributions ───────────────────────────────────────────────
    print(f"\n{'-'*70}")
    print(f"  LABEL DISTRIBUTIONS")
    print(f"{'-'*70}")
    for name, labels in [("Gold",     data["gold"]),
                          ("Kittipat", data["kittipat"]),
                          ("Mayuree",  data["mayuree"]),
                          ("LLM",      data["llm"])]:
        dist = dict(Counter(labels))
        print(f"  {name:<10}: {dist}")

    # ── Save results ──────────────────────────────────────────────────────
    results = {
        "dataset":    "D3 — Full AIT Corpus (50-item stratified sample)",
        "n_items":    n,
        "annotators": ["author_gold (majority-vote)", "kittipat", "mayuree", "llm"],
        "human_irr": {
            "fleiss_kappa_multiclass":    round(fk_3human, 4),
            "fleiss_interpretation":      interpret_kappa(fk_3human),
            "fleiss_kappa_binary":        round(fk_bin, 4),
            "fleiss_binary_interpretation": interpret_kappa(fk_bin),
            "pairwise_cohens_kappa": {
                "gold_vs_kittipat":  round(ck_gold_ki, 4),
                "gold_vs_mayuree":   round(ck_gold_ma, 4),
                "kittipat_vs_mayuree": round(ck_ki_ma, 4),
            },
            "distribution": {
                "gold":     dict(Counter(data["gold"])),
                "kittipat": dict(Counter(data["kittipat"])),
                "mayuree":  dict(Counter(data["mayuree"])),
            },
        },
        "llm_accuracy": {
            "accuracy":            llm_metrics["accuracy"],
            "macro_precision":     llm_metrics["macro_precision"],
            "macro_recall":        llm_metrics["macro_recall"],
            "macro_f1":            llm_metrics["macro_f1"],
            "cohens_kappa_vs_gold":      round(ck_llm_gold, 4),
            "cohens_kappa_interpretation": interpret_kappa(ck_llm_gold),
            "cohens_kappa_vs_kittipat":  round(ck_llm_ki, 4),
            "cohens_kappa_vs_mayuree":   round(ck_llm_ma, 4),
            "per_class":           llm_metrics["per_class"],
            "n_correct":           int(llm_metrics["accuracy"] * n),
            "n_errors":            len(llm_errors),
            "distribution": dict(Counter(data["llm"])),
        },
        "four_annotator_fleiss_kappa": round(fk_4annotators, 4),
        "llm_errors": llm_errors,
        "n_human_disagreements": sum(1 for d in disagreements if not d["human_agree"]),
    }

    out_path = output_dir / "external_annotator_agreement.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Saved: {out_path}")

    # ── Summary ───────────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"  SUMMARY (D3-grounded, N=50)")
    print(f"{'='*70}")
    print(f"  Human IRR -- Fleiss kappa (3 humans, multi-class): {fk_3human:.4f}  [{interpret_kappa(fk_3human)}]")
    print(f"  Human IRR -- Fleiss kappa (binary):               {fk_bin:.4f}  [{interpret_kappa(fk_bin)}]")
    print(f"  LLM Accuracy vs Human Gold                      : {llm_metrics['accuracy']:.4f}  ({int(llm_metrics['accuracy']*n)}/{n})")
    print(f"  LLM Macro F1                                    : {llm_metrics['macro_f1']:.4f}")
    print(f"  LLM Cohen kappa vs Gold                         : {ck_llm_gold:.4f}  [{interpret_kappa(ck_llm_gold)}]")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
