"""
Enhanced graph visualizer using Mermaid + Pyppeteer for professional diagrams.

This module provides high-quality workflow visualizations using Mermaid diagrams
rendered with Pyppeteer for crisp, scalable output.
"""

import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

try:
    import pyppeteer
    from pyppeteer import launch
    PYPPETEER_AVAILABLE = True
except ImportError:
    PYPPETEER_AVAILABLE = False

from .yaml_parser import WorkflowInfo


@dataclass
class VisualizationConfig:
    """Configuration for Mermaid graph visualization."""
    output_format: str = "png"  # png, svg, pdf
    layout_algorithm: str = "hierarchical"  # hierarchical, flowchart, graph
    figure_size: Tuple[int, int] = (24, 16)  # width, height in inches
    dpi: int = 300
    show_labels: bool = True
    show_edge_labels: bool = False
    color_scheme: str = "default"  # default, colorful, monochrome
    # Enhanced visualization options
    show_loops: bool = True
    loop_grouping: bool = True
    node_spacing: float = 2.0
    show_node_types: bool = True
    max_label_length: int = 20
    theme: str = "default"  # default, dark, forest, neutral


class GraphVisualizer:
    """Professional graph visualizer using Mermaid + Pyppeteer."""
    
    def __init__(self, config: Optional[VisualizationConfig] = None):
        """
        Initialize the graph visualizer.
        
        Args:
            config: Visualization configuration
        """
        self.config = config or VisualizationConfig()
        
        # Node type colors (Mermaid-compatible)
        self.node_colors = {
            'start': '#4CAF50',      # Green
            'end': '#F44336',        # Red
            'llm': '#2196F3',        # Blue
            'assigner': '#FF9800',   # Orange
            'loop': '#9C27B0',       # Purple
            'loop-start': '#9C27B0', # Purple
            'code': '#607D8B',       # Blue Grey
            'default': '#E1E1E1'     # Light Grey
        }
    
    def visualize_workflow(self, workflow_info: WorkflowInfo, output_path: str) -> str:
        """
        Generate a professional visualization of the workflow using Mermaid.
        
        Args:
            workflow_info: Parsed workflow information
            output_path: Path to save the visualization
            
        Returns:
            Path to the generated visualization file
        """
        if not PYPPETEER_AVAILABLE:
            raise ImportError("Pyppeteer is not available. Please install it: pip install pyppeteer")
        
        # Generate Mermaid diagram
        mermaid_code = self._generate_mermaid_diagram(workflow_info)
        
        # Render with Pyppeteer
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        return self._render_with_pyppeteer(mermaid_code, output_path)
    
    def _generate_mermaid_diagram(self, workflow_info: WorkflowInfo) -> str:
        """Generate Mermaid diagram code from workflow information."""
        lines = []
        
        # Add diagram type and configuration
        if self.config.layout_algorithm == "hierarchical":
            lines.append("graph TD")
        elif self.config.layout_algorithm == "flowchart":
            lines.append("flowchart TD")
        else:
            lines.append("graph TD")
        
        # Add theme configuration
        if self.config.theme != "default":
            lines.append(f"%%{{init: {{'theme':'{self.config.theme}'}}}}%%")
        
        lines.append("")
        
        # Group nodes by loops and standalone
        standalone_nodes = []
        loop_groups = {}
        
        for node in workflow_info.nodes:
            if node.is_in_loop and node.loop_id:
                if node.loop_id not in loop_groups:
                    loop_groups[node.loop_id] = []
                loop_groups[node.loop_id].append(node)
            else:
                standalone_nodes.append(node)
        
        # Add standalone nodes
        for node in standalone_nodes:
            node_def = self._create_mermaid_node(node)
            lines.append(f"    {node_def}")
        
        lines.append("")
        
        # Add loop subgraphs
        for loop_id, loop_nodes in loop_groups.items():
            loop_info = None
            for loop in workflow_info.loops:
                if loop.id == loop_id:
                    loop_info = loop
                    break
            
            lines.append(f"    subgraph {self._sanitize_id(loop_id)} [\"🔄 {loop_info.title if loop_info else 'Loop'}\"]")
            for node in loop_nodes:
                node_def = self._create_mermaid_node(node)
                lines.append(f"        {node_def}")
            lines.append("    end")
            lines.append("")
        
        # Add edges
        for edge in workflow_info.edges:
            edge_def = self._create_mermaid_edge(edge)
            lines.append(f"    {edge_def}")
        
        return "\n".join(lines)
    
    def _create_mermaid_node(self, node) -> str:
        """Create a Mermaid node definition."""
        node_id = self._sanitize_id(node.id)
        title = node.title or node.id
        
        # Truncate long titles
        if len(title) > self.config.max_label_length:
            title = title[:self.config.max_label_length-3] + "..."
        
        # Create node definition with emoji and proper Mermaid syntax
        if node.node_type == 'start':
            return f"{node_id}[\"🚀 {title}\"]"
        elif node.node_type == 'end':
            return f"{node_id}[\"🏁 {title}\"]"
        elif node.node_type == 'llm':
            return f"{node_id}[\"🤖 {title}\"]"
        elif node.node_type == 'assigner':
            return f"{node_id}[\"⚙️ {title}\"]"
        elif node.node_type in ['loop', 'loop-start']:
            return f"{node_id}[\"🔄 {title}\"]"
        else:
            return f"{node_id}[\"📦 {title}\"]"
    
    def _create_mermaid_edge(self, edge) -> str:
        """Create a Mermaid edge definition."""
        source_id = self._sanitize_id(edge.source)
        target_id = self._sanitize_id(edge.target)
        
        # Add edge label if enabled and available
        edge_label = ""
        if self.config.show_edge_labels:
            if hasattr(edge, 'data') and edge.data and 'label' in edge.data:
                edge_label = f"|{edge.data['label']}|"
        
        # Different styling for loop edges
        if edge.is_in_loop:
            return f"{source_id} -.->{edge_label} {target_id}"
        else:
            return f"{source_id} -->{edge_label} {target_id}"
    
    def _sanitize_id(self, node_id: str) -> str:
        """Sanitize node ID for Mermaid compatibility."""
        # Replace non-alphanumeric characters with underscores
        sanitized = "".join(c if c.isalnum() else "_" for c in node_id)
        # Remove multiple underscores
        sanitized = "_".join(part for part in sanitized.split("_") if part)
        # Ensure it starts with a letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = "node_" + sanitized
        return sanitized
    
    def _render_with_pyppeteer(self, mermaid_code: str, output_path: Path) -> str:
        """Render Mermaid diagram using Pyppeteer."""
        import asyncio
        
        async def render_diagram():
            # Launch browser
            browser = await launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            try:
                page = await browser.newPage()
                
                # Set viewport size
                width = int(self.config.figure_size[0] * self.config.dpi)
                height = int(self.config.figure_size[1] * self.config.dpi)
                await page.setViewport({'width': width, 'height': height})
                
                # Create HTML with Mermaid
                html_content = self._create_html_template(mermaid_code)
                await page.setContent(html_content)
                
                # Wait for Mermaid to render
                await page.waitForSelector('.mermaid', {'timeout': 10000})
                
                # Check for any console errors
                page.on('console', lambda msg: print(f'Console {msg.type}: {msg.text}'))
                page.on('pageerror', lambda err: print(f'Page error: {err}'))
                
                await page.waitForFunction(
                    'document.querySelector(".mermaid svg") !== null',
                    {'timeout': 10000}
                )
                
                # Get the SVG element
                svg_element = await page.querySelector('.mermaid svg')
                
                if self.config.output_format == 'svg':
                    # Get SVG content
                    svg_content = await page.evaluate('(element) => element.outerHTML', svg_element)
                    
                    # Save SVG
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(svg_content)
                
                else:
                    # Take screenshot
                    await svg_element.screenshot({
                        'path': str(output_path),
                        'type': self.config.output_format
                    })
                
                return str(output_path)
                
            finally:
                await browser.close()
        
        # Run the async function
        return asyncio.get_event_loop().run_until_complete(render_diagram())
    
    def _create_html_template(self, mermaid_code: str) -> str:
        """Create HTML template for Mermaid rendering."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="https://unpkg.com/mermaid@10.9.1/dist/mermaid.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: white;
        }}
        .mermaid {{
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="mermaid">
{mermaid_code}
    </div>
    
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: '{self.config.theme}',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }},
            themeVariables: {{
                primaryColor: '#ffffff',
                primaryTextColor: '#000000',
                primaryBorderColor: '#000000',
                lineColor: '#000000',
                secondaryColor: '#f4f4f4',
                tertiaryColor: '#ffffff'
            }},
            securityLevel: 'loose'
        }});
    </script>
</body>
</html>
"""


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
