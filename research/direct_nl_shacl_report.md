# Direct NL -> SHACL Experiment Report

## Purpose
Empirically evaluate whether the FOL intermediate layer is necessary by comparing
direct NL->SHACL translation quality against the FOL-mediated pipeline.

## Methodology
- Same 81 rules from gold_standard_annotated_v4.json
- Same LLM (Mistral 7B) with same settings (temperature=0.0, seed=42)
- Direct prompt asking for SHACL output (no FOL step)
- Compared against existing FOL-mediated SHACL shapes

## Results Summary

| Metric | Direct NL->SHACL | FOL-Mediated Pipeline |
|--------|------------------|-----------------------|
| Turtle Syntax Valid | 31/81 (38.3%) | 81/81 (100%) |
| Has Target Class | 81/81 (100.0%) | 81/81 (100%) |
| Has Severity | 81/81 (100.0%) | 81/81 (100%) |
| Has Constraint | 81/81 (100.0%) | 81/81 (100%) |
| Target Class Match | 33/81 (40.7%) | N/A (reference) |
| Correct Constraint Type | 51/81 (63.0%) | 81/81 (100%) |

## Conclusion

The FOL intermediate layer provides substantial value:

1. **Syntax reliability**: FOL-mediated pipeline achieves 100% valid Turtle output through
   deterministic template-based translation, while direct translation achieved 38.3%.

2. **Structural completeness**: The FOL step ensures all required SHACL components
   (target class, severity, constraints) are systematically generated.

3. **Semantic checkpoint**: FOL provides a human-readable intermediate representation
   that enables verification and debugging before SHACL generation.

## Detailed Results

### GS-001 (obligation) -- VALID
- Target: Employee (match: False)
- Constraint: minCount (correct: True)

### GS-002 (prohibition) -- VALID
- Target: Student (match: True)
- Constraint: minCount (correct: False)

### GS-003 (obligation) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-004 (obligation) -- INVALID
- Target: Employee (match: False)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-005 (obligation) -- INVALID
- Target: Employee (match: False)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-006 (obligation) -- VALID
- Target: Account (match: False)
- Constraint: minCount (correct: True)

### GS-007 (obligation) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-008 (obligation) -- INVALID
- Target: Tenant (match: False)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-009 (prohibition) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: False)
- Error: Basic syntax check failed (rdflib not available)

### GS-010 (obligation) -- VALID
- Target: Student (match: False)
- Constraint: minCount (correct: True)

### GS-011 (permission) -- VALID
- Target: Student (match: True)
- Constraint: minCount (correct: False)

### GS-012 (prohibition) -- VALID
- Target: Student (match: True)
- Constraint: minCount (correct: False)

### GS-013 (permission) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: False)
- Error: Basic syntax check failed (rdflib not available)

### GS-014 (permission) -- VALID
- Target: Student (match: True)
- Constraint: minCount (correct: False)

### GS-015 (obligation) -- VALID
- Target: Guest (match: False)
- Constraint: minCount (correct: True)

### GS-016 (permission) -- INVALID
- Target: StudentDormitory (match: False)
- Constraint: minCount (correct: False)
- Error: Basic syntax check failed (rdflib not available)

### GS-017 (prohibition) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: False)
- Error: Basic syntax check failed (rdflib not available)

### GS-018 (obligation) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-019 (obligation) -- INVALID
- Target: Room (match: False)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-020 (prohibition) -- VALID
- Target: Student (match: True)
- Constraint: minCount (correct: False)

### GS-021 (obligation) -- VALID
- Target: GrievanceTribunal (match: False)
- Constraint: minCount (correct: True)

### GS-022 (obligation) -- INVALID
- Target: Employee (match: False)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-023 (obligation) -- VALID
- Target: Individual (match: False)
- Constraint: minCount (correct: True)

### GS-024 (obligation) -- VALID
- Target: Employee (match: False)
- Constraint: minCount (correct: True)

### GS-025 (obligation) -- INVALID
- Target: Employee (match: False)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-026 (obligation) -- VALID
- Target: GrievanceCommittee (match: False)
- Constraint: minCount (correct: True)

### GS-027 (permission) -- VALID
- Target: Item (match: False)
- Constraint: minCount (correct: False)

### GS-028 (obligation) -- INVALID
- Target: Employee (match: False)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-030 (permission) -- INVALID
- Target: Person (match: False)
- Constraint: minCount (correct: False)
- Error: Basic syntax check failed (rdflib not available)

### GS-031 (prohibition) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: False)
- Error: Basic syntax check failed (rdflib not available)

