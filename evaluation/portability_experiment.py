"""
Portability Experiment — Cross-Domain Pipeline Evaluation
==========================================================
Tests the pipeline's ability to generalize beyond the AIT corpus by
processing a small set of GDPR policy rules and comparing results
with and without the Corpus Adapter vocabulary injection.

This produces quantitative evidence for the Discussion section:
- With adapter:    vocabulary-guided property generation
- Without adapter: open-vocabulary (no property hints)

Usage:
    python -m evaluation.portability_experiment
    python -m evaluation.portability_experiment --save
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Optional

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ── GDPR sample rules (manually curated for the experiment) ──────────────
GDPR_RULES = [
    {
        "rule_id": "GDPR-001",
        "text": "Data controllers must obtain explicit consent from data subjects before processing their personal data.",
        "rule_type": "obligation",
        "expected_property": "obtainExplicitConsent",
    },
    {
        "rule_id": "GDPR-002",
        "text": "Organizations must not transfer personal data to third countries without adequate safeguards.",
        "rule_type": "prohibition",
        "expected_property": "transferDataWithoutSafeguards",
    },
    {
        "rule_id": "GDPR-003",
        "text": "Data subjects may request access to their personal data at any time.",
        "rule_type": "permission",
        "expected_property": "requestDataAccess",
    },
    {
        "rule_id": "GDPR-004",
        "text": "Controllers must notify the supervisory authority of a personal data breach within 72 hours.",
        "rule_type": "obligation",
        "expected_property": "notifyDataBreach",
    },
    {
        "rule_id": "GDPR-005",
        "text": "Organizations must appoint a Data Protection Officer when processing operations require regular monitoring.",
        "rule_type": "obligation",
        "expected_property": "appointDataProtectionOfficer",
    },
    {
        "rule_id": "GDPR-006",
        "text": "Data subjects may request the erasure of their personal data under the right to be forgotten.",
        "rule_type": "permission",
        "expected_property": "requestErasure",
    },
    {
        "rule_id": "GDPR-007",
        "text": "Processors must not engage another processor without prior written authorization of the controller.",
        "rule_type": "prohibition",
        "expected_property": "processPersonalData",
    },
    {
        "rule_id": "GDPR-008",
        "text": "Controllers must conduct a data protection impact assessment before processing that is likely to result in high risk.",
        "rule_type": "obligation",
        "expected_property": "conductDataProtectionImpactAssessment",
    },
    {
        "rule_id": "GDPR-009",
        "text": "Data subjects may object to the processing of their personal data for direct marketing purposes.",
        "rule_type": "permission",
        "expected_property": "objectToProcessing",
    },
    {
        "rule_id": "GDPR-010",
        "text": "Organizations must implement appropriate technical and organizational measures to ensure data security.",
        "rule_type": "obligation",
        "expected_property": "implementSecurityMeasures",
    },
    {
        "rule_id": "GDPR-011",
        "text": "Controllers must maintain records of processing activities under their responsibility.",
        "rule_type": "obligation",
        "expected_property": "maintainProcessingRecords",
    },
    {
        "rule_id": "GDPR-012",
        "text": "Data subjects may request restriction of processing when the accuracy of data is contested.",
        "rule_type": "permission",
        "expected_property": "restrictProcessing",
    },
    {
        "rule_id": "GDPR-013",
        "text": "Organizations must not process personal data of children under 16 without parental consent.",
        "rule_type": "prohibition",
        "expected_property": "obtainParentalConsent",
    },
    {
        "rule_id": "GDPR-014",
        "text": "Controllers must provide clear and transparent privacy notices to data subjects.",
        "rule_type": "obligation",
        "expected_property": "providePrivacyNotice",
    },
    {
        "rule_id": "GDPR-015",
        "text": "Data subjects may request portability of their personal data in a structured, commonly used format.",
        "rule_type": "permission",
        "expected_property": "requestDataPortability",
    },
]


@dataclass
class PortabilityResult:
    """Result of processing one rule in a specific configuration."""
    rule_id: str
    rule_type: str
    expected_property: str
    generated_property: str
    deontic_correct: bool
    property_match: str  # "exact" | "fuzzy" | "miss"
    fol_formula: str
    config: str  # "with_adapter" | "without_adapter"


def _run_fol_for_rule(text: str, rule_type: str, vocabulary_hint: str) -> dict:
    """Run the FOL generation for a single rule with a given vocabulary hint."""
    from langchain_core.messages import HumanMessage
    from langgraph_agent.llm import get_llm

    prompt = f"""\
