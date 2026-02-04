"""
Research Demo UI - Simple Flask App
Uses existing scripts to demonstrate 4-phase methodology
For presentation to TA/Professor
"""

from flask import Flask, render_template, request, jsonify
import json
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent / 'scripts'))

# Import your existing modules
from populate_llm_annotations_v2 import classify_single_rule
from generate_fol_v2 import formalize_single_rule
from fol_to_shacl_v2 import translate_single_rule

app = Flask(__name__)

# Load pre-computed results for fast demo
RESEARCH_DIR = Path(__file__).parent / 'research'

def load_demo_data():
    """Load sample data for demonstration"""
    with open(RESEARCH_DIR / 'gold_standard_annotated_v2.json', 'r', encoding='utf-8') as f:
        gold_standard = json.load(f)
    
    with open(RESEARCH_DIR / 'error_analysis_v2_results.json', 'r', encoding='utf-8') as f:
        error_analysis = json.load(f)
    
    # Select representative examples
    examples = {
        'obligation': gold_standard['rules'][0],  # First obligation
        'permission': None,
        'prohibition': None
    }
    
    # Find one of each type
    for rule in gold_standard['rules']:
        if rule.get('deontic_type') == 'permission' and examples['permission'] is None:
            examples['permission'] = rule
        elif rule.get('deontic_type') == 'prohibition' and examples['prohibition'] is None:
            examples['prohibition'] = rule
    
    return examples, gold_standard, error_analysis

DEMO_EXAMPLES, GOLD_STANDARD, ERROR_ANALYSIS = load_demo_data()


@app.route('/')
def index():
    """Landing page with demo overview"""
    stats = {
        'total_rules': len(GOLD_STANDARD['rules']),
        'accuracy': '99%',
        'triples': 1309,
        'formalization_success': '100%'
    }
    return render_template('index.html', stats=stats)


@app.route('/phase1')
def phase1_simplification():
    """Demonstrate text simplification"""
    examples = [
        {
            'raw': "Students must pay all\noutstanding fees before\nregistering for the next\nsemester.",
            'simplified': "Students must pay all outstanding fees before registering for the next semester.",
            'changes': {
                'line_breaks_removed': 3,
                'whitespace_normalized': 2
            }
        },
        {
            'raw': "International students may\napply for on-campus\naccommodation in the first   year   only.",
            'simplified': "International students may apply for on-campus accommodation in the first year only.",
            'changes': {
                'line_breaks_removed': 2,
                'whitespace_normalized': 3
            }
        }
    ]
    
    stats = {
        'rules_affected': '85/97 (88%)',
        'line_breaks_removed': 247,
        'accuracy_improvement': '+15pp'
    }
    
    return render_template('phase1.html', examples=examples, stats=stats)


@app.route('/phase2')
def phase2_classification():
    """Demonstrate LLM classification"""
    examples = {
        'obligation': DEMO_EXAMPLES['obligation'],
        'permission': DEMO_EXAMPLES['permission'],
        'prohibition': DEMO_EXAMPLES['prohibition']
    }
    
    stats = {
        'overall_accuracy': '99%',
        'obligation_accuracy': '100%',
        'permission_accuracy': '70%',
        'permission_improvement': '+33.6pp (36% → 70%)',
        'prohibition_accuracy': '100%'
    }
    
    return render_template('phase2.html', examples=examples, stats=stats)


@app.route('/api/classify', methods=['POST'])
def classify_api():
    """Live classification endpoint"""
    data = request.json
    rule_text = data.get('text', '')
    
    try:
        # Use your existing classification function
        result = classify_single_rule(rule_text)
        return jsonify({
            'success': True,
            'is_rule': result.get('is_rule', False),
            'deontic_type': result.get('deontic_type', 'unknown'),
            'confidence': result.get('confidence', 0),
            'reasoning': result.get('reasoning', '')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/phase3')
def phase3_formalization():
    """Demonstrate FOL formalization"""
    example = {
        'rule_text': "Students must pay all outstanding fees before registering for the next semester.",
        'classification': 'Obligation',
        'fol_formula': "∀x (Student(x) → Obligated(x, Before(PayFees(x), Register(x))))",
        'components': [
            {'name': 'Quantifier', 'value': '∀x', 'description': 'All students'},
            {'name': 'Type Predicate', 'value': 'Student(x)', 'description': 'Student entity'},
            {'name': 'Deontic Operator', 'value': 'Obligated', 'description': 'Must (obligation)'},
            {'name': 'Temporal', 'value': 'Before', 'description': 'Temporal constraint'},
            {'name': 'Actions', 'value': 'PayFees, Register', 'description': 'Predicates'}
        ]
    }
    
    stats = {
        'formalization_success': '100% (97/97)',
        'requires_hol': '0 rules (0%)',
        'fol_sufficient': 'Yes'
    }
    
    return render_template('phase3.html', example=example, stats=stats)


@app.route('/phase4')
def phase4_shacl():
    """Demonstrate SHACL translation"""
    example = {
        'fol': "∀x (Student(x) → Obligated(x, PayFees(x)))",
        'shacl': """ait:PaymentShape a sh:NodeShape ;
    sh:targetClass ait:Student ;
    sh:property [
        sh:path ait:paidFees ;
        sh:minCount 1 ;
        sh:severity sh:Violation
    ] .""",
        'mapping': [
            {'fol': '∀x', 'shacl': 'sh:targetClass ait:Student'},
            {'fol': 'Obligated', 'shacl': 'sh:minCount 1 + sh:Violation'},
            {'fol': 'PayFees', 'shacl': 'sh:path ait:paidFees'}
        ]
    }
    
    stats = {
        'total_triples': 1309,
        'total_shapes': 97,
        'validation': 'All shapes valid'
    }
    
    return render_template('phase4.html', example=example, stats=stats)


@app.route('/results')
def results_summary():
    """Show comprehensive results"""
    results = {
        'llm_performance': {
            'mistral': {'accuracy': '99.0%', 'status': 'winner'},
            'llama_70b': {'accuracy': '92.8%', 'status': ''},
            'mixtral': {'accuracy': '88.7%', 'status': ''},
            'gemma': {'accuracy': '85.6%', 'status': ''},
            'phi': {'accuracy': '82.3%', 'status': ''}
        },
        'baselines': {
            'regex': '82.5%',
            'majority': '48.5%',
            'random': '28.9%'
        },
        'ablation': {
            'baseline': '0%',
            'e1_explicit': '70%',
            'e2_context': '70%',
            'e3_contrastive': '30%'
        },
        'overall': {
            'rules_processed': 97,
            'classification_accuracy': '99%',
            'formalization_success': '100%',
            'rdf_triples': 1309,
            'false_positive_rate': '0%'
        }
    }
    
    return render_template('results.html', results=results)


if __name__ == '__main__':
    print("=" * 60)
    print("Research Demo UI Starting...")
    print("=" * 60)
    print("\nAvailable Pages:")
    print("  http://localhost:5001/          - Overview")
    print("  http://localhost:5001/phase1    - Text Simplification")
    print("  http://localhost:5001/phase2    - LLM Classification")
    print("  http://localhost:5001/phase3    - FOL Formalization")
    print("  http://localhost:5001/phase4    - SHACL Translation")
    print("  http://localhost:5001/results   - Comprehensive Results")
    print("\n" + "=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5001)
