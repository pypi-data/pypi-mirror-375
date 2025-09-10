"""Marlo sentiment analysis client implementation."""

import json
from typing import Dict, List, Optional, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .types import Industry, SentimentResponse, MarloClientConfig
from .exceptions import (
    MarloError,
    MarloAPIError,
    MarloValidationError,
    MarloAuthenticationError,
    MarloRateLimitError
)


class MarloClient:
    """Client for Marlo sentiment analysis API with industry-specific intelligence."""
    
    DEFAULT_BASE_URL = "https://your-api-gateway-url.amazonaws.com/prod"
    DEFAULT_TIMEOUT = 10.0
    SUPPORTED_INDUSTRIES: List[Industry] = [
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
    
    def __init__(self, config: Union[MarloClientConfig, str]) -> None:
        """Initialize Marlo client.
        
        Args:
            config: Either a MarloClientConfig dict or API key string
        """
        if isinstance(config, str):
            config = {"api_key": config}
            
        self.api_key = config["api_key"]
        self.base_url = config.get("base_url", self.DEFAULT_BASE_URL)
        self.timeout = config.get("timeout", self.DEFAULT_TIMEOUT)
        
        # Setup session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "sentiment-api.rapidapi.com",
            "User-Agent": "marlo-sentiment-python/1.0.0"
        })
    
    def analyze(self, text: str, industry: Optional[Industry] = None) -> SentimentResponse:
        """Analyze sentiment of text with optional industry context.
        
        Args:
            text: Text to analyze (max 5000 characters)
            industry: Optional industry context for improved accuracy
            
        Returns:
            SentimentResponse with analysis results
            
        Raises:
            MarloValidationError: Invalid input parameters
            MarloAuthenticationError: Invalid API key
            MarloRateLimitError: Rate limit exceeded
            MarloAPIError: Other API errors
        """
        self._validate_text(text)
        
        if industry and industry not in self.SUPPORTED_INDUSTRIES:
            raise MarloValidationError(
                f"Unsupported industry: {industry}. "
                f"Supported: {', '.join(self.SUPPORTED_INDUSTRIES)}"
            )
        
        payload = {"text": text}
        if industry:
            payload["industry"] = industry
            
        try:
            response = self.session.post(
                f"{self.base_url}/analyze",
                json=payload,
                timeout=self.timeout
            )
            self._handle_response(response)
            return response.json()
            
        except requests.exceptions.Timeout:
            raise MarloAPIError("Request timeout", 408)
        except requests.exceptions.ConnectionError:
            raise MarloAPIError("Connection error", 503)
        except requests.exceptions.RequestException as e:
            raise MarloAPIError(f"Request failed: {str(e)}", 500)
    
    def batch_analyze(
        self, 
        texts: List[str], 
        industry: Optional[Industry] = None
    ) -> List[SentimentResponse]:
        """Analyze multiple texts in batch.
        
        Args:
            texts: List of texts to analyze (max 100 items)
            industry: Optional industry context for all texts
            
        Returns:
            List of SentimentResponse objects
            
        Raises:
            MarloValidationError: Invalid input parameters
            MarloAPIError: API errors
        """
        if not texts:
            raise MarloValidationError("Texts list cannot be empty")
            
        if len(texts) > 100:
            raise MarloValidationError("Cannot analyze more than 100 texts at once")
        
        results = []
        for text in texts:
            result = self.analyze(text, industry)
            results.append(result)
            
        return results
    
    def get_supported_industries(self) -> List[Industry]:
        """Get list of supported industries.
        
        Returns:
            List of supported industry identifiers
        """
        return self.SUPPORTED_INDUSTRIES.copy()
    
    def set_api_key(self, api_key: str) -> None:
        """Update API key.
        
        Args:
            api_key: New API key
        """
        self.api_key = api_key
        self.session.headers["X-RapidAPI-Key"] = api_key
    
    def set_base_url(self, base_url: str) -> None:
        """Update base URL.
        
        Args:
            base_url: New base URL
        """
        self.base_url = base_url
    
    def _validate_text(self, text: str) -> None:
        """Validate input text."""
        if not text or not text.strip():
            raise MarloValidationError("Text cannot be empty")
            
        if len(text) > 5000:
            raise MarloValidationError("Text cannot exceed 5000 characters")
    
    def _handle_response(self, response: requests.Response) -> None:
        """Handle HTTP response and raise appropriate exceptions."""
        if response.status_code == 200:
            return
            
        try:
            error_data = response.json()
            error_message = error_data.get("message", response.text)
        except (json.JSONDecodeError, ValueError):
            error_message = response.text or "Unknown error"
        
        if response.status_code == 401:
            raise MarloAuthenticationError(error_message, response.status_code)
        elif response.status_code == 429:
            raise MarloRateLimitError(error_message, response.status_code)
        elif response.status_code >= 400:
            raise MarloAPIError(error_message, response.status_code)
        else:
            raise MarloError(error_message, response.status_code)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.session.close()