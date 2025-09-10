"""
Test converter functionality
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from yaml_to_langgraph.converter import YAMLToLangGraphConverter
from yaml_to_langgraph.yaml_parser import YAMLWorkflowParser
from yaml_to_langgraph.code_generator import LangGraphCodeGenerator


class TestConverter:
    """Test converter functionality."""
    
    @pytest.fixture
    def sample_yaml_content(self):
        """Sample YAML workflow content."""
        return {
            'app': {
                'name': 'TestWorkflow',
                'description': 'A test workflow for unit testing'
            },
            'workflow': {
                'graph': {
                    'nodes': [
                        {
                            'id': 'start_node',
                            'data': {
                                'type': 'start',
                                'title': 'Start',
                                'variables': [
                                    {
                                        'label': 'input_text',
                                        'required': True,
                                        'max_length': 1000
                                    }
                                ]
                            }
                        },
                        {
                            'id': 'llm_node_1',
                            'data': {
                                'type': 'llm',
                                'title': 'Process Text',
                                'prompt_template': [
                                    {
                                        'role': 'system',
                                        'content': 'You are a helpful assistant.'
                                    },
                                    {
                                        'role': 'user',
                                        'content': 'Process this text: {input_text}'
                                    }
                                ],
                                'model': 'gpt-4'
                            }
                        },
                        {
                            'id': 'assigner_node',
                            'data': {
                                'type': 'assigner',
                                'title': 'Assign Result',
                                'assignments': [
                                    {
                                        'variable': 'result',
                                        'value': 'processed_text'
                                    }
                                ]
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
                            'target': 'llm_node_1',
                            'type': 'custom'
                        },
                        {
                            'id': 'edge2',
                            'source': 'llm_node_1',
                            'target': 'assigner_node',
                            'type': 'custom'
                        },
                        {
                            'id': 'edge3',
                            'source': 'assigner_node',
                            'target': 'end_node',
                            'type': 'custom'
                        }
                    ]
                }
            },
            'kind': 'app',
            'version': '0.1.0'
        }
    
    def create_temp_yaml_file(self, content):
        """Create a temporary YAML file with given content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(content, f)
            return f.name
    
    def test_yaml_parser(self, sample_yaml_content):
        """Test YAML parser functionality."""
        yaml_file = self.create_temp_yaml_file(sample_yaml_content)
        try:
            parser = YAMLWorkflowParser(yaml_file)
            workflow_info = parser.parse()
            
            assert workflow_info is not None
            assert hasattr(workflow_info, 'name')
            assert hasattr(workflow_info, 'description')
            assert workflow_info.name == 'TestWorkflow'
            assert len(workflow_info.nodes) == 4
            assert len(workflow_info.edges) == 3
        finally:
            Path(yaml_file).unlink()
    
    def test_code_generator(self, sample_yaml_content):
        """Test code generator functionality."""
        yaml_file = self.create_temp_yaml_file(sample_yaml_content)
        try:
            parser = YAMLWorkflowParser(yaml_file)
            workflow_info = parser.parse()
            
            generator = LangGraphCodeGenerator("test_output")
            
            # Test that generator can be created
            assert generator is not None
            assert generator.output_dir == Path("test_output")
            assert generator.workflow_info is None  # Not set until generate() is called
        finally:
            Path(yaml_file).unlink()
    
    def test_converter_integration(self, sample_yaml_content):
        """Test full converter integration."""
        yaml_file = self.create_temp_yaml_file(sample_yaml_content)
        try:
            converter = YAMLToLangGraphConverter(yaml_file, "test_converter_output")
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
            
            # Check that node files were generated
            nodes_dir = output_path / 'nodes'
            node_files = list(nodes_dir.glob('*.py'))
            assert len(node_files) > 0, "No node files were generated"
            
            # Check that prompt files were generated
            prompts_dir = output_path / 'prompts'
            prompt_files = list(prompts_dir.glob('*.py'))
            assert len(prompt_files) > 0, "No prompt files were generated"
            
            # Clean up
            import shutil
            shutil.rmtree(output_path)
        finally:
            Path(yaml_file).unlink()
    
    def test_converter_with_custom_output_dir(self, sample_yaml_content):
        """Test converter with custom output directory."""
        yaml_file = self.create_temp_yaml_file(sample_yaml_content)
        try:
            custom_output = "custom_test_output"
            converter = YAMLToLangGraphConverter(yaml_file, custom_output)
            output_path = converter.convert()
            
            assert output_path.name == custom_output
            assert output_path.exists()
            
            # Clean up
            import shutil
            shutil.rmtree(output_path)
        finally:
            Path(yaml_file).unlink()
    
    def test_converter_with_none_output_dir(self, sample_yaml_content):
        """Test converter with None output directory (should use default)."""
        yaml_file = self.create_temp_yaml_file(sample_yaml_content)
        try:
            converter = YAMLToLangGraphConverter(yaml_file, None)
            output_path = converter.convert()
            
            # Should create a directory based on workflow name
            assert output_path.name.startswith('generated_')
            assert 'testworkflow' in output_path.name.lower()
            assert output_path.exists()
            
            # Clean up
            import shutil
            shutil.rmtree(output_path)
        finally:
            Path(yaml_file).unlink()
    
    def test_converter_error_handling(self):
        """Test converter error handling with invalid file."""
        with pytest.raises(Exception):
            converter = YAMLToLangGraphConverter("nonexistent.yml", "test_output")
            converter.convert()
    
    def test_generated_files_content(self, sample_yaml_content):
        """Test that generated files contain expected content."""
        yaml_file = self.create_temp_yaml_file(sample_yaml_content)
        try:
            converter = YAMLToLangGraphConverter(yaml_file, "content_test_output")
            output_path = converter.convert()
            
            # Test workflow_graph.py content
            workflow_file = output_path / 'workflow_graph.py'
            assert workflow_file.exists()
            
            with open(workflow_file, 'r') as f:
                content = f.read()
                assert 'StateGraph' in content
                assert 'workflow' in content.lower()
                assert 'start_node' in content
                assert 'def create_workflow_graph' in content
            
            # Test requirements.txt content
            requirements_file = output_path / 'requirements.txt'
            assert requirements_file.exists()
            
            with open(requirements_file, 'r') as f:
                content = f.read()
                assert 'langchain' in content
                assert 'langgraph' in content
                assert 'pydantic' in content
            
            # Test README.md content
            readme_file = output_path / 'README.md'
            assert readme_file.exists()
            
            with open(readme_file, 'r') as f:
                content = f.read()
                assert 'LangGraph' in content
                assert 'workflow' in content.lower()
            
            # Clean up
            import shutil
            shutil.rmtree(output_path)
        finally:
            Path(yaml_file).unlink()
    
    def test_prompt_generation(self, sample_yaml_content):
        """Test that prompt files are generated correctly."""
        yaml_file = self.create_temp_yaml_file(sample_yaml_content)
        try:
            converter = YAMLToLangGraphConverter(yaml_file, "prompt_test_output")
            output_path = converter.convert()
            
            prompts_dir = output_path / 'prompts'
            prompt_files = list(prompts_dir.glob('*.py'))
            
            # Should have at least one prompt file for the LLM node
            assert len(prompt_files) > 0
            
            # Check that prompt files contain expected content
            for prompt_file in prompt_files:
                with open(prompt_file, 'r') as f:
                    content = f.read()
                    assert 'PROMPT' in content
                    assert len(content) > 50  # Should have some content
            
            # Clean up
            import shutil
            shutil.rmtree(output_path)
        finally:
            Path(yaml_file).unlink()
    
    def test_node_generation(self, sample_yaml_content):
        """Test that node files are generated correctly."""
        yaml_file = self.create_temp_yaml_file(sample_yaml_content)
        try:
            converter = YAMLToLangGraphConverter(yaml_file, "node_test_output")
            output_path = converter.convert()
            
            nodes_dir = output_path / 'nodes'
            node_files = list(nodes_dir.glob('*.py'))
            
            # Should have multiple node files
            assert len(node_files) >= 3  # start, llm, assigner, end nodes
            
            # Check that specific node files exist
            node_file_names = [f.name for f in node_files]
            assert any('start' in name for name in node_file_names)
            assert any('llm' in name for name in node_file_names)
            assert any('workflow' in name for name in node_file_names)
            
            # Clean up
            import shutil
            shutil.rmtree(output_path)
        finally:
            Path(yaml_file).unlink()
