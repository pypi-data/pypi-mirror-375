"""
Clappia Tools - LangChain integration for Clappia API

This package provides a unified client for interacting with Clappia APIs.
"""

from .client.app_definition_client import AppDefinitionClient
from .client.submission_client import SubmissionClient
from .client.workflow_definition_client import WorkflowDefinitionClient
from .client.analytics_client import AnalyticsClient
from .client.workplace_client import WorkplaceClient
from .client.base_client import BaseClappiaClient


__version__ = "1.0.2"
__all__ = [
    "AppDefinitionClient",
    "SubmissionClient",
    "WorkflowDefinitionClient",
    "AnalyticsClient",
    "WorkplaceClient",
    "BaseClappiaClient",
]


def __dir__():
    return __all__
