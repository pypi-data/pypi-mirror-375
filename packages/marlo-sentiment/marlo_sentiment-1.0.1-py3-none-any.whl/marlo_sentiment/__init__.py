"""Marlo Sentiment Analysis Client

A Python client for the Marlo sentiment analysis API with industry-specific intelligence.
"""

from .client import MarloClient
from .exceptions import MarloError
from .types import (
    SentimentResponse,
    SentimentScores,
    Industry,
    AnalyzeRequest,
    MarloClientConfig
)

__version__ = "1.0.1"
__author__ = "Marlo Team"
__email__ = "team@marlo.cloud"

__all__ = [
    "MarloClient",
    "MarloError", 
    "SentimentResponse",
    "SentimentScores",
    "Industry",
    "AnalyzeRequest",
    "MarloClientConfig"
]