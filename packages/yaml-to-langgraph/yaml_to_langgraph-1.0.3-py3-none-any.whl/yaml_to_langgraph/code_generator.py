"""
LangGraph Code Generator

Generates LangGraph code from parsed workflow information.
"""

from typing import Optional
from pathlib import Path
from .yaml_parser import WorkflowInfo, NodeInfo
from .graph_visualizer import GraphVisualizer, VisualizationConfig


class LangGraphCodeGenerator:
    """Generator for LangGraph code from workflow information."""
    
    def __init__(self, output_dir: str = "generated_graph", generate_visualization: bool = True):
        """
        Initialize the code generator.
        
        Args:
            output_dir: Directory to output generated code
            generate_visualization: Whether to generate graph visualization
        """
        self.output_dir = Path(output_dir)
        self.workflow_info: Optional[WorkflowInfo] = None
        self.generate_visualization = generate_visualization
        
    def generate(self, workflow_info: WorkflowInfo) -> None:
        """
        Generate LangGraph code from workflow information.
        
        Args:
            workflow_info: Parsed workflow information
        """
        self.workflow_info = workflow_info
        
        # Create output directory structure
        self._create_directory_structure()
        
        # Generate prompts
        self._generate_prompts()
        
        # Generate nodes
        self._generate_nodes()
        
        # Generate edges
        self._generate_edges()
        
        # Generate main graph
        self._generate_main_graph()
        
        # Generate requirements and documentation
        self._generate_requirements()
        self._generate_readme()
        self._generate_example()
        
        # Generate loop-aware graph structure
        self._generate_loop_aware_graph()
        
        # Generate graph visualization
        if self.generate_visualization:
            self._generate_visualization()
    
    def _create_directory_structure(self) -> None:
        """Create the output directory structure."""
        directories = [
            self.output_dir,
            self.output_dir / "prompts",
            self.output_dir / "nodes", 
            self.output_dir / "edges"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _generate_prompts(self) -> None:
        """Generate prompt files for LLM nodes."""
        llm_nodes = [node for node in self.workflow_info.nodes if node.node_type == 'llm']
        
        for node in llm_nodes:
            if node.prompt_template:
                self._generate_prompt_file(node)
    
    def _generate_prompt_file(self, node: NodeInfo) -> None:
        """Generate a prompt file for a specific LLM node."""
        safe_name = self._sanitize_name(node.title or node.id)
        filename = f"{safe_name}.py"
        filepath = self.output_dir / "prompts" / filename
        
        # Extract system and user prompts
        system_prompt = ""
        user_prompt = ""
        
        for prompt in node.prompt_template:
            if prompt.get('role') == 'system':
                system_prompt = prompt.get('text', '')
            elif prompt.get('role') == 'user':
                user_prompt = prompt.get('text', '')
        
        # Convert template variables to Python format
        user_prompt = self._convert_template_variables(user_prompt)
        
        content = f'''"""
Prompt template for {node.title or node.id} node
"""

{self._sanitize_name(node.title or node.id).upper()}_SYSTEM_PROMPT = """{system_prompt}"""

{self._sanitize_name(node.title or node.id).upper()}_USER_PROMPT = """{user_prompt}"""
'''
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_nodes(self) -> None:
        """Generate node files."""
        # Generate basic node types
        self._generate_basic_nodes()
        
        # Generate workflow-specific nodes
        self._generate_workflow_nodes()
    
    def _generate_basic_nodes(self) -> None:
        """Generate basic node implementations."""
        
        # Start node
        start_node_content = '''"""
Start node for the workflow
"""

from typing import Dict, Any


def start_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Start node that initializes the workflow.
    
    Args:
        state: Current state
        
    Returns:
        Updated state with initial variables
    """
    return {
        **state,
        "workflow_started": True
    }
'''
        
        with open(self.output_dir / "nodes" / "start_node.py", 'w', encoding='utf-8') as f:
            f.write(start_node_content)
        
        # End node
        end_node_content = '''"""
End node for the workflow
"""

from typing import Dict, Any


def end_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    End node that finalizes the workflow.
    
    Args:
        state: Current state
        
    Returns:
        Final state with completed workflow flag
    """
    return {
        **state,
        "workflow_completed": True
    }
'''
        
        with open(self.output_dir / "nodes" / "end_node.py", 'w', encoding='utf-8') as f:
            f.write(end_node_content)
        
        # Enhanced LLM node template with proper state management
        llm_node_content = '''"""
Enhanced LLM node for processing with language models and proper state management
"""

from typing import Dict, Any, List
try:
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_core.language_models import BaseLanguageModel
except ImportError:
    BaseLanguageModel = object
    HumanMessage = SystemMessage = object


def create_llm_node_with_state(
    system_prompt: str,
    user_prompt_template: str,
    model: BaseLanguageModel,
    output_keys: List[str]
):
    """
    Create an LLM node function with proper state management.
    
    Args:
        system_prompt: System prompt for the LLM
        user_prompt_template: User prompt template with placeholders
        model: LangChain language model instance
        output_keys: List of state keys to store outputs
        
    Returns:
        Node function for use in LangGraph
    """
    def llm_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        LLM node that processes input using the specified model and prompts.
        
        Args:
            state: Current state containing input variables
            
        Returns:
            Updated state with LLM outputs
        """
        try:
            # Format the user prompt with state variables
            user_prompt = user_prompt_template.format(**state)
            
            # Create messages
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            # Get response from model
            response = model.invoke(messages)
            
            # Extract text content
            if hasattr(response, 'content'):
                output_text = response.content
            else:
                output_text = str(response)
            
            # Update state with all output keys
            updated_state = {**state}
            for output_key in output_keys:
                updated_state[output_key] = output_text
            
            return updated_state
            
        except Exception as e:
            # Update state with error for all output keys
            updated_state = {**state}
            error_msg = f"Error in LLM processing: {str(e)}"
            for output_key in output_keys:
                updated_state[output_key] = error_msg
            return updated_state
    
    return llm_node


def create_llm_node(
    system_prompt: str,
    user_prompt_template: str,
    model: BaseLanguageModel,
    output_key: str = "text"
):
    """
    Legacy LLM node function for backward compatibility.
    
    Args:
        system_prompt: System prompt for the LLM
        user_prompt_template: User prompt template with placeholders
        model: LangChain language model instance
        output_key: Key to store the output in state
        
    Returns:
        Node function for use in LangGraph
    """
    return create_llm_node_with_state(
        system_prompt=system_prompt,
        user_prompt_template=user_prompt_template,
        model=model,
        output_keys=[output_key]
    )
'''
        
        with open(self.output_dir / "nodes" / "llm_node.py", 'w', encoding='utf-8') as f:
            f.write(llm_node_content)
    
    def _generate_workflow_nodes(self) -> None:
        """Generate workflow-specific node implementations."""
        llm_nodes = [node for node in self.workflow_info.nodes if node.node_type == 'llm']
        
        if not llm_nodes:
            return
        
        # Generate imports
        imports = []
        for node in llm_nodes:
            if node.prompt_template:
                safe_name = self._sanitize_name(node.title or node.id)
                imports.append(f"from prompts.{safe_name} import {safe_name.upper()}_SYSTEM_PROMPT, {safe_name.upper()}_USER_PROMPT")
        
        # Generate node creation functions
        node_functions = []
        for node in llm_nodes:
            if node.prompt_template:
                safe_name = self._sanitize_name(node.title or node.id)
                output_key = f"{safe_name}_output"
                
                node_functions.append(f'''    # {node.title or node.id} Node
    nodes["{safe_name}"] = create_llm_node(
        system_prompt={safe_name.upper()}_SYSTEM_PROMPT,
        user_prompt_template={safe_name.upper()}_USER_PROMPT,
        model=model,
        output_key="{output_key}"
    )''')
        
        # Generate special nodes (assigner, etc.)
        special_nodes = [node for node in self.workflow_info.nodes if node.node_type == 'assigner']
        for node in special_nodes:
            safe_name = self._sanitize_name(node.title or node.id)
            node_functions.append(f'''    # {node.title or node.id} Node
    nodes["{safe_name}"] = create_assigner_node([])  # TODO: Configure assignments''')
        
        content = f'''"""
Workflow-specific node implementations
"""

from typing import Dict, Any
from nodes.llm_node import create_llm_node
from nodes.assigner_node import create_assigner_node

{chr(10).join(imports)}


def create_workflow_nodes(model):
    """
    Create all workflow-specific nodes with the given model.
    
    Args:
        model: LangChain language model instance
        
    Returns:
        Dictionary of node functions
    """
    nodes = {{}}
    
{chr(10).join(node_functions)}
    
    return nodes
'''
        
        with open(self.output_dir / "nodes" / "workflow_nodes.py", 'w') as f:
            f.write(content)
    
    def _generate_edges(self) -> None:
        """Generate edge files."""
        
        # Generate routing logic
        routing_content = '''"""
Routing logic for the workflow
"""

from typing import Dict, Any, Literal


def route_after_start(state: Dict[str, Any]) -> Literal["end"]:
    """
    Route after start node.
    
    Args:
        state: Current state
        
    Returns:
        Next node to execute
    """
    _ = state  # Suppress unused argument warning
    return "end"


def route_after_llm(state: Dict[str, Any]) -> Literal["end"]:
    """
    Route after LLM node.
    
    Args:
        state: Current state
        
    Returns:
        Next node to execute
    """
    _ = state  # Suppress unused argument warning
    return "end"


def route_after_objection_check(state: Dict[str, Any]) -> Literal["end", "continue"]:
    """
    Route after objection check based on the result.
    
    Args:
        state: Current state
        
    Returns:
        Next node to execute
    """
    objection = state.get("Objection", "")
    
    if "No Objection" in objection:
        return "end"
    else:
        return "continue"
'''
        
        with open(self.output_dir / "edges" / "routing.py", 'w') as f:
            f.write(routing_content)
    
    def _generate_main_graph(self) -> None:
        """Generate the main graph file."""
        
        # Get node names
        node_names = []
        for node in self.workflow_info.nodes:
            safe_name = self._sanitize_name(node.title or node.id)
            node_names.append(f'"{safe_name}"')
        
        # Generate basic graph structure
        content = f'''"""
Main workflow graph
"""

from typing import Dict, Any, Optional
try:
    from langgraph.graph import StateGraph
    from langchain_core.language_models import BaseLanguageModel
except ImportError:
    StateGraph = object
    BaseLanguageModel = object

from nodes.start_node import start_node
from nodes.end_node import end_node
from nodes.workflow_nodes import create_workflow_nodes
from edges.routing import route_after_start, route_after_llm, route_after_objection_check


def create_workflow_graph(model: BaseLanguageModel) -> StateGraph:
    """
    Create the workflow graph.
    
    Args:
        model: LangChain language model instance
        
    Returns:
        Configured StateGraph ready for compilation
    """
    # Create all nodes
    nodes = create_workflow_nodes(model)
    
    # Add basic nodes
    nodes["start"] = start_node
    nodes["end"] = end_node
    
    # Create the graph
    workflow = StateGraph(Dict[str, Any])
    
    # Add all nodes
    for node_name, node_func in nodes.items():
        workflow.add_node(node_name, node_func)
    
    # Define the workflow edges
    # TODO: Configure edges based on workflow structure
    workflow.add_edge("start", "end")
    
    # Set entry point
    workflow.set_entry_point("start")
    
    return workflow


def create_compiled_graph(model: BaseLanguageModel) -> Any:
    """
    Create and compile the workflow graph.
    
    Args:
        model: LangChain language model instance
        
    Returns:
        Compiled graph ready for execution
    """
    workflow = create_workflow_graph(model)
    return workflow.compile()


# Example usage function
def run_workflow(
    model: BaseLanguageModel,
    input_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Run the workflow.
    
    Args:
        model: LangChain language model instance
        input_data: Input data for the workflow
        
    Returns:
        Final state with results
    """
    # Create and compile the graph
    graph = create_compiled_graph(model)
    
    # Run the workflow
    final_state = graph.invoke(input_data)
    
    return final_state
'''
        
        with open(self.output_dir / "workflow_graph.py", 'w') as f:
            f.write(content)
    
    def _generate_requirements(self) -> None:
        """Generate requirements.txt file."""
        content = '''langchain>=0.1.0
langchain-core>=0.1.0
langgraph>=0.1.0
pydantic>=2.0.0
pyyaml>=6.0
rich>=13.0.0
'''
        
        with open(self.output_dir / "requirements.txt", 'w') as f:
            f.write(content)
    
    def _generate_readme(self) -> None:
        """Generate README.md file."""
        content = f'''# {self.workflow_info.name} - LangGraph Implementation

This is an auto-generated LangGraph implementation from a YAML workflow definition.

## Project Structure

```
generated_graph/
├── prompts/                    # Prompt templates for LLM nodes
├── nodes/                      # Node implementations
├── edges/                      # Edge definitions and routing logic
├── workflow_graph.py          # Main graph assembly
├── example_usage.py           # Usage example
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## Usage

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from langchain_openai import ChatOpenAI
from workflow_graph import run_workflow

# Initialize model
model = ChatOpenAI(model="gpt-4", temperature=0.7)

# Run workflow
result = run_workflow(
    model=model,
    input_data={{"your_input": "value"}}
)

print(result)
```

## Workflow Description

{self.workflow_info.description}

## Generated from

This workflow was automatically generated from a YAML definition.
'''
        
        with open(self.output_dir / "README.md", 'w') as f:
            f.write(content)
    
    def _generate_example(self) -> None:
        """Generate example usage file."""
        content = '''"""
Example usage of the generated workflow
"""

try:
    from langchain_openai import ChatOpenAI
    from workflow_graph import run_workflow
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install the required dependencies: pip install -r requirements.txt")
    exit(1)


def main():
    """
    Example of how to use the generated workflow.
    """
    # Initialize the model (you'll need to set your API key)
    model = ChatOpenAI(
        model="gpt-4",
        temperature=0.7,
        max_tokens=2048
    )
    
    # Example input data
    input_data = {
        "input_text": "Your input here",
        "user_preferences": "Any preferences"
    }
    
    try:
        # Run the workflow
        result = run_workflow(
            model=model,
            input_data=input_data
        )
        
        # Print the results
        print("Workflow completed!")
        print(f"Final result: {result}")
        
    except Exception as e:
        print(f"Error running workflow: {e}")


if __name__ == "__main__":
    main()
'''
        
        with open(self.output_dir / "example_usage.py", 'w') as f:
            f.write(content)
    
    def _generate_visualization(self) -> None:
        """Generate graph visualization."""
        try:
            # Create enhanced visualization config
            config = VisualizationConfig(
                output_format="png",
                layout_algorithm="hierarchical",
                figure_size=(24, 16),
                dpi=300,
                show_labels=True,
                show_edge_labels=False,  # Disabled by default to reduce clutter
                color_scheme="default",
                show_loops=True,
                loop_grouping=True,
                theme="default"
            )
            
            # Generate the visualization
            visualizer = GraphVisualizer(config)
            output_path = self.output_dir / "workflow_graph.png"
            
            visualization_path = visualizer.visualize_workflow(self.workflow_info, str(output_path))
            
            print(f"Graph visualization saved to: {visualization_path}")
            
        except ImportError as e:
            print(f"Warning: Could not generate graph visualization. Missing dependencies: {e}")
            print("Install graphviz and matplotlib to enable visualization: pip install graphviz matplotlib networkx")
        except Exception as e:
            print(f"Warning: Failed to generate graph visualization: {e}")
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize a name for use as a Python identifier."""
        # Replace spaces and special characters with underscores
        sanitized = "".join(c if c.isalnum() else "_" for c in name)
        # Remove multiple underscores
        sanitized = "_".join(part for part in sanitized.split("_") if part)
        # Ensure it starts with a letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = "node_" + sanitized
        return sanitized.lower()
    
    def _convert_template_variables(self, template: str) -> str:
        """Convert YAML template variables to Python format string variables."""
        import re
        
        # Convert {{#node_id.field#}} to {node_id_field}
        pattern = r'\{\{#([^#]+)#\}\}'
        matches = re.findall(pattern, template)
        
        for match in matches:
            parts = match.split('.')
            if len(parts) >= 2:
                node_id = parts[0]
                field_name = parts[-1]
                
                # Create state variable name
                state_var_name = f"{node_id}_{field_name}"
                template = template.replace(f'{{{{#{match}#}}}}', f'{{{state_var_name}}}')
        
        return template
    
    def _generate_loop_aware_graph(self) -> None:
        """Generate a loop-aware graph structure."""
        if not self.workflow_info.loops:
            return
        
        # Generate loop handling code
        loop_functions = []
        loop_conditions = []
        
        for loop in self.workflow_info.loops:
            # Generate loop condition function
            condition_func = self._generate_loop_condition(loop)
            loop_conditions.append(condition_func)
            
            # Generate loop body function
            loop_body = self._generate_loop_body(loop)
            loop_functions.append(loop_body)
        
        content = f'''"""
Loop-aware graph structure for complex workflows
"""

from typing import Dict, Any, List
try:
    from langgraph.graph import StateGraph, For
    from langchain_core.language_models import BaseLanguageModel
except ImportError:
    StateGraph = object
    For = object
    BaseLanguageModel = object

from nodes.start_node import start_node
from nodes.end_node import end_node
from nodes.workflow_nodes import create_workflow_nodes

{chr(10).join(loop_conditions)}

{chr(10).join(loop_functions)}


def create_loop_aware_graph(model: BaseLanguageModel) -> StateGraph:
    """
    Create a loop-aware workflow graph.
    
    Args:
        model: LangChain language model instance
        
    Returns:
        Configured StateGraph with proper loop handling
    """
    # Create all nodes
    nodes = create_workflow_nodes(model)
    
    # Add basic nodes
    nodes["start"] = start_node
    nodes["end"] = end_node
    
    # Create the graph
    workflow = StateGraph(Dict[str, Any])
    
    # Add standalone nodes (not in loops)
    standalone_nodes = [node for node in self.workflow_info.nodes if not node.is_in_loop]
    for node in standalone_nodes:
        safe_name = self._sanitize_name(node.title or node.id)
        if safe_name in nodes:
            workflow.add_node(safe_name, nodes[safe_name])
    
    # Add loop structures
    for loop in self.workflow_info.loops:
        loop_name = self._sanitize_name(loop.title or loop.id)
        
        # Create loop subgraph
        loop_graph = StateGraph(Dict[str, Any])
        
        # Add loop nodes
        for child_node_id in loop.child_nodes:
            child_node = next((n for n in self.workflow_info.nodes if n.id == child_node_id), None)
            if child_node:
                safe_name = self._sanitize_name(child_node.title or child_node.id)
                if safe_name in nodes:
                    loop_graph.add_node(safe_name, nodes[safe_name])
        
        # Add loop edges
        loop_edges = [edge for edge in self.workflow_info.edges if edge.loop_id == loop.id]
        for edge in loop_edges:
            source_name = self._sanitize_name(edge.source)
            target_name = self._sanitize_name(edge.target)
            loop_graph.add_edge(source_name, target_name)
        
        # Set loop entry point
        start_name = self._sanitize_name(loop.start_node_id)
        loop_graph.set_entry_point(start_name)
        
        # Compile loop subgraph
        compiled_loop = loop_graph.compile()
        
        # Add loop to main graph
        workflow.add_node(loop_name, compiled_loop)
    
    # Add main workflow edges (non-loop edges)
    main_edges = [edge for edge in self.workflow_info.edges if not edge.is_in_loop]
    for edge in main_edges:
        source_name = self._sanitize_name(edge.source)
        target_name = self._sanitize_name(edge.target)
        workflow.add_edge(source_name, target_name)
    
    # Set entry point
    workflow.set_entry_point("start")
    
    return workflow


def create_compiled_loop_aware_graph(model: BaseLanguageModel) -> Any:
    """
    Create and compile the loop-aware workflow graph.
    
    Args:
        model: LangChain language model instance
        
    Returns:
        Compiled graph ready for execution
    """
    workflow = create_loop_aware_graph(model)
    return workflow.compile()
'''
        
        with open(self.output_dir / "loop_aware_graph.py", 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_loop_condition(self, loop) -> str:
        """Generate loop condition function."""
        condition_name = f"check_{self._sanitize_name(loop.id)}_condition"
        
        conditions = []
        for break_condition in loop.break_conditions:
            var_selector = break_condition.get('variable_selector', [])
            if len(var_selector) >= 2:
                var_name = var_selector[1]
                operator = break_condition.get('comparison_operator', 'contains')
                value = break_condition.get('value', '')
                
                if operator == 'contains':
                    conditions.append(f'"{value}" in state.get("{var_name}", "")')
                elif operator == 'equals':
                    conditions.append(f'state.get("{var_name}", "") == "{value}"')
                elif operator == 'not_equals':
                    conditions.append(f'state.get("{var_name}", "") != "{value}"')
        
        # Combine conditions with logical operator
        logical_op = loop.logical_operator.upper() if loop.logical_operator else 'AND'
        combined_condition = f' {logical_op} '.join(conditions) if conditions else 'True'
        
        return f'''
def {condition_name}(state: Dict[str, Any]) -> bool:
    """
    Check if loop should continue based on break conditions.
    
    Args:
        state: Current state
        
    Returns:
        True if loop should continue, False to break
    """
    # Check iteration count
    iteration_count = state.get("iteration_count", 0)
    if iteration_count >= {loop.max_iterations}:
        return False
    
    # Check break conditions
    if {combined_condition}:
        return False  # Break condition met
    
    return True  # Continue loop
'''
    
    def _generate_loop_body(self, loop) -> str:
        """Generate loop body function."""
        body_name = f"execute_{self._sanitize_name(loop.id)}_body"
        
        return f'''
def {body_name}(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute loop body with proper state management.
    
    Args:
        state: Current state
        
    Returns:
        Updated state after loop iteration
    """
    # Increment iteration count
    updated_state = {{
        **state,
        "iteration_count": state.get("iteration_count", 0) + 1
    }}
    
    # Execute loop nodes in sequence
    # This would be replaced with actual loop node execution
    # based on the loop's child nodes and edges
    
    return updated_state
'''
