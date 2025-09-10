"""
YAML Schema Validator

Validates YAML workflow files to ensure they have the required structure and attributes.
"""

import yaml
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ValidationError:
    """Represents a validation error."""
    path: str
    message: str
    severity: str = "error"  # error, warning, info


@dataclass
class ValidationResult:
    """Result of YAML schema validation."""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    info: List[ValidationError]
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0


class YAMLWorkflowSchemaValidator:
    """Validator for YAML workflow files."""
    
    def __init__(self):
        """Initialize the validator."""
        self.required_top_level_keys = {
            'app', 'workflow', 'kind', 'version'
        }
        
        self.required_app_keys = {
            'name', 'description'
        }
        
        self.required_workflow_keys = {
            'graph'
        }
        
        self.required_graph_keys = {
            'nodes', 'edges'
        }
        
        self.required_node_keys = {
            'id', 'data'
        }
        
        self.required_node_data_keys = {
            'type'
        }
        
        self.required_edge_keys = {
            'id', 'source', 'target'
        }
        
        self.valid_node_types = {
            'start', 'end', 'llm', 'assigner', 'loop', 'loop-start'
        }
        
        self.valid_edge_types = {
            'custom', 'default'
        }
    
    def validate(self, yaml_file_path: str) -> ValidationResult:
        """
        Validate a YAML workflow file.
        
        Args:
            yaml_file_path: Path to the YAML file to validate
            
        Returns:
            ValidationResult with validation status and messages
        """
        errors = []
        warnings = []
        info = []
        
        try:
            # Load YAML file
            with open(yaml_file_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
            
            if not isinstance(data, dict):
                errors.append(ValidationError(
                    path="root",
                    message="YAML file must contain a dictionary at the root level"
                ))
                return ValidationResult(False, errors, warnings, info)
            
            # Validate top-level structure
            self._validate_top_level(data, errors, warnings, info)
            
            # Validate app section
            if 'app' in data:
                self._validate_app_section(data['app'], errors, warnings, info)
            
            # Validate workflow section
            if 'workflow' in data:
                self._validate_workflow_section(data['workflow'], errors, warnings, info)
            
            # Validate graph section
            if 'workflow' in data and 'graph' in data['workflow']:
                self._validate_graph_section(data['workflow']['graph'], errors, warnings, info)
            
            # Additional validations
            self._validate_workflow_integrity(data, errors, warnings, info)
            
        except yaml.YAMLError as e:
            errors.append(ValidationError(
                path="yaml_parsing",
                message=f"YAML parsing error: {str(e)}"
            ))
        except FileNotFoundError:
            errors.append(ValidationError(
                path="file",
                message=f"File not found: {yaml_file_path}"
            ))
        except Exception as e:
            errors.append(ValidationError(
                path="validation",
                message=f"Validation error: {str(e)}"
            ))
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings, info)
    
    def _validate_top_level(self, data: Dict[str, Any], errors: List[ValidationError], 
                           warnings: List[ValidationError], info: List[ValidationError]):
        """Validate top-level structure."""
        missing_keys = self.required_top_level_keys - set(data.keys())
        
        for key in missing_keys:
            if key == 'app':
                errors.append(ValidationError(
                    path="root",
                    message=f"Missing required top-level key: '{key}' - contains workflow metadata"
                ))
            elif key == 'workflow':
                errors.append(ValidationError(
                    path="root",
                    message=f"Missing required top-level key: '{key}' - contains workflow definition"
                ))
            elif key == 'kind':
                warnings.append(ValidationError(
                    path="root",
                    message=f"Missing optional top-level key: '{key}' - should be 'app'"
                ))
            elif key == 'version':
                warnings.append(ValidationError(
                    path="root",
                    message=f"Missing optional top-level key: '{key}' - workflow version"
                ))
    
    def _validate_app_section(self, app_data: Dict[str, Any], errors: List[ValidationError],
                             warnings: List[ValidationError], info: List[ValidationError]):
        """Validate app section."""
        if not isinstance(app_data, dict):
            errors.append(ValidationError(
                path="app",
                message="App section must be a dictionary"
            ))
            return
        
        missing_keys = self.required_app_keys - set(app_data.keys())
        
        for key in missing_keys:
            if key == 'name':
                errors.append(ValidationError(
                    path="app",
                    message=f"Missing required app key: '{key}' - workflow name"
                ))
            elif key == 'description':
                warnings.append(ValidationError(
                    path="app",
                    message=f"Missing optional app key: '{key}' - workflow description"
                ))
        
        # Validate name format
        if 'name' in app_data:
            name = app_data['name']
            if not isinstance(name, str) or not name.strip():
                errors.append(ValidationError(
                    path="app.name",
                    message="App name must be a non-empty string"
                ))
            elif not name.replace('_', '').replace('-', '').isalnum():
                warnings.append(ValidationError(
                    path="app.name",
                    message="App name should contain only alphanumeric characters, underscores, and hyphens"
                ))
    
    def _validate_workflow_section(self, workflow_data: Dict[str, Any], errors: List[ValidationError],
                                  warnings: List[ValidationError], info: List[ValidationError]):
        """Validate workflow section."""
        if not isinstance(workflow_data, dict):
            errors.append(ValidationError(
                path="workflow",
                message="Workflow section must be a dictionary"
            ))
            return
        
        missing_keys = self.required_workflow_keys - set(workflow_data.keys())
        
        for key in missing_keys:
            if key == 'graph':
                errors.append(ValidationError(
                    path="workflow",
                    message=f"Missing required workflow key: '{key}' - contains nodes and edges"
                ))
    
    def _validate_graph_section(self, graph_data: Dict[str, Any], errors: List[ValidationError],
                               warnings: List[ValidationError], info: List[ValidationError]):
        """Validate graph section."""
        if not isinstance(graph_data, dict):
            errors.append(ValidationError(
                path="workflow.graph",
                message="Graph section must be a dictionary"
            ))
            return
        
        missing_keys = self.required_graph_keys - set(graph_data.keys())
        
        for key in missing_keys:
            if key == 'nodes':
                errors.append(ValidationError(
                    path="workflow.graph",
                    message=f"Missing required graph key: '{key}' - workflow nodes"
                ))
            elif key == 'edges':
                errors.append(ValidationError(
                    path="workflow.graph",
                    message=f"Missing required graph key: '{key}' - workflow edges"
                ))
        
        # Validate nodes
        if 'nodes' in graph_data:
            self._validate_nodes(graph_data['nodes'], errors, warnings, info)
        
        # Validate edges
        if 'edges' in graph_data:
            self._validate_edges(graph_data['edges'], errors, warnings, info)
    
    def _validate_nodes(self, nodes_data: List[Dict[str, Any]], errors: List[ValidationError],
                       warnings: List[ValidationError], info: List[ValidationError]):
        """Validate nodes array."""
        if not isinstance(nodes_data, list):
            errors.append(ValidationError(
                path="workflow.graph.nodes",
                message="Nodes must be a list"
            ))
            return
        
        if len(nodes_data) == 0:
            warnings.append(ValidationError(
                path="workflow.graph.nodes",
                message="No nodes found in workflow"
            ))
            return
        
        node_ids = set()
        node_types = {}
        
        for i, node in enumerate(nodes_data):
            node_path = f"workflow.graph.nodes[{i}]"
            
            if not isinstance(node, dict):
                errors.append(ValidationError(
                    path=node_path,
                    message="Node must be a dictionary"
                ))
                continue
            
            # Validate required node keys
            missing_keys = self.required_node_keys - set(node.keys())
            for key in missing_keys:
                errors.append(ValidationError(
                    path=node_path,
                    message=f"Missing required node key: '{key}'"
                ))
            
            # Validate node ID
            if 'id' in node:
                node_id = node['id']
                if not isinstance(node_id, str) or not node_id.strip():
                    errors.append(ValidationError(
                        path=f"{node_path}.id",
                        message="Node ID must be a non-empty string"
                    ))
                elif node_id in node_ids:
                    errors.append(ValidationError(
                        path=f"{node_path}.id",
                        message=f"Duplicate node ID: '{node_id}'"
                    ))
                else:
                    node_ids.add(node_id)
            
            # Validate node data
            if 'data' in node:
                self._validate_node_data(node['data'], f"{node_path}.data", errors, warnings, info)
                
                # Track node types
                if isinstance(node['data'], dict) and 'type' in node['data']:
                    node_type = node['data']['type']
                    if node_type not in node_types:
                        node_types[node_type] = 0
                    node_types[node_type] += 1
        
        # Validate node type distribution
        if 'start' not in node_types:
            errors.append(ValidationError(
                path="workflow.graph.nodes",
                message="No start node found - workflow must have at least one start node"
            ))
        
        if 'end' not in node_types:
            warnings.append(ValidationError(
                path="workflow.graph.nodes",
                message="No end node found - workflow should have at least one end node"
            ))
        
        if node_types.get('llm', 0) == 0:
            warnings.append(ValidationError(
                path="workflow.graph.nodes",
                message="No LLM nodes found - workflow may not have any language model processing"
            ))
    
    def _validate_node_data(self, data: Dict[str, Any], path: str, errors: List[ValidationError],
                           warnings: List[ValidationError], info: List[ValidationError]):
        """Validate node data."""
        if not isinstance(data, dict):
            errors.append(ValidationError(
                path=path,
                message="Node data must be a dictionary"
            ))
            return
        
        missing_keys = self.required_node_data_keys - set(data.keys())
        
        for key in missing_keys:
            if key == 'type':
                errors.append(ValidationError(
                    path=path,
                    message=f"Missing required node data key: '{key}'"
                ))
        
        # Validate node type
        if 'type' in data:
            node_type = data['type']
            if not isinstance(node_type, str):
                errors.append(ValidationError(
                    path=f"{path}.type",
                    message="Node type must be a string"
                ))
            elif node_type not in self.valid_node_types:
                warnings.append(ValidationError(
                    path=f"{path}.type",
                    message=f"Unknown node type: '{node_type}'. Valid types: {', '.join(self.valid_node_types)}"
                ))
        
        # Validate LLM node specific requirements
        if data.get('type') == 'llm':
            if 'prompt_template' not in data:
                warnings.append(ValidationError(
                    path=path,
                    message="LLM node should have 'prompt_template' for proper functionality"
                ))
            
            if 'model' not in data:
                warnings.append(ValidationError(
                    path=path,
                    message="LLM node should have 'model' configuration"
                ))
    
    def _validate_edges(self, edges_data: List[Dict[str, Any]], errors: List[ValidationError],
                       warnings: List[ValidationError], info: List[ValidationError]):
        """Validate edges array."""
        if not isinstance(edges_data, list):
            errors.append(ValidationError(
                path="workflow.graph.edges",
                message="Edges must be a list"
            ))
            return
        
        edge_ids = set()
        
        for i, edge in enumerate(edges_data):
            edge_path = f"workflow.graph.edges[{i}]"
            
            if not isinstance(edge, dict):
                errors.append(ValidationError(
                    path=edge_path,
                    message="Edge must be a dictionary"
                ))
                continue
            
            # Validate required edge keys
            missing_keys = self.required_edge_keys - set(edge.keys())
            for key in missing_keys:
                errors.append(ValidationError(
                    path=edge_path,
                    message=f"Missing required edge key: '{key}'"
                ))
            
            # Validate edge ID
            if 'id' in edge:
                edge_id = edge['id']
                if not isinstance(edge_id, str) or not edge_id.strip():
                    errors.append(ValidationError(
                        path=f"{edge_path}.id",
                        message="Edge ID must be a non-empty string"
                    ))
                elif edge_id in edge_ids:
                    errors.append(ValidationError(
                        path=f"{edge_path}.id",
                        message=f"Duplicate edge ID: '{edge_id}'"
                    ))
                else:
                    edge_ids.add(edge_id)
            
            # Validate source and target
            for key in ['source', 'target']:
                if key in edge:
                    value = edge[key]
                    if not isinstance(value, str) or not value.strip():
                        errors.append(ValidationError(
                            path=f"{edge_path}.{key}",
                            message=f"Edge {key} must be a non-empty string"
                        ))
    
    def _validate_workflow_integrity(self, data: Dict[str, Any], errors: List[ValidationError],
                                    warnings: List[ValidationError], info: List[ValidationError]):
        """Validate workflow integrity and consistency."""
        # Check if we have both nodes and edges
        if 'workflow' in data and 'graph' in data['workflow']:
            graph = data['workflow']['graph']
            
            if 'nodes' in graph and 'edges' in graph:
                nodes = graph['nodes']
                edges = graph['edges']
                
                if isinstance(nodes, list) and isinstance(edges, list):
                    # Extract node IDs
                    node_ids = set()
                    for node in nodes:
                        if isinstance(node, dict) and 'id' in node:
                            node_ids.add(node['id'])
                    
                    # Check edge references
                    for i, edge in enumerate(edges):
                        if isinstance(edge, dict):
                            edge_path = f"workflow.graph.edges[{i}]"
                            
                            for key in ['source', 'target']:
                                if key in edge:
                                    ref_id = edge[key]
                                    if ref_id not in node_ids:
                                        errors.append(ValidationError(
                                            path=f"{edge_path}.{key}",
                                            message=f"Edge {key} references non-existent node: '{ref_id}'"
                                        ))
                    
                    # Check for orphaned nodes
                    referenced_nodes = set()
                    for edge in edges:
                        if isinstance(edge, dict):
                            for key in ['source', 'target']:
                                if key in edge:
                                    referenced_nodes.add(edge[key])
                    
                    orphaned_nodes = node_ids - referenced_nodes
                    if len(orphaned_nodes) > 1:  # Allow one orphaned node (start or end)
                        for node_id in orphaned_nodes:
                            warnings.append(ValidationError(
                                path="workflow.graph.nodes",
                                message=f"Node '{node_id}' is not connected to any edges"
                            ))


def validate_yaml_workflow(yaml_file_path: str) -> ValidationResult:
    """
    Validate a YAML workflow file.
    
    Args:
        yaml_file_path: Path to the YAML file to validate
        
    Returns:
        ValidationResult with validation status and messages
    """
    validator = YAMLWorkflowSchemaValidator()
    return validator.validate(yaml_file_path)
