"""
Evaluation Config Helper
========================
Provides corpus-aware path resolution for evaluation scripts.
Instead of hardcoding paths to AIT-specific files, evaluation scripts
can import these helpers to work with any configured corpus.

Usage::

    from evaluation.eval_config import get_eval_paths, get_eval_namespace

    paths = get_eval_paths()          # returns (gold_shapes, test_data, ontology, generated_shapes)
    ns    = get_eval_namespace()      # returns rdflib.Namespace
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Tuple

from rdflib import Namespace

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def _corpus_name() -> str:
    """Determine active corpus from environment (default: ait)."""
    return os.environ.get("POLICYCHECKER_CORPUS", "ait")


def get_eval_paths(corpus: str | None = None) -> Tuple[Path, Path, Path, Path]:
    """Return (gold_shapes, test_data, ontology, generated_shapes_dir) for the corpus.

    Falls back to hardcoded AIT paths if the corpus config is unavailable.
    """
    corpus = corpus or _corpus_name()

    try:
        from langgraph_agent.corpus_config import get_corpus_config
        cfg = get_corpus_config(corpus)
        generated_dir = PROJECT_ROOT / "output" / corpus
        return cfg.gold_shapes_path, cfg.test_data_path, cfg.ontology_path, generated_dir
    except Exception:
        # Fallback to legacy AIT paths
        return (
            PROJECT_ROOT / "shacl" / "shapes"    / "ait_policy_shapes.ttl",
            PROJECT_ROOT / "shacl" / "test_data" / "tdd_test_data_fixed.ttl",
            PROJECT_ROOT / "shacl" / "ontology"  / "ait_policy_ontology.ttl",
            PROJECT_ROOT / "output" / "ait",
        )


def get_eval_namespace(corpus: str | None = None) -> Namespace:
    """Return the RDF Namespace for the corpus."""
    corpus = corpus or _corpus_name()

    try:
        from langgraph_agent.corpus_config import get_corpus_config
        cfg = get_corpus_config(corpus)
        return Namespace(cfg.namespace)
    except Exception:
        return Namespace("http://example.org/ait-policy#")


def get_eval_prefix(corpus: str | None = None) -> str:
    """Return the Turtle prefix string (e.g. 'ait') for the corpus."""
    corpus = corpus or _corpus_name()

    try:
        from langgraph_agent.corpus_config import get_corpus_config
        cfg = get_corpus_config(corpus)
        return cfg.prefix
    except Exception:
        return "ait"
