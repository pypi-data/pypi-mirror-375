"""
Benchmark objectives for different evaluation scenarios.

This module contains various objective types for evaluating AI agent performance:
- BaseBenchmarkObjective: Abstract base class for all objectives
- CombinedBenchmarkObjective: Combines multiple objectives
- LLMJudgeObjective: LLM-based evaluation
- OutputBenchmarkObjective: Output-based evaluation
- PathBenchmarkObjective: Path-based evaluation
- StateBenchmarkObjective: State-based evaluation
"""

from omnibench.objectives.base import BaseBenchmarkObjective
from omnibench.objectives.combined import CombinedBenchmarkObjective
from omnibench.objectives.llm_judge import LLMJudgeObjective
from omnibench.objectives.output import StringEqualityObjective, RegexMatchObjective
from omnibench.objectives.path import PathEqualityObjective, PartialPathEqualityObjective
from omnibench.objectives.state import StateEqualityObjective, PartialStateEqualityObjective

__all__ = [
    "BaseBenchmarkObjective",
    "CombinedBenchmarkObjective", 
    "LLMJudgeObjective",
    "StringEqualityObjective",
    "RegexMatchObjective", 
    "PathEqualityObjective",
    "PartialPathEqualityObjective",
    "StateEqualityObjective",
    "PartialStateEqualityObjective",
]
