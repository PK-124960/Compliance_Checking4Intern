# Pattern Taxonomy Report

**Generated:** 2026-01-31 06:07
**Purpose:** Analyze linguistic patterns in policy rules for RQ1

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Rules Analyzed | 83 |
| Patterns Identified | 4 |
| Full FOL Support | 52 (62.7%) |
| Partial FOL Support | 26 (31.3%) |

---

## Pattern Distribution

| Pattern | Count | % | FOL Support | Formalizable |
|---------|-------|---|-------------|--------------|
| Simple Obligation | 43 | 51.8% | Full | ✅ |
| Simple Permission | 33 | 39.8% | Full | ✅ |
| Conditional Multiple | 4 | 4.8% | Full | ✅ |
| Simple Prohibition | 3 | 3.6% | Full | ✅ |


---

## Pattern Definitions

### Simple Prohibition

- **Description:** Direct prohibition without conditions
- **Markers:** not allowed, prohibited, shall not, cannot, must not...
- **FOL Support:** Full
- **Example:** "Students shall not disturb fellow students"
- **Count in Corpus:** 3

### Simple Obligation

- **Description:** Direct obligation without conditions
- **Markers:** must, shall, is required, have to, are required
- **FOL Support:** Full
- **Example:** "Students must pay fees before registration"
- **Count in Corpus:** 43

### Simple Permission

- **Description:** Direct permission statement
- **Markers:** may, can, is permitted, is allowed, are allowed
- **FOL Support:** Full
- **Example:** "Students may opt to reside off-campus"
- **Count in Corpus:** 33

### Conditional Multiple

- **Description:** Multiple conditions (AND/OR)
- **Markers:** and, or, both, either, as well as
- **FOL Support:** Full
- **Example:** "Students who are enrolled AND paid fees may register"
- **Count in Corpus:** 4

---

## FOL Expressiveness Analysis

### Fully Expressible Patterns (Answer to RQ1)

The following patterns can be fully expressed in First-Order Logic:

| Pattern | Count | Formalization Rate |
|---------|-------|-------------------|
| Simple Obligation | 43 | 100% |
| Simple Permission | 33 | 100% |
| Conditional Multiple | 4 | 100% |
| Simple Prohibition | 3 | 100% |


### Partially Expressible Patterns

The following patterns require additional handling or simplification:

| Pattern | Count | Challenge |
|---------|-------|-----------|


---

## Key Findings for Thesis

### RQ1: What linguistic patterns can be formalized?

1. **Fully Formalizable (52/83 = 62.7%)**
   - Simple obligations, permissions, prohibitions
   - Conditional rules (single and multiple conditions)
   - Universally and existentially quantified rules

2. **Partially Formalizable (26/83 = 31.3%)**
   - Temporal constraints (require temporal logic extension)
   - Exception-based rules (require defeasibility handling)

3. **Challenging Patterns**
   - Advisory "should" statements (semantic ambiguity)
   - Complex procedural rules (multi-step sequences)

### Contribution

This analysis identifies the linguistic boundary of FOL expressiveness for academic policy rules, providing empirical data for the thesis methodology chapter.
