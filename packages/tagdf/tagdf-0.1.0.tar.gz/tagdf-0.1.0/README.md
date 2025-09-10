# tagdf

Tools for annotating and labelling Pandas DataFrames and general Python objects.

## Installation

### From Source
```bash
git clone https://github.com/idin/tagdf.git
cd tagdf
conda env create -f environment.yml
conda activate tagdf
pip install -e .
```

### From PyPI (when published)
```bash
pip install tagdf
```

## Quick Start

```python
from tagdf import __version__

print(__version__)
```

## Features

- Feature 1: Description
- Feature 2: Description
- Feature 3: Description

## Documentation

For detailed documentation, see the `demos/` directory for working examples.

## Development

### Setup Development Environment
```bash
conda env create -f environment.yml
conda activate package-name
pip install -e ".[dev]"
```

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
flake8 .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run tests and formatting
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### Version 0.1.0
- Initial release
- Basic functionality implemented
