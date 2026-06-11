# Brim CLI Extension Guide

This guide explains how to add new commands and error handling to the existing Brim CLI.

## Table of Contents

1. [Overview](#overview)
2. [CLI Structure](#cli-structure)
3. [Adding New Commands](#adding-new-commands)
4. [Error Handling](#error-handling)
5. [Advanced Features](#advanced-features)
6. [Best Practices](#best-practices)
7. [Examples](#examples)

## Overview

The Brim CLI is built using:
- **Click**: Command-line interface creation kit
- **Rich**: Rich text and beautiful formatting in the terminal
- **Pydantic**: Data validation using Python type annotations
- **Custom Error System**: Structured error handling with exit codes

## CLI Structure

### Current Command Groups

```
brim/
├── users/           # User management
│   ├── create
│   ├── list
│   ├── update
│   └── delete
├── groups/          # Group management
│   ├── create
│   ├── list
│   ├── add-member
│   └── remove-member
├── claims/          # Claim management
│   ├── create
│   ├── list
│   ├── validate
│   └── show
├── network/         # Network operations
│   ├── status
│   ├── connect
│   └── peers
└── config/          # Configuration
    ├── set
    ├── get
    └── list
```

## Adding New Commands

### 1. Basic Command Structure

```python
@main.group()
def your_group():
    """Description of your command group"""
    pass

@your_group.command()
@click.argument('required_arg')
@click.option('--optional-flag', is_flag=True, help='Description')
@click.option('--value', default='default', help='Description')
@handle_errors
def your_command(required_arg: str, optional_flag: bool, value: str):
    """Description of your command"""
    # Your command logic here
    pass
```

### 2. Command Decorators

- `@click.group()`: Creates a command group
- `@click.command()`: Creates a command
- `@click.argument()`: Required positional argument
- `@click.option()`: Optional named argument
- `@handle_errors`: Error handling decorator

### 3. Argument Types

```python
# Basic types
@click.argument('name', type=str)
@click.argument('count', type=int)
@click.argument('file', type=click.Path(exists=True))

# Options with choices
@click.option('--role', type=click.Choice(['admin', 'user', 'guest']))

# Flags
@click.option('--verbose', is_flag=True, help='Enable verbose output')

# Multiple values
@click.option('--tags', multiple=True, help='Add multiple tags')
```

### 4. Adding to Main CLI

To add your new commands to the main CLI, import and register them:

```python
# In cli.py
from .your_module import create_your_commands

# Add to main group
create_your_commands(main)
```

## Error Handling

### 1. Error Classes

The CLI includes several error classes with specific exit codes:

```python
class BrimCLIError(Exception):
    """Base exception for Brim CLI errors"""
    error_code = 1

class ValidationError(BrimCLIError):
    """Input validation errors"""
    error_code = 2

class AuthenticationError(BrimCLIError):
    """Authentication failures"""
    error_code = 3

class AuthorizationError(BrimCLIError):
    """Authorization failures"""
    error_code = 4

class NetworkError(BrimCLIError):
    """Network operation failures"""
    error_code = 5

class ResourceNotFoundError(BrimCLIError):
    """Resource not found"""
    error_code = 6

class ConfigurationError(BrimCLIError):
    """Configuration errors"""
    error_code = 7

class TimeoutError(BrimCLIError):
    """Operation timeouts"""
    error_code = 8
```

### 2. Using Error Handling

```python
@handle_errors
def your_command():
    # Validation
    if not some_condition:
        raise ValidationError("Invalid input")
    
    # Authentication
    if not is_authenticated():
        raise AuthenticationError("Please login first")
    
    # Resource not found
    if not resource_exists():
        raise ResourceNotFoundError("User", user_id)
    
    # Network errors
    try:
        api_call()
    except requests.RequestException:
        raise NetworkError("Failed to connect to API")
```

### 3. Validation Helpers

```python
from .errors import validate_required, validate_length, validate_choice, validate_uuid

# Required field validation
validate_required(username, "username")

# Length validation
validate_length(username, "username", 3, 50)

# Choice validation
validate_choice(role, "role", ["admin", "user", "guest"])

# UUID validation
validate_uuid(user_id, "user_id")
```

## Advanced Features

### 1. Progress Bars

```python
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    console=console
) as progress:
    task = progress.add_task("Processing...", total=100)
    
    for i in range(100):
        # Do work
        progress.update(task, advance=1)
```

### 2. Interactive Prompts

```python
from rich.prompt import Prompt, Confirm

# Text input
name = Prompt.ask("Enter your name")

# Password input
password = Prompt.ask("Enter password", password=True)

# Confirmation
if Confirm.ask("Continue?"):
    # Proceed
    pass

# Choice selection
choice = Prompt.ask("Select option", choices=["a", "b", "c"])
```

### 3. Rich Tables

```python
from rich.table import Table

table = Table(show_header=True, header_style="bold magenta")
table.add_column("ID")
table.add_column("Name")
table.add_column("Status")

for item in items:
    table.add_row(
        str(item.id),
        item.name,
        f"[green]{item.status}[/green]"
    )

console.print(table)
```

### 4. Confirmation Dialogs

```python
@click.confirmation_option(prompt='Are you sure you want to delete?')
def delete_command():
    # Command will only execute if user confirms
    pass
```

## Best Practices

### 1. Command Design

- **Use descriptive names**: `create-user` not `add`
- **Provide help text**: Always include docstrings
- **Group related commands**: Use logical groupings
- **Consistent naming**: Follow existing patterns

### 2. Error Handling

- **Validate early**: Check inputs at the start
- **Use specific errors**: Choose the most appropriate error type
- **Provide context**: Include relevant details in error messages
- **Handle gracefully**: Don't crash on expected errors

### 3. User Experience

- **Clear output**: Use colors and formatting
- **Progress feedback**: Show progress for long operations
- **Confirmation**: Ask before destructive operations
- **Helpful messages**: Explain what happened

### 4. Code Organization

- **Separate concerns**: Keep commands, models, and utilities separate
- **Reusable functions**: Extract common logic
- **Type hints**: Use type annotations
- **Documentation**: Comment complex logic

## Examples

### Example 1: Simple Command

```python
@main.command()
@click.argument('message')
@click.option('--repeat', default=1, help='Number of times to repeat')
@handle_errors
def echo(message: str, repeat: int):
    """Echo a message multiple times"""
    validate_required(message, "message")
    validate_length(message, "message", 1, 1000)
    
    for i in range(repeat):
        console.print(f"[blue]{i+1}:[/blue] {message}")
```

### Example 2: Complex Command with Progress

```python
@main.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--format', type=click.Choice(['json', 'csv']), default='json')
@handle_errors
def import_data(file_path: str, format: str):
    """Import data from file"""
    validate_required(file_path, "file_path")
    
    # Read file
    with open(file_path, 'r') as f:
        data = f.readlines()
    
    total_lines = len(data)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Importing data...", total=total_lines)
        
        for i, line in enumerate(data):
            # Process line
            process_line(line.strip())
            progress.update(task, advance=1)
    
    console.print(f"[green]Successfully imported {total_lines} records[/green]")
```

### Example 3: Interactive Command

```python
@main.command()
@handle_errors
def setup():
    """Interactive setup wizard"""
    console.print("[bold blue]Setup Wizard[/bold blue]")
    
    # Get configuration
    api_url = Prompt.ask("API URL", default="http://localhost:8080")
    token = Prompt.ask("API Token", password=True)
    
    # Confirm
    console.print(f"\nAPI URL: {api_url}")
    console.print(f"Token: {'*' * len(token)}")
    
    if Confirm.ask("Save configuration?"):
        save_config(api_url, token)
        console.print("[green]Configuration saved![/green]")
    else:
        console.print("[yellow]Setup cancelled[/yellow]")
```

### Example 4: Command with Table Output

```python
@main.command()
@click.option('--status', help='Filter by status')
@handle_errors
def list_jobs(status: Optional[str]):
    """List background jobs"""
    jobs = get_jobs(status)
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Progress")
    table.add_column("Created")
    
    for job in jobs:
        status_color = "green" if job.status == "completed" else "yellow"
        table.add_row(
            job.id,
            job.type,
            f"[{status_color}]{job.status}[/{status_color}]",
            f"{job.progress}%",
            job.created_at.isoformat()
        )
    
    console.print(table)
```

## Testing Your Commands

### 1. Manual Testing

```bash
# Install in development mode
pip install -e .

# Test your command
brim your-group your-command --help
brim your-group your-command arg1 --option value
```

### 2. Unit Testing

```python
import pytest
from click.testing import CliRunner
from python_node.cli import main

def test_your_command():
    runner = CliRunner()
    result = runner.invoke(main, ['your-group', 'your-command', 'test-arg'])
    assert result.exit_code == 0
    assert "Success" in result.output

def test_your_command_validation():
    runner = CliRunner()
    result = runner.invoke(main, ['your-group', 'your-command', ''])
    assert result.exit_code == 2  # Validation error
    assert "required" in result.output
```

## Integration with Existing Code

The CLI is designed to be easily extensible. When adding new commands:

1. **Follow existing patterns**: Use the same structure and naming
2. **Use the error system**: Leverage existing error classes and handlers
3. **Add to appropriate groups**: Place commands in logical groups
4. **Update documentation**: Document new commands and features
5. **Test thoroughly**: Ensure commands work as expected

## Conclusion

This guide covers the essential aspects of extending the Brim CLI. The existing structure provides a solid foundation for adding new commands with proper error handling, user-friendly output, and consistent behavior.

For more complex features, refer to the `advanced_commands.py` example file which demonstrates progress bars, interactive prompts, and advanced validation patterns. 