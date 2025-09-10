"""
Graph Visualizer for YAML to LangGraph Workflows

Generates visual representations of workflow graphs using multiple backends.
"""

from typing import Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import graphviz
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False

from .yaml_parser import WorkflowInfo


@dataclass
class VisualizationConfig:
    """Configuration for graph visualization."""
    output_format: str = "png"  # png, svg, pdf
    layout_algorithm: str = "hierarchical"  # hierarchical, spring, circular
    node_size: int = 1000
    font_size: int = 10
    figure_size: Tuple[int, int] = (16, 10)
    dpi: int = 300
    show_labels: bool = True
    show_edge_labels: bool = True
    color_scheme: str = "default"  # default, colorful, monochrome


class GraphVisualizer:
    """Visualizer for workflow graphs."""
    
    def __init__(self, config: Optional[VisualizationConfig] = None):
        """
        Initialize the graph visualizer.
        
        Args:
            config: Visualization configuration
        """
        self.config = config or VisualizationConfig()
        self.node_colors = self._get_node_colors()
        
    def visualize_workflow(self, workflow_info: WorkflowInfo, output_path: str) -> str:
        """
        Generate a visual representation of the workflow.
        
        Args:
            workflow_info: Parsed workflow information
            output_path: Path to save the visualization
            
        Returns:
            Path to the generated visualization file
        """
        if not MATPLOTLIB_AVAILABLE and not GRAPHVIZ_AVAILABLE:
            raise ImportError("Neither matplotlib nor graphviz is available. Please install at least one.")
        
        # Try Graphviz first (better for hierarchical layouts)
        if GRAPHVIZ_AVAILABLE and self.config.layout_algorithm == "hierarchical":
            try:
                return self._visualize_with_graphviz(workflow_info, output_path)
            except Exception as e:
                print(f"Graphviz visualization failed: {e}. Falling back to matplotlib.")
        
        # Fallback to matplotlib
        if MATPLOTLIB_AVAILABLE:
            return self._visualize_with_matplotlib(workflow_info, output_path)
        
        raise RuntimeError("No visualization backend available")
    
    def _visualize_with_graphviz(self, workflow_info: WorkflowInfo, output_path: str) -> str:
        """Generate visualization using Graphviz."""
        # Create a new directed graph
        dot = graphviz.Digraph(comment=workflow_info.name)
        dot.attr(rankdir='LR', size='12,8')
        dot.attr('node', shape='box', style='rounded,filled', fontname='Arial')
        dot.attr('edge', fontname='Arial', fontsize='10')
        
        # Add nodes
        for node in workflow_info.nodes:
            node_id = self._sanitize_node_id(node.id)
            node_title = node.title or node.id
            node_type = node.node_type
            
            # Set node color based on type
            color = self.node_colors.get(node_type, '#E1E1E1')
            
            # Create node label with type and title
            label = f"{node_title}\\n({node_type})"
            
            dot.node(node_id, label, fillcolor=color, fontcolor='black')
        
        # Add edges
        for edge in workflow_info.edges:
            source_id = self._sanitize_node_id(edge.source)
            target_id = self._sanitize_node_id(edge.target)
            
            # Get edge label if available
            edge_label = ""
            if hasattr(edge, 'data') and edge.data and 'label' in edge.data:
                edge_label = edge.data['label']
            
            dot.edge(source_id, target_id, label=edge_label)
        
        # Render the graph
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate the file
        dot.render(output_path.with_suffix(''), format=self.config.output_format, cleanup=True)
        
        return str(output_path.with_suffix(f'.{self.config.output_format}'))
    
    def _visualize_with_matplotlib(self, workflow_info: WorkflowInfo, output_path: str) -> str:
        """Generate visualization using matplotlib and networkx."""
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add nodes with attributes
        for node in workflow_info.nodes:
            node_id = self._sanitize_node_id(node.id)
            G.add_node(
                node_id,
                title=node.title or node.id,
                node_type=node.node_type,
                position=node.position
            )
        
        # Add edges with labels
        for edge in workflow_info.edges:
            source_id = self._sanitize_node_id(edge.source)
            target_id = self._sanitize_node_id(edge.target)
            
            edge_label = ""
            if hasattr(edge, 'data') and edge.data and 'label' in edge.data:
                edge_label = edge.data['label']
            
            G.add_edge(source_id, target_id, label=edge_label)
        
        # Create the plot
        plt.figure(figsize=self.config.figure_size, dpi=self.config.dpi)
        
        # Choose layout
        if self.config.layout_algorithm == "hierarchical":
            pos = self._hierarchical_layout(G, workflow_info)
        elif self.config.layout_algorithm == "spring":
            pos = nx.spring_layout(G, k=3, iterations=50)
        elif self.config.layout_algorithm == "circular":
            pos = nx.circular_layout(G)
        else:
            pos = nx.spring_layout(G)
        
        # Draw nodes
        node_colors = []
        node_labels = {}
        
        for node_id in G.nodes():
            node_data = G.nodes[node_id]
            node_type = node_data.get('node_type', 'unknown')
            node_colors.append(self.node_colors.get(node_type, '#E1E1E1'))
            
            if self.config.show_labels:
                node_labels[node_id] = node_data.get('title', node_id)
        
        # Draw the graph
        nx.draw_networkx_nodes(
            G, pos,
            node_color=node_colors,
            node_size=self.config.node_size,
            alpha=0.8
        )
        
        if self.config.show_labels:
            nx.draw_networkx_labels(
                G, pos,
                labels=node_labels,
                font_size=self.config.font_size,
                font_weight='bold'
            )
        
        # Draw edges
        nx.draw_networkx_edges(
            G, pos,
            edge_color='gray',
            arrows=True,
            arrowsize=20,
            arrowstyle='->',
            alpha=0.6
        )
        
        # Draw edge labels
        if self.config.show_edge_labels:
            edge_labels = nx.get_edge_attributes(G, 'label')
            nx.draw_networkx_edge_labels(
                G, pos,
                edge_labels=edge_labels,
                font_size=8
            )
        
        # Create legend
        self._create_legend()
        
        # Set title and layout
        plt.title(f"Workflow: {workflow_info.name}", fontsize=16, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout()
        
        # Save the plot
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, format=self.config.output_format, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _hierarchical_layout(self, G: nx.DiGraph, workflow_info: WorkflowInfo) -> Dict[str, Tuple[float, float]]:
        """Create a hierarchical layout using node positions from YAML if available."""
        pos = {}
        
        # Try to use positions from YAML first
        has_positions = False
        for node in workflow_info.nodes:
            node_id = self._sanitize_node_id(node.id)
            if node.position:
                # Scale positions to fit the figure
                x = node.position.get('x', 0) / 100.0
                y = -node.position.get('y', 0) / 100.0  # Flip Y axis
                pos[node_id] = (x, y)
                has_positions = True
        
        if not has_positions:
            # Fallback to automatic hierarchical layout
            try:
                pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
            except:
                # If graphviz layout fails, use spring layout
                pos = nx.spring_layout(G, k=3, iterations=50)
        
        return pos
    
    def _create_legend(self):
        """Create a legend for node types."""
        legend_elements = []
        for node_type, color in self.node_colors.items():
            legend_elements.append(
                mpatches.Patch(color=color, label=node_type.title())
            )
        
        if legend_elements:
            plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1))
    
    def _get_node_colors(self) -> Dict[str, str]:
        """Get color scheme for different node types."""
        if self.config.color_scheme == "colorful":
            return {
                'start': '#4CAF50',      # Green
                'end': '#F44336',        # Red
                'llm': '#2196F3',        # Blue
                'assigner': '#FF9800',   # Orange
                'loop': '#9C27B0',       # Purple
                'loop-start': '#9C27B0', # Purple
                'code': '#607D8B',       # Blue Grey
                'default': '#E1E1E1'     # Light Grey
            }
        elif self.config.color_scheme == "monochrome":
            return {
                'start': '#2E2E2E',      # Dark Grey
                'end': '#2E2E2E',        # Dark Grey
                'llm': '#5A5A5A',        # Medium Grey
                'assigner': '#8A8A8A',   # Light Grey
                'loop': '#5A5A5A',       # Medium Grey
                'loop-start': '#5A5A5A', # Medium Grey
                'code': '#8A8A8A',       # Light Grey
                'default': '#E1E1E1'     # Very Light Grey
            }
        else:  # default
            return {
                'start': '#4CAF50',      # Green
                'end': '#F44336',        # Red
                'llm': '#2196F3',        # Blue
                'assigner': '#FF9800',   # Orange
                'loop': '#9C27B0',       # Purple
                'loop-start': '#9C27B0', # Purple
                'code': '#607D8B',       # Blue Grey
                'default': '#E1E1E1'     # Light Grey
            }
    
    def _sanitize_node_id(self, node_id: str) -> str:
        """Sanitize node ID for use in graph libraries."""
        # Replace special characters with underscores
        sanitized = "".join(c if c.isalnum() else "_" for c in node_id)
        # Remove multiple underscores
        sanitized = "_".join(part for part in sanitized.split("_") if part)
        return sanitized


def create_workflow_visualization(
    workflow_info: WorkflowInfo,
    output_path: str,
    config: Optional[VisualizationConfig] = None
) -> str:
    """
    Convenience function to create a workflow visualization.
    
    Args:
        workflow_info: Parsed workflow information
        output_path: Path to save the visualization
        config: Optional visualization configuration
        
    Returns:
        Path to the generated visualization file
    """
    visualizer = GraphVisualizer(config)
    return visualizer.visualize_workflow(workflow_info, output_path)
