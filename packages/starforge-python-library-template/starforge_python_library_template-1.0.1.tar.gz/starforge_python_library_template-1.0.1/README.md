# Starforge Python Library Template

A production-ready Python library template for Starforge projects. This template provides a complete foundation for building, testing, and publishing Python libraries with modern tooling and best practices.

## 🚀 Features

- **Modern Python Packaging**: Uses `pyproject.toml` for configuration
- **Comprehensive Testing**: Supports both unittest and pytest
- **Code Quality**: Integrated pylint, coverage, and formatting tools
- **CI/CD Pipeline**: GitHub Actions workflows for testing and publishing
- **Documentation Ready**: Sphinx configuration for professional docs
- **CLI Support**: Built-in command-line interface functionality
- **Type Hints**: Full type annotation support
- **Professional Structure**: Follows Python packaging best practices

## 📦 Quick Start

### Installation

```bash
# Clone the template
git clone <repository-url>
cd python-library-template

# Install in development mode
pip install -e ".[dev]"

# Or install with all dependencies
make install-dev
```

### Usage

```python
from starforge_library_template import HelloWorld

# Basic usage
greeter = HelloWorld()
print(greeter.greet())  # Output: Hello

# Personalized greeting
print(greeter.greet_with_name("Python"))  # Output: Hello, Python!
```

### Command Line Interface

```bash
# Run the CLI
python -m starforge_library_template

# Or if installed
starforge_library_template
```

## 🛠️ Development

### Setup Development Environment

```bash
# Install development dependencies
make install-dev

# Run tests
make test

# Run tests with coverage
make test-cov

# Run linting
make lint

# Build package
make build
```

### Available Commands

| Command | Description |
|---------|-------------|
| `make install` | Install package in development mode |
| `make install-dev` | Install with development dependencies |
| `make test` | Run test suite |
| `make test-cov` | Run tests with coverage report |
| `make lint` | Run pylint code quality checks |
| `make clean` | Clean build artifacts |
| `make build` | Build package for distribution |
| `make check-dist` | Check distribution files |
| `make demo` | Run CLI demo |

## 🧪 Testing

The template includes comprehensive testing setup:

```bash
# Run with unittest
python -m unittest discover tests/ -v

# Run with pytest
python -m pytest tests/ -v

# Run with coverage
python -m coverage run -m unittest discover tests/ -v
python -m coverage report
```

## 📋 Project Structure

```
python-library-template/
├── .github/
│   └── workflows/           # GitHub Actions CI/CD
├── starforge_library_template/
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # CLI entry point
│   └── hello_world.py      # Example library code
├── tests/
│   ├── test_hello_world.py # Unit tests
│   └── test-requirements.txt
├── pyproject.toml          # Modern Python configuration
├── Makefile               # Development commands
├── MANIFEST.in            # Package manifest
└── README.md              # This file
```

## 🔧 Configuration

### Package Configuration

The template uses `pyproject.toml` for all configuration:

- **Package metadata**: Name, version, description, authors
- **Dependencies**: Core and development dependencies
- **Build system**: Modern setuptools configuration
- **Tool configuration**: Pylint, coverage, pytest settings

### GitHub Actions

- **Pull Request Checks**: Automated testing and linting on PRs
- **Publishing**: Automated PyPI publishing on releases
- **Modular Workflows**: Reusable workflow components

## 📚 Documentation

### Building Documentation

```bash
# Install documentation dependencies
pip install sphinx sphinx-rtd-theme

# Build documentation
sphinx-build -b html docs/ docs/_build/html
```

### Code Documentation

The template follows Google-style docstrings:

```python
def greet_with_name(self, name: str) -> str:
    """
    Return a personalized greeting message.
    
    Args:
        name (str): The name to include in the greeting.
        
    Returns:
        str: A personalized greeting message.
    """
    return f'Hello, {name}!'
```

## 🚀 Publishing

### PyPI Publishing

1. **Create a release** on GitHub
2. **Set up PyPI credentials** in repository secrets:
   - `PYPI_API_TOKEN`: Your PyPI API token
3. **Publishing happens automatically** via GitHub Actions

### Manual Publishing

```bash
# Build package
make build

# Check distribution
make check-dist

# Upload to PyPI
make upload-pypi
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass and code quality checks
6. Submit a pull request

## 📄 License

This project is licensed under the terms specified in the LICENSE file.

## 🏗️ Using as a Template

To use this template for a new project:

1. **Clone this repository**
2. **Update package information** in `pyproject.toml`
3. **Replace example code** in `starforge_library_template/`
4. **Update tests** in `tests/`
5. **Customize workflows** in `.github/workflows/`
6. **Update this README** with your project details

## 🔗 Links

- **Homepage**: [GitHub Repository](https://github.com/starforge-universe/python-library-template)
- **Documentation**: [Read the Docs](https://python-library-template.readthedocs.io/)
- **Issues**: [Bug Tracker](https://github.com/starforge-universe/python-library-template/issues)

---

**Built with ❤️ for the Starforge ecosystem**
