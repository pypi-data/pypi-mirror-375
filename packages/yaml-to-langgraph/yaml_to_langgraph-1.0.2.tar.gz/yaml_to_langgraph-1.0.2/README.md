# YAML to LangGraph Converter

A powerful tool for converting Defy YAML workflow files to LangGraph implementations with comprehensive validation, beautiful CLI output, and professional workflow visualization.

## Features

- 🔍 **YAML Schema Validation**: Comprehensive validation of workflow structure
- 🎨 **Rich CLI Interface**: Beautiful command-line interface with Click
- ⚡ **Fast Conversion**: Efficient parsing and code generation
- 🧪 **Comprehensive Testing**: Full test suite with pytest
- 📦 **Modern Packaging**: Standard Python package structure
- 🛠️ **Extensible**: Easy to customize and extend
- 🎨 **Professional Visualization**: High-quality workflow diagrams using Mermaid + Pyppeteer
- 🔄 **Advanced Loop Support**: Proper handling of complex loop structures with break conditions
- 📊 **State Management**: Intelligent variable reference handling and state tracking
- 🎯 **Multiple Themes**: Default, dark, forest, and neutral visualization themes

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

#### Basic Commands

```bash
# Validate YAML workflow file
yaml-to-langgraph validate workflow.yml

# Convert YAML to LangGraph implementation
yaml-to-langgraph convert workflow.yml

# Convert with custom output directory
yaml-to-langgraph convert workflow.yml --output my_workflow

# Convert with verbose output
yaml-to-langgraph convert workflow.yml --verbose

# Skip validation (not recommended)
yaml-to-langgraph convert workflow.yml --skip-validation

# List all nodes in the workflow
yaml-to-langgraph list-nodes workflow.yml

# Dry run to see what would be generated
yaml-to-langgraph dry-run workflow.yml

# Get help for any command
yaml-to-langgraph --help
yaml-to-langgraph convert --help
yaml-to-langgraph validate --help
```

#### 🎨 Workflow Visualization

```bash
# Generate a visual representation of the workflow
yaml-to-langgraph visualize workflow.yml

# Visualize with different themes
yaml-to-langgraph visualize workflow.yml --theme dark
yaml-to-langgraph visualize workflow.yml --theme forest
yaml-to-langgraph visualize workflow.yml --theme neutral

# Customize visualization output
yaml-to-langgraph visualize workflow.yml --output my_workflow.png
yaml-to-langgraph visualize workflow.yml --format svg
yaml-to-langgraph visualize workflow.yml --size 30 20
yaml-to-langgraph visualize workflow.yml --dpi 300

# Different layout algorithms
yaml-to-langgraph visualize workflow.yml --layout hierarchical
yaml-to-langgraph visualize workflow.yml --layout flowchart
yaml-to-langgraph visualize workflow.yml --layout graph

# Show edge labels (can make complex graphs cluttered)
yaml-to-langgraph visualize workflow.yml --show-edge-labels

# Disable loop grouping
yaml-to-langgraph visualize workflow.yml --no-loops
```

#### Validation Examples

```bash
# Basic validation
yaml-to-langgraph validate workflow.yml

# Strict validation (treats warnings as errors)
yaml-to-langgraph validate workflow.yml --strict

# Validate with detailed output
yaml-to-langgraph validate workflow.yml --verbose
```

#### Conversion Examples

```bash
# Simple conversion (includes automatic visualization)
yaml-to-langgraph convert sample_workflow.yml

# Convert without visualization
yaml-to-langgraph convert sample_workflow.yml --no-visualization

# Convert to specific directory
yaml-to-langgraph convert sample_workflow.yml --output generated_workflow

# Convert with verbose output to see all generated files
yaml-to-langgraph convert sample_workflow.yml --verbose

# Convert multiple workflows
for file in workflows/*.yml; do
    yaml-to-langgraph convert "$file" --output "generated_$(basename "$file" .yml)"
done
```

### Python API

#### Basic Usage

```python
from yaml_to_langgraph import YAMLToLangGraphConverter
from yaml_to_langgraph.schema_validator import validate_yaml_workflow

# Validate a workflow
result = validate_yaml_workflow("workflow.yml")
if result.is_valid:
    print("Workflow is valid!")
    if result.warnings:
        print(f"Warnings: {[w.message for w in result.warnings]}")
else:
    print(f"Validation failed: {[e.message for e in result.errors]}")

# Convert YAML workflow to LangGraph
converter = YAMLToLangGraphConverter("workflow.yml", "output_dir")
output_path = converter.convert()
print(f"Generated workflow at: {output_path}")
```

