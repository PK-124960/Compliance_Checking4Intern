"""
Metrics Framework for Agentic Policy Formalization System
Provides measurable, academic-standard metrics for each pipeline step
with automatic improvement when below threshold.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum
import json


class MetricStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


@dataclass
class Metric:
    """Single metric with threshold and auto-improvement"""
    name: str
    value: float
    threshold: float
    unit: str = ""
    higher_is_better: bool = True
    improvement_action: str = ""
    
    @property
    def status(self) -> MetricStatus:
        if self.higher_is_better:
            if self.value >= self.threshold:
                return MetricStatus.PASS
            elif self.value >= self.threshold * 0.9:
                return MetricStatus.WARNING
            return MetricStatus.FAIL
        else:
            if self.value <= self.threshold:
                return MetricStatus.PASS
            elif self.value <= self.threshold * 1.1:
                return MetricStatus.WARNING
            return MetricStatus.FAIL
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self.value,
            "threshold": self.threshold,
            "unit": self.unit,
            "status": self.status.value,
            "improvement_action": self.improvement_action
        }


@dataclass
class StepMetrics:
    """Metrics for a single pipeline step"""
    step_id: int
    step_name: str
    rq: Optional[str] = None  # RQ1, RQ2, RQ3
    metrics: List[Metric] = field(default_factory=list)
    start_time: datetime = None
    end_time: datetime = None
    
    @property
    def duration(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def all_pass(self) -> bool:
        return all(m.status == MetricStatus.PASS for m in self.metrics)
    
    @property
    def needs_improvement(self) -> bool:
        return any(m.status == MetricStatus.FAIL for m in self.metrics)
    
    def get_failed_metrics(self) -> List[Metric]:
        return [m for m in self.metrics if m.status == MetricStatus.FAIL]
    
    def to_dict(self) -> dict:
        return {
            "step_id": self.step_id,
            "step_name": self.step_name,
            "rq": self.rq,
            "duration": self.duration,
            "all_pass": self.all_pass,
            "needs_improvement": self.needs_improvement,
            "metrics": [m.to_dict() for m in self.metrics]
        }


class MetricsCollector:
    """Collects and manages metrics across all pipeline steps"""
    
    # Academic threshold standards
    THRESHOLDS = {
        # RQ1: Classification
        "accuracy": 0.95,
        "f1_score": 0.90,
        "cohens_kappa": 0.80,
        "confidence": 0.85,
        
        # RQ2: Formalization
        "parse_success": 1.00,
        "syntactic_validity": 1.00,
        "semantic_accuracy": 0.95,
        
        # RQ3: Translation
        "translation_rate": 1.00,
        "false_positive": 0.02,  # Lower is better
        "false_negative": 0.01,  # Lower is better
    }
    
    IMPROVEMENT_ACTIONS = {
        "accuracy": "Switch to larger model (7B → 70B)",
        "f1_score": "Adjust classification prompt",
        "cohens_kappa": "Add few-shot examples",
        "confidence": "Lower decision threshold",
        "parse_success": "Use manual JSON extraction",
        "semantic_accuracy": "Flag for human review",
        "false_positive": "Adjust SHACL severity",
        "false_negative": "Tighten constraints",
    }
    
    def __init__(self):
        self.steps: Dict[int, StepMetrics] = {}
        self.run_id = datetime.now().isoformat()
    
    def start_step(self, step_id: int, step_name: str, rq: str = None):
        """Start tracking a pipeline step"""
        self.steps[step_id] = StepMetrics(
            step_id=step_id,
            step_name=step_name,
            rq=rq,
            start_time=datetime.now()
        )
    
    def end_step(self, step_id: int):
        """End tracking a pipeline step"""
        if step_id in self.steps:
            self.steps[step_id].end_time = datetime.now()
    
    def add_metric(self, step_id: int, name: str, value: float, 
                   unit: str = "", higher_is_better: bool = True):
        """Add a metric to a step"""
        if step_id not in self.steps:
            return
        
        threshold = self.THRESHOLDS.get(name, 0.95)
        improvement = self.IMPROVEMENT_ACTIONS.get(name, "Manual review")
        
        metric = Metric(
            name=name,
            value=value,
            threshold=threshold,
            unit=unit,
            higher_is_better=higher_is_better,
            improvement_action=improvement
        )
        self.steps[step_id].metrics.append(metric)
    
    def get_step_summary(self, step_id: int) -> dict:
        """Get summary for a single step"""
        if step_id in self.steps:
            return self.steps[step_id].to_dict()
        return {}
    
    def get_full_report(self) -> dict:
        """Get full metrics report"""
        total_steps = len(self.steps)
        passed_steps = sum(1 for s in self.steps.values() if s.all_pass)
        
        # Group by RQ
        rq_metrics = {"RQ1": [], "RQ2": [], "RQ3": []}
        for step in self.steps.values():
            if step.rq:
                rq_metrics[step.rq].append(step.to_dict())
        
        return {
            "run_id": self.run_id,
            "total_steps": total_steps,
            "passed_steps": passed_steps,
            "pass_rate": passed_steps / total_steps if total_steps > 0 else 0,
            "steps": [s.to_dict() for s in self.steps.values()],
            "by_research_question": rq_metrics,
            "needs_improvement": [
                s.to_dict() for s in self.steps.values() 
                if s.needs_improvement
            ]
        }
    
    def calculate_cohens_kappa(self, human_labels: List[int], 
                                llm_labels: List[int]) -> float:
        """Calculate Cohen's Kappa for inter-rater agreement"""
        if len(human_labels) != len(llm_labels) or len(human_labels) == 0:
            return 0.0
        
        n = len(human_labels)
        
        # Observed agreement
        agree = sum(1 for h, l in zip(human_labels, llm_labels) if h == l)
        po = agree / n
        
        # Expected agreement
        h_pos = sum(human_labels) / n
        l_pos = sum(llm_labels) / n
        pe = (h_pos * l_pos) + ((1 - h_pos) * (1 - l_pos))
        
        # Kappa
        if pe == 1:
            return 1.0
        return (po - pe) / (1 - pe)
    
    def calculate_f1(self, tp: int, fp: int, fn: int) -> float:
        """Calculate F1 score"""
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)


class SelfImprovement:
    """Automatic improvement when metrics below threshold"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.collector = metrics_collector
        self.improvement_history = []
    
    def check_and_improve(self, step_id: int) -> List[dict]:
        """Check step metrics and return improvement actions"""
        if step_id not in self.collector.steps:
            return []
        
        step = self.collector.steps[step_id]
        actions = []
        
        for metric in step.get_failed_metrics():
            action = {
                "metric": metric.name,
                "current_value": metric.value,
                "threshold": metric.threshold,
                "action": metric.improvement_action,
                "timestamp": datetime.now().isoformat()
            }
            actions.append(action)
            self.improvement_history.append(action)
        
        return actions
    
    def get_improvement_history(self) -> List[dict]:
        return self.improvement_history


# Global metrics collector instance
metrics_collector = MetricsCollector()
self_improvement = SelfImprovement(metrics_collector)
