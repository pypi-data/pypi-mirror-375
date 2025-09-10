# marlo-sentiment

Python client for the [Marlo sentiment analysis API](https://marlo.cloud) with industry-specific intelligence.

## Installation

```bash
pip install marlo-sentiment
```

## Usage

### Basic Usage

```python
from marlo_sentiment import MarloClient

client = MarloClient(api_key='your-rapidapi-key')

# Analyze text sentiment
result = client.analyze('I love this product!')
print(result)
# {
#     'sentiment': 'positive',
#     'confidence': 0.9162,
#     'scores': {
#         'positive': 0.647,
#         'neutral': 0.353,
#         'negative': 0.0,
#         'compound': 0.9162
#     },
#     'text_length': 20
# }
```

### Industry-Specific Analysis

```python
# Healthcare context
healthcare_result = client.analyze(
    'Strong medication led to successful treatment',
    industry='healthcare'
)

# Gaming context  
gaming_result = client.analyze(
    'Epic gameplay but pay-to-win ruins it',
    industry='gaming'
)

# Technology context
tech_result = client.analyze(
    'Memory leak in the application',
    industry='technology'
)
```

### Batch Analysis

```python
texts = [
    'Great customer service!',
    'Product arrived damaged', 
    'Fast shipping, excellent quality'
]

results = client.batch_analyze(texts, industry='retail')
```

### Supported Industries

```python
industries = client.get_supported_industries()
print(industries)
# ['healthcare', 'technology', 'gaming', 'finance', 'restaurant',
#  'automotive', 'real_estate', 'fitness', 'education', 'retail']
```

## Configuration

### Using Configuration Dict

```python
from marlo_sentiment import MarloClient

client = MarloClient({
    'api_key': 'your-rapidapi-key',
    'base_url': 'https://custom-endpoint.com',  # optional
    'timeout': 5.0  # optional, default 10.0 seconds
})
```

### Using API Key String

```python
client = MarloClient('your-rapidapi-key')
```

## Error Handling

```python
from marlo_sentiment import MarloClient, MarloError, MarloValidationError

try:
    result = client.analyze('')
except MarloValidationError as e:
    print(f"Validation error: {e}")
except MarloError as e:
    print(f"API error {e.status_code}: {e.message}")
```

## Context Manager Support

```python
with MarloClient('your-api-key') as client:
    result = client.analyze('Great service!')
    print(result.sentiment)
```

## Type Hints

Full type hint support:

```python
from marlo_sentiment import MarloClient, SentimentResponse, Industry

client = MarloClient('your-key')
result: SentimentResponse = client.analyze('text', industry='healthcare')
```

## Requirements

- Python 3.8+
- requests >= 2.28.0

## Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
isort src/
```

### Type Checking

```bash
mypy src/
```

## Resources

- **[Marlo API Documentation](https://marlo.cloud)** - Complete API guide and examples
- **[PyPI Package](https://pypi.org/project/marlo-sentiment/)** - Install via pip
- **[GitHub Repository](https://github.com/marlocloud/clients)** - Source code and issues
- **[Support](https://marlo.cloud/support)** - Get help and contact support

## License

MIT