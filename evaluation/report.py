"""
Thesis Metrics Report — D3-Grounded (M3, M5, IRR, LLM Accuracy)
=================================================================
Computes the D3-grounded thesis metrics after retiring D1.

Retained metrics:
  M3 — FOL Quality Rate       (purely D3-based)
  M5 — Output Stability       (hash of shapes_generated.ttl)

New D3-grounded metrics:
  IRR — Fleiss' Kappa (3 human annotators on 50-item D3 sample)
  LLM — Classification Accuracy vs human majority-vote gold

Removed (D1/D2-dependent):
  M1 — Extraction Coverage    (required D2 SHACL gold alignment)
  M2 — Classification Accuracy via D1 alignment
  M4 — Shape Correctness F1   (required D2 Pos/Neg test entities)

Usage:
    python -m evaluation.report           # pretty-print + JSON output
    python -m evaluation.report --md      # Markdown table for thesis
    python -m evaluation.report --save    # also write thesis_metrics.json
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent


# ── Metric dataclass ───────────────────────────────────────────────────────

@dataclass
class MetricsReport:
    """D3-grounded thesis metrics."""

    # M3 — FOL Quality Rate
    m3_fol_quality: float = 0.0
    m3_semantic: int = 0
    m3_total_fol: int = 0

    # M5 — Reproducibility
    m5_reproducible: Optional[bool] = None

    # D3 Pipeline Statistics
    d3_sentences_extracted:   int = 0
    d3_candidates_prefiltered: int = 0
    d3_rules_classified:      int = 0
    d3_rules_obligation:      int = 0
    d3_rules_permission:      int = 0
    d3_rules_prohibition:     int = 0
    d3_fol_ok:                int = 0
    d3_fol_failed:            int = 0
    d3_shacl_shapes_total:    int = 0
    d3_shacl_shapes_valid:    int = 0
    d3_shacl_fol_mediated:    int = 0
    d3_shacl_direct_nl:       int = 0

    # Human IRR (3 annotators: author, Kittipat, Mayuree)
    irr_n_items:                   int = 50
    irr_fleiss_kappa_multiclass:   float = 0.0
    irr_fleiss_interpretation:     str = ""
    irr_fleiss_kappa_binary:       float = 0.0
    irr_kappa_gold_vs_kittipat:    float = 0.0
    irr_kappa_gold_vs_mayuree:     float = 0.0
    irr_kappa_kittipat_vs_mayuree: float = 0.0

    # LLM Classification Accuracy (vs 50-item human gold)
    llm_accuracy:       float = 0.0
    llm_macro_f1:       float = 0.0
    llm_cohens_kappa:   float = 0.0
    llm_kappa_interpretation: str = ""
    llm_n_correct:      int = 0
    llm_n_total:        int = 0


# ── Metric computations ───────────────────────────────────────────────────

_PLACEHOLDER_PREDS = re.compile(
    r"[OPF]\(\s*(Action|Subject|Predicate|Condition|Thing|Entity|x|y|z|\?\w)\s*[()]",
    re.IGNORECASE,
)


def compute_m3(fol_formulas: list[dict]) -> tuple[float, int, int]:
    """M3 — FOL quality rate: fraction of FOL formulas with non-placeholder predicates."""
    _PLACEHOLDER_ACTIONS = {
        "action", "subject", "predicate", "condition",
        "thing", "entity", "x", "y", "z", "n", "m",
    }
    total = len(fol_formulas)
    placeholders = 0
    for f in fol_formulas:
        formula   = f.get("deontic_formula", "")
        expansion = f.get("fol_expansion", "")
        formula_is_ph   = _PLACEHOLDER_PREDS.search(formula)   if formula   else True
        expansion_is_ph = _PLACEHOLDER_PREDS.search(expansion) if expansion else True
        preds = f.get("predicates") or {}
        raw_action = preds.get("action", "") if isinstance(preds, dict) else ""
        if isinstance(raw_action, (dict, list)):
            raw_action = " ".join(str(v) for v in
                                  (raw_action.values() if isinstance(raw_action, dict) else raw_action))
        action = str(raw_action).strip()
        action_is_semantic = len(action) > 1 and action.lower() not in _PLACEHOLDER_ACTIONS
        if formula_is_ph and expansion_is_ph and not action_is_semantic:
            placeholders += 1
    semantic = total - placeholders
    return (semantic / total if total else 0.0), semantic, total


def compute_m5(output_dir: Path) -> Optional[bool]:
    """M5 — Output stability: hash shapes_generated.ttl and compare to stored hash."""
    shapes_path = output_dir / "shapes_generated.ttl"
    hash_path   = output_dir / ".m5_hash"
    if not shapes_path.exists():
        return None
    current_hash = hashlib.sha256(shapes_path.read_bytes()).hexdigest()[:8]
    if hash_path.exists():
        previous_hash = hash_path.read_text(encoding="utf-8").strip()
        match = current_hash == previous_hash
        hash_path.write_text(current_hash, encoding="utf-8")
        return match
    else:
        hash_path.write_text(current_hash, encoding="utf-8")
        return None


# ── Aggregate report ──────────────────────────────────────────────────────

def build_report(source: str = "ait") -> MetricsReport:
    """Load all intermediate outputs and compute D3-grounded metrics."""
    out = PROJECT_ROOT / "output" / source

    fol_formulas    = _load_json(out / "fol_formulas.json", [])
    pipeline_report = _load_json(out / "pipeline_report.json", {})
    irr_data        = _load_json(out / "external_annotator_agreement.json", {})

    # M3
    m3_val, m3_sem, m3_total = compute_m3(fol_formulas)

    # M5
    m5 = compute_m5(out)

    # D3 pipeline stats
    ps = pipeline_report.get("summary", {})
    rule_dist = pipeline_report.get("rule_type_distribution", {})

    # IRR (3-human)
    h_irr = irr_data.get("human_irr", {})
    pk    = h_irr.get("pairwise_cohens_kappa", {})

    # LLM accuracy
    llm_acc = irr_data.get("llm_accuracy", {})

    report = MetricsReport(
        # M3
        m3_fol_quality=m3_val,
        m3_semantic=m3_sem,
        m3_total_fol=m3_total,

        # M5
        m5_reproducible=m5,

        # D3 stats
        d3_sentences_extracted=    ps.get("sentences_extracted", 0),
        d3_candidates_prefiltered= ps.get("candidates_prefiltered", 0),
        d3_rules_classified=       ps.get("rules_classified", 0),
        d3_rules_obligation=       rule_dist.get("obligation", 0),
        d3_rules_permission=       rule_dist.get("permission", 0),
        d3_rules_prohibition=      rule_dist.get("prohibition", 0),
        d3_fol_ok=                 ps.get("fol_formulas_ok", 0),
        d3_fol_failed=             ps.get("fol_formulas_failed", 0),
        d3_shacl_shapes_total=     ps.get("shacl_shapes_total", 0),
        d3_shacl_shapes_valid=     ps.get("shacl_shapes_valid", 0),
        d3_shacl_fol_mediated=     ps.get("shacl_shapes_fol_mediated", 0),
        d3_shacl_direct_nl=        ps.get("shacl_shapes_direct_nl", 0),

        # IRR
        irr_n_items=                    irr_data.get("n_items", 50),
        irr_fleiss_kappa_multiclass=    h_irr.get("fleiss_kappa_multiclass", 0.0),
        irr_fleiss_interpretation=      h_irr.get("fleiss_interpretation", ""),
        irr_fleiss_kappa_binary=        h_irr.get("fleiss_kappa_binary", 0.0),
        irr_kappa_gold_vs_kittipat=     pk.get("gold_vs_kittipat", 0.0),
        irr_kappa_gold_vs_mayuree=      pk.get("gold_vs_mayuree", 0.0),
        irr_kappa_kittipat_vs_mayuree=  pk.get("kittipat_vs_mayuree", 0.0),

        # LLM accuracy
        llm_accuracy=       llm_acc.get("accuracy", 0.0),
        llm_macro_f1=       llm_acc.get("macro_f1", 0.0),
        llm_cohens_kappa=   llm_acc.get("cohens_kappa_vs_gold", 0.0),
        llm_kappa_interpretation= llm_acc.get("cohens_kappa_interpretation", ""),
        llm_n_correct=      llm_acc.get("n_correct", 0),
        llm_n_total=        irr_data.get("n_items", 50),
    )
    return report


def _load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


# ── Formatters ─────────────────────────────────────────────────────────────

def format_console(r: MetricsReport) -> str:
    _m5 = ("PASS (hash-identical to previous run)" if r.m5_reproducible is True
           else "FAIL (output changed)" if r.m5_reproducible is False
           else "NOT YET TESTED (run report again to compare)")
    lines = [
        "",
        "=" * 65,
        "  THESIS METRICS REPORT  (D3-grounded)",
        "=" * 65,
        "",
        "  ── D3 CORPUS STATISTICS ──────────────────────────────────────",
        f"  Sentences extracted      : {r.d3_sentences_extracted:,}",
        f"  Pre-filter candidates    : {r.d3_candidates_prefiltered:,}  "
        f"({r.d3_candidates_prefiltered/r.d3_sentences_extracted*100:.1f}% of corpus)" if r.d3_sentences_extracted else "",
        f"  Rules classified (total) : {r.d3_rules_classified:,}",
        f"    Obligation  (O)        : {r.d3_rules_obligation:,}  "
        f"({r.d3_rules_obligation/r.d3_rules_classified*100:.1f}%)" if r.d3_rules_classified else "",
        f"    Permission  (P)        : {r.d3_rules_permission:,}  "
        f"({r.d3_rules_permission/r.d3_rules_classified*100:.1f}%)" if r.d3_rules_classified else "",
        f"    Prohibition (F)        : {r.d3_rules_prohibition:,}  "
        f"({r.d3_rules_prohibition/r.d3_rules_classified*100:.1f}%)" if r.d3_rules_classified else "",
        "",
        "  ── M3  FOL Quality Rate ──────────────────────────────────────",
        f"  M3 — FOL Quality Rate    : {r.m3_fol_quality:.1%}  "
        f"({r.m3_semantic}/{r.m3_total_fol} semantic predicates)",
        "",
        "  ── M5  Reproducibility ───────────────────────────────────────",
        f"  M5 — Output Stability    : {_m5}",
        "",
        "  -- IRR  Human Inter-Rater Reliability (N=50) --------------------",
        f"  Fleiss kappa (3 humans, multi-class) : {r.irr_fleiss_kappa_multiclass:.4f}  [{r.irr_fleiss_interpretation}]",
        f"  Fleiss kappa (binary deontic/non)    : {r.irr_fleiss_kappa_binary:.4f}",
        f"  Cohen kappa  Gold vs Kittipat        : {r.irr_kappa_gold_vs_kittipat:.4f}",
        f"  Cohen kappa  Gold vs Mayuree         : {r.irr_kappa_gold_vs_mayuree:.4f}",
        f"  Cohen kappa  Kittipat vs Mayuree     : {r.irr_kappa_kittipat_vs_mayuree:.4f}",
        "",
        "  -- LLM Classification Accuracy (N=50) ---------------------------",
        f"  Accuracy   (vs majority-vote gold) : {r.llm_accuracy:.4f}  ({r.llm_n_correct}/{r.llm_n_total})",
        f"  Macro F1   (vs majority-vote gold) : {r.llm_macro_f1:.4f}",
        f"  Cohen kappa (LLM vs gold)          : {r.llm_cohens_kappa:.4f}  [{r.llm_kappa_interpretation}]",
        "",
        "=" * 65,
    ]
    return "\n".join(lines)


def format_markdown(r: MetricsReport) -> str:
    _m5 = "PASS" if r.m5_reproducible is True else ("FAIL" if r.m5_reproducible is False else "Not yet tested")
    opc_total = r.d3_rules_obligation + r.d3_rules_permission + r.d3_rules_prohibition
    return f"""## Thesis Metrics — D3-Grounded Evaluation Results

