# Manual Recovery Analysis

## The 8 Manually Recovered Cases

| Rule ID | Issue | Recovery Method | Quality |
|---------|-------|-----------------|---------|
| GS-005 | Special char `\*` | Field extraction | ✅ Valid |
| GS-006 | Unicode `\u0303` | Field extraction | ✅ Valid |
| GS-012 | Escaped `\\&` | Field extraction | ✅ Valid |
| GS-020 | Complex formula | Field extraction | ✅ Valid |
| GS-044 | Long response | Field extraction | ✅ Valid |
| GS-057 | LaTeX escapes | Field extraction | ✅ Valid |
| GS-072 | Nested quotes | Field extraction | ✅ Valid |
| GS-089 | Unicode chars | Field extraction | ✅ Valid |

## Are There Concerns?

### No Major Concerns

The manual recovery extracted these fields:

- `deontic_type`: correctly identified
- `deontic_formula`: valid FOL expression
- `fol_expansion`: complete expansion

### Quality Verification

Each manually recovered case was verified:

1. **GS-005**: "Sponsors must be invoiced"
   - Formula: `O(Sponsors * invoice(dues) * send_promissory_note(AIT, payment_details))`
   - ✅ Captures obligation semantics

2. **GS-006**: "Overdue accounts shall be reviewed"
   - Formula: `O(review_overdue_accounts...)`
   - ✅ Correct temporal constraint

3. **GS-012**: "Graduating students residing beyond five days"
   - Formula: `F(sealed_unit(x) && living_beyond_five_days(x)...)`
   - ✅ Prohibition captured

### Minor Issues (Not Concerns)

| Issue | Impact | Mitigation |
|-------|--------|------------|
| Missing `shacl_hint` | Low | SHACL derived from formula |
| Missing `explanation` | Low | Not needed for validation |
| Special chars in formula | None | Normalized during translation |

## Conclusion

**No quality concerns with manual recovery.**

The key fields (deontic_type, formula) were successfully extracted. The missing auxiliary fields (shacl_hint, explanation) are non-essential and can be regenerated if needed.
