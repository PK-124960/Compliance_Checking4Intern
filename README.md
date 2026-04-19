# PolicyChecker - AI Policy Formalization System

Automated **agentic pipeline** for extracting, classifying, and formalizing institutional policy rules using LLMs and Knowledge Graphs.

## 🎯 Research Questions

| RQ | Question | Result |
|----|----------|--------|
| **RQ1** | Can LLMs effectively identify policy rules? | ✅ 99% accuracy (GLM 4.7 Flash) |
| **RQ2** | Is FOL sufficient for policy formalization? | ✅ 100% success rate |
| **RQ3** | Can FOL be translated to SHACL? | ✅ 1,309 triples generated |

## 📈 Academic Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Accuracy | 99% | ≥ 95% | ✅ |
| F1-Score | 0.95 | ≥ 0.90 | ✅ |
| Cohen's κ | 0.85 | ≥ 0.80 | ✅ |
| FOL Success | 100% | 100% | ✅ |

## ⚙️ Architecture

This repository operates entirely on a **LangGraph** orchestration structure. It processes institutional policy PDFs, passes them through multiple logical nodes (classification, First-Order Logic extraction, etc.), handles exceptions, and dynamically executes LLM functions with fallback redundancy.

**For a deep-dive into graph structure, nodes, and how to operate the repository as an incoming developer, read the onboarding guide:** 
👉 **[ARCHITECTURE.md](ARCHITECTURE.md)**

## 📁 Project Structure

```
RuleChecker_PoCv1/
├── core/                        # Utility & SQLite Cache engine
├── institutional_policy/        # Target academic PDFs (AIT)
├── langgraph_agent/             # LangGraph Core Logic
│   ├── edges/                   # Conditional routers
│   ├── nodes/                   # Processing steps (FOL, classify, etc.)
│   ├── graph.py                 # Graph assembly schema
│   ├── state.py                 # Graph typing schema
│   └── run.py                   # Main Execution CLI Entrypoint
├── output/                      # Generated pipeline reports and JSON
├── shacl/                       # Authoritative RDF Shapes & Ontology
├── tests/                       # Pytest TDD verification matrix
└── ARCHITECTURE.md              # Intern onboarding docs
```

## 🚀 Quick Start

### 1. Requirements

Install standard dependencies:
```bash
pip install -r requirements.txt
```

Ensure you have a local instance of **Ollama** installed on your system to run inference endpoints. 
* Pull down lightweight development models:
`ollama pull mistral`

### 2. Environment Configuration

Copy the example `.env` layout:
```bash
cp .env.example .env
```
Ensure that `OLLAMA_HOST` properly points to your local machine (`http://localhost:11434`) or your High Performance Computing (HPC) edge nodes.

### 3. Run Pipeline 

Execute the full LangGraph directly from the terminal (run from project root):
```bash
python -m langgraph_agent.run --source ait --verbose
```
The results and metric analysis will populate in `output/ait/pipeline_report.json`.

### 4. Running the Tests

Verify all LangGraph validations and SHACL definitions using `pytest`:
```bash
pytest
```

## 📝 License
Academic research project - AIT Master's Thesis
