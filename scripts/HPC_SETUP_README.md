┌────────────────────────────────────────────────────────────────────┐
│                        YOUR SETUP                                   │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐         ┌─────────────┐         ┌──────────────┐  │
│  │  Windows PC │   git   │     VPS     │  HTTP   │  HPC Server  │  │
│  │  (Dev)      │ ──────► │  (Linux)    │ ──────► │  (GPU+LLMs)  │  │
│  └─────────────┘  push   └─────────────┘  :11434 └──────────────┘  │
│        │                       │                       │           │
│        │                       │                       │           │
│   Edit code              Run scripts              Ollama + Models  │
│   Push to GitHub         compare_models.py        - llama3.2       │
│                                                   - phi3           │
│                                                   - mistral        │
│                                                   - mixtral        │
│                                                   - llama3.1:70b   │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘

```

## Network

- VPS and HPC are on the **same network**
- HPC hostname: `compute02`
- Ollama port: `11434`
- Access URL: `http://compute02:11434`

## Folder Structure

### Windows PC (Development)

```

d:\Thesis-PoC_v1\
├── .venv/                          # Python virtual environment
└── RuleChecker_PoCv1/              # Git repository
    ├── scripts/
    │   ├── compare_models.py       # Main comparison script
    │   ├── hpc_ollama_setup.sh     # HPC job script
    │   ├── run_comparison.sh       # VPS runner
    │   └── verify_rules.py         # Single model test
    └── research/
        ├── gold_standard_template.json   # 97 rules for testing
        └── extracted_rules.json          # All 492 rules

```

### VPS (Execution)

```

~/RuleChecker_PoCv1/                # Cloned from GitHub
├── scripts/
│   ├── compare_models.py           # Run this!
│   └── ...
└── research/
    └── gold_standard_template.json

```

### HPC (Ollama Server)

```

/path/to/job/
├── bin/ollama                      # Ollama binary
├── ollama-models/                  # Downloaded models (~110GB)
├── logs/ollama_server.log          # Server logs
└── connection_info.txt             # Host and port info

```

## Quick Start

### Step 1: HPC - Start Ollama (via GUI)

Since you can use the GUI, models are already installed:

- llama3.2 (2GB)
- phi3 (2.2GB)
- mistral (4.4GB)
- mixtral (26GB)
- llama3.1:70b (42GB)

Just ensure the job is running and server is accessible.

### Step 2: VPS - Test Connection

```bash
# Test if HPC Ollama is accessible
curl http://compute02:11434/api/tags
```

Expected output:

```json
{"models":[{"name":"llama3.2:latest",...},...]}
```

### Step 3: VPS - Run Comparison

```bash
cd ~/RuleChecker_PoCv1

# Test with 5 rules first
python scripts/compare_models.py \
    --ollama-url http://compute02:11434 \
    --limit 5

# Full run (all 97 rules)
python scripts/compare_models.py \
    --ollama-url http://compute02:11434
```

### Step 4: Check Results

```bash
# Results will be saved to:
cat research/model_comparison_results.json
cat research/model_comparison_report.md
```

## Troubleshooting

### "Connection refused"

```bash
# Check if HPC job is running (via GUI or):
ssh hpc 'squeue -u $USER'

# Check if port is accessible
nc -zv compute02 11434
```

### "Model not found"

```bash
# List available models
curl http://compute02:11434/api/tags | python3 -m json.tool
```

### Ollama keeps dying

The job might have timed out. Resubmit via GUI with longer time limit.

## Files Reference

| File | Location | Purpose |
|------|----------|---------|
| `compare_models.py` | VPS | Main script to run |
| `hpc_ollama_setup.sh` | HPC | Job script (use via GUI) |
| `gold_standard_template.json` | VPS | Your 97 test rules |
| `model_comparison_results.json` | VPS (output) | Raw results |
| `model_comparison_report.md` | VPS (output) | Thesis report |
