# Pygmalion CLI Framework 🎭

**A micro-framework for building adaptive CLI interfaces that learn from user behavior**

## �🎯 Concept

Pygmalion CLI Framework transforms static command-line interfaces into **self-evolving CLIs** that adapt to how you use them. Unlike traditional frameworks like `argparse`, `click`, or `typer`, Pygmalion CLI Framework creates intelligent interfaces that:

- 📊 **Track your command usage patterns**
- 🤖 **Suggest shortcuts and aliases automatically**
- 🔄 **Create intelligent command workflows**
- 🎯 **Personalize help menus based on your habits**
- 💡 **Discover and suggest unused features**

## 🚀 Quick Start

### Installation

```bash
pip install pygmalion-cli-framework
```

### Basic Usage

Transform any Click-based CLI into an adaptive interface:

```python
import pygmalion
import click

@pygmalion.command()
@click.option('--count', default=1, help='Number of greetings')
@click.option('--name', prompt='Your name', help='The person to greet')
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for _ in range(count):
        click.echo(f'Hello, {name}!')

if __name__ == '__main__':
    hello()
```

### Advanced Example

```python
import pygmalion
import click

# Initialize Pygmalion CLI Framework with custom settings
app = pygmalion.PygmalionApp(
    name="myapp",
    storage_backend="sqlite",  # or "json"
    suggestion_threshold=3,    # suggest after 3 uses
)

@app.command()
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--format', type=click.Choice(['json', 'csv', 'table']), 
              default='table', help='Output format')
def export(verbose, format):
    """Export data in various formats."""
    click.echo(f"Exporting in {format} format...")
    if verbose:
        click.echo("Verbose mode enabled")

@app.command()
@click.argument('filename')
@click.option('--backup', is_flag=True, help='Create backup before processing')
def process(filename, backup):
    """Process a file with optional backup."""
    if backup:
        click.echo(f"Creating backup of {filename}")
    click.echo(f"Processing {filename}")

if __name__ == '__main__':
    app.run()
```

## ✨ Features

### 1. **Command Tracking**
Pygmalion CLI Framework automatically tracks:
- Command frequency and timestamps
- Option combinations used
- Command sequences and patterns
- User preferences over time

### 2. **Smart Alias Suggestions**
After detecting repetitive command patterns, Pygmalion CLI Framework will suggest:
```bash
$ myapp export --format json --verbose
# After 3+ uses, Pygmalion CLI Framework suggests:
💡 You often use 'export --format json --verbose'
   Would you like to create an alias? [y/N]: y
   Alias name [export-json-verbose]: ejv
✅ Alias 'ejv' created!

$ myapp ejv  # Now works as shortcut
```

### 3. **Workflow Builder**
Detects command sequences and suggests macros:
```bash
$ myapp process data.csv --backup
$ myapp export --format json
# Pygmalion CLI Framework detects pattern and suggests:
💡 You often run 'process' followed by 'export'
   Create a workflow? [y/N]: y
   Workflow name: process-and-export
✅ Workflow created!
```

### 4. **Adaptive Help System**
Your most-used commands appear first in help:
```bash
$ myapp --help
Your Most Used Commands:
  export          Export data (used 15 times)
  process         Process files (used 12 times)
  
Other Commands:
  config          Configure settings
  init            Initialize project
  
💡 Try: myapp export --format csv (you haven't used CSV format yet!)
```

### 5. **Usage Analytics**
```bash
$ myapp --stats
📊 Pygmalion CLI Framework Usage Analytics

Most Used Commands:
  export (45%)    ████████████████████
  process (32%)   ██████████████
  config (23%)    ██████████

Suggested Optimizations:
  • Create alias for 'export --format json --verbose' (used 8 times)
  • Try 'process --parallel' for faster processing
  • You haven't used 'config --advanced' yet
```

## 🏗️ Architecture

Pygmalion CLI Framework works as a wrapper around Click, extending it with intelligence:

```
┌─────────────────────────────────────┐
│           Your CLI App              │
├─────────────────────────────────────┤
│    Pygmalion CLI Framework Layer    │
│  ┌─────────────┬─────────────────┐  │
│  │   Tracker   │   Suggestions   │  │
│  ├─────────────┼─────────────────┤  │
│  │   Storage   │   Analytics     │  │
│  └─────────────┴─────────────────┘  │
├─────────────────────────────────────┤
│           Click Framework           │
└─────────────────────────────────────┘
```

## 🛠️ Configuration

### Storage Options

**JSON (Default)**
```python
app = pygmalion.PygmalionApp(storage_backend="json")
# Creates ~/.pygmalion/myapp.json
```

**SQLite (Recommended for heavy use)**
```python
app = pygmalion.PygmalionApp(storage_backend="sqlite")
# Creates ~/.pygmalion/myapp.db
```

### Customization

```python
app = pygmalion.PygmalionApp(
    name="myapp",
    storage_backend="sqlite",
    storage_path="./custom/path/",
    suggestion_threshold=5,      # Suggest aliases after 5 uses
    workflow_threshold=3,        # Suggest workflows after 3 sequences
    analytics_enabled=True,      # Enable usage analytics
    suggestions_enabled=True,    # Enable smart suggestions
    help_personalization=True,   # Personalize help menus
)
```

## 🧪 Testing

Run the test suite:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=pygmalion
```

## 📊 Example Demo

Try the included demo application:

```bash
pygmalion-demo --help
```

The demo showcases all Pygmalion features with a sample file management CLI.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/Okymi-X/pygmalion.git
cd pygmalion
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
black pygmalion tests
flake8 pygmalion tests
mypy pygmalion
```

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on top of the excellent [Click](https://click.palletsprojects.com/) framework
- Inspired by adaptive user interfaces and machine learning principles
- Thanks to all contributors and early adopters

---

**Transform your CLI from static to smart with Pygmalion! 🎭✨**
