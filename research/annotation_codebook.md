# Policy Rule Annotation Codebook

## Purpose

This document provides guidelines for human annotators to classify policy statements from AIT institutional documents. The goal is to achieve consistent annotations for calculating inter-rater reliability (Cohen's Kappa).

---

## What is a Policy Rule?

A **policy rule** is a statement that:

1. **Prescribes specific behavior** (obligation, permission, or prohibition)
2. **Uses deontic language** (must, shall, may, should, cannot, etc.)
3. **Has identifiable subjects** (students, employees, faculty, etc.)
4. **Contains actionable requirements**

---

## Deontic Markers Reference

### Strong Deontic Markers (Almost Always = Rule)

| Marker | Rule Type | Example |
|--------|-----------|---------|
| **must** | Obligation | "Students *must* submit fees before registration" |
| **shall** | Obligation | "The committee *shall* review applications" |
| **required/required to** | Obligation | "Students are *required* to attend orientation" |
| **have to** | Obligation | "Employees *have to* report conflicts" |
| **cannot/can not** | Prohibition | "Students *cannot* enroll without payment" |
| **shall not** | Prohibition | "Members *shall not* disclose confidential..." |
| **prohibited/forbidden** | Prohibition | "Smoking is *prohibited* in dormitories" |
| **may** | Permission | "Students *may* appeal decisions" |
| **permitted/allowed** | Permission | "Visitors are *permitted* to use facilities" |

### Weak Deontic Markers (Context-Dependent)

| Marker | Default | When It's a Rule | When It's NOT a Rule |
|--------|---------|------------------|---------------------|
| **should** | Recommendation | Clear mandatory context | Advisory/suggestion |
| **is expected to** | Expectation | Backed by policy | Social norm |
| **will be** | Future | Consequence stated | Passive description |

---

## Decision Tree

```
                              Does the text contain a deontic marker?
                                           │
                              ┌────────────┼────────────┐
                              │            │            │
                             YES        UNCLEAR         NO
                              │            │            │
                              ▼            ▼            ▼
                        Is there a    Check for      NOT A RULE
                    clear subject?   implicit duty
                              │            │
                    ┌────────┼───────┐    │
                   YES      NO       │    │
                    │        │       │    │
                    ▼        ▼       ▼    │
              Is action   NOT A    MAYBE  │
              specified?   RULE     ───────┘
                    │
           ┌───────┼───────┐
          YES              NO
           │                │
           ▼                ▼
      ✅ RULE         NOT A RULE
```

---

## Examples with Annotations

### Example 1: Clear Obligation ✅ RULE

> "Students **must** pay all fees before the start of the semester."

| Field | Value |
|-------|-------|
| is_rule | **true** |
| rule_type | **obligation** |
| deontic_marker | must |
| subject | Students |
| action | pay all fees |
| confidence | 5 |

---

### Example 2: Clear Permission ✅ RULE

> "Students **may** appeal the decision to the Vice President."

| Field | Value |
|-------|-------|
| is_rule | **true** |
| rule_type | **permission** |
| deontic_marker | may |
| subject | Students |
| action | appeal the decision |
| confidence | 5 |

---

### Example 3: Clear Prohibition ✅ RULE

> "Sub-letting rooms is **prohibited** and may result in eviction."

| Field | Value |
|-------|-------|
| is_rule | **true** |
| rule_type | **prohibition** |
| deontic_marker | prohibited |
| subject | (Students - implied) |
| action | sub-letting rooms |
| confidence | 5 |

---

### Example 4: Recommendation ❌ NOT A RULE

> "The committee **should** proceed to analyze the grievance."

| Field | Value |
|-------|-------|
| is_rule | **false** |
| rule_type | null |
| notes | "Should" is advisory here |
| confidence | 3 |

**Why not a rule?** "Should" without mandatory context is a recommendation, not an enforceable rule.

---

### Example 5: Description ❌ NOT A RULE

> "Students ride a pick-up known as 'Luth' to campus."

| Field | Value |
|-------|-------|
| is_rule | **false** |
| rule_type | null |
| notes | Descriptive statement, no deontic content |
| confidence | 5 |

---

### Example 6: Borderline Case - Annotate as RULE with Low Confidence

> "The settlement **should** be supported by collated receipts."

| Field | Value |
|-------|-------|
| is_rule | **true** |
| rule_type | **obligation** |
| deontic_marker | should |
| notes | Borderline - could be recommendation |
| confidence | 2 |

**When uncertain:** Annotate as you interpret it, but lower confidence (1-2).

---

## Confidence Scale

| Score | Meaning |
|-------|---------|
| 5 | Very confident - clear-cut case |
| 4 | Confident - minor interpretation needed |
| 3 | Moderately confident - some ambiguity |
| 2 | Uncertain - could go either way |
| 1 | Very uncertain - guessing |

---

## Special Cases

### 1. "Should" Statements

**Default:** NOT a rule (recommendation)

**Exception - IS a rule if:**

- Followed by consequences ("should... otherwise...")
- Part of a policy with enforcement mechanisms
- Context makes it clearly mandatory

### 2. Conditional Statements

Still a rule if the condition + action are clear:
> "If a student fails to pay, they shall be deregistered."

**→ IS a rule** (conditional obligation)

### 3. Passive Voice

Rewrite mentally to identify subject:
> "Fees are required to be paid before registration."
> → "Students are required to pay fees..."

**→ IS a rule** (obligation)

### 4. Lists within Rules

If the sentence is part of a numbered list under a rule heading, it likely IS a rule.

---

## Annotation Template

For each text, provide:

```json
{
  "is_rule": true | false,
  "rule_type": "obligation" | "permission" | "prohibition" | null,
  "deontic_marker": "the specific word" | null,
  "subject": "who this applies to" | null,
  "action": "what must/may/cannot be done" | null,
  "condition": "when/if this applies" | null,
  "confidence": 1-5,
  "notes": "any clarification"
}
```

---

## Annotator Agreement

After independent annotation:

1. Calculate Cohen's Kappa on `is_rule` (binary)
2. Resolve disagreements through discussion
3. Document final consensus

**Target:** κ ≥ 0.80 (substantial agreement)

---

*Version: 1.0 | Created: 2026-01-31*
