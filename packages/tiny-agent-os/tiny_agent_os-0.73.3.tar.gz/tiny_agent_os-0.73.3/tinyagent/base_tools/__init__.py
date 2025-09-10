"""
Base Tools Package

Collection of common tools that can be used with ReactAgent.
Each tool module is designed to be imported independently or as a group.
"""

from .web_search import web_search

__all__ = [
    "web_search",
]