### D3 Corpus Statistics

| Statistic | Value |
|-----------|------:|
| Total sentences extracted | {r.d3_sentences_extracted:,} |
| Pre-filter candidates | {r.d3_candidates_prefiltered:,} ({r.d3_candidates_prefiltered/r.d3_sentences_extracted*100:.1f}%) |
| Rules classified | **{r.d3_rules_classified:,}** |
| — Obligation (O) | {r.d3_rules_obligation} ({r.d3_rules_obligation/r.d3_rules_classified*100:.1f}%) |
| — Permission (P) | {r.d3_rules_permission} ({r.d3_rules_permission/r.d3_rules_classified*100:.1f}%) |
| — Prohibition (F) | {r.d3_rules_prohibition} ({r.d3_rules_prohibition/r.d3_rules_classified*100:.1f}%) |
| FOL formulas (ok / fail) | {r.d3_fol_ok} / {r.d3_fol_failed} |
| SHACL shapes (total / valid) | {r.d3_shacl_shapes_total} / {r.d3_shacl_shapes_valid} |

### Evaluation Metrics

| Metric | Definition | Value |
|--------|-----------|------:|
| **M3** FOL quality rate | Formulas with semantic predicates | **{r.m3_fol_quality:.1%}** ({r.m3_semantic}/{r.m3_total_fol}) |
| **M5** Reproducibility | Identical output across clean-cache runs | **{_m5}** |
| **IRR** Fleiss kappa (3 humans) | Human agreement on 50-item D3 sample | **{r.irr_fleiss_kappa_multiclass:.4f}** [{r.irr_fleiss_interpretation}] |
| **LLM** Accuracy | LLM vs majority-vote human gold (N=50) | **{r.llm_accuracy:.4f}** ({r.llm_n_correct}/{r.llm_n_total}) |
| **LLM** Macro F1 | Macro-averaged F1 across all classes | **{r.llm_macro_f1:.4f}** |
| **LLM** Cohen kappa | LLM vs gold agreement | **{r.llm_cohens_kappa:.4f}** [{r.llm_kappa_interpretation}] |
"""


# ── CLI entry point ───────────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Compute D3-grounded thesis metrics")
    parser.add_argument("--source", default="ait", help="Source institution (default: ait)")
    parser.add_argument("--md",   action="store_true", help="Output Markdown table")
    parser.add_argument("--save", action="store_true", help="Save JSON to output dir")
    args = parser.parse_args()

    report = build_report(args.source)

    if args.md:
        print(format_markdown(report))
    else:
        print(format_console(report))

    if args.save:
        out_dir  = PROJECT_ROOT / "output" / args.source
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "thesis_metrics.json"
        out_path.write_text(
            json.dumps(asdict(report), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
