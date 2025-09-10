"""
Demo CLI application showcasing Pygmalion's adaptive features.

This demo provides a complete example of how to build an adaptive CLI
using Pygmalion that learns from user behavior.
"""

import os
import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.table import Table

import pygmalion
from pygmalion.decorators import set_default_app


# Initialize Pygmalion app
app = pygmalion.PygmalionApp(
    name="pygmalion-demo",
    storage_backend="json",  # Use JSON for easy inspection
    suggestion_threshold=3,
    workflow_threshold=2,
    analytics_enabled=True,
    suggestions_enabled=True,
    help_personalization=True
)

# Set as default for decorators
set_default_app(app)

console = Console()


@click.group(invoke_without_command=True)
@click.option('--suggestions', is_flag=True, help='Show optimization suggestions')
@click.option('--analytics', is_flag=True, help='Show usage analytics') 
@click.option('--aliases', is_flag=True, help='List available aliases')
@click.option('--workflows', is_flag=True, help='List available workflows')
@click.option('--version', is_flag=True, help='Show version information')
@click.pass_context
def main(ctx, suggestions, analytics, aliases, workflows, version):
    """
    Pygmalion Demo - An adaptive CLI that learns from your usage patterns.
    
    This demo showcases how Pygmalion transforms static CLIs into intelligent
    interfaces that adapt to your behavior over time.
    
    Try running commands multiple times to see suggestions appear!
    """
    if ctx.invoked_subcommand is None:
        if version:
            console.print(f"Pygmalion Demo v{pygmalion.__version__}")
            return
        elif suggestions:
            app.show_suggestions()
            return
        elif analytics:
            app.show_analytics()
            return
        elif aliases:
            app.list_aliases()
            return
        elif workflows:
            app.list_workflows()
            return
        else:
            # Show enhanced help with usage patterns
            enhanced_help = app.help.generate_main_help(ctx, ctx.get_help())
            console.print(enhanced_help)


@main.command()
@click.argument('filename')
@click.option('--format', type=click.Choice(['json', 'csv', 'xml', 'yaml']), 
              default='json', help='Output format')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--compress', is_flag=True, help='Compress output')
def export(filename, format, verbose, compress):
    """Export data to various formats."""
    # Track command usage
    app.tracker.record_command("export", {
        "filename": filename,
        "format": format, 
        "verbose": verbose,
        "compress": compress
    })
    
    console.print(f"📤 Exporting data to {filename}")
    console.print(f"   Format: {format}")
    
    if verbose:
        console.print(f"   Verbose mode enabled")
        console.print(f"   Compression: {'enabled' if compress else 'disabled'}")
    
    # Simulate export process
    import time
    import random
    
    with console.status(f"Exporting in {format} format..."):
        time.sleep(random.uniform(0.5, 1.5))
    
    console.print(f"✅ Export completed successfully!", style="green")
    
    if verbose:
        console.print(f"   File size: {random.randint(100, 9999)} KB")
        console.print(f"   Records exported: {random.randint(500, 5000)}")
    
    # Check for suggestions after command execution
    app._check_and_show_suggestions()


@main.command()
@click.argument('filename')
@click.option('--backup', is_flag=True, help='Create backup before processing')
@click.option('--parallel', is_flag=True, help='Enable parallel processing')
@click.option('--output', '-o', help='Output file path')
def process(filename, backup, parallel, output):
    """Process files with various options."""
    # Track command usage
    app.tracker.record_command("process", {
        "filename": filename,
        "backup": backup,
        "parallel": parallel,
        "output": output
    })
    
    console.print(f"⚙️  Processing file: {filename}")
    
    if backup:
        console.print(f"   Creating backup: {filename}.bak")
    
    if parallel:
        console.print(f"   Parallel processing enabled")
    
    if output:
        console.print(f"   Output will be saved to: {output}")
    
    # Simulate processing
    import time
    import random
    
    steps = ["Reading file", "Analyzing data", "Applying transformations", "Writing output"]
    
    for step in steps:
        with console.status(f"{step}..."):
            time.sleep(random.uniform(0.3, 0.8))
    
    console.print(f"✅ Processing completed!", style="green")
    
    # Check for suggestions after command execution
    app._check_and_show_suggestions()


@main.command()
@click.option('--level', type=click.Choice(['basic', 'advanced', 'expert']),
              default='basic', help='Configuration level')
@click.option('--reset', is_flag=True, help='Reset to defaults')
@click.option('--show', is_flag=True, help='Show current configuration')
def config(level, reset, show):
    """Configure application settings."""
    
    if show:
        console.print("📋 Current Configuration:")
        config_data = app.get_config()
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in config_data.items():
            table.add_row(key, str(value))
        
        console.print(table)
        return
    
    if reset:
        console.print("🔄 Resetting configuration to defaults...")
        # Reset logic would go here
        console.print("✅ Configuration reset!", style="green")
        return
    
    console.print(f"⚙️  Configuring at {level} level")
    
    if level == "advanced":
        console.print("   Advanced options available:")
        console.print("   • Custom export formats")
        console.print("   • Advanced processing algorithms")
        console.print("   • Performance tuning")
    elif level == "expert":
        console.print("   Expert options available:")
        console.print("   • Plugin system configuration")
        console.print("   • Custom scripting support")
        console.print("   • Advanced analytics")
    
    console.print("✅ Configuration updated!", style="green")


