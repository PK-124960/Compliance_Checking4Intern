# LLM Model Comparison for Policy Rule Verification

**Generated:** 2026-01-29T16:56:43.790947

## Overview

This report compares three Large Language Models (LLMs) for their ability to identify policy rules in academic documents. This comparison supports the methodology of the thesis by providing empirical justification for model selection.

## Models Tested

| Model | Type | Size | Purpose |
|-------|------|------|---------|
| Llama 3.2 | Open Source (Meta) | 3B | Baseline, efficient classification |
| Mistral | Open Source | 7B | Instruction-following, extraction |
| Phi3 | Open Source (Microsoft) | 3.8B | Compact reasoning |

## Results Summary

### Classification Statistics

| Model | Rules Found | Not Rules | Errors | Rule Rate | Avg Confidence |
|-------|-------------|-----------|--------|-----------|----------------|
| llama3.2 | 93 | 0 | 4 | 95.9% | 0.88 |
| phi3 | 92 | 1 | 4 | 94.8% | 0.91 |
| mistral | 96 | 1 | 0 | 99.0% | 0.98 |
| mixtral | 95 | 0 | 2 | 97.9% | 0.91 |
| llama3.1:70b | 90 | 5 | 2 | 92.8% | 0.89 |

### Inter-Model Agreement

| Model Pair | Agreement Rate |
|------------|----------------|
| llama3.2 vs phi3 | 90.7% |
| llama3.2 vs mistral | 94.8% |
| llama3.2 vs mixtral | 93.8% |
| llama3.2 vs llama3.1:70b | 88.7% |
| phi3 vs mistral | 95.9% |
| phi3 vs mixtral | 93.8% |
| phi3 vs llama3.1:70b | 89.7% |
| mistral vs mixtral | 96.9% |
| mistral vs llama3.1:70b | 93.8% |
| mixtral vs llama3.1:70b | 90.7% |

## Sample Comparisons

The following table shows how models classified the same rule text:

| Rule ID | Llama 3.2 | Mistral | Phi3 |
|---------|-----------|---------|------|
| GS-001 | ✅ | ✅ | ✅ |
| GS-002 | ✅ | ✅ | ✅ |
| GS-003 | ✅ | ✅ | ✅ |
| GS-004 | ✅ | ✅ | ✅ |
| GS-005 | ✅ | ✅ | ✅ |
| GS-006 | ✅ | ✅ | ✅ |
| GS-007 | ✅ | ✅ | ✅ |
| GS-008 | ✅ | ✅ | ✅ |
| GS-009 | ✅ | ✅ | ✅ |
| GS-010 | ✅ | ✅ | ✅ |

## Methodology Notes

1. **Prompt Design**: All models used identical prompts for fair comparison
2. **Temperature**: Set to 0.1 for consistent, deterministic outputs
3. **Evaluation**: Binary classification (is_rule: true/false)

## Recommendations for Thesis

Based on the comparison results:

1. **Primary Model**: [To be determined based on results]
2. **Validation**: Cross-validate with model showing highest agreement
3. **Documentation**: Report inter-model agreement as measure of reliability

## References

- Meta AI. (2024). Llama 3.2 Technical Report.
- Mistral AI. (2023). Mistral 7B.
- Microsoft Research. (2024). Phi-3 Technical Report.
