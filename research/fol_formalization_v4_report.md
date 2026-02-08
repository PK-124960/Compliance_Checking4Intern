# FOL Formalization Report v4

## Metadata
- **Timestamp**: 2026-02-08T19:56:58.894419
- **Model**: mistral
- **Input**: gold_standard_annotated_v4.json
- **Total Candidates**: 97
- **Rules Processed**: 81

## Statistics
| Metric | Count |
|--------|-------|
| Success | 81 |
| Manual Parse | 7 |
| Failed | 0 |
| **Success Rate** | **100.0%** |

## Distribution by Deontic Type
| Type | Count | Percentage |
|------|-------|------------|
| Obligation | 48 | 59.3% |
| Permission | 15 | 18.5% |
| Prohibition | 18 | 22.2% |

## Sample Formalizations

### 1. GS-001
**Original**: Contracted research may
entail confidentiality and restriction on publication....

**Deontic Type**: obligation

**Formula**: `O(C(research) -> R(confidentiality) && R(publication_restriction))`

---

### 2. GS-002
**Original**: Their educational visas may also be
cancelled....

**Deontic Type**: prohibition

**Formula**: `F(hasEducationalVisa & cancels)`

---

### 3. GS-003
**Original**: (2) Continuing full-time postgraduate (PG) students (Master, Doctor and
Diploma), i.e., those who co...

**Deontic Type**: obligation

**Formula**: `O(Student is PG && CompletedAtLeastOneSemester => PayFeesEachTerm)`

---

### 4. GS-004
**Original**: Writing-off of doubtful accounts will be requested by OFIN and have to be
approved by the President,...

**Deontic Type**: obligation

**Formula**: `O(writeOffDoubtfulAccounts iff requestedByOFIN and approvedByPresidentOrVP)`

---

### 5. GS-005
**Original**: Sponsors must be invoiced for outstanding
dues and requested to send AIT a promissory note detailing...

**Deontic Type**: obligation

**Formula**: `O(Sponsors \* invoiced \* for(dues, outstanding) \* send(AIT, promissory_note) \* detailing(when, payment) \* how(payment))`

---