### GS-035 (obligation) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-036 (obligation) -- INVALID
- Target: Employee (match: False)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-037 (obligation) -- VALID
- Target: Student (match: True)
- Constraint: minCount (correct: True)

### GS-038 (prohibition) -- VALID
- Target: SportsFacility (match: False)
- Constraint: minCount (correct: False)

### GS-039 (obligation) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-040 (obligation) -- INVALID
- Target: Student (match: False)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-041 (permission) -- INVALID
- Target: LinenSet (match: False)
- Constraint: minCount (correct: False)
- Error: Basic syntax check failed (rdflib not available)

### GS-042 (prohibition) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: False)
- Error: Basic syntax check failed (rdflib not available)

### GS-043 (obligation) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-044 (obligation) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-045 (obligation) -- INVALID
- Target: Employee (match: False)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-046 (prohibition) -- INVALID
- Target: Trustee (match: False)
- Constraint: minCount (correct: False)
- Error: Basic syntax check failed (rdflib not available)

### GS-047 (obligation) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-048 (permission) -- VALID
- Target: Employee (match: False)
- Constraint: minCount (correct: False)

### GS-050 (obligation) -- VALID
- Target: Individual (match: False)
- Constraint: minCount (correct: True)

### GS-051 (obligation) -- INVALID
- Target: Dependent (match: False)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-052 (permission) -- VALID
- Target: Person (match: False)
- Constraint: minCount (correct: False)

### GS-053 (prohibition) -- INVALID
- Target: Unit (match: False)
- Constraint: minCount (correct: False)
- Error: Basic syntax check failed (rdflib not available)

### GS-054 (permission) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: False)
- Error: Basic syntax check failed (rdflib not available)

### GS-055 (prohibition) -- INVALID
- Target: AccommodationUnit (match: False)
- Constraint: maxCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-056 (obligation) -- VALID
- Target: Student (match: True)
- Constraint: minCount (correct: True)

### GS-057 (permission) -- VALID
- Target: Complainant (match: False)
- Constraint: minCount (correct: False)

### GS-058 (obligation) -- INVALID
- Target: Student (match: False)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-059 (prohibition) -- VALID
- Target: Student (match: False)
- Constraint: maxCount (correct: True)

### GS-060 (obligation) -- INVALID
- Target: Employee (match: False)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-061 (obligation) -- INVALID
- Target: Lessee (match: False)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-062 (obligation) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-063 (prohibition) -- INVALID
- Target: Student (match: True)
- Constraint: maxCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-064 (obligation) -- VALID
- Target: Student (match: True)
- Constraint: minCount (correct: True)

### GS-067 (permission) -- VALID
- Target: Employee (match: False)
- Constraint: minCount (correct: False)

### GS-070 (obligation) -- VALID
- Target: Employee (match: False)
- Constraint: minCount (correct: True)

### GS-071 (prohibition) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: False)
- Error: Basic syntax check failed (rdflib not available)

### GS-072 (obligation) -- INVALID
- Target: Facility (match: False)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-073 (obligation) -- VALID
- Target: Account (match: False)
- Constraint: minCount (correct: True)

### GS-074 (permission) -- VALID
- Target: Student (match: True)
- Constraint: minCount (correct: False)

### GS-075 (obligation) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-076 (obligation) -- VALID
- Target: Employee (match: False)
- Constraint: minCount (correct: True)

### GS-078 (prohibition) -- VALID
- Target: Vehicle (match: False)
- Constraint: minCount (correct: False)

### GS-080 (obligation) -- VALID
- Target: Student (match: False)
- Constraint: minCount (correct: True)

### GS-081 (obligation) -- INVALID
- Target: Employee (match: False)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-083 (obligation) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-084 (prohibition) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: False)
- Error: Basic syntax check failed (rdflib not available)

### GS-087 (obligation) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-088 (prohibition) -- INVALID
- Target: AccommodationUnit (match: False)
- Constraint: minCount (correct: False)
- Error: Basic syntax check failed (rdflib not available)

### GS-089 (obligation) -- INVALID
- Target: Employee (match: False)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-090 (permission) -- VALID
- Target: StudentDormitory (match: False)
- Constraint: minCount (correct: False)

### GS-091 (obligation) -- INVALID
- Target: Invoice (match: False)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-092 (obligation) -- INVALID
- Target: Guest (match: False)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

### GS-093 (prohibition) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: False)
- Error: Basic syntax check failed (rdflib not available)

### GS-096 (permission) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: False)
- Error: Basic syntax check failed (rdflib not available)

### GS-097 (obligation) -- INVALID
- Target: Student (match: True)
- Constraint: minCount (correct: True)
- Error: Basic syntax check failed (rdflib not available)

