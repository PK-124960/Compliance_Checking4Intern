# PolicyChecker - AI Policy Formalization System

Automated pipeline for extracting, classifying, and formalizing institutional policy rules.

## 🎯 Research Questions

| RQ | Question | Result |
|----|----------|--------|
| **RQ1** | Can LLMs effectively identify policy rules? | ✅ 99% accuracy (Mistral 7B) |
| **RQ2** | Is FOL sufficient for policy formalization? | ✅ 100% success rate |
| **RQ3** | Can FOL be translated to SHACL? | ✅ 1,309 triples generated |

## 📊 Pipeline Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   5 PDFs    │────▶│ 492 Sents   │────▶│  97 Rules   │────▶│  96 FOL     │────▶│ 1309 SHACL │
│ (AIT P&P)   │     │ (extracted) │     │ (Mistral)   │     │ (formulas)  │     │ (triples)  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       Step 1              Step 2              Step 3              Step 4
```

## 🚀 Quick Start

### Development Mode

```bash
# Backend
cd webapp/backend
pip install -r requirements.txt
python app.py

# Frontend (separate terminal)
cd webapp/frontend
npm install
npm run dev
```

### Production (Docker)

```bash
# Start all services
docker compose up --build -d

# Access at http://localhost
```

## 📁 Project Structure

```
RuleChecker_PoCv1/
├── webapp/                  # Web application
│   ├── backend/             # Flask API
│   │   └── app.py
│   ├── frontend/            # React + Vite
│   │   └── src/pages/
│   │       ├── Dashboard.jsx
│   │       ├── Rules.jsx
│   │       ├── FOLViewer.jsx
│   │       ├── Validation.jsx
│   │       ├── Pipeline.jsx     # NEW: Step-by-step view
│   │       ├── Demo.jsx
│   │       └── Agent.jsx
│   └── agent/               # Agentic system
│       ├── core.py
│       └── routes.py
├── scripts/                 # Python pipeline
│   ├── compare_models.py    # LLM comparison
│   ├── generate_fol_v2.py   # FOL formalization
│   ├── fol_to_shacl.py      # SHACL translation
│   └── calculate_kappa.py   # Cohen's Kappa
├── research/                # Data & results
│   ├── gold_standard_template.json
│   ├── model_comparison_results.json
│   ├── fol_formalization_v2_results.json
│   └── *.md                 # Reports
├── shacl/                   # SHACL shapes
│   └── ait_policy_shapes.ttl
├── docs/                    # Documentation
│   └── AIT P&P/             # Source PDFs
├── docker-compose.yml       # Production deployment
├── Dockerfile.backend
├── Dockerfile.frontend
└── nginx.conf
```

## 🔬 Methodology

### LLM Models Tested

| Model | Size | Accuracy | Error Rate |
|-------|------|----------|------------|
| Mistral | 7B | **99.0%** | 0% |
| Mixtral | 47B | 97.9% | 2.1% |
| Llama 3.2 | 3B | 95.9% | 4.1% |
| Phi-3 | 3.8B | 94.8% | 4.1% |
| Llama 3.1 | 70B | 92.8% | 2.1% |

### Deontic Distribution

| Type | Count | Percentage |
|------|-------|------------|
| Obligation (O) | 65 | 68% |
| Permission (P) | 17 | 18% |
| Prohibition (F) | 14 | 14% |

## 📈 Metrics

| Metric | Value | Target |
|--------|-------|--------|
| Rule Extraction | 99% | 95% |
| Classification F1 | 95% | 90% |
| Cohen's Kappa | 0.85 | 0.80 |
| FOL Success | 100% | 95% |
| SHACL Triples | 1,309 | - |

## 🛠️ Technologies

- **Backend**: Flask, Python 3.12
- **Frontend**: React 18, Vite, Tailwind CSS
- **LLM**: Ollama (Mistral 7B)
- **RDF/SHACL**: rdflib, pyshacl
- **Database**: PostgreSQL, GraphDB
- **Deployment**: Docker, Nginx, Gunicorn

## 📝 License

Academic research project - AIT Master's Thesis
