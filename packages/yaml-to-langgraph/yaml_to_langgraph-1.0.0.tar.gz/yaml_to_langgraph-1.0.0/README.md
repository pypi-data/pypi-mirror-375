# YAML to LangGraph Converter

A powerful tool for converting Defy YAML workflow files to LangGraph implementations with comprehensive validation and beautiful CLI output.

## Features

- 🔍 **YAML Schema Validation**: Comprehensive validation of workflow structure
- 🎨 **Rich CLI Interface**: Beautiful command-line interface with Click
- ⚡ **Fast Conversion**: Efficient parsing and code generation
- 🧪 **Comprehensive Testing**: Full test suite with pytest
- 📦 **Modern Packaging**: Standard Python package structure
- 🛠️ **Extensible**: Easy to customize and extend

## Installation

### From Source

```bash
git clone https://github.com/example/yaml-to-langgraph.git
cd yaml-to-langgraph
pip install -e .
```

### With Development Dependencies

```bash
pip install -e ".[dev]"
```

### With LangChain Dependencies

```bash
pip install -e ".[langchain]"
```

## Usage

### Command Line Interface

```bash
# Validate Defy YAML workflow
yaml-to-langgraph validate workflow.yml

# Convert Defy YAML to LangGraph
yaml-to-langgraph convert workflow.yml

# Convert with custom output directory
yaml-to-langgraph convert workflow.yml -o my_workflow

# List nodes without generating code
yaml-to-langgraph list-nodes workflow.yml

# Dry run to see what would be generated
yaml-to-langgraph dry-run workflow.yml

# Get help
yaml-to-langgraph --help
```

### Python API

```python
from yaml_to_langgraph import YAMLToLangGraphConverter

# Convert YAML workflow
converter = YAMLToLangGraphConverter("workflow.yml", "output_dir")
output_path = converter.convert()
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/example/yaml-to-langgraph.git
cd yaml-to-langgraph

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/yaml_to_langgraph --cov-report=html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

## Project Structure

```
yaml_to_langgraph/
├── src/
│   └── yaml_to_langgraph/
│       ├── __init__.py
│       ├── cli.py              # Command-line interface
│       ├── converter.py        # Main converter logic
│       ├── schema_validator.py # YAML validation
│       ├── yaml_parser.py      # YAML parsing
│       └── code_generator.py   # Code generation
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_sample_workflow.py
│   ├── test_cli.py
│   ├── test_converter.py
│   └── test_schema_validation.py
├── pyproject.toml
└── README.md
```

## Testing

The project includes a comprehensive test suite with 41 tests covering:

- **Schema Validation**: YAML structure validation
- **CLI Functionality**: Command-line interface testing
- **Core Converter**: Conversion logic testing
- **Sample Workflow**: Real-world workflow testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_schema_validation.py -v
pytest tests/test_cli.py -v
pytest tests/test_converter.py -v
pytest tests/test_sample_workflow.py -v
```

## Publishing

The package can be published to PyPI using several methods:

### Using UV (Recommended)
```bash
# Build the package
make build

# Publish with environment variables
export UV_PUBLISH_USERNAME=your-username
export UV_PUBLISH_PASSWORD=your-password
make publish

# Or publish with token
make publish-token TOKEN=your-pypi-token

# Publish to Test PyPI first
make publish-test TOKEN=your-testpypi-token
```

### Using Twine (Fallback)
If you prefer to use your existing `~/.pypirc` configuration:

```bash
# Build the package
make build

# Publish using twine (reads ~/.pypirc)
make publish-twine

# Publish to Test PyPI using twine
make publish-test-twine
```

### Manual Publishing
```bash
# Build
uv build

# Publish with uv
uv publish --token your-token

# Or with twine
python -m twine upload dist/*
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/example/yaml-to-langgraph/issues)
- **Documentation**: [GitHub Wiki](https://github.com/example/yaml-to-langgraph/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/example/yaml-to-langgraph/discussions)