#### Advanced Usage

```python
from yaml_to_langgraph import YAMLToLangGraphConverter
from yaml_to_langgraph.yaml_parser import YAMLWorkflowParser
from yaml_to_langgraph.code_generator import LangGraphCodeGenerator

# Parse YAML workflow
parser = YAMLWorkflowParser("workflow.yml")
workflow_data = parser.parse()

# Generate code
generator = LangGraphCodeGenerator(workflow_data)
code_files = generator.generate_code("output_dir")

# Access specific components
print(f"Workflow name: {workflow_data.app.name}")
print(f"Number of nodes: {len(workflow_data.graph.nodes)}")
print(f"Number of edges: {len(workflow_data.graph.edges)}")

# Get LLM nodes
llm_nodes = [node for node in workflow_data.graph.nodes if node.type == "llm"]
print(f"LLM nodes: {[node.id for node in llm_nodes]}")

# Access loop information
for loop in workflow_data.loops:
    print(f"Loop {loop.id}: {loop.title}")
    print(f"  Max iterations: {loop.max_iterations}")
    print(f"  Break conditions: {loop.break_conditions}")
    print(f"  Child nodes: {[node.id for node in loop.child_nodes]}")

# Access state variables
for var in workflow_data.state_variables:
    print(f"State variable: {var.node_id}.{var.variable_name} ({var.variable_type})")
```

#### 🎨 Visualization API

```python
from yaml_to_langgraph.graph_visualizer import GraphVisualizer, VisualizationConfig
from yaml_to_langgraph.yaml_parser import YAMLWorkflowParser

# Parse workflow
parser = YAMLWorkflowParser("workflow.yml")
workflow_info = parser.parse()

# Create visualization config
config = VisualizationConfig(
    output_format="png",           # png, svg, pdf
    layout_algorithm="hierarchical", # hierarchical, flowchart, graph
    figure_size=(24, 16),          # width, height in inches
    dpi=300,                       # resolution
    theme="default",               # default, dark, forest, neutral
    show_edge_labels=False,        # show edge labels
    show_loops=True,               # enable loop grouping
    loop_grouping=True,            # group loop nodes
    max_label_length=20            # truncate long labels
)

# Generate visualization
visualizer = GraphVisualizer(config)
output_path = visualizer.visualize_workflow(workflow_info, "workflow_diagram.png")
print(f"Visualization saved to: {output_path}")
```

#### Error Handling

```python
from yaml_to_langgraph import YAMLToLangGraphConverter
from yaml_to_langgraph.schema_validator import ValidationError

try:
    converter = YAMLToLangGraphConverter("invalid_workflow.yml", "output")
    output_path = converter.convert()
except ValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Path: {e.path}")
except FileNotFoundError:
    print("YAML file not found")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Generated Code Structure

When you convert a YAML workflow, the following structure is generated:

```
generated_workflow/
├── prompts/                    # Prompt templates for LLM nodes
│   ├── node1_prompt.py
│   ├── node2_prompt.py
│   └── ...
├── nodes/                      # Node implementations
│   ├── workflow_nodes.py
│   ├── llm_node.py            # Enhanced LLM nodes with state management
│   └── custom_nodes.py
├── edges/                      # Edge definitions and routing logic
│   ├── routing.py
│   └── conditions.py
├── workflow_graph.py          # Main graph assembly
├── loop_aware_graph.py        # Advanced loop handling with LangGraph For constructs
├── example_usage.py           # Usage example
├── requirements.txt           # Dependencies
├── workflow_graph.png         # Professional workflow visualization
└── README.md                  # Generated documentation
```

### Using the Generated Workflow

```python
# After conversion, use the generated workflow
from workflow_graph import create_workflow_graph, run_workflow
from langchain_openai import ChatOpenAI

# Initialize your model
model = ChatOpenAI(model="gpt-4", temperature=0.7)

# Create the workflow graph
graph = create_workflow_graph(model)

# Run the workflow
result = run_workflow(
    graph=graph,
    input_data={"user_input": "Hello, world!"}
)

print(result)
```

### Real-World Examples

#### Example 1: Simple Chat Workflow

```yaml
# simple_chat.yml
app:
  name: "simple-chat"
  description: "A simple chat workflow"