You are a formal logician specialising in deontic logic for institutional policy.

Convert the policy rule below into a First-Order Logic (FOL) formula using \
deontic operators:
  O(φ) — Obligation: the subject MUST perform φ
  P(φ) — Permission: the subject MAY perform φ
  F(φ) — Prohibition (Forbidden): the subject MUST NOT perform φ

Rule type: {rule_type}
Rule text: "{text}"

DOMAIN VOCABULARY — When choosing a predicate name for the action, you MUST \
prefer one from this list of known policy properties. Pick the \
one that BEST matches the rule's main action or constraint:
{vocabulary_hint}

If NO property in the list is a reasonable match, you may create a new \
camelCase predicate — but this should be rare.

Output ONLY a JSON object (no markdown):
{{
  "deontic_type": "obligation"/"permission"/"prohibition",
  "deontic_formula": "O/P/F(predicate(subject))",
  "fol_expansion": "∀x (Subject(x) ∧ Condition(x) → O/P/F(Action(x)))",
  "predicates": {{"subject": "...", "action": "...", "condition": "..."}},
  "shacl_hint": "brief hint for SHACL translation"
}}"""

    llm = get_llm()
    response = llm.invoke([HumanMessage(content=prompt)])
    raw = response.content

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {}


def _extract_property(parsed: dict) -> str:
    """Extract the property name from parsed FOL output."""
    # Try from deontic_formula: O(obtainExplicitConsent(dataController))
    formula = parsed.get("deontic_formula", "")
    m = re.search(r"[OPF]\(([a-zA-Z_]\w*)", formula)
    if m:
        return m.group(1)

    # Try from predicates.action
    preds = parsed.get("predicates", {})
    if isinstance(preds, dict):
        action = preds.get("action", "")
        if isinstance(action, str) and len(action) > 1:
            return action

    return ""


def _match_property(generated: str, expected: str) -> str:
    """Check if generated property matches expected."""
    if not generated:
        return "miss"
    if generated.lower() == expected.lower():
        return "exact"

    # Fuzzy: check if key words overlap
    import difflib
    ratio = difflib.SequenceMatcher(None, generated.lower(), expected.lower()).ratio()
    if ratio >= 0.6:
        return "fuzzy"

    return "miss"


def run_experiment(save: bool = False) -> dict:
    """Run the portability experiment in two configurations."""
    from langgraph_agent.corpus_config import get_corpus_config

    print("=" * 60)
    print("  PORTABILITY EXPERIMENT — Cross-Domain Pipeline Evaluation")
    print("=" * 60)

    results_with: List[PortabilityResult] = []
    results_without: List[PortabilityResult] = []

    # ── Configuration A: WITH Corpus Adapter (GDPR vocabulary) ──
    print("\n▶ Configuration A: WITH Corpus Adapter (GDPR vocabulary)")
    print("-" * 60)

    os.environ["POLICYCHECKER_CORPUS"] = "gdpr"
    from langgraph_agent.corpus_config import reset_config_cache
    reset_config_cache()
    cfg = get_corpus_config("gdpr")
    vocab_hint = cfg.vocabulary_hint()

    from tqdm import tqdm
    for rule in tqdm(GDPR_RULES, desc="With adapter", leave=False):
        parsed = _run_fol_for_rule(rule["text"], rule["rule_type"], vocab_hint)
        gen_prop = _extract_property(parsed)
        deontic_type = parsed.get("deontic_type", "")
        formula = parsed.get("deontic_formula", "")

        results_with.append(PortabilityResult(
            rule_id=rule["rule_id"],
            rule_type=rule["rule_type"],
            expected_property=rule["expected_property"],
            generated_property=gen_prop,
            deontic_correct=deontic_type.lower() == rule["rule_type"].lower(),
            property_match=_match_property(gen_prop, rule["expected_property"]),
            fol_formula=formula,
            config="with_adapter",
        ))

    # ── Configuration B: WITHOUT Corpus Adapter (open vocabulary) ──
    print("\n▶ Configuration B: WITHOUT Corpus Adapter (open vocabulary)")
    print("-" * 60)

    no_vocab_hint = "(no domain vocabulary available — create a new camelCase predicate)"

    for rule in tqdm(GDPR_RULES, desc="Without adapter", leave=False):
        parsed = _run_fol_for_rule(rule["text"], rule["rule_type"], no_vocab_hint)
        gen_prop = _extract_property(parsed)
        deontic_type = parsed.get("deontic_type", "")
        formula = parsed.get("deontic_formula", "")

        results_without.append(PortabilityResult(
            rule_id=rule["rule_id"],
            rule_type=rule["rule_type"],
            expected_property=rule["expected_property"],
            generated_property=gen_prop,
            deontic_correct=deontic_type.lower() == rule["rule_type"].lower(),
            property_match=_match_property(gen_prop, rule["expected_property"]),
            fol_formula=formula,
            config="without_adapter",
        ))

    # Reset back to AIT
    os.environ["POLICYCHECKER_CORPUS"] = "ait"
    reset_config_cache()

    # ── Compute metrics ──
    report = _compute_metrics(results_with, results_without)
    _print_report(report, results_with, results_without)

    if save:
        out_dir = PROJECT_ROOT / "output" / "portability_experiment"
        out_dir.mkdir(parents=True, exist_ok=True)

        # Save detailed results
        (out_dir / "results_with_adapter.json").write_text(
            json.dumps([asdict(r) for r in results_with], indent=2), encoding="utf-8"
        )
        (out_dir / "results_without_adapter.json").write_text(
            json.dumps([asdict(r) for r in results_without], indent=2), encoding="utf-8"
        )
        (out_dir / "portability_report.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )
        print(f"\nSaved results to: {out_dir}")

    return report


def _compute_metrics(with_adapter: list, without_adapter: list) -> dict:
    """Compute comparison metrics."""
    def _stats(results):
        n = len(results)
        deontic_correct = sum(1 for r in results if r.deontic_correct)
        exact_match = sum(1 for r in results if r.property_match == "exact")
        fuzzy_match = sum(1 for r in results if r.property_match == "fuzzy")
        miss = sum(1 for r in results if r.property_match == "miss")
        return {
            "n": n,
            "deontic_accuracy": round(deontic_correct / n, 3) if n else 0,
            "property_exact": exact_match,
            "property_fuzzy": fuzzy_match,
            "property_miss": miss,
            "property_match_rate": round((exact_match + fuzzy_match) / n, 3) if n else 0,
        }

    return {
        "with_adapter": _stats(with_adapter),
        "without_adapter": _stats(without_adapter),
        "n_rules": len(GDPR_RULES),
        "corpus": "GDPR",
    }


def _print_report(report: dict, with_results: list, without_results: list):
    """Print a formatted comparison report."""
    w = report["with_adapter"]
    wo = report["without_adapter"]

    print(f"\n{'=' * 60}")
    print(f"  PORTABILITY EXPERIMENT RESULTS")
    print(f"{'=' * 60}")
    print(f"  Corpus: GDPR ({report['n_rules']} rules)")
    print()
    print(f"  {'Metric':<30s} {'With Adapter':>15s} {'Without':>15s}")
    print(f"  {'-'*60}")
    print(f"  {'Deontic type accuracy':<30s} {w['deontic_accuracy']:>15.1%} {wo['deontic_accuracy']:>15.1%}")
    print(f"  {'Property exact match':<30s} {w['property_exact']:>15d} {wo['property_exact']:>15d}")
    print(f"  {'Property fuzzy match':<30s} {w['property_fuzzy']:>15d} {wo['property_fuzzy']:>15d}")
    print(f"  {'Property miss':<30s} {w['property_miss']:>15d} {wo['property_miss']:>15d}")
    print(f"  {'Property match rate':<30s} {w['property_match_rate']:>15.1%} {wo['property_match_rate']:>15.1%}")
    print(f"  {'-'*60}")

    delta = w['property_match_rate'] - wo['property_match_rate']
    print(f"\n  Δ Property match rate: {delta:+.1%} (adapter advantage)")

    print(f"\n  Per-rule detail (WITH adapter):")
    for r in with_results:
        status = "✓" if r.property_match in ("exact", "fuzzy") else "✗"
        print(f"    {status} {r.rule_id}: {r.generated_property:<40s} (expected: {r.expected_property})")

    print(f"\n  Per-rule detail (WITHOUT adapter):")
    for r in without_results:
        status = "✓" if r.property_match in ("exact", "fuzzy") else "✗"
        print(f"    {status} {r.rule_id}: {r.generated_property:<40s} (expected: {r.expected_property})")

    print(f"\n{'=' * 60}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Portability Experiment")
    parser.add_argument("--save", action="store_true", help="Save results to output/portability_experiment/")
    args = parser.parse_args()
    run_experiment(save=args.save)


if __name__ == "__main__":
    main()