@main.command()
@click.argument('path', default='.')
@click.option('--recursive', '-r', is_flag=True, help='Scan recursively')
@click.option('--filter', help='File filter pattern')
@click.option('--size', is_flag=True, help='Show file sizes')
def scan(path, recursive, filter, size):
    """Scan directories and files."""
    console.print(f"🔍 Scanning path: {path}")
    
    if recursive:
        console.print("   Recursive scan enabled")
    
    if filter:
        console.print(f"   Filter pattern: {filter}")
    
    # Simulate scanning
    import time
    import random
    
    with console.status("Scanning files..."):
        time.sleep(random.uniform(1.0, 2.0))
    
    # Show mock results
    file_count = random.randint(10, 100)
    dir_count = random.randint(2, 20)
    
    console.print(f"📊 Scan Results:")
    console.print(f"   Files found: {file_count}")
    console.print(f"   Directories: {dir_count}")
    
    if size:
        total_size = random.randint(1024, 1024*1024)
        console.print(f"   Total size: {total_size} bytes")


@main.command()
@click.argument('action', type=click.Choice(['start', 'stop', 'restart', 'status']))
@click.option('--port', default=8080, help='Server port')
@click.option('--host', default='localhost', help='Server host')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def server(action, port, host, debug):
    """Manage server operations."""
    console.print(f"🖥️  Server {action}")
    
    if action == "start":
        console.print(f"   Starting server on {host}:{port}")
        if debug:
            console.print("   Debug mode enabled")
        console.print("✅ Server started!", style="green")
    
    elif action == "stop":
        console.print("   Stopping server...")
        console.print("✅ Server stopped!", style="green")
    
    elif action == "restart":
        console.print("   Restarting server...")
        console.print("✅ Server restarted!", style="green")
    
    elif action == "status":
        console.print("   Server status: Running")
        console.print(f"   Host: {host}")
        console.print(f"   Port: {port}")
        console.print(f"   Debug: {'enabled' if debug else 'disabled'}")


@main.command()
@click.option('--days', default=7, help='Number of days to analyze')
@click.option('--export', help='Export analytics to file')
def analytics(days, export):
    """Show detailed usage analytics."""
    app.show_analytics(days)
    
    if export:
        if app.export_data(export, "json"):
            console.print(f"✅ Analytics exported to {export}", style="green")
        else:
            console.print(f"❌ Failed to export analytics", style="red")


@main.command()
def suggestions():
    """Show and act on optimization suggestions."""
    app.show_suggestions()


@main.command()
@click.argument('name')
@click.argument('command')
@click.argument('args', nargs=-1)
def create_alias(name, command, args):
    """Create a command alias."""
    # Parse args into a dictionary (simplified)
    parsed_args = {}
    for arg in args:
        if arg.startswith('--'):
            if '=' in arg:
                key, value = arg[2:].split('=', 1)
                parsed_args[key] = value
            else:
                parsed_args[arg[2:]] = True
    
    if app.create_alias(name, command, parsed_args):
        console.print(f"✅ Alias '{name}' created!", style="green")
    else:
        console.print(f"❌ Failed to create alias '{name}'", style="red")


@main.command()
@click.argument('name')
@click.argument('commands', nargs=-1)
def create_workflow(name, commands):
    """Create a command workflow."""
    workflow_commands = [{"command": cmd, "args": {}} for cmd in commands]
    
    if app.create_workflow(name, workflow_commands):
        console.print(f"✅ Workflow '{name}' created!", style="green")
        console.print(f"   Steps: {' → '.join(commands)}")
    else:
        console.print(f"❌ Failed to create workflow '{name}'", style="red")


@main.command()
def reset():
    """Reset all Pygmalion data."""
    if click.confirm("This will delete all tracking data, aliases, and workflows. Continue?"):
        if app.reset_data(confirm=True):
            console.print("✅ All data reset successfully!", style="green")
        else:
            console.print("❌ Failed to reset data", style="red")


@main.command()
def demo():
    """Run an interactive demo of Pygmalion features."""
    console.print("🎭 Welcome to the Pygmalion Interactive Demo!\n")
    
    console.print("This demo will show you how Pygmalion learns from your usage patterns.")
    console.print("Try running these commands multiple times to see suggestions appear:\n")
    
    demo_commands = [
        "pygmalion-demo export data.json --format json --verbose",
        "pygmalion-demo process input.txt --backup",
        "pygmalion-demo scan /path/to/dir --recursive --size",
        "pygmalion-demo server start --port 8080 --debug",
    ]
    
    console.print("Suggested commands to try:")
    for i, cmd in enumerate(demo_commands, 1):
        console.print(f"  {i}. {cmd}")
    
    console.print("\nAfter running commands a few times, try:")
    console.print("  • pygmalion-demo --suggestions  (see optimization suggestions)")
    console.print("  • pygmalion-demo --analytics    (view usage analytics)")
    console.print("  • pygmalion-demo --aliases      (list created aliases)")
    console.print("  • pygmalion-demo --workflows    (list created workflows)")
    
    console.print("\n🎯 The more you use it, the smarter it gets!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n👋 Goodbye!", style="yellow")
        sys.exit(0)
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        sys.exit(1)
