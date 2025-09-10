"""
YAML Workflow Parser

Parses YAML workflow files and extracts structured information for LangGraph generation.
"""

import yaml
from typing import Dict, List, Any, Optional
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
    # Enhanced fields for state management
    parent_id: Optional[str] = None
    is_in_loop: bool = False
    loop_id: Optional[str] = None
    output_keys: Optional[List[str]] = None
    input_variables: Optional[List[str]] = None


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
    # Enhanced fields for loop and state management
    is_in_loop: bool = False
    loop_id: Optional[str] = None
    source_type: Optional[str] = None
    target_type: Optional[str] = None


@dataclass
class LoopInfo:
    """Information about a loop structure."""
    id: str
    title: str
    start_node_id: str
    max_iterations: int
    break_conditions: List[Dict[str, Any]]
    loop_variables: List[Dict[str, Any]]
    logical_operator: str
    error_handle_mode: str
    child_nodes: List[str]  # Node IDs inside the loop


@dataclass
class StateVariable:
    """Information about a state variable."""
    node_id: str
    variable_name: str
    variable_type: str
    is_loop_variable: bool
    loop_id: Optional[str] = None


@dataclass
class WorkflowInfo:
    """Complete workflow information."""
    name: str
    description: str
    nodes: List[NodeInfo]
    edges: List[EdgeInfo]
    variables: List[Dict[str, Any]]
    features: Dict[str, Any]
    # Enhanced fields for loop and state management
    loops: List[LoopInfo]
    state_variables: List[StateVariable]
    node_dependencies: Dict[str, List[str]]  # node_id -> list of dependent node_ids


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
        
        # Parse loops and state variables
        loops = self._parse_loops(nodes)
        state_variables = self._parse_state_variables(nodes, edges)
        node_dependencies = self._build_dependency_graph(nodes, edges)
        
        return WorkflowInfo(
            name=app_info.get('name', 'unnamed_workflow'),
            description=app_info.get('description', ''),
            nodes=nodes,
            edges=edges,
            variables=variables,
            features=workflow_section.get('features', {}),
            loops=loops,
            state_variables=state_variables,
            node_dependencies=node_dependencies
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
            
            # Extract enhanced fields
            parent_id = node_data.get('parentId')
            is_in_loop = data.get('isInLoop', False)
            loop_id = data.get('loop_id')
            
            # Extract input variables from prompt templates
            input_variables = self._extract_input_variables(prompt_template)
            
            # Extract output keys (for now, we'll infer from node type)
            output_keys = self._infer_output_keys(data.get('type', ''), data)
            
            node_info = NodeInfo(
                id=node_data.get('id', ''),
                title=data.get('title', ''),
                node_type=data.get('type', ''),
                prompt_template=prompt_template,
                variables=variables,
                model_config=model_config,
                position=position,
                loop_config=loop_config,
                parent_id=parent_id,
                is_in_loop=is_in_loop,
                loop_id=loop_id,
                output_keys=output_keys,
                input_variables=input_variables
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
                loop_config=loop_config,
                is_in_loop=data.get('isInLoop', False),
                loop_id=data.get('loop_id'),
                source_type=data.get('sourceType'),
                target_type=data.get('targetType')
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
    
    def _extract_input_variables(self, prompt_template: Optional[List[Dict[str, str]]]) -> List[str]:
        """Extract input variables from prompt templates."""
        if not prompt_template:
            return []
        
        import re
        variables = []
        pattern = r'\{\{#([^#]+)#\}\}'
        
        for prompt in prompt_template:
            if isinstance(prompt, dict) and 'text' in prompt:
                matches = re.findall(pattern, prompt['text'])
                variables.extend(matches)
        
        return list(set(variables))  # Remove duplicates
    
    def _infer_output_keys(self, node_type: str, data: Dict[str, Any]) -> List[str]:
        """Infer output keys based on node type and data."""
        if node_type == 'llm':
            # For LLM nodes, we typically get 'text' output
            return ['text']
        elif node_type == 'assigner':
            # For assigner nodes, check the items configuration
            items = data.get('items', [])
            output_keys = []
            for item in items:
                if 'variable_selector' in item and len(item['variable_selector']) >= 2:
                    output_keys.append(item['variable_selector'][1])
            return output_keys
        elif node_type == 'start':
            # Start nodes might have specific output keys
            return ['workflow_started']
        elif node_type == 'end':
            # End nodes might have specific output keys
            return ['workflow_completed']
        else:
            # Default output key
            return ['output']
    
    def _parse_loops(self, nodes: List[NodeInfo]) -> List[LoopInfo]:
        """Parse loop information from nodes."""
        loops = []
        
        for node in nodes:
            if node.node_type == 'loop' and node.loop_config:
                # Find child nodes (nodes with this loop as parent)
                child_nodes = [n.id for n in nodes if n.parent_id == node.id]
                
                loop_info = LoopInfo(
                    id=node.id,
                    title=node.title,
                    start_node_id=node.loop_config.get('start_node_id', ''),
                    max_iterations=node.loop_config.get('loop_count', 1),
                    break_conditions=node.loop_config.get('break_conditions', []),
                    loop_variables=node.loop_config.get('loop_variables', []),
                    logical_operator=node.loop_config.get('logical_operator', 'and'),
                    error_handle_mode=node.loop_config.get('error_handle_mode', 'terminated'),
                    child_nodes=child_nodes
                )
                loops.append(loop_info)
        
        return loops
    
    def _parse_state_variables(self, nodes: List[NodeInfo], edges: List[EdgeInfo]) -> List[StateVariable]:
        """Parse state variables from nodes and their relationships."""
        _ = edges  # Suppress unused argument warning
        state_variables = []
        
        for node in nodes:
            # Add output variables for each node
            if node.output_keys:
                for output_key in node.output_keys:
                    state_var = StateVariable(
                        node_id=node.id,
                        variable_name=output_key,
                        variable_type='string',  # Default type
                        is_loop_variable=node.is_in_loop,
                        loop_id=node.loop_id
                    )
                    state_variables.append(state_var)
            
            # Add loop variables
            if node.loop_config and 'loop_variables' in node.loop_config:
                for loop_var in node.loop_config['loop_variables']:
                    state_var = StateVariable(
                        node_id=node.id,
                        variable_name=loop_var.get('label', ''),
                        variable_type=loop_var.get('var_type', 'string'),
                        is_loop_variable=True,
                        loop_id=node.id
                    )
                    state_variables.append(state_var)
        
        return state_variables
    
    def _build_dependency_graph(self, nodes: List[NodeInfo], edges: List[EdgeInfo]) -> Dict[str, List[str]]:
        """Build a dependency graph showing which nodes depend on which other nodes."""
        dependencies = {}
        
        # Initialize dependencies for all nodes
        for node in nodes:
            dependencies[node.id] = []
        
        # Build dependencies from edges
        for edge in edges:
            if edge.target in dependencies:
                dependencies[edge.target].append(edge.source)
        
        return dependencies
