# PolicyChecker - AI Policy Formalization System

Automated **agentic pipeline** for extracting, classifying, and formalizing institutional policy rules using LLMs.

## 🎯 Research Questions

| RQ | Question | Result |
|----|----------|--------|
| **RQ1** | Can LLMs effectively identify policy rules? | ✅ 99% accuracy (GLM 4.7 Flash) |
| **RQ2** | Is FOL sufficient for policy formalization? | ✅ 100% success rate |
| **RQ3** | Can FOL be translated to SHACL? | ✅ 1,309 triples generated |

## 📊 8-Step Agentic Pipeline

```
PDF → Segment → Filter → Classify → Simplify → Formalize → Translate → Validate
 1       2         3        4          5          6           7           8
                         (RQ1)                  (RQ2)       (RQ3)
```

| Step | Endpoint | Description | RQ |
|------|----------|-------------|-----|
| 1 | `/api/pipeline/upload` | Extract text from PDF | - |
| 2 | `/api/pipeline/segment` | Split into sentences | - |
| 3 | `/api/pipeline/filter` | Remove non-candidates | - |
| 4 | `/api/pipeline/classify` | Identify rules + reasoning | RQ1 |
| 5 | `/api/pipeline/simplify` | Rewrite complex rules | - |
| 6 | `/api/pipeline/formalize` | Generate FOL formulas | RQ2 |
| 7 | `/api/pipeline/translate` | Create SHACL shapes | RQ3 |
| 8 | `/api/pipeline/validate` | Test constraints | - |

## 🤖 Available Models

| Model | Size | Best For |
|-------|------|----------|
| **GLM 4.7 Flash** ★ | 19 GB | Classification, Formalization |
| Mistral | 4.4 GB | Fast extraction |
| Mixtral | 26 GB | Complex reasoning |
| Qwen3 32B | 20 GB | Multilingual |
| Qwen2.5 Instruct | 19 GB | Instruction following |
| Llama 3.1 70B | 42 GB | Long context (128k) |

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
# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start all services
docker compose up --build -d

# Access at http://localhost
```

## 📁 Project Structure

```
RuleChecker_PoCv1/
├── webapp/
│   ├── backend/
│   │   ├── app.py                 # Flask main
│   │   └── routes/
│   │       └── pipeline.py        # 8 API endpoints
│   ├── frontend/
│   │   └── src/pages/
│   │       ├── Upload.jsx         # Main pipeline UI
│   │       ├── ModelComparison.jsx
│   │       ├── Dashboard.jsx
│   │       ├── Rules.jsx
│   │       ├── FOLViewer.jsx
│   │       └── Validation.jsx
│   └── agent/
│       ├── llm_service.py         # 8 models configured
│       ├── ocr_service.py         # DeepSeek-OCR 2
│       ├── metrics.py             # Academic metrics
│       └── core.py                # Agentic orchestrator
├── scripts/                       # Python utilities
├── research/                      # Data & results
├── shacl/                         # SHACL shapes
├── docs/                          # Documentation
└── docker-compose.yml
```

## 📈 Academic Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Accuracy | 99% | ≥ 95% | ✅ |
| F1-Score | 0.95 | ≥ 0.90 | ✅ |
| Cohen's κ | 0.85 | ≥ 0.80 | ✅ |
| FOL Success | 100% | 100% | ✅ |
| SHACL Triples | 1,309 | - | ✅ |

## 🔧 Configuration

### Environment Variables

```bash
# .env
OLLAMA_HOST=http://compute02:11434   # HPC Ollama API
GRAPHDB_URL=http://localhost:7200    # GraphDB
POSTGRES_HOST=localhost
```

### HPC Setup

```bash
# Pull GLM 4.7 Flash
ollama pull glm-4.7-flash

# Verify models
ollama list
```

## 🛠️ Technologies

- **Backend**: Flask, Python 3.12
- **Frontend**: React 18, Vite
- **LLM**: Ollama (GLM 4.7 Flash, Mistral)
- **RDF/SHACL**: rdflib, pyshacl
- **Database**: PostgreSQL, GraphDB
- **Deployment**: Docker, Nginx, Gunicorn

## 📝 License

Academic research project - AIT Master's Thesis
