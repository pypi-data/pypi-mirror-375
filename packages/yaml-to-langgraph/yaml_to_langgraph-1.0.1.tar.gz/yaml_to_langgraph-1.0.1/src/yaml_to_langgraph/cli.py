"""
Command Line Interface for YAML to LangGraph Converter

Provides a user-friendly CLI for converting YAML workflows to LangGraph implementations.
"""

import sys
from pathlib import Path
from typing import Optional

import click

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.syntax import Syntax
    from rich.tree import Tree
    from rich import print as rprint
    from rich.traceback import install
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Fallback functions
    def Console(*args, **kwargs):
        return None
    def Panel(*args, **kwargs):
        return str(args[0]) if args else ""
    def Table(*args, **kwargs):
        return None
    def Progress(*args, **kwargs):
        return None
    def Syntax(*args, **kwargs):
        return str(args[0]) if args else ""
    def Tree(*args, **kwargs):
        return None
    def rprint(*args, **kwargs):
        print(*args)
    def install(*args, **kwargs):
        pass

from .converter import YAMLToLangGraphConverter
from .schema_validator import validate_yaml_workflow

# Initialize Rich console
console = Console() if RICH_AVAILABLE else None

# Install Rich traceback handler
if RICH_AVAILABLE:
    install(show_locals=True)


# Click CLI Configuration
CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help'],
    max_content_width=120
)

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version="1.0.0", prog_name="yaml-to-langgraph")
@click.pass_context
def cli(ctx):
    """
    🚀 YAML to LangGraph Converter
    
    Convert YAML workflow files to LangGraph implementations with beautiful output.
    
    Examples:
    
    \b
      # Validate YAML file schema
      yaml-to-langgraph validate workflow.yml
      
      # Convert a YAML file to LangGraph
      yaml-to-langgraph convert workflow.yml
      
      # Convert with custom output directory
      yaml-to-langgraph convert workflow.yml -o my_workflow
      
      # Generate graph visualization
      yaml-to-langgraph visualize workflow.yml
      
      # List nodes without generating code
      yaml-to-langgraph list-nodes workflow.yml
      
      # Dry run to see what would be generated
      yaml-to-langgraph dry-run workflow.yml
    """
    ctx.ensure_object(dict)


@cli.command()
@click.argument('yaml_file', type=click.Path(exists=True, path_type=Path))
@click.option('-o', '--output', 'output_dir', 
              help='Output directory for generated code (default: based on workflow name)')
@click.option('-v', '--verbose', is_flag=True, 
              help='Enable verbose output showing all generated files')
@click.option('--skip-validation', is_flag=True,
              help='Skip YAML schema validation (not recommended)')
@click.option('--no-visualization', is_flag=True,
              help='Skip generating graph visualization')
@click.option('--visualization-format', 
              type=click.Choice(['png', 'svg', 'pdf']), 
              default='png',
              help='Format for graph visualization (default: png)')
@click.option('--visualization-layout', 
              type=click.Choice(['hierarchical', 'spring', 'circular']), 
              default='hierarchical',
              help='Layout algorithm for graph visualization (default: hierarchical)')
