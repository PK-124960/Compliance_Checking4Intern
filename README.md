# PolicyChecker — Automated Policy Formalization Pipeline

An end-to-end agentic pipeline that converts institutional policy documents (PDF) into machine-executable SHACL validation rules. Built as a thesis research project at the Asian Institute of Technology (AIT).

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Project Organization](#2-project-organization)
3. [Local Development Setup](#3-local-development-setup)
4. [Deployment with Docker](#4-deployment-with-docker)

---

## 1. Project Overview

PolicyChecker addresses the **Policy Compliance Gap** — the difficulty of translating hundreds of pages of natural language institutional policies into enforceable, machine-readable rules.

### What It Does

The pipeline takes PDF policy documents as input and automatically produces SHACL (Shapes Constraint Language) validation rules that can be run against a university's student database to detect compliance violations.

### Pipeline Stages

```
PDF Policies → Text Extraction → Rule Prefiltering → LLM Classification → FOL Formalization → SHACL Translation → Validation 
```

Report

| Stage | Description |
|-------|-------------|
| **Phase 1 — Extraction** | Extracts and segments sentences from PDF policy documents using `pdfplumber`, with optional sentence segmentation via spaCy sentencizer |
| **Phase 1b — Prefiltering** | Heuristically filters non-rule content using deontic markers, section-aware weighting, speech-act classification, and epistemic vs. deontic modal disambiguation |
| **Phase 2 — Classification** | Uses a local LLM (Mistral via Ollama) to classify candidate sentences as obligations, permissions, or prohibitions, enriched with contextual hints from the prefilter stage |
| **Phase 2c — Reclassification** | Performs a second-opinion LLM pass for uncertain classifications using a configurable secondary model |
| **Phase 3 — FOL Formalization** | Converts classified rules into First-Order Logic (FOL) formulas using deontic operators such as O(φ), P(φ), and F(φ), with placeholder rejection and retry handling |
| **Phase 4 — SHACL Generation (FOL-mediated)** | Translates FOL formulas into executable SHACL NodeShapes with confidence-weighted severity, named property shapes, and `sh:targetSubjectsOf` fallback targeting |
| **Phase 4b — SHACL Generation (NL fallback)** | Directly converts natural-language rules into SHACL for cases where FOL formalization fails, including an automatic syntax repair loop |
| **Phase 5 — Validation** | Merges generated SHACL shapes with gold-standard shapes and runs `pyshacl` validation against TDD test data, including false-positive triage |
| **Phase 6 — Reporting** | Produces a structured JSON report containing pipeline statistics, validation results, environment metadata, and severity breakdowns |

### Technology Stack

| Category | Technology | Purpose |
|----------|------------|---------|
| Agent Framework | LangGraph | Orchestrates the multi-step pipeline as a stateful graph |
| LLM | Mistral 7B via Ollama | Classification, FOL generation, SHACL generation |
| PDF Processing | pdfplumber, PyMuPDF | Text extraction from policy PDFs |
| RDF / SHACL | rdflib, pyshacl | Knowledge graph construction and SHACL validation |
| Web Dashboard | FastAPI, Jinja2 | Compliance results browser |
| Database | PostgreSQL | University student data (RDF source) |
| Cache | SQLite | LLM response cache to avoid redundant API calls |
| Package Manager | uv | Dependency management and virtual environment |
| Dev Environment | Docker + devcontainer | Reproducible development environment |

---

## 2. Project Organization

```
policy-checker/
│
├── .devcontainer/                  # VS Code devcontainer configuration
│   └── dev/
│       ├── devcontainer.json
│       └── devcontainer-lock.json
│
├── .env                            # Local secrets (never committed)
├── .env.example                    # Safe template — copy to .env to get started
├── dockerfile                      # Ubuntu 24.04 dev container image
├── docker-compose.yml              # Orchestrates dev + postgres + ollama
├── pyproject.toml                  # Project dependencies (uv)
├── uv.lock                         # Pinned dependency lockfile
│
├── docs/                           # Documentation
├── data/                           # Tabular / CSV data (placeholder)
├── models/                         # Model weights placeholder (see models/README.md)
├── notebooks/                      # Jupyter notebooks (placeholder)
├── logs/                           # Runtime logs (placeholder)
│
├── institutional_policy/           # Source PDF policy documents (research input)
│   └── AIT/
│       ├── AA-4-1-1 Academic Integrity (...).pdf
│       ├── FB-6-1-1 Credit Policy (...).pdf
│       ├── FS-1-1-1 Campus Accommodation (...).pdf
│       ├── PA-2-1-2 Ethical Behavior (...).pdf
│       └── Student-Handbook_August-2021.pdf
│
├── shacl/                          # RDF research artifacts (not Python code)
│   ├── ontology/
│   │   └── ait_policy_ontology.ttl     # AIT domain ontology
│   ├── shapes/
│   │   └── ait_policy_shapes.ttl       # Gold-standard SHACL shapes (ground truth)
│   └── test_data/
│       └── tdd_test_data_fixed.ttl     # TDD test fixtures (Pos/Neg entity pairs)
│
├── output/                         # Runtime pipeline outputs (git-ignored)
│   └── ait/
│       ├── classified_rules.json
│       ├── fol_formulas.json
│       ├── shapes_generated.ttl
│       ├── validation_results.json
│       └── pipeline_report.json
│
├── cache/                          # SQLite LLM response cache (git-ignored)
│   └── llm_cache.db
│
├── graphdb_data/                   # GraphDB runtime data (git-ignored)
│
└── src/
    └── policy_checker/             # Main Python package
        │
        ├── __init__.py             # Defines canonical PROJECT_ROOT
        │
        ├── core/                   # Shared services
        │   ├── llm_cache.py        # SQLite-backed LLM response cache (LRU)
        │   ├── prefilter.py        # Heuristic sentence pre-filter (deontic markers)
        │   └── mcp_server.py       # MCP JSON-RPC server for external tool access
        │
        ├── db/                     # PostgreSQL integration
        │   ├── connection.py       # psycopg2 connection manager
        │   ├── rdf_converter.py    # Converts DB rows to RDF Turtle (data graph)
        │   ├── seed.py             # Seeds realistic AIT demo data
        │   └── schema.sql          # Database schema (students, fees, accommodations...)
        │
        ├── models/        # LangGraph pipeline
        │   ├── graph.py            # Builds and compiles the StateGraph
        │   ├── state.py            # PipelineState TypedDict definition
        │   ├── llm.py              # ChatOllama factory (deterministic decoding)
        │   ├── run.py              # CLI entry point (--source, --verbose, --ablation)
        │   ├── _stubs.py           # No-op node stubs for incremental development
        │   ├── edges/
        │   │   └── route_classify.py   # Conditional routing after classification
        │   └── nodes/              # One file per pipeline node
        │       ├── extract.py          # Phase 1: PDF → sentences
        │       ├── prefilter.py        # Phase 2a: heuristic filter
        │       ├── classify.py         # Phase 2b: LLM classification
        │       ├── reclassify.py       # Phase 2c: second-opinion LLM
        │       ├── fol.py              # Phase 3: FOL generation
        │       ├── shacl.py            # Phase 4a: FOL → SHACL shapes
        │       ├── direct_shacl.py     # Phase 4b: NL fallback → SHACL
        │       ├── validate.py         # Phase 5: pyshacl validation
        │       └── report.py           # Phase 6: pipeline report
        │
        ├── evaluation/             # Thesis metrics (M1–M5)
        │   ├── align.py            # M1: align pipeline rules to gold shapes
        │   ├── per_rule_eval.py    # M4: per-rule Pos/Neg correctness test
        │   └── report.py           # M1–M5 aggregated metrics report
        │
        └── web/                    # Compliance dashboard (FastAPI)
            ├── app.py              # API routes + validation endpoint
            ├── static/
            │   ├── app.js
            │   └── style.css
            └── templates/
                └── index.html
```

---

## 3. Local Development Setup

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 24.0+
- [VS Code](https://code.visualstudio.com/) with the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension

> All Python dependencies, PostgreSQL, and Ollama run inside Docker. Nothing needs to be installed on your host machine beyond Docker and VS Code.

### Step 1 — Clone and configure environment

```bash
git clone [<repo-url>](https://github.com/A4niia/python-project-starter.git)
cd policy-checker

# Copy the env template and fill in values
cp .env.example .env
```

The only required change in `.env` for local dev is:

```bash
PROJECT_NAME=policy-checker   # must match your folder name
POSTGRES_HOST=postgres        # use service name, not localhost, inside Docker
```

### Step 2 — Start the containers

```bash
docker compose up -d
```

This starts three services:

| Service | Port | Purpose |
|---------|------|---------|
| `dev` | — | Ubuntu 24.04 dev container (`sleep infinity`) |
| `postgres` | 5432 | PostgreSQL 16 database |
| `ollama` | 11434 | Ollama LLM server |

### Step 3 — Open in VS Code devcontainer

1. Open the project folder in VS Code
2. When prompted, click **Reopen in Container**
   - Or press `Ctrl+Shift+P` → **Dev Containers: Reopen in Container**
3. VS Code attaches to the running `dev` container

### Step 4 — Install dependencies

Inside the VS Code terminal (you are now inside the container):

```bash
uv sync
```

### Step 5 — Pull the LLM model

From PowerShell on your **host machine** (not inside the container):

```bash
docker compose exec ollama ollama pull mistral
```

> Mistral 7B is approximately 4 GB. This only needs to be done once — the model is stored in the `ollama_data` Docker volume.

### Step 6 — Seed the database

```bash
uv run python -m policy_checker.database.seed
```

### Step 7 — Run the pipeline

```bash
# Standard run
uv run python -m policy_checker.models.run --source ait

# With per-step statistics
uv run python -m policy_checker.models.run --source ait --verbose

# Ablation study (thesis §7)
uv run python -m policy_checker.models.run --source ait --ablation no-hints
```

### Step 8 — Run the web dashboard

```bash
uv run uvicorn policy_checker.web.app:app --host=0.0.0.0 --port=8000
```

Open `http://localhost:8000` in your browser.

### Optional — Run evaluation metrics (M1–M5)

```bash
# Install evaluation dependencies first
uv sync --group eval

# Align pipeline rules to gold standard
uv run python -m policy_checker.evaluation.align

# Per-rule correctness evaluation
uv run python -m policy_checker.evaluation.per_rule_eval

# Full thesis metrics report
uv run python -m policy_checker.evaluation.report
uv run python -m policy_checker.evaluation.report --md   # Markdown table
```

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PROJECT_NAME` | Yes | — | Docker container/image name prefix |
| `POSTGRES_HOST` | Yes | `postgres` | Use `postgres` inside Docker, `localhost` outside |
| `POSTGRES_PORT` | No | `5432` | PostgreSQL port |
| `POSTGRES_DB` | Yes | `ait_database` | Database name |
| `POSTGRES_USER` | Yes | `myuser` | Database user |
| `POSTGRES_PASSWORD` | Yes | — | Database password |
| `OLLAMA_HOST` | Yes | `http://ollama:11434` | Ollama server URL |
| `OLLAMA_MODEL` | No | `mistral` | Primary LLM model |
| `OLLAMA_SECOND_MODEL` | No | `mistral` | Second-opinion model for reclassification |
| `OLLAMA_SEED` | No | `42` | Random seed for reproducibility (M5) |
| `PIPELINE_VERSION` | No | `dev` | Version tag in pipeline reports |
| `EXTRACT_SPACY` | No | `0` | Set to `1` to use spaCy sentence segmentation |
| `CACHE_MAX_ENTRIES` | No | `2000` | Max LLM cache entries before LRU eviction |

---

## 4. Deployment with Docker

The project uses a **devcontainer pattern** — Docker is the primary runtime for both development and deployment. There is no separate production image configuration; the same `dockerfile` and `docker-compose.yml` are used in both contexts.

### Services

```yaml
dev       # Python application container (Ubuntu 24.04 + uv)
postgres  # PostgreSQL 16 (student data)
ollama    # Ollama LLM server (Mistral 7B)
```

### Start all services

```bash
docker compose up -d
```

### Stop all services

```bash
docker compose down
```

### Stop and remove all volumes (full reset)

```bash
docker compose down -v
```

> This removes `.venv`, `.python`, `.uv_cache`, and all database data. After this, run `uv sync` and `uv run python -m policy_checker.database.seed` again.

### Rebuild the image

Run this after changing the `dockerfile`:

```bash
docker compose build --no-cache
docker compose up -d
```

### Named Volumes

| Volume | Purpose |
|--------|---------|
| `venv` | Python virtual environment (`.venv/`) |
| `python` | uv-managed Python install (`.python/`) |
| `uv_cache` | uv download cache (`.uv_cache/`) |
| `postgres_data` | PostgreSQL data directory |
| `ollama_data` | Ollama model weights |

### Running commands in the container

```bash
# Open a shell in the dev container
docker compose exec dev bash

# Run the pipeline directly
docker compose exec dev uv run python -m policy_checker.models.run --source ait

# Seed the database
docker compose exec dev uv run python -m policy_checker.database.seed

# Pull a different LLM model
docker compose exec ollama ollama pull mistral
docker compose exec ollama ollama list
```

### Checking service health

```bash
docker compose ps
```

Expected output when everything is running:

```
NAME                              STATUS
policy-checker-dev-1              running
policy-checker-postgres-1         running (healthy)
policy-checker-ollama-1           running
```

---

**Status**: Research / In Development

**Maintainer**: AIT Internship Project
