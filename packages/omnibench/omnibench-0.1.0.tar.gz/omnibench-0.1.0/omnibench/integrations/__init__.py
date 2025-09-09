"""
OmniBench Integrations

This package contains integration modules for various AI agent frameworks and libraries.
Each integration provides framework-specific benchmarkers and utilities to seamlessly
work with OmniBench.

Available integrations:
- pydantic_ai: Integration for Pydantic AI agents
"""

# Re-export integration modules for convenience
from . import pydantic_ai

__all__ = ["pydantic_ai"]
