"""
PolicyChecker - Real-World Use Case Demo
Automated Student Compliance Verification System

This demonstrates the INTELLIGENT AUTOMATED PIPELINE:
1. Upload student data (RDF)
2. System automatically checks against all policy rules
3. Generate compliance report with violations

REAL-WORLD SCENARIO: University Admissions/Registration Office
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

PROJECT_ROOT = Path(__file__).parent.parent.parent
SHACL_DIR = PROJECT_ROOT / "shacl"

# ============================================
# SAMPLE STUDENT DATA (Real-world scenario)
# ============================================

SAMPLE_STUDENTS = [
    {
        "id": "STU001",
        "name": "John Doe",
        "program": "Master of Computer Science",
        "status": "enrolled",
        "fees_paid": True,
        "accommodation": "on_campus",
        "visa_valid": True,
        "gpa": 3.5,
        "semester": 2
    },
    {
        "id": "STU002", 
        "name": "Jane Smith",
        "program": "PhD in Data Science",
        "status": "enrolled",
        "fees_paid": False,  # VIOLATION: Unpaid fees
        "accommodation": "on_campus",
        "visa_valid": True,
        "gpa": 3.8,
        "semester": 3
    },
    {
        "id": "STU003",
        "name": "Bob Wilson",
        "program": "Master of Engineering",
        "status": "graduated",
        "fees_paid": True,
        "accommodation": "on_campus",  # VIOLATION: Should vacate after graduation
        "days_after_graduation": 10,  # > 5 days limit
        "visa_valid": False,
        "gpa": 3.2,
        "semester": 4
    },
    {
        "id": "STU004",
        "name": "Alice Brown",
        "program": "Diploma in AI",
        "status": "suspended",
        "fees_paid": True,
        "accommodation": "on_campus",  # VIOLATION: Suspended students cannot stay
        "visa_valid": True,
        "gpa": 1.8,  # VIOLATION: Below minimum GPA
        "semester": 1
    }
]

# ============================================
# POLICY RULES ENGINE (Intelligent Algorithm)
# ============================================

class PolicyEngine:
    """Intelligent rule-based compliance checker."""
    
    def __init__(self):
        self.rules = self._load_rules()
    
    def _load_rules(self):
        """Load formalized policy rules."""
        # In production, this would load from FOL/SHACL
        return [
            {
                "id": "FB-6-1-1-R002",
                "type": "obligation",
                "description": "Students must pay fees before registration",
                "check": lambda s: s.get("fees_paid") == True or s.get("status") != "enrolled",
                "violation_msg": "Outstanding fees not paid"
            },
            {
                "id": "FS-1-1-1-R048",
                "type": "prohibition",
                "description": "Graduated students cannot stay beyond 5 days without approval",
                "check": lambda s: not (s.get("status") == "graduated" and s.get("days_after_graduation", 0) > 5),
                "violation_msg": "Overstaying after graduation"
            },
            {
                "id": "DOC-R058",
                "type": "prohibition",
                "description": "Suspended students cannot use campus accommodation",
                "check": lambda s: not (s.get("status") == "suspended" and s.get("accommodation") == "on_campus"),
                "violation_msg": "Suspended student in campus accommodation"
            },
            {
                "id": "AA-GPA-MIN",
                "type": "obligation",
                "description": "Students must maintain minimum GPA of 2.0",
                "check": lambda s: s.get("gpa", 0) >= 2.0 or s.get("status") != "enrolled",
                "violation_msg": "GPA below minimum requirement"
            },
            {
                "id": "VISA-VALID",
                "type": "obligation",
                "description": "International students must have valid visa",
                "check": lambda s: s.get("visa_valid") == True,
                "violation_msg": "Invalid or expired visa"
            }
        ]
    
    def check_compliance(self, student: dict) -> dict:
        """Check student against all policy rules."""
        violations = []
        passed = []
        
        for rule in self.rules:
            try:
                if rule["check"](student):
                    passed.append({
                        "rule_id": rule["id"],
                        "type": rule["type"],
                        "description": rule["description"],
                        "status": "PASS"
                    })
                else:
                    violations.append({
                        "rule_id": rule["id"],
                        "type": rule["type"],
                        "description": rule["description"],
                        "violation": rule["violation_msg"],
                        "status": "VIOLATION",
                        "severity": "high" if rule["type"] == "obligation" else "critical"
                    })
            except Exception as e:
                pass  # Rule not applicable
        
        return {
            "student_id": student["id"],
            "student_name": student["name"],
            "total_rules_checked": len(self.rules),
            "passed": len(passed),
            "violations": len(violations),
            "compliance_rate": round(len(passed) / len(self.rules) * 100, 1),
            "is_compliant": len(violations) == 0,
            "passed_rules": passed,
            "violation_details": violations,
            "checked_at": datetime.now().isoformat()
        }
    
    def check_all_students(self, students: list) -> dict:
        """Check all students and generate compliance report."""
        results = []
        total_violations = 0
        compliant_count = 0
        
        for student in students:
            result = self.check_compliance(student)
            results.append(result)
            total_violations += result["violations"]
            if result["is_compliant"]:
                compliant_count += 1
        
        return {
            "report_date": datetime.now().isoformat(),
            "total_students": len(students),
            "compliant_students": compliant_count,
            "non_compliant_students": len(students) - compliant_count,
            "total_violations": total_violations,
            "compliance_rate": round(compliant_count / len(students) * 100, 1),
            "student_results": results,
            "summary": {
                "status": "ATTENTION REQUIRED" if total_violations > 0 else "ALL COMPLIANT",
                "action_items": total_violations
            }
        }

# Initialize engine
engine = PolicyEngine()

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/demo/students', methods=['GET'])
def get_students():
    """Get sample students."""
    return jsonify(SAMPLE_STUDENTS)

@app.route('/api/demo/check/<student_id>', methods=['GET'])
def check_student(student_id):
    """Check single student compliance."""
    student = next((s for s in SAMPLE_STUDENTS if s["id"] == student_id), None)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    result = engine.check_compliance(student)
    return jsonify(result)

@app.route('/api/demo/check-all', methods=['GET'])
def check_all():
    """Check all students and generate report."""
    report = engine.check_all_students(SAMPLE_STUDENTS)
    return jsonify(report)

@app.route('/api/demo/rules', methods=['GET'])
def get_rules():
    """Get all policy rules in the engine."""
    rules = [{"id": r["id"], "type": r["type"], "description": r["description"]} for r in engine.rules]
    return jsonify(rules)


if __name__ == '__main__':
    print("=" * 60)
    print("PolicyChecker - Real-World Demo Server")
    print("Automated Student Compliance Verification")
    print("=" * 60)
    print("\nEndpoints:")
    print("  GET /api/demo/students     - List sample students")
    print("  GET /api/demo/check/<id>   - Check single student")
    print("  GET /api/demo/check-all    - Generate compliance report")
    print("  GET /api/demo/rules        - List policy rules")
    print("=" * 60)
    app.run(debug=True, port=5001)
