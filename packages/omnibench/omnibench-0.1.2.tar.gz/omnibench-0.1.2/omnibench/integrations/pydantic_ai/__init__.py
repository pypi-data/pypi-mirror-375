"""
Pydantic AI Integration for OmniBench

This module provides seamless integration between OmniBench and Pydantic AI agents.
It includes a specialized benchmarker that handles Pydantic AI's AgentRunResult objects
and converts them to the dictionary format expected by OmniBench objectives.

Key components:
- PydanticAIOmniBenchmarker: Custom benchmarker with output conversion for Pydantic AI
"""

from .benchmarker import PydanticAIOmniBenchmarker

__all__ = ["PydanticAIOmniBenchmarker"]
