# FOL Formalization Results (v2 Improved)

**Generated:** 2026-01-29T18:58:17.367733
**Model:** mistral
**Version:** v2_improved

## Performance Metrics

| Metric | Value |
|--------|-------|
| Total Processed | 96 |
| Successful | 96 |
| Manual Parse Recovery | 8 |
| Failed | 0 |
| **Success Rate** | **100.0%** |

## Improvements Applied

- ✅ Increased response length (num_predict: 1024)
- ✅ LaTeX escape character handling
- ✅ Multi-strategy JSON parsing (5 strategies)
- ✅ Retry mechanism for failed requests
- ✅ Manual field extraction fallback

## Deontic Type Distribution

| Type | Count |
|------|-------|
| Obligation | 65 |
| Permission | 17 |
| Prohibition | 14 |
| Other | 0 |

## Sample Formalizations

### GS-001

**Text:** Contracted research may
entail confidentiality and restriction on publication....

**Type:** obligation

**Formula:**
```
O(Confidentiality(research) && R(publication, research))
```

---

### GS-002

**Text:** Their educational visas may also be
cancelled....

**Type:** prohibition

**Formula:**
```
F(cancelled(educational_visa))
```

---

### GS-003

**Text:** (2) Continuing full-time postgraduate (PG) students (Master, Doctor and
Diploma), i.e., those who co...

**Type:** obligation

**Formula:**
```
O(Continuing_PG_student(x) implies Within(semester2, semester, Invoice(x)))
```

---

### GS-004

**Text:** Writing-off of doubtful accounts will be requested by OFIN and have to be
approved by the President,...

**Type:** obligation

**Formula:**
```
O(request_writing_off_doubtful_accounts(OFIN) implies approved_by_president_or_vp_designate(approval))
```

---

### GS-005

**Text:** Sponsors must be invoiced for outstanding
dues and requested to send AIT a promissory note detailing...

**Type:** obligation

**Formula:**
```
O(Sponsors \* invoice(dues) \* send_promissory_note(AIT, payment_details))
```

---

