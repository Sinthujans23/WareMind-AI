
"""Compatibility helper for Experta on modern Python."""

import collections
import collections.abc

if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping

from experta import Fact, KnowledgeEngine, Rule

__all__ = ["Fact", "KnowledgeEngine", "Rule"]
