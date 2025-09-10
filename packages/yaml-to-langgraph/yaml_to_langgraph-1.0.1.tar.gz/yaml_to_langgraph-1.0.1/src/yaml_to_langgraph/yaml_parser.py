"""
YAML Workflow Parser

Parses YAML workflow files and extracts structured information for LangGraph generation.
"""

import yaml
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class NodeInfo:
    """Information about a workflow node."""
    id: str
    title: str
    node_type: str
    prompt_template: Optional[List[Dict[str, str]]] = None
    variables: Optional[List[Dict[str, Any]]] = None
    model_config: Optional[Dict[str, Any]] = None
    position: Optional[Dict[str, float]] = None
    loop_config: Optional[Dict[str, Any]] = None


@dataclass
class EdgeInfo:
    """Information about a workflow edge."""
    id: str
    source: str
    target: str
    source_handle: Optional[str] = None
    target_handle: Optional[str] = None
    edge_type: str = "custom"
    loop_config: Optional[Dict[str, Any]] = None


@dataclass
class WorkflowInfo:
    """Complete workflow information."""
    name: str
    description: str
    nodes: List[NodeInfo]
    edges: List[EdgeInfo]
    variables: List[Dict[str, Any]]
    features: Dict[str, Any]


class YAMLWorkflowParser:
    """Parser for YAML workflow files."""
    
    def __init__(self, yaml_file_path: str):
        """
        Initialize the parser with a YAML file path.
        
        Args:
            yaml_file_path: Path to the YAML workflow file
        """
        self.yaml_file_path = Path(yaml_file_path)
        self.workflow_data: Dict[str, Any] = {}
        
    def parse(self) -> WorkflowInfo:
        """
        Parse the YAML file and extract workflow information.
        
        Returns:
            WorkflowInfo object containing all parsed data
        """
        with open(self.yaml_file_path, 'r', encoding='utf-8') as file:
            self.workflow_data = yaml.safe_load(file)
        
        # Extract basic workflow info
        app_info = self.workflow_data.get('app', {})
        workflow_section = self.workflow_data.get('workflow', {})
        graph_section = workflow_section.get('graph', {})
        
        # Parse nodes
        nodes = self._parse_nodes(graph_section.get('nodes', []))
        
        # Parse edges
        edges = self._parse_edges(graph_section.get('edges', []))
        
        # Parse variables
        variables = self._parse_variables(workflow_section.get('conversation_variables', []))
        
        return WorkflowInfo(
            name=app_info.get('name', 'unnamed_workflow'),
            description=app_info.get('description', ''),
            nodes=nodes,
            edges=edges,
            variables=variables,
            features=workflow_section.get('features', {})
        )
    
    def _parse_nodes(self, nodes_data: List[Dict[str, Any]]) -> List[NodeInfo]:
        """Parse node information from YAML data."""
        nodes = []
        
        for node_data in nodes_data:
            data = node_data.get('data', {})
            
            # Extract prompt template if it's an LLM node
            prompt_template = None
            if data.get('type') == 'llm' and 'prompt_template' in data:
                prompt_template = data['prompt_template']
            
            # Extract model configuration
            model_config = None
            if 'model' in data:
                model_config = data['model']
            
            # Extract variables
            variables = data.get('variables', [])
            
            # Extract loop configuration
            loop_config = None
            if data.get('type') in ['loop', 'loop-start']:
                loop_config = {
                    'loop_id': data.get('loop_id'),
                    'break_conditions': data.get('break_conditions', []),
                    'loop_count': data.get('loop_count', 0),
                    'loop_variables': data.get('loop_variables', [])
                }
            
            # Extract position information
            position = None
            if 'position' in node_data:
                position = node_data['position']
            
            node_info = NodeInfo(
                id=node_data.get('id', ''),
                title=data.get('title', ''),
                node_type=data.get('type', ''),
                prompt_template=prompt_template,
                variables=variables,
                model_config=model_config,
                position=position,
                loop_config=loop_config
            )
            
            nodes.append(node_info)
        
        return nodes
    
    def _parse_edges(self, edges_data: List[Dict[str, Any]]) -> List[EdgeInfo]:
        """Parse edge information from YAML data."""
        edges = []
        
        for edge_data in edges_data:
            data = edge_data.get('data', {})
            
            # Extract loop configuration
            loop_config = None
            if data.get('isInLoop') or data.get('loop_id'):
                loop_config = {
                    'is_in_loop': data.get('isInLoop', False),
                    'is_in_iteration': data.get('isInIteration', False),
                    'loop_id': data.get('loop_id'),
                    'source_type': data.get('sourceType'),
                    'target_type': data.get('targetType')
                }
            
            edge_info = EdgeInfo(
                id=edge_data.get('id', ''),
                source=edge_data.get('source', ''),
                target=edge_data.get('target', ''),
                source_handle=edge_data.get('sourceHandle'),
                target_handle=edge_data.get('targetHandle'),
                edge_type=edge_data.get('type', 'custom'),
                loop_config=loop_config
            )
            
            edges.append(edge_info)
        
        return edges
    
    def _parse_variables(self, variables_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse variable information from YAML data."""
        return variables_data
    
    def get_node_by_id(self, node_id: str) -> Optional[NodeInfo]:
        """Get a node by its ID."""
        workflow_info = self.parse()
        for node in workflow_info.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_edges_from_node(self, node_id: str) -> List[EdgeInfo]:
        """Get all edges originating from a specific node."""
        workflow_info = self.parse()
        return [edge for edge in workflow_info.edges if edge.source == node_id]
    
    def get_edges_to_node(self, node_id: str) -> List[EdgeInfo]:
        """Get all edges leading to a specific node."""
        workflow_info = self.parse()
        return [edge for edge in workflow_info.edges if edge.target == node_id]
    
    def get_llm_nodes(self) -> List[NodeInfo]:
        """Get all LLM nodes from the workflow."""
        workflow_info = self.parse()
        return [node for node in workflow_info.nodes if node.node_type == 'llm']
    
    def get_loop_nodes(self) -> List[NodeInfo]:
        """Get all loop-related nodes from the workflow."""
        workflow_info = self.parse()
        return [node for node in workflow_info.nodes if node.node_type in ['loop', 'loop-start']]
    
    def get_start_nodes(self) -> List[NodeInfo]:
        """Get all start nodes from the workflow."""
        workflow_info = self.parse()
        return [node for node in workflow_info.nodes if node.node_type == 'start']
    
    def get_end_nodes(self) -> List[NodeInfo]:
        """Get all end nodes from the workflow."""
        workflow_info = self.parse()
        return [node for node in workflow_info.nodes if node.node_type == 'end']
