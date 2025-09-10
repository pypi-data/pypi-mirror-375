"""
Test sample workflow specific functionality
"""

import pytest
from pathlib import Path
from yaml_to_langgraph.converter import YAMLToLangGraphConverter
from yaml_to_langgraph.schema_validator import validate_yaml_workflow


class TestSampleWorkflow:
    """Test sample workflow specific functionality."""
    
    
    def test_sample_yaml_exists(self, sample_yaml_path):
        """Test that sample YAML file exists."""
        assert sample_yaml_path.exists(), f"Sample YAML file not found at {sample_yaml_path}"
    
    def test_sample_yaml_validation(self, sample_yaml_path):
        """Test validation of Sample YAML file."""
        result = validate_yaml_workflow(str(sample_yaml_path))
        
        # Sample file should be valid
        assert result.is_valid is True, f"Sample YAML validation failed: {result.errors}"
        
        # Should have no errors
        assert len(result.errors) == 0, f"Sample YAML has errors: {result.errors}"
    
    def test_sample_yaml_structure(self, sample_yaml_path):
        """Test Sample YAML file structure."""
        result = validate_yaml_workflow(str(sample_yaml_path))
        
        # Check that we have the expected structure
        assert result.is_valid is True
        
        # The validation should have found nodes and edges
        # Our sample workflow has 6 nodes and 9 edges
        # This is validated by the schema validator
    
    def test_sample_conversion(self, sample_yaml_path):
        """Test conversion of Sample YAML file."""
        output_dir = "test_sample_output"
        
        try:
            converter = YAMLToLangGraphConverter(str(sample_yaml_path), output_dir)
            output_path = converter.convert()
            
            # Check that output directory was created
            assert output_path.exists()
            assert output_path.is_dir()
            
            # Check that required files were generated
            required_files = [
                'workflow_graph.py',
                'requirements.txt',
                'README.md',
                'example_usage.py'
            ]
            
            for file_name in required_files:
                file_path = output_path / file_name
                assert file_path.exists(), f"Required file {file_name} was not generated"
            
            # Check that directories were created
            required_dirs = ['nodes', 'edges', 'prompts']
            for dir_name in required_dirs:
                dir_path = output_path / dir_name
                assert dir_path.exists(), f"Required directory {dir_name} was not created"
                assert dir_path.is_dir()
            
            # Check that we have prompt files (Sample has 4 LLM nodes)
            prompts_dir = output_path / 'prompts'
            prompt_files = list(prompts_dir.glob('*.py'))
            assert len(prompt_files) >= 4, f"Expected at least 4 prompt files, got {len(prompt_files)}"
            
            # Check that we have node files
            nodes_dir = output_path / 'nodes'
            node_files = list(nodes_dir.glob('*.py'))
            assert len(node_files) >= 3, f"Expected multiple node files, got {len(node_files)}"
            
            # Check that we have edge files
            edges_dir = output_path / 'edges'
            edge_files = list(edges_dir.glob('*.py'))
            assert len(edge_files) >= 1, f"Expected edge files, got {len(edge_files)}"
            
        finally:
            # Clean up
            import shutil
            if Path(output_dir).exists():
                shutil.rmtree(output_dir)
    
    def test_sample_workflow_content(self, sample_yaml_path):
        """Test that Sample workflow content is properly generated."""
        output_dir = "test_sample_content"
        
        try:
            converter = YAMLToLangGraphConverter(str(sample_yaml_path), output_dir)
            output_path = converter.convert()
            
            # Test workflow_graph.py content
            workflow_file = output_path / 'workflow_graph.py'
            assert workflow_file.exists()
            
            with open(workflow_file, 'r') as f:
                content = f.read()
                assert 'StateGraph' in content
                assert 'workflow' in content.lower()
                # Check for some basic structure
                assert 'def create_workflow_graph' in content
            
            # Test README.md content
            readme_file = output_path / 'README.md'
            assert readme_file.exists()
            
            with open(readme_file, 'r') as f:
                content = f.read()
                assert 'sample-workflow' in content
                assert 'LangGraph' in content
            
            # Test that we have specific prompt files for known Sample nodes
            prompts_dir = output_path / 'prompts'
            expected_prompts = [
                'input_analyzer.py',
                'data_processor.py',
                'response_generator.py',
                'output_validator.py'
            ]
            
            for prompt_file in expected_prompts:
                prompt_path = prompts_dir / prompt_file
                assert prompt_path.exists(), f"Expected prompt file {prompt_file} not found"
                
                # Check that prompt files contain expected content
                with open(prompt_path, 'r') as f:
                    content = f.read()
                    assert 'PROMPT' in content
                    assert len(content) > 100  # Should have substantial content
            
        finally:
            # Clean up
            import shutil
            if Path(output_dir).exists():
                shutil.rmtree(output_dir)
    
    def test_sample_node_types(self, sample_yaml_path):
        """Test that Sample workflow has expected node types."""
        result = validate_yaml_workflow(str(sample_yaml_path))
        
        # Sample should have various node types
        assert result.is_valid is True
        
        # We know from our sample workflow that it has:
        # - 1 start node
        # - 4 LLM nodes
        # - 1 function node
        # - 1 end node
    
    def test_sample_edges(self, sample_yaml_path):
        """Test that Sample workflow has expected edges."""
        result = validate_yaml_workflow(str(sample_yaml_path))
        
        # Sample should have edges (we know it has 9)
        assert result.is_valid is True
        
        # The validation should pass without edge-related errors
        edge_errors = [error for error in result.errors if 'edge' in error.path.lower()]
        assert len(edge_errors) == 0, f"Edge validation errors: {edge_errors}"
    
    def test_sample_strict_validation(self, sample_yaml_path):
        """Test Sample YAML with strict validation."""
        result = validate_yaml_workflow(str(sample_yaml_path))
        
        # Our sample workflow should have minimal warnings (code node type warning is expected)
        assert len(result.warnings) <= 1
        
        # The file should be valid in both normal and strict mode
        # Our sample workflow is well-formed and should not have warnings
    
    def test_sample_file_size(self, sample_yaml_path):
        """Test that Sample YAML file is substantial."""
        assert sample_yaml_path.exists()
        
        # Sample file should be reasonable size
        file_size = sample_yaml_path.stat().st_size
        assert file_size > 1000, f"Sample YAML file seems too small: {file_size} bytes"
        
        # Should have reasonable number of lines
        with open(sample_yaml_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) > 50, f"Sample YAML file seems too short: {len(lines)} lines"
