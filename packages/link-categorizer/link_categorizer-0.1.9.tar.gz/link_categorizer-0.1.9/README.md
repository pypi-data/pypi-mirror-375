# Link Categorizer

A Python library that categorizes HTML links based on their domain names,
title text, and anchor text.

## Overview

Link Categorizer analyzes an array of Python dictionaries representing HTML
anchor tags and assigns each link to a category based on its domain name. The
library extracts the domain from the `href` attribute and matches it against
known patterns to determine the most appropriate category.

If a link's domain does not match any known patterns, it is assigned to the
"unknown" category by default.

## Installation

```bash
pip install link-categorizer
```
## Development Installation

To install the package for development:

```bash
# Clone the repository
git clone https://github.com/heysamtexas/link-categorizer.git
cd link-categorizer

# Install with uv (recommended)
uv pip install -e .[dev]

# Alternative: Create virtual environment first
uv venv
uv pip install -e .[dev]
```

## Usage

```python
from link_categorizer import categorize_links

# Example list of link dictionaries
links = [
    {"href": "https://github.com/user/repo", "title": "Source code", "text": "GitHub Repository"},
    {"href": "https://medium.com/article", "title": "My thoughts", "text": "Read my blog"},
    {"href": "https://x.com/username", "text": "Follow me"},
    {"href": "https://twitter.com/username", "text": "Follow me on Twitter"},
    {"href": "https://docs.python.org/3/", "text": "Python Documentation"},
]

# Categorize the links
categorized_links = categorize_links(links)

# Result will be a dictionary with categories as keys and lists of links as values
# {
#   "repository": [{"href": "https://github.com/user/repo", ...}],
#   "blog": [{"href": "https://medium.com/article", ...}],
#   "social": [{"href": "https://x.com/username", ...}, {"href": "https://twitter.com/username", ...}],
#   "documentation": [{"href": "https://docs.python.org/3/", ...}]
# }
```

## How Categorization Works

The library employs a straightforward domain-based approach to categorize links:

1. Extract the domain name from the link's `href` attribute
2. Compare the domain against a predefined list of domain patterns
3. Assign the category associated with the matching domain pattern
4. If no match is found, assign the "unknown" category


## Supported Categories

The library can identify various link categories including:

- Repository (code hosting platforms)
- Social media
- Blog platforms
- Documentation sites
- News outlets
- Video platforms
- E-commerce sites
- And more...

## Project Structure

```
link-categorizer/
├── src/
│   └── link_categorizer/
│       ├── __init__.py
│       └── categorizer.py
├── tests/
├── setup.py
├── LICENSE
└── README.md
```

## Running Tests

To run the tests:

```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest --cov=src/link_categorizer tests/

# Run specific test
uv run pytest tests/link_categorizer_test.py::test_categorize_link_domains -v

# Run code quality checks
uv run ruff check src/
uv run mypy src/
```

## Adding More Tests

The test structure is designed to be easily expandable:

### Adding new test cases to existing categories

Open `tests/link_categorizer_test.py` and add new test cases to the appropriate test method:

### Best practices for tests

- Keep test methods focused on specific categories or behaviors
- Use descriptive test method names
- Add docstrings to explain what each test is verifying
- Use the `self.subTest()` context manager for better error reporting (already implemented)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is released under the MIT License.
