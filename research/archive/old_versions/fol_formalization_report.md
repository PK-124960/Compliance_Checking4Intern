# FOL Formalization Results

**Generated:** 2026-01-29T18:44:46.174485
**Model:** mistral
**Total Rules Formalized:** 96

## Deontic Type Distribution

| Type | Count |
|------|-------|
| Obligation | 51 |
| Permission | 13 |
| Prohibition | 12 |
| Other | 20 |

## Sample Formalizations

### GS-001

**Text:** Contracted research may
entail confidentiality and restriction on publication....

**Deontic Type:** obligation

**Formula:**
```
O(confidentiality(c) && restrictionOnPublication(c))
```

**SHACL Hint:** Using SHACL, this could be expressed as a constraint on the ContractedResearch shape requiring both confidentiality and restrictionOnPublication properties to exist for any instance.

---

### GS-002

**Text:** Their educational visas may also be
cancelled....

**Deontic Type:** prohibition

**Formula:**
```
F(cancelled(their educational visas))
```

**SHACL Hint:** Using SHACL, this could be expressed as a property shape constraint for 'cancelled' on the 'educationalVisa' class, with a valueShape that requires no 'cancelled' values.

---

### GS-003

**Text:** (2) Continuing full-time postgraduate (PG) students (Master, Doctor and
Diploma), i.e., those who co...

**Deontic Type:** obligation

**Formula:**
```
O(P(R) ∧ P(T) ∧ P(O) ∧ (∀ s) ((Student(s) ∧ PG(s) ∧ CompletedAtLeastOneSemester(s) ∧ SemesterNumber(s) > 1) → (Invoice(s, R, T, O)) ∧ (PaidInAdvanceOrFullyPaidBeforeStart(s, R, T, O))) ∧ F(RegisterIfNotPaid(s)))
```

**SHACL Hint:** Student has a property PG with value Master, Doctor or Diploma. Student also has properties CompletedAtLeastOneSemester and SemesterNumber. Invoice has properties student, registration fee (R), tuition fee (T), other fees (O). RegisterIfNotPaid is a property that indicates whether the student is registered or not based on the payment status.

---

### GS-004

**Text:** Writing-off of doubtful accounts will be requested by OFIN and have to be
approved by the President,...

**Deontic Type:** N/A

**Formula:**
```
Error
```

**SHACL Hint:** N/A

---

### GS-005

**Text:** Sponsors must be invoiced for outstanding
dues and requested to send AIT a promissory note detailing...

**Deontic Type:** obligation

**Formula:**
```
O(Sponsors are invoiced for outstanding dues) ∧ O(Sponsors send a promissory note detailing when and how payment will be made)
```

**SHACL Hint:** { Sponsor sh:class _:Sponsor; owesDues sh:property owesDues . PromissoryNote a _:PromissoryNote; sender sh:property sender; containsPaymentDetails sh:property containsPaymentDetails; willBeSent sh:property willBeSent }

---

### GS-006

**Text:** (20) Overdue accounts shall be reviewed periodically, and follow-up
collections shall be initiated....

**Deontic Type:** obligation

**Formula:**
```
O(OverdueAccountsReviewed) ∧ O(FollowUpCollectionsInitiated)
```

**SHACL Hint:** In SHACL, this could be expressed as a set of constraints on the OverdueAccount and FollowUpCollection classes, requiring that every OverdueAccount has a property Reviewed and that there exists at least one FollowUpCollection for each OverdueAccount with the property Initiated.

---

### GS-007

**Text:** (10) Additional payments for audited and repeated courses, as well as beyond
the minimum 3 credits f...

**Deontic Type:** obligation

**Formula:**
```
O(pay) ∧ pay → (audited_and_repeated_course ∨ part_time_student ∧ semester_or_term ∧ before(mid_semester_exam, payment))
```

**SHACL Hint:** Obligation on Pay shape to have AuditedAndRepeatedCourse, PartTimeStudent, SemesterOrTerm, and MidSemesterExam properties with appropriate datatypes and values.

---

### GS-008

**Text:** FB-6-1-1: CREDIT POLICY
notice from the Accommodation Unit, and the tenant is required to
vacate the...

**Deontic Type:** N/A

**Formula:**
```
Error
```

**SHACL Hint:** N/A

---

### GS-009

**Text:** Students shall not disturb fellow students in the residential areas....

**Deontic Type:** N/A

**Formula:**
```
Error
```

**SHACL Hint:** N/A

---

### GS-010

**Text:** Exceptions to this may only be
given to those whose exchange program is less than two months....

**Deontic Type:** prohibition

**Formula:**
```
F(∃x (ExchangeProgram(x) ∧ (< two months x ExchangeProgram(x)) ⇒ !Exception(x)))
```

**SHACL Hint:** In SHACL, this could be expressed as a constraint on the 'Exception' class, stating that if 'ExchangeProgram' has a property 'duration' with value less than '2 months', then 'Exception' should not have any values for its property 'grantedTo'.

---

