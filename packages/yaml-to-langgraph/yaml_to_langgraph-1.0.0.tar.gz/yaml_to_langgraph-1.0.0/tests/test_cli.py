"""
Test CLI functionality
"""

import pytest
import subprocess
import tempfile
import yaml
import os
from pathlib import Path
import sys


class TestCLI:
    """Test CLI functionality."""
    
    @pytest.fixture
    def valid_yaml_content(self):
        """Valid YAML workflow content."""
        return {
            'app': {
                'name': 'TestWorkflow',
                'description': 'A test workflow'
            },
            'workflow': {
                'graph': {
                    'nodes': [
                        {
                            'id': 'start_node',
                            'data': {
                                'type': 'start',
                                'title': 'Start'
                            }
                        },
                        {
                            'id': 'llm_node',
                            'data': {
                                'type': 'llm',
                                'title': 'LLM Node',
                                'prompt_template': [
                                    {
                                        'role': 'system',
                                        'content': 'You are a helpful assistant.'
                                    },
                                    {
                                        'role': 'user',
                                        'content': 'Test prompt'
                                    }
                                ],
                                'model': 'gpt-4'
                            }
                        },
                        {
                            'id': 'end_node',
                            'data': {
                                'type': 'end',
                                'title': 'End'
                            }
                        }
                    ],
                    'edges': [
                        {
                            'id': 'edge1',
                            'source': 'start_node',
                            'target': 'llm_node'
                        },
                        {
                            'id': 'edge2',
                            'source': 'llm_node',
                            'target': 'end_node'
                        }
                    ]
                }
            },
            'kind': 'app',
            'version': '0.1.0'
        }
    
    @pytest.fixture
    def invalid_yaml_content(self):
        """Invalid YAML workflow content."""
        return {
            'app': {
                'name': 'Test Workflow',  # Invalid name with space
                # Missing description
            },
            # Missing workflow section
            'kind': 'app',
            'version': '0.1.0'
        }
    
    def create_temp_yaml_file(self, content):
        """Create a temporary YAML file with given content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(content, f)
            return f.name
    
    def run_cli_command(self, args, timeout=30):
        """Run a CLI command and return the result."""
        # Use the src path for the module
        src_path = Path(__file__).parent.parent / "src"
        cmd = [sys.executable, "-m", "yaml_to_langgraph"] + args
        env = os.environ.copy()
        env["PYTHONPATH"] = str(src_path)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
        )
        return result
    
    def test_cli_help(self):
        """Test CLI help command."""
        result = self.run_cli_command(["--help"])
        
        assert result.returncode == 0
        assert "YAML to LangGraph Converter" in result.stdout
        assert "convert" in result.stdout
        assert "validate" in result.stdout
        assert "list-nodes" in result.stdout
        assert "dry-run" in result.stdout
    
    def test_cli_version(self):
        """Test CLI version command."""
        result = self.run_cli_command(["--version"])
        
        assert result.returncode == 0
        assert "yaml-to-langgraph, version 1.0.0" in result.stdout
    
    def test_validate_command_help(self):
        """Test validate command help."""
        result = self.run_cli_command(["validate", "--help"])
        
        assert result.returncode == 0
        assert "Validate YAML workflow file schema" in result.stdout
        assert "--strict" in result.stdout
    
    def test_convert_command_help(self):
        """Test convert command help."""
        result = self.run_cli_command(["convert", "--help"])
        
        assert result.returncode == 0
        assert "Convert YAML workflow to LangGraph" in result.stdout
        assert "--output" in result.stdout
        assert "--verbose" in result.stdout
        assert "--skip-validation" in result.stdout
    
    def test_validate_valid_yaml(self, valid_yaml_content):
        """Test validation of valid YAML file."""
        yaml_file = self.create_temp_yaml_file(valid_yaml_content)
        try:
            result = self.run_cli_command(["validate", yaml_file])
            
            assert result.returncode == 0
            assert "YAML file is valid" in result.stdout
        finally:
            Path(yaml_file).unlink()
    
    def test_validate_invalid_yaml(self, invalid_yaml_content):
        """Test validation of invalid YAML file."""
        yaml_file = self.create_temp_yaml_file(invalid_yaml_content)
        try:
            result = self.run_cli_command(["validate", yaml_file])
            
            assert result.returncode == 1
            assert "validation issues" in result.stdout
            assert "Missing required" in result.stdout
        finally:
            Path(yaml_file).unlink()
    
    def test_validate_strict_mode(self, valid_yaml_content):
        """Test validation with strict mode."""
        # Create YAML with warnings
        content_with_warnings = valid_yaml_content.copy()
        content_with_warnings['app'].pop('description')  # Remove description (warning)
        
        yaml_file = self.create_temp_yaml_file(content_with_warnings)
        try:
            # Test without strict mode
            result_normal = self.run_cli_command(["validate", yaml_file])
            assert result_normal.returncode == 0
            
            # Test with strict mode
            result_strict = self.run_cli_command(["validate", yaml_file, "--strict"])
            assert result_strict.returncode == 1
            assert "validation issues" in result_strict.stdout
        finally:
            Path(yaml_file).unlink()
    
    def test_convert_valid_yaml(self, valid_yaml_content):
        """Test conversion of valid YAML file."""
        yaml_file = self.create_temp_yaml_file(valid_yaml_content)
        try:
            result = self.run_cli_command(["convert", yaml_file, "-o", "test_output"])
            
            assert result.returncode == 0
            assert "Conversion complete" in result.stdout
            assert "Next Steps" in result.stdout
            
            # Check if output directory was created
            output_dir = Path("test_output")
            assert output_dir.exists()
            assert (output_dir / "workflow_graph.py").exists()
            assert (output_dir / "requirements.txt").exists()
            
            # Clean up
            import shutil
            shutil.rmtree(output_dir)
        finally:
            Path(yaml_file).unlink()
    
    def test_convert_invalid_yaml(self, invalid_yaml_content):
        """Test conversion of invalid YAML file."""
        yaml_file = self.create_temp_yaml_file(invalid_yaml_content)
        try:
            result = self.run_cli_command(["convert", yaml_file])
            
            assert result.returncode == 1
            assert "validation failed" in result.stdout
            assert "fix the following errors" in result.stdout
        finally:
            Path(yaml_file).unlink()
    
    def test_convert_skip_validation(self, invalid_yaml_content):
        """Test conversion with skip validation."""
        yaml_file = self.create_temp_yaml_file(invalid_yaml_content)
        try:
            result = self.run_cli_command(["convert", yaml_file, "--skip-validation"])
            
            assert result.returncode == 0
            assert "Conversion complete" in result.stdout
            
            # Clean up
            output_dir = Path("generated_test_workflow")
            if output_dir.exists():
                import shutil
                shutil.rmtree(output_dir)
        finally:
            Path(yaml_file).unlink()
    
    def test_list_nodes_command(self, valid_yaml_content):
        """Test list-nodes command."""
        yaml_file = self.create_temp_yaml_file(valid_yaml_content)
        try:
            result = self.run_cli_command(["list-nodes", yaml_file])
            
            assert result.returncode == 0
            assert "Workflow Information" in result.stdout
            assert "Nodes by Type" in result.stdout
            assert "start" in result.stdout
            assert "llm" in result.stdout
            assert "end" in result.stdout
        finally:
            Path(yaml_file).unlink()
    
    def test_dry_run_command(self, valid_yaml_content):
        """Test dry-run command."""
        yaml_file = self.create_temp_yaml_file(valid_yaml_content)
        try:
            result = self.run_cli_command(["dry-run", yaml_file])
            
            assert result.returncode == 0
            assert "Dry Run Summary" in result.stdout
            assert "would be generated" in result.stdout
            assert "workflow_graph.py" in result.stdout
        finally:
            Path(yaml_file).unlink()
    
    def test_nonexistent_file(self):
        """Test commands with nonexistent file."""
        # Test validate with nonexistent file
        result = self.run_cli_command(["validate", "nonexistent.yml"])
        assert result.returncode == 2  # Click returns 2 for invalid arguments
        
        # Test convert with nonexistent file
        result = self.run_cli_command(["convert", "nonexistent.yml"])
        assert result.returncode == 2  # Click returns 2 for invalid arguments
    
    def test_convert_verbose_output(self, valid_yaml_content):
        """Test convert command with verbose output."""
        yaml_file = self.create_temp_yaml_file(valid_yaml_content)
        try:
            result = self.run_cli_command(["convert", yaml_file, "-o", "verbose_test", "-v"])
            
            assert result.returncode == 0
            assert "Generated files:" in result.stdout
            assert "workflow_graph.py" in result.stdout
            assert "requirements.txt" in result.stdout
            
            # Clean up
            output_dir = Path("verbose_test")
            if output_dir.exists():
                import shutil
                shutil.rmtree(output_dir)
        finally:
            Path(yaml_file).unlink()
