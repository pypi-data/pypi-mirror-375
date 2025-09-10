"""Type definitions for Marlo sentiment analysis client."""

from typing import Dict, Literal, Optional, TypedDict

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict


class SentimentScores(TypedDict):
    """Sentiment scores breakdown."""
    positive: float
    neutral: float
    negative: float
    compound: float


class SentimentResponse(TypedDict):
    """Response from sentiment analysis API."""
    sentiment: Literal['positive', 'negative', 'neutral']
    confidence: float
    scores: SentimentScores
    text_length: int
    industry: Optional[str]


class AnalyzeRequest(TypedDict, total=False):
    """Request payload for sentiment analysis."""
    text: str
    industry: Optional[str]


class MarloClientConfig(TypedDict, total=False):
    """Configuration for MarloClient."""
    api_key: str
    base_url: Optional[str]
    timeout: Optional[float]


# Industry types
Industry = Literal[
    'healthcare',
    'technology',
    'gaming',
    'finance', 
    'restaurant',
    'automotive',
    'real_estate',
    'fitness',
    'education',
    'retail'
]