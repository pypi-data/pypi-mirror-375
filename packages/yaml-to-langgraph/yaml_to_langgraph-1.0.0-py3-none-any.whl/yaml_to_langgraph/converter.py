"""
Main YAML to LangGraph Converter

Orchestrates the conversion process from YAML workflow to LangGraph implementation.
"""

import sys
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich import print as rprint
    from rich.traceback import install
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    def Console(*args, **kwargs):
        return None
    def Panel(*args, **kwargs):
        return str(args[0]) if args else ""
    def Progress(*args, **kwargs):
        return None
    def rprint(*args, **kwargs):
        print(*args)
    def install(*args, **kwargs):
        pass

from .yaml_parser import YAMLWorkflowParser
from .code_generator import LangGraphCodeGenerator

# Initialize Rich console
console = Console() if RICH_AVAILABLE else None

# Install Rich traceback handler
if RICH_AVAILABLE:
    install(show_locals=True)


class YAMLToLangGraphConverter:
    """Main converter class that orchestrates the conversion process."""
    
    def __init__(self, yaml_file_path: str, output_dir: Optional[str] = None):
        """
        Initialize the converter.
        
        Args:
            yaml_file_path: Path to the YAML workflow file
            output_dir: Output directory for generated code (default: based on workflow name)
        """
        self.yaml_file_path = Path(yaml_file_path)
        self.output_dir = output_dir
        
        if not self.yaml_file_path.exists():
            raise FileNotFoundError(f"YAML file not found: {yaml_file_path}")
    
    def convert(self) -> Path:
        """
        Convert YAML workflow to LangGraph implementation.
        
        Returns:
            Path to the generated output directory
        """
        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                # Parse YAML file
                task = progress.add_task("Parsing YAML file...", total=100)
                progress.update(task, advance=20)
                
                parser = YAMLWorkflowParser(str(self.yaml_file_path))
                workflow_info = parser.parse()
                progress.update(task, advance=30, description="YAML parsed successfully")
                
                # Display workflow info
                info_text = f"[bold blue]Workflow:[/bold blue] {workflow_info.name}\n"
                info_text += f"[bold blue]Description:[/bold blue] {workflow_info.description}\n"
                info_text += f"[bold blue]Nodes:[/bold blue] {len(workflow_info.nodes)}\n"
                info_text += f"[bold blue]Edges:[/bold blue] {len(workflow_info.edges)}\n"
                info_text += f"[bold blue]LLM Nodes:[/bold blue] {len([n for n in workflow_info.nodes if n.node_type == 'llm'])}"
                
                console.print(Panel(info_text, title="[bold green]Workflow Information[/bold green]", border_style="green"))
                progress.update(task, advance=20, description="Workflow analyzed")
                
                # Determine output directory
                if self.output_dir is None:
                    safe_name = self._sanitize_name(workflow_info.name)
                    self.output_dir = f"generated_{safe_name}"
                
                progress.update(task, advance=10, description="Generating LangGraph code...")
                
                # Generate the code
                generator = LangGraphCodeGenerator(self.output_dir)
                generator.generate(workflow_info)
                
                progress.update(task, completed=100, description="Conversion complete!")
        else:
            print(f"Parsing YAML file: {self.yaml_file_path}")
            
            # Parse the YAML file
            parser = YAMLWorkflowParser(str(self.yaml_file_path))
            workflow_info = parser.parse()
            
            print(f"Found workflow: {workflow_info.name}")
            print(f"  - {len(workflow_info.nodes)} nodes")
            print(f"  - {len(workflow_info.edges)} edges")
            print(f"  - {len([n for n in workflow_info.nodes if n.node_type == 'llm'])} LLM nodes")
            
            # Determine output directory
            if self.output_dir is None:
                safe_name = self._sanitize_name(workflow_info.name)
                self.output_dir = f"generated_{safe_name}"
            
            print(f"Generating LangGraph code in: {self.output_dir}")
            
            # Generate the code
            generator = LangGraphCodeGenerator(self.output_dir)
            generator.generate(workflow_info)
            
            print("Conversion completed successfully!")
            print(f"Generated files in: {Path(self.output_dir).absolute()}")
        
        return Path(self.output_dir)
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize a name for use as a directory name."""
        # Replace spaces and special characters with underscores
        sanitized = "".join(c if c.isalnum() else "_" for c in name)
        # Remove multiple underscores
        sanitized = "_".join(part for part in sanitized.split("_") if part)
        return sanitized.lower()


def main():
    """Main entry point for the converter."""
    # This function is kept for backward compatibility
    # The main CLI is now handled by the Click-based cli.py
    print("This converter now uses Click-based CLI. Use 'yaml-to-langgraph --help' for usage information.")
    sys.exit(1)


if __name__ == "__main__":
    main()