workflow:
  graph:
    nodes:
      - id: "start"
        type: "start"
        data:
          type: "start"
          title: "Start"
      - id: "chat"
        type: "llm"
        data:
          type: "llm"
          title: "Chat Response"
          model:
            provider: "openai"
            name: "gpt-4"
          prompt_template:
            - role: "user"
              content: "{{user_input}}"
      - id: "end"
        type: "end"
        data:
          type: "end"
          title: "End"
    edges:
      - id: "edge1"
        source: "start"
        target: "chat"
        data:
          label: "always"
      - id: "edge2"
        source: "chat"
        target: "end"
        data:
          label: "always"
```

Convert and use:
```bash
yaml-to-langgraph convert simple_chat.yml --output simple_chat_workflow
cd simple_chat_workflow
pip install -r requirements.txt
python example_usage.py
```

#### Example 2: Multi-Step Processing Workflow

```yaml
# processing_workflow.yml
app:
  name: "data-processor"
  description: "Multi-step data processing workflow"

workflow:
  graph:
    nodes:
      - id: "start"
        type: "start"
        data:
          type: "start"
      - id: "analyze"
        type: "llm"
        data:
          type: "llm"
          title: "Data Analyzer"
          model:
            provider: "openai"
            name: "gpt-4"
          prompt_template:
            - role: "system"
              content: "Analyze the following data: {{input_data}}"
      - id: "process"
        type: "llm"
        data:
          type: "llm"
          title: "Data Processor"
          model:
            provider: "openai"
            name: "gpt-4"
          prompt_template:
            - role: "system"
              content: "Process the analyzed data: {{analyze.output}}"
      - id: "validate"
        type: "llm"
        data:
          type: "llm"
          title: "Data Validator"
          model:
            provider: "openai"
            name: "gpt-4"
          prompt_template:
            - role: "system"
              content: "Validate the processed data: {{process.output}}"
      - id: "end"
        type: "end"
        data:
          type: "end"
    edges:
      - id: "e1"
        source: "start"
        target: "analyze"
        data:
          label: "always"
      - id: "e2"
        source: "analyze"
        target: "process"
        data:
          label: "success"
      - id: "e3"
        source: "process"
        target: "validate"
        data:
          label: "success"
      - id: "e4"
        source: "validate"
        target: "end"
        data:
          label: "valid"
```

#### Example 3: Complex Loop Workflow

```yaml
# loop_workflow.yml
app:
  name: "iterative-processor"
  description: "Workflow with iterative processing loop"

workflow:
  graph:
    nodes:
      - id: "start"
        type: "start"
        data:
          type: "start"
          title: "Start Processing"
      - id: "main_loop"
        type: "loop"
        data:
          type: "loop"
          title: "Main Processing Loop"
          loop_config:
            max_iterations: 5
            break_conditions:
              - condition: "{{Objection}} == 'resolved'"
                description: "Stop when objection is resolved"
            loop_variables:
              - name: "iteration_count"
                initial_value: 0
              - name: "Objection"
                initial_value: "pending"
        children:
          - id: "loop_start"
            type: "loop-start"
            data:
              type: "loop-start"
              title: "Loop Start"
          - id: "process_item"
            type: "llm"
            data:
              type: "llm"
              title: "Process Item"
              model:
                provider: "openai"
                name: "gpt-4"
              prompt_template:
                - role: "system"
                  content: "Process item {{iteration_count}}: {{input_data}}"
          - id: "check_objection"
            type: "llm"
            data:
              type: "llm"
              title: "Check for Objections"
              model:
                provider: "openai"
                name: "gpt-4"
              prompt_template:
                - role: "system"
                  content: "Check if there are objections: {{process_item.output}}"
      - id: "end"
        type: "end"
        data:
          type: "end"
          title: "End"
    edges:
      - id: "e1"
        source: "start"
        target: "main_loop"
        data:
          label: "always"
      - id: "e2"
        source: "main_loop"
        target: "end"
        data:
          label: "loop_complete"
```

### Using Make Commands

The project includes a comprehensive Makefile for development:

```bash
# Development setup
make dev-setup          # Install in development mode
make test               # Run all tests
make demo               # Convert sample workflow
make validate-demo      # Validate sample workflow

# Code quality
make format             # Format code
make lint               # Run linting
make check              # Run all quality checks

