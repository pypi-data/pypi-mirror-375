<img src="https://www.bitbuffet.dev/_next/image?url=%2Fbitbuffet-logo-closed-transparent.png&w=64&q=75" alt="BitBuffet Logo" width="64" height="64">

# BitBuffet Python SDK

[![PyPI version](https://badge.fury.io/py/bitbuffet.svg)](https://badge.fury.io/py/bitbuffet)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

A powerful Python SDK for the BitBuffet API that allows you to extract structured data from any web content using Pydantic models in under two seconds.

## 🚀 Features

- **Universal**: Works with any website or web content (url, image, video, audio, youtube, pdf, etc.)
- **Type-safe**: Built with Pydantic for complete type safety and validation
- **Fast**: Extract structured data in under 2 seconds
- **Flexible**: Support for custom prompts and reasoning levels
- **Easy to use**: Simple, intuitive API
- **Well-tested**: Comprehensive test suite with integration tests

## 📦 Installation

```bash
pip install bitbuffet
# or
poetry add bitbuffet
# or
uv add bitbuffet
```

## 🏃‍♂️ Quick Start

```python
from bitbuffet import BitBuffet
from pydantic import BaseModel, Field
from typing import List, Optional

# Define your data structure with Pydantic
class Article(BaseModel):
    title: str = Field(description="The main title of the article")
    author: str = Field(description="The author of the article")
    publish_date: str = Field(description="When the article was published")
    content: str = Field(description="The main content/body of the article")
    tags: List[str] = Field(description="Article tags or categories")
    summary: str = Field(description="A brief summary of the article")

# Initialize the client with your API key
client = BitBuffet(api_key="your-api-key-here") # Get your API key from https://bitbuffet.dev

# Extract structured data from any URL
try:
    result: Article = client.extract(
        url="https://example.com/article",
        schema_class=Article
    )
    
    print(f"Title: {result.title}")
    print(f"Author: {result.author}")
    print(f"Published: {result.publish_date}")
    print(f"Tags: {', '.join(result.tags)}")
except Exception as error:
    print(f"Extraction failed: {error}")
```

## ⚙️ Configuration Options

Customize the extraction process with various options:

```python
result = client.extract(
    url="https://example.com/complex-page",
    schema_class=Article,
    timeout=30,  # Timeout in seconds (default: 30)
    reasoning_effort="high",  # 'medium' | 'high' - Higher effort for complex pages
    prompt="Focus on extracting the main article content, ignoring ads and navigation",
    temperature=0.1,  # Lower for more consistent results (0.0 - 1.5)
    # OR use top_p instead of temperature
    # top_p=0.9
)
```

## 📚 Advanced Examples

### E-commerce Product Extraction

```python
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional

class Product(BaseModel):
    name: str
    price: float
    currency: str
    description: str
    images: List[HttpUrl]
    in_stock: bool
    rating: Optional[float] = Field(None, ge=0, le=5)
    reviews: Optional[int] = None

product = client.extract(
    url="https://shop.example.com/product/123",
    schema_class=Product,
    reasoning_effort="high"
)

print(f"Product: {product.name}")
print(f"Price: {product.price} {product.currency}")
print(f"In Stock: {product.in_stock}")
```

### News Article with Nested Models

```python
class Author(BaseModel):
    name: str
    bio: Optional[str] = None

class RelatedArticle(BaseModel):
    title: str
    url: HttpUrl

class NewsArticle(BaseModel):
    headline: str
    subheadline: Optional[str] = None
    author: Author
    published_at: str
    category: str
    content: str
    related_articles: Optional[List[RelatedArticle]] = None

article = client.extract(
    url="https://news.example.com/breaking-news",
    schema_class=NewsArticle
)

print(f"Headline: {article.headline}")
print(f"Author: {article.author.name}")
print(f"Category: {article.category}")
```

### Batch Processing Multiple URLs

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

def extract_article(url: str) -> Article:
    return client.extract(url=url, schema_class=Article)

# Process multiple URLs concurrently
urls = [
    "https://example.com/article1",
    "https://example.com/article2",
    "https://example.com/article3"
]

with ThreadPoolExecutor(max_workers=3) as executor:
    articles = list(executor.map(extract_article, urls))

for article in articles:
    print(f"Extracted: {article.title}")
```

## 🔧 API Reference

### `BitBuffet` Class

#### Constructor
```python
BitBuffet(api_key: str, base_url: str = None, timeout: int = 30)
```

#### Methods

##### `extract(url: str, schema_class: Type[BaseModel], **kwargs) -> BaseModel`

Extracts structured data from a URL using the provided Pydantic model.

**Parameters:**
- `url`: The URL to extract data from
- `schema_class`: Pydantic model class defining the expected data structure
- `timeout`: Request timeout in seconds (default: 30)
- `reasoning_effort`: 'medium' | 'high' (default: 'medium')
- `prompt`: Custom extraction prompt (optional)
- `temperature`: Sampling temperature 0.0-1.0 (optional)
- `top_p`: Alternative to temperature (optional)

**Returns:** Instance of the provided Pydantic model with extracted data

## 🛠️ Development

```bash
# Install dependencies with uv (recommended)
uv sync

# Or with pip
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=bitbuffet

# Run integration tests
pytest -m integration

# Build the package
python -m build
```

## 📋 Requirements

- Python >= 3.9
- pydantic >= 2.11.7
- requests >= 2.32.5

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Complete API Documentation](https://bitbuffet.dev/docs/overview) - Full API reference and guides
- [GitHub Repository](https://github.com/ystefanov6/bitbuffet-clients)
- [PyPI Package](https://pypi.org/project/bitbuffet/)
- [Report Issues](https://github.com/ystefanov6/bitbuffet-clients/issues)

## 💡 Need Help?

For detailed documentation, examples, and API reference, visit our [complete documentation](https://bitbuffet.dev/docs/overview).

If you encounter any issues or have questions, please [open an issue](https://github.com/ystefanov6/bitbuffet-clients/issues) on GitHub.