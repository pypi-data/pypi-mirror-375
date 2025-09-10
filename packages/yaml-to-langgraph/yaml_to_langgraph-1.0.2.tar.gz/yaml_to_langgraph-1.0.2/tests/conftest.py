"""
Shared pytest fixtures and configuration
"""

import pytest
import tempfile
import yaml
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_workflow_data():
    """Sample workflow data for testing."""
    return {
        'app': {
            'name': 'SampleWorkflow',
            'description': 'A sample workflow for testing'
        },
        'workflow': {
            'graph': {
                'nodes': [
                    {
                        'id': 'start',
                        'data': {
                            'type': 'start',
                            'title': 'Start Node'
                        }
                    },
                    {
                        'id': 'llm',
                        'data': {
                            'type': 'llm',
                            'title': 'LLM Node',
                            'prompt_template': {
                                'system': 'You are a helpful assistant.',
                                'user': 'Process: {input}'
                            }
                        }
                    },
                    {
                        'id': 'end',
                        'data': {
                            'type': 'end',
                            'title': 'End Node'
                        }
                    }
                ],
                'edges': [
                    {
                        'id': 'edge1',
                        'source': 'start',
                        'target': 'llm'
                    },
                    {
                        'id': 'edge2',
                        'source': 'llm',
                        'target': 'end'
                    }
                ]
            }
        },
        'kind': 'app',
        'version': '0.1.0'
    }


@pytest.fixture
def create_temp_yaml_file():
    """Factory for creating temporary YAML files."""
    def _create_file(content, suffix='.yml'):
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
            yaml.dump(content, f)
            return f.name
    return _create_file


@pytest.fixture
def sample_yaml_path():
    """Path to the sample YAML file."""
    # Look for the sample YAML file in the test exports directory
    path = Path(__file__).parent / "exports" / "sample_workflow.yml"
    if not path.exists():
        pytest.skip("Sample YAML file not found")
    return path


@pytest.fixture(scope="session")
def sample_workflow_data():
    """Load sample workflow data once per session."""
    path = Path(__file__).parent / "exports" / "sample_workflow.yml"
    if not path.exists():
        pytest.skip("Sample YAML file not found")
    
    with open(path, 'r') as f:
        return yaml.safe_load(f)