# Package management
make build              # Build package
make publish-token TOKEN=your-token  # Publish to PyPI
make pypi-help          # Show PyPI setup instructions

# UV commands
make uv-sync            # Sync dependencies
make uv-add PACKAGE=requests  # Add new package
make uv-update          # Update dependencies
```

## Quick Reference

### Common Commands

| Command | Description |
|---------|-------------|
| `yaml-to-langgraph validate workflow.yml` | Validate YAML workflow |
| `yaml-to-langgraph convert workflow.yml` | Convert to LangGraph |
| `yaml-to-langgraph convert workflow.yml --output my_dir` | Convert to specific directory |
| `yaml-to-langgraph visualize workflow.yml` | Generate workflow diagram |
| `yaml-to-langgraph visualize workflow.yml --theme dark` | Generate dark theme diagram |
| `yaml-to-langgraph list-nodes workflow.yml` | List all nodes |
| `yaml-to-langgraph dry-run workflow.yml` | Preview what would be generated |

### Visualization Options

| Option | Description | Default |
|--------|-------------|---------|
| `--theme` | Theme: default, dark, forest, neutral | default |
| `--layout` | Layout: hierarchical, flowchart, graph | hierarchical |
| `--format` | Output format: png, svg, pdf | png |
| `--size` | Figure size (width height) | 24 16 |
| `--dpi` | Resolution | 300 |
| `--show-edge-labels` | Show edge labels | false |
| `--no-loops` | Disable loop grouping | false |

### Make Commands

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make test` | Run all tests |
| `make demo` | Convert sample workflow |
| `make build` | Build package |
| `make publish-token TOKEN=xxx` | Publish to PyPI |
| `make pypi-help` | Show PyPI setup help |

### YAML Structure

```yaml
app:
  name: "workflow-name"
  description: "Workflow description"

workflow:
  graph:
    nodes:
      - id: "node_id"
        type: "llm|start|end|code|loop|loop-start|assigner"
        data:
          type: "llm|start|end|code|loop|loop-start|assigner"
          title: "Node Title"
          # ... node-specific data
    edges:
      - id: "edge_id"
        source: "source_node"
        target: "target_node"
        data:
          label: "condition"
```

### Generated Files

- `workflow_graph.py` - Main graph implementation
- `loop_aware_graph.py` - Advanced loop handling
- `prompts/` - LLM prompt templates
- `nodes/` - Node implementations
- `edges/` - Routing logic
- `example_usage.py` - Usage example
- `requirements.txt` - Dependencies
- `workflow_graph.png` - Professional workflow visualization

## Advanced Features

### 🔄 Loop Support

The converter provides advanced loop handling:

- **Hierarchical Loop Structure**: Proper handling of `loop` containers with `loop-start` nodes
- **Break Conditions**: Support for conditional loop exit based on state variables
- **Loop Variables**: Automatic tracking of loop-specific state variables
- **LangGraph Integration**: Generates proper `For` constructs for LangGraph execution

### 📊 State Management

Intelligent state management features:

- **Variable References**: Automatic detection of `{{#node_id.field#}}` patterns in prompts
- **State Variable Tracking**: Comprehensive tracking of all state variables across the workflow
- **Dependency Analysis**: Automatic detection of node dependencies based on variable usage
- **Enhanced LLM Nodes**: LLM nodes automatically update state with multiple output keys

### 🎨 Professional Visualization

High-quality workflow visualization using Mermaid + Pyppeteer:

- **Multiple Themes**: Default, dark, forest, and neutral themes
- **Loop Grouping**: Visual grouping of loop nodes with subgraphs
- **Emoji Icons**: Visual node type identification (🚀 Start, 🏁 End, 🤖 LLM, etc.)
- **Compact Output**: Small file sizes (90%+ smaller than previous backends)
- **Scalable Quality**: Vector-based rendering maintains perfect quality at any size

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
│       ├── yaml_parser.py      # YAML parsing with loop/state support
│       ├── code_generator.py   # Code generation with loop awareness
│       └── graph_visualizer.py # Mermaid + Pyppeteer visualization
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

The project includes a comprehensive test suite covering:

- **Schema Validation**: YAML structure validation
- **CLI Functionality**: Command-line interface testing
- **Core Converter**: Conversion logic testing
- **Sample Workflow**: Real-world workflow testing
- **Loop Handling**: Complex loop structure testing
- **State Management**: Variable reference and state tracking testing
- **Visualization**: Mermaid diagram generation testing

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