def convert(yaml_file: Path, output_dir: Optional[str], verbose: bool, skip_validation: bool, 
            no_visualization: bool, visualization_format: str, visualization_layout: str):
    """
    🔄 Convert YAML workflow to LangGraph implementation.
    
    YAML_FILE: Path to the YAML workflow file to convert
    """
    try:
        # Validate YAML schema first (unless skipped)
        if not skip_validation:
            if RICH_AVAILABLE:
                with console.status("[bold green]Validating YAML schema..."):
                    validation_result = validate_yaml_workflow(str(yaml_file))
            else:
                validation_result = validate_yaml_workflow(str(yaml_file))
            
            if not validation_result.is_valid:
                if RICH_AVAILABLE:
                    console.print("[bold red]❌ YAML validation failed![/bold red]")
                    console.print("[bold red]Please fix the following errors before converting:[/bold red]")
                    for error in validation_result.errors:
                        console.print(f"  [red]•[/red] [bold]{error.path}[/bold]: {error.message}")
                    console.print(f"\n[yellow]Use 'yaml-to-langgraph validate {yaml_file}' for detailed validation[/yellow]")
                else:
                    click.echo("❌ YAML validation failed!", err=True)
                    click.echo("Please fix the following errors before converting:", err=True)
                    for error in validation_result.errors:
                        click.echo(f"  • {error.path}: {error.message}", err=True)
                    click.echo(f"\nUse 'yaml-to-langgraph validate {yaml_file}' for detailed validation", err=True)
                sys.exit(1)
            
            if validation_result.has_warnings():
                if RICH_AVAILABLE:
                    console.print(f"[bold yellow]⚠️  YAML validation passed with {len(validation_result.warnings)} warnings[/bold yellow]")
                    console.print(f"[yellow]Use 'yaml-to-langgraph validate {yaml_file}' to see details[/yellow]")
                else:
                    click.echo(f"⚠️  YAML validation passed with {len(validation_result.warnings)} warnings")
                    click.echo(f"Use 'yaml-to-langgraph validate {yaml_file}' to see details")
        
        # Proceed with conversion
        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Converting YAML to LangGraph...", total=100)
                
                converter = YAMLToLangGraphConverter(str(yaml_file), output_dir, not no_visualization)
                progress.update(task, advance=30, description="Parsing YAML file...")
                
                output_path = converter.convert()
                progress.update(task, advance=70, description="Generating code...")
                
                progress.update(task, completed=100, description="Conversion complete!")
        else:
            converter = YAMLToLangGraphConverter(str(yaml_file), output_dir, not no_visualization)
            output_path = converter.convert()
        
        if verbose:
            if RICH_AVAILABLE:
                # Create file tree for verbose output
                tree = Tree(f"[bold green]{output_path.name}/[/bold green]")
                
                for file_path in sorted(output_path.rglob("*")):
                    if file_path.is_file():
                        rel_path = file_path.relative_to(output_path)
                        parts = rel_path.parts
                        
                        current = tree
                        for part in parts[:-1]:
                            # Find or create branch
                            found = False
                            for child in current.children:
                                if hasattr(child.label, 'plain') and child.label.plain == f"{part}/":
                                    current = child
                                    found = True
                                    break
                                elif str(child.label) == f"[bold blue]{part}/[/bold blue]":
                                    current = child
                                    found = True
                                    break
                            if not found:
                                current = current.add(f"[bold blue]{part}/[/bold blue]")
                        
                        # Add file
                        if parts[-1].endswith('.py'):
                            current.add(f"[bold cyan]{parts[-1]}[/bold cyan]")
                        elif parts[-1].endswith('.md'):
                            current.add(f"[bold yellow]{parts[-1]}[/bold yellow]")
                        elif parts[-1].endswith('.txt'):
                            current.add(f"[bold white]{parts[-1]}[/bold white]")
                        else:
                            current.add(f"[bold white]{parts[-1]}[/bold white]")
                
                console.print("\n[bold green]Generated files:[/bold green]")
                console.print(tree)
            else:
                click.echo(f"\nGenerated files:")
                for file_path in sorted(output_path.rglob("*")):
                    if file_path.is_file():
                        rel_path = file_path.relative_to(output_path)
                        click.echo(f"  - {rel_path}")
        
        # Next steps
        if RICH_AVAILABLE:
            next_steps = f"[bold blue]1.[/bold blue] cd {output_path}\n"
            next_steps += f"[bold blue]2.[/bold blue] pip install -r requirements.txt\n"
            next_steps += f"[bold blue]3.[/bold blue] python example_usage.py"
            
            console.print(Panel(next_steps, title="[bold green]Next Steps[/bold green]", border_style="green"))
            
            customization = f"[bold blue]•[/bold blue] Edit prompts in the prompts/ directory\n"
            customization += f"[bold blue]•[/bold blue] Modify routing logic in edges/routing.py\n"
            customization += f"[bold blue]•[/bold blue] Add custom nodes in nodes/workflow_nodes.py"
            
            console.print(Panel(customization, title="[bold yellow]Customization[/bold yellow]", border_style="yellow"))
        else:
            click.echo(f"\nNext steps:")
            click.echo(f"1. cd {output_path}")
            click.echo(f"2. pip install -r requirements.txt")
            click.echo(f"3. python example_usage.py")
            
            click.echo(f"\nTo customize the generated workflow:")
            click.echo(f"- Edit prompts in the prompts/ directory")
            click.echo(f"- Modify routing logic in edges/routing.py")
            click.echo(f"- Add custom nodes in nodes/workflow_nodes.py")
        
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[bold red]Error:[/bold red] {e}")
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('yaml_file', type=click.Path(exists=True, path_type=Path))
@click.option('-o', '--output', 'output_file', 
              help='Output file path for the visualization (default: workflow_graph.png)')
@click.option('--format', 'output_format',
              type=click.Choice(['png', 'svg', 'pdf']), 
              default='png',
              help='Format for graph visualization (default: png)')
@click.option('--layout', 'layout_algorithm',
              type=click.Choice(['hierarchical', 'spring', 'circular']), 
              default='hierarchical',
              help='Layout algorithm for graph visualization (default: hierarchical)')
@click.option('--size', 'figure_size',
              type=(int, int), 
              default=(16, 10),
              help='Figure size as width height (default: 16 10)')
@click.option('--dpi', 
              type=int, 
              default=300,
              help='DPI for the output image (default: 300)')
def visualize(yaml_file: Path, output_file: Optional[str], output_format: str, 
              layout_algorithm: str, figure_size: tuple, dpi: int):
    """
    🎨 Generate a visual representation of the workflow graph.
    
    YAML_FILE: Path to the YAML workflow file to visualize
    """
    try:
        from .yaml_parser import YAMLWorkflowParser
        from .graph_visualizer import GraphVisualizer, VisualizationConfig
        
        if RICH_AVAILABLE:
            with console.status("[bold green]Parsing YAML file..."):
                parser = YAMLWorkflowParser(str(yaml_file))
                workflow_info = parser.parse()
        else:
            parser = YAMLWorkflowParser(str(yaml_file))
            workflow_info = parser.parse()
        
        # Determine output file path
        if output_file is None:
            safe_name = "".join(c if c.isalnum() else "_" for c in workflow_info.name)
            safe_name = "_".join(part for part in safe_name.split("_") if part)
            output_file = f"{safe_name.lower()}_graph.{output_format}"
        
        # Create visualization config
        config = VisualizationConfig(
            output_format=output_format,
            layout_algorithm=layout_algorithm,
            figure_size=figure_size,
            dpi=dpi,
            show_labels=True,
            show_edge_labels=True,
            color_scheme="default"
        )
        
        if RICH_AVAILABLE:
            with console.status("[bold green]Generating graph visualization..."):
                visualizer = GraphVisualizer(config)
                visualization_path = visualizer.visualize_workflow(workflow_info, output_file)
        else:
            visualizer = GraphVisualizer(config)
            visualization_path = visualizer.visualize_workflow(workflow_info, output_file)
        
        if RICH_AVAILABLE:
            console.print(f"[bold green]✅ Graph visualization saved to:[/bold green] {visualization_path}")
            
            # Show workflow info
            info_text = f"[bold blue]Workflow:[/bold blue] {workflow_info.name}\n"
            info_text += f"[bold blue]Nodes:[/bold blue] {len(workflow_info.nodes)}\n"
            info_text += f"[bold blue]Edges:[/bold blue] {len(workflow_info.edges)}\n"
            info_text += f"[bold blue]Format:[/bold blue] {output_format.upper()}\n"
            info_text += f"[bold blue]Layout:[/bold blue] {layout_algorithm}"
            
            console.print(Panel(info_text, title="[bold green]Visualization Info[/bold green]", border_style="green"))
        else:
            click.echo(f"✅ Graph visualization saved to: {visualization_path}")
            click.echo(f"Workflow: {workflow_info.name}")
            click.echo(f"Nodes: {len(workflow_info.nodes)}, Edges: {len(workflow_info.edges)}")
            click.echo(f"Format: {output_format.upper()}, Layout: {layout_algorithm}")
        
    except ImportError as e:
        if RICH_AVAILABLE:
            console.print(f"[bold red]❌ Missing dependencies for visualization:[/bold red] {e}")
            console.print("[bold yellow]Install required packages:[/bold yellow] pip install graphviz matplotlib networkx")
        else:
            click.echo(f"❌ Missing dependencies for visualization: {e}", err=True)
            click.echo("Install required packages: pip install graphviz matplotlib networkx", err=True)
        sys.exit(1)
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[bold red]Error generating visualization:[/bold red] {e}")
        else:
            click.echo(f"Error generating visualization: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('yaml_file', type=click.Path(exists=True, path_type=Path))
def list_nodes(yaml_file: Path):
    """
    📋 List all nodes found in the YAML file without generating code.
    
    YAML_FILE: Path to the YAML workflow file to analyze
    """
    list_yaml_info(str(yaml_file))


@cli.command()
@click.argument('yaml_file', type=click.Path(exists=True, path_type=Path))
@click.option('-o', '--output', 'output_dir', 
              help='Output directory for generated code (default: based on workflow name)')
def dry_run(yaml_file: Path, output_dir: Optional[str]):
    """
    🔍 Show what would be generated without actually creating files.
    
    YAML_FILE: Path to the YAML workflow file to analyze
    """
    dry_run_conversion(str(yaml_file), output_dir)


@cli.command()
@click.argument('yaml_file', type=click.Path(exists=True, path_type=Path))
@click.option('--strict', is_flag=True, 
              help='Treat warnings as errors')
def validate(yaml_file: Path, strict: bool):
    """
    ✅ Validate YAML workflow file schema and structure.
    
    YAML_FILE: Path to the YAML workflow file to validate
    """
    try:
        if RICH_AVAILABLE:
            with console.status("[bold green]Validating YAML schema..."):
                result = validate_yaml_workflow(str(yaml_file))
        else:
            result = validate_yaml_workflow(str(yaml_file))
        
        # Display validation results
        if RICH_AVAILABLE:
            if result.is_valid and not (strict and result.has_warnings()):
                console.print("[bold green]✅ YAML file is valid![/bold green]")
            else:
                console.print("[bold red]❌ YAML file has validation issues[/bold red]")
            
            # Display errors
            if result.errors:
                console.print(f"\n[bold red]Errors ({len(result.errors)}):[/bold red]")
                for error in result.errors:
                    console.print(f"  [red]•[/red] [bold]{error.path}[/bold]: {error.message}")
            
            # Display warnings
            if result.warnings:
                if strict:
                    console.print(f"\n[bold red]Warnings (treated as errors) ({len(result.warnings)}):[/bold red]")
                    for warning in result.warnings:
                        console.print(f"  [red]•[/red] [bold]{warning.path}[/bold]: {warning.message}")
                else:
                    console.print(f"\n[bold yellow]Warnings ({len(result.warnings)}):[/bold yellow]")
                    for warning in result.warnings:
                        console.print(f"  [yellow]•[/yellow] [bold]{warning.path}[/bold]: {warning.message}")
            
            # Display info
            if result.info:
                console.print(f"\n[bold blue]Info ({len(result.info)}):[/bold blue]")
                for info in result.info:
                    console.print(f"  [blue]•[/blue] [bold]{info.path}[/bold]: {info.message}")
            
            # Summary
            if result.is_valid and not (strict and result.has_warnings()):
                console.print(f"\n[bold green]Validation Summary:[/bold green]")
                console.print(f"  [green]✅ Valid YAML workflow file[/green]")
                if result.warnings and not strict:
                    console.print(f"  [yellow]⚠️  {len(result.warnings)} warnings (use --strict to treat as errors)[/yellow]")
                if result.info:
                    console.print(f"  [blue]ℹ️  {len(result.info)} informational messages[/blue]")
            else:
                console.print(f"\n[bold red]Validation Summary:[/bold red]")
                console.print(f"  [red]❌ Invalid YAML workflow file[/red]")
                console.print(f"  [red]🔧 Please fix the issues above before processing[/red]")
        else:
            # Fallback for when Rich is not available
            if result.is_valid and not (strict and result.has_warnings()):
                click.echo("✅ YAML file is valid!")
            else:
                click.echo("❌ YAML file has validation issues")
            
            # Display errors
            if result.errors:
                click.echo(f"\nErrors ({len(result.errors)}):")
                for error in result.errors:
                    click.echo(f"  • {error.path}: {error.message}")
            
            # Display warnings
            if result.warnings:
                if strict:
                    click.echo(f"\nWarnings (treated as errors) ({len(result.warnings)}):")
                    for warning in result.warnings:
                        click.echo(f"  • {warning.path}: {warning.message}")
                else:
                    click.echo(f"\nWarnings ({len(result.warnings)}):")
                    for warning in result.warnings:
                        click.echo(f"  • {warning.path}: {warning.message}")
            
            # Display info
            if result.info:
                click.echo(f"\nInfo ({len(result.info)}):")
                for info in result.info:
                    click.echo(f"  • {info.path}: {info.message}")
        
        # Exit with appropriate code
        if not result.is_valid or (strict and result.has_warnings()):
            sys.exit(1)
        
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[bold red]Validation error:[/bold red] {e}")
        else:
            click.echo(f"Validation error: {e}", err=True)
        sys.exit(1)


def list_yaml_info(yaml_file: str) -> None:
    """List information about the YAML file without generating code."""
    try:
        from .yaml_parser import YAMLWorkflowParser
        
        if RICH_AVAILABLE:
            with console.status("[bold green]Parsing YAML file..."):
                parser = YAMLWorkflowParser(yaml_file)
                workflow_info = parser.parse()
        else:
            parser = YAMLWorkflowParser(yaml_file)
            workflow_info = parser.parse()
        
        # Create workflow info panel
        if RICH_AVAILABLE:
            info_text = f"[bold blue]Workflow:[/bold blue] {workflow_info.name}\n"
            info_text += f"[bold blue]Description:[/bold blue] {workflow_info.description}\n"
            info_text += f"[bold blue]Total nodes:[/bold blue] {len(workflow_info.nodes)}\n"
            info_text += f"[bold blue]Total edges:[/bold blue] {len(workflow_info.edges)}"
            
            console.print(Panel(info_text, title="[bold green]Workflow Information[/bold green]", border_style="green"))
        else:
            print(f"Workflow: {workflow_info.name}")
            print(f"Description: {workflow_info.description}")
            print(f"Total nodes: {len(workflow_info.nodes)}")
            print(f"Total edges: {len(workflow_info.edges)}")
        
        # Group nodes by type
        node_types = {}
        for node in workflow_info.nodes:
            node_type = node.node_type
            if node_type not in node_types:
                node_types[node_type] = []
            node_types[node_type].append(node.title or node.id)
        
        # Create nodes table
        if RICH_AVAILABLE:
            table = Table(title="[bold green]Nodes by Type[/bold green]")
            table.add_column("Type", style="cyan", no_wrap=True)
            table.add_column("Count", justify="right", style="magenta")
            table.add_column("Examples", style="white")
            
            for node_type, nodes in node_types.items():
                examples = ", ".join(nodes[:3])
                if len(nodes) > 3:
                    examples += f" ... (+{len(nodes) - 3} more)"
                table.add_row(node_type, str(len(nodes)), examples)
            
            console.print(table)
        else:
            print("\nNodes by type:")
            for node_type, nodes in node_types.items():
                print(f"  {node_type}: {len(nodes)} nodes")
                for node in nodes[:5]:  # Show first 5
                    print(f"    - {node}")
                if len(nodes) > 5:
                    print(f"    ... and {len(nodes) - 5} more")
        
        # Show edges summary
        if RICH_AVAILABLE:
            edges_text = f"[bold blue]Total edges:[/bold blue] {len(workflow_info.edges)}\n"
            edges_text += "[bold blue]Sample edges:[/bold blue]\n"
            for edge in workflow_info.edges[:5]:
                edges_text += f"  • {edge.source} → {edge.target}\n"
            if len(workflow_info.edges) > 5:
                edges_text += f"  ... and {len(workflow_info.edges) - 5} more"
            
            console.print(Panel(edges_text, title="[bold green]Edges Summary[/bold green]", border_style="blue"))
        else:
            print(f"\nEdges: {len(workflow_info.edges)}")
            for edge in workflow_info.edges[:10]:  # Show first 10
                print(f"  {edge.source} -> {edge.target}")
            if len(workflow_info.edges) > 10:
                print(f"  ... and {len(workflow_info.edges) - 10} more")
            
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[bold red]Error parsing YAML file:[/bold red] {e}")
        else:
            print(f"Error parsing YAML file: {e}", file=sys.stderr)
        sys.exit(1)


def dry_run_conversion(yaml_file: str, output_dir: Optional[str] = None) -> None:
    """Show what would be generated without actually creating files."""
    try:
        from .yaml_parser import YAMLWorkflowParser
        
        if RICH_AVAILABLE:
            with console.status("[bold green]Analyzing YAML file..."):
                parser = YAMLWorkflowParser(yaml_file)
                workflow_info = parser.parse()
        else:
            parser = YAMLWorkflowParser(yaml_file)
            workflow_info = parser.parse()
        
        # Determine output directory
        if output_dir is None:
            safe_name = "".join(c if c.isalnum() else "_" for c in workflow_info.name)
            safe_name = "_".join(part for part in safe_name.split("_") if part)
            output_dir = f"generated_{safe_name.lower()}"
        
        # Create summary panel
        if RICH_AVAILABLE:
            summary_text = f"[bold blue]Output directory:[/bold blue] {output_dir}\n"
            summary_text += f"[bold blue]Workflow:[/bold blue] {workflow_info.name}\n"
            summary_text += f"[bold blue]Nodes:[/bold blue] {len(workflow_info.nodes)}\n"
            summary_text += f"[bold blue]Edges:[/bold blue] {len(workflow_info.edges)}"
            
            console.print(Panel(summary_text, title="[bold yellow]Dry Run Summary[/bold yellow]", border_style="yellow"))
        else:
            print(f"Would generate code in: {output_dir}")
            print(f"Workflow: {workflow_info.name}")
        
        # Show what files would be created
        llm_nodes = [node for node in workflow_info.nodes if node.node_type == 'llm']
        
        if RICH_AVAILABLE:
            # Create file tree
            tree = Tree(f"[bold green]{output_dir}/[/bold green]")
            
            # Core files
            tree.add("[bold cyan]requirements.txt[/bold cyan]")
            tree.add("[bold cyan]README.md[/bold cyan]")
            tree.add("[bold cyan]example_usage.py[/bold cyan]")
            tree.add("[bold cyan]workflow_graph.py[/bold cyan]")
            
            # Nodes directory
            nodes_branch = tree.add("[bold blue]nodes/[/bold blue]")
            nodes_branch.add("[bold white]start_node.py[/bold white]")
            nodes_branch.add("[bold white]end_node.py[/bold white]")
            nodes_branch.add("[bold white]llm_node.py[/bold white]")
            nodes_branch.add("[bold white]workflow_nodes.py[/bold white]")
            
            # Edges directory
            edges_branch = tree.add("[bold blue]edges/[/bold blue]")
            edges_branch.add("[bold white]routing.py[/bold white]")
            
            # Prompts directory
            if llm_nodes:
                prompts_branch = tree.add("[bold blue]prompts/[/bold blue]")
                for node in llm_nodes:
                    if node.prompt_template:
                        safe_name = "".join(c if c.isalnum() else "_" for c in (node.title or node.id))
                        safe_name = "_".join(part for part in safe_name.split("_") if part)
                        prompts_branch.add(f"[bold white]{safe_name.lower()}.py[/bold white]")
            
            console.print(tree)
            
            # Summary
            total_files = 9 + len([n for n in llm_nodes if n.prompt_template])
            console.print(f"\n[bold green]Total: {total_files} files would be generated[/bold green]")
        else:
            print(f"\nFiles that would be generated:")
            print(f"  - {output_dir}/requirements.txt")
            print(f"  - {output_dir}/README.md")
            print(f"  - {output_dir}/example_usage.py")
            print(f"  - {output_dir}/workflow_graph.py")
            print(f"  - {output_dir}/nodes/start_node.py")
            print(f"  - {output_dir}/nodes/end_node.py")
            print(f"  - {output_dir}/nodes/llm_node.py")
            print(f"  - {output_dir}/nodes/workflow_nodes.py")
            print(f"  - {output_dir}/edges/routing.py")
            
            if llm_nodes:
                print(f"  - {output_dir}/prompts/ (directory)")
                for node in llm_nodes:
                    if node.prompt_template:
                        safe_name = "".join(c if c.isalnum() else "_" for c in (node.title or node.id))
                        safe_name = "_".join(part for part in safe_name.split("_") if part)
                        print(f"    - {safe_name.lower()}.py")
            
            print(f"\nTotal: {4 + len(llm_nodes)} files would be generated")
        
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[bold red]Error analyzing YAML file:[/bold red] {e}")
        else:
            print(f"Error analyzing YAML file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
