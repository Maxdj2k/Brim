"""
Advanced CLI commands example
This file demonstrates how to add complex commands with advanced features
"""

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from datetime import datetime, timedelta
import time
import json
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from .errors import (
    handle_errors, ValidationError, NetworkError, 
    validate_required, validate_length, validate_uuid
)

console = Console()

class BatchOperation(BaseModel):
    id: str
    type: str
    status: str
    total_items: int
    completed_items: int
    created_at: datetime
    completed_at: Optional[datetime] = None

class AuditLog(BaseModel):
    id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    details: Dict[str, Any]
    timestamp: datetime
    ip_address: Optional[str] = None

def create_advanced_commands(main_group):
    """Create advanced command groups and add them to the main CLI"""
    
    # Batch operations group
    @main_group.group()
    def batch():
        """Batch operations for bulk processing"""
        pass

    @batch.command()
    @click.argument('operation_type')
    @click.option('--file', type=click.Path(exists=True), help='Input file with data')
    @click.option('--dry-run', is_flag=True, help='Show what would be done without executing')
    @click.option('--parallel', default=1, help='Number of parallel workers')
    @handle_errors
    def process(operation_type: str, file: Optional[str], dry_run: bool, parallel: int):
        """Process batch operations"""
        validate_required(operation_type, "operation_type")
        validate_choice(operation_type, "operation_type", ["users", "claims", "groups"])
        
        if parallel < 1 or parallel > 10:
            raise ValidationError("Parallel workers must be between 1 and 10")
        
        if dry_run:
            console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]")
        
        # Simulate batch processing with progress bar
        total_items = 100
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"Processing {operation_type}...", total=total_items)
            
            for i in range(total_items):
                time.sleep(0.05)  # Simulate work
                progress.update(task, advance=1)
                
                if i % 20 == 0:
                    progress.update(task, description=f"Processing {operation_type}... ({i}/{total_items})")
        
        console.print(f"[green]Successfully processed {total_items} {operation_type}[/green]")

    @batch.command()
    @handle_errors
    def status():
        """Show status of batch operations"""
        # TODO: Implement actual API call
        operations = [
            BatchOperation(
                id="batch-1",
                type="users",
                status="completed",
                total_items=100,
                completed_items=100,
                created_at=datetime.now() - timedelta(hours=1),
                completed_at=datetime.now() - timedelta(minutes=30)
            ),
            BatchOperation(
                id="batch-2",
                type="claims",
                status="running",
                total_items=50,
                completed_items=25,
                created_at=datetime.now() - timedelta(minutes=10)
            )
        ]
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID")
        table.add_column("Type")
        table.add_column("Status")
        table.add_column("Progress")
        table.add_column("Created")
        table.add_column("Completed")
        
        for op in operations:
            progress = f"{op.completed_items}/{op.total_items}"
            status_color = "green" if op.status == "completed" else "yellow"
            completed = op.completed_at.isoformat() if op.completed_at else "-"
            
            table.add_row(
                op.id,
                op.type,
                f"[{status_color}]{op.status}[/{status_color}]",
                progress,
                op.created_at.isoformat(),
                completed
            )
        
        console.print(table)

    # Audit and logging group
    @main_group.group()
    def audit():
        """Audit and logging operations"""
        pass

    @audit.command()
    @click.option('--user-id', help='Filter by user ID')
    @click.option('--action', help='Filter by action type')
    @click.option('--resource-type', help='Filter by resource type')
    @click.option('--since', help='Show logs since (ISO datetime)')
    @click.option('--limit', default=50, help='Maximum number of logs to show')
    @handle_errors
    def logs(user_id: Optional[str], action: Optional[str], resource_type: Optional[str], 
             since: Optional[str], limit: int):
        """Show audit logs"""
        if limit < 1 or limit > 1000:
            raise ValidationError("Limit must be between 1 and 1000")
        
        # TODO: Implement actual API call
        logs = [
            AuditLog(
                id="log-1",
                user_id="user-123",
                action="create",
                resource_type="user",
                resource_id="new-user-456",
                details={"username": "john_doe", "role": "user"},
                timestamp=datetime.now() - timedelta(minutes=5),
                ip_address="192.168.1.100"
            ),
            AuditLog(
                id="log-2",
                user_id="admin-789",
                action="validate",
                resource_type="claim",
                resource_id="claim-abc",
                details={"valid": True, "comment": "Verified"},
                timestamp=datetime.now() - timedelta(minutes=10),
                ip_address="192.168.1.101"
            )
        ]
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Timestamp")
        table.add_column("User")
        table.add_column("Action")
        table.add_column("Resource")
        table.add_column("Details")
        table.add_column("IP")
        
        for log in logs[:limit]:
            details_str = json.dumps(log.details, indent=2)[:50] + "..." if len(json.dumps(log.details)) > 50 else json.dumps(log.details)
            table.add_row(
                log.timestamp.isoformat(),
                log.user_id,
                log.action,
                f"{log.resource_type}:{log.resource_id}",
                details_str,
                log.ip_address or "-"
            )
        
        console.print(table)

    @audit.command()
    @click.argument('export_path', type=click.Path())
    @click.option('--format', type=click.Choice(['json', 'csv']), default='json')
    @click.option('--since', help='Export logs since (ISO datetime)')
    @click.option('--until', help='Export logs until (ISO datetime)')
    @handle_errors
    def export(export_path: str, format: str, since: Optional[str], until: Optional[str]):
        """Export audit logs to file"""
        validate_required(export_path, "export_path")
        
        # TODO: Implement actual API call
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Exporting audit logs...", total=100)
            
            for i in range(100):
                time.sleep(0.02)  # Simulate export work
                progress.update(task, advance=1)
        
        console.print(f"[green]Exported audit logs to {export_path} in {format.upper()} format[/green]")

    # Interactive commands group
    @main_group.group()
    def interactive():
        """Interactive commands with prompts and confirmations"""
        pass

    @interactive.command()
    @handle_errors
    def setup():
        """Interactive setup wizard"""
        console.print(Panel.fit(
            "[bold blue]Brim Network Setup Wizard[/bold blue]\n"
            "This will guide you through the initial configuration.",
            title="Welcome"
        ))
        
        # Get API endpoint
        api_endpoint = Prompt.ask(
            "Enter API endpoint",
            default="http://localhost:8080"
        )
        
        # Get authentication token
        auth_token = Prompt.ask(
            "Enter authentication token",
            password=True
        )
        
        # Confirm settings
        console.print(f"\n[bold]Configuration Summary:[/bold]")
        console.print(f"API Endpoint: {api_endpoint}")
        console.print(f"Auth Token: {'*' * len(auth_token)}")
        
        if Confirm.ask("Save these settings?"):
            # TODO: Save configuration
            console.print("[green]Configuration saved successfully![/green]")
        else:
            console.print("[yellow]Setup cancelled[/yellow]")

    @interactive.command()
    @handle_errors
    def wizard():
        """Interactive command wizard"""
        console.print(Panel.fit(
            "[bold blue]Command Wizard[/bold blue]\n"
            "Choose what you want to do:",
            title="Available Actions"
        ))
        
        actions = [
            "Create a new user",
            "Create a new group", 
            "Create a new claim",
            "Validate a claim",
            "Show network status"
        ]
        
        for i, action in enumerate(actions, 1):
            console.print(f"{i}. {action}")
        
        choice = Prompt.ask(
            "Select an action",
            choices=[str(i) for i in range(1, len(actions) + 1)]
        )
        
        choice_idx = int(choice) - 1
        selected_action = actions[choice_idx]
        
        console.print(f"\n[bold]Selected: {selected_action}[/bold]")
        
        # Handle different actions
        if "user" in selected_action.lower():
            username = Prompt.ask("Enter username")
            role = Prompt.ask(
                "Select role",
                choices=["user", "validator", "group_admin", "global_admin"],
                default="user"
            )
            console.print(f"[green]Would create user '{username}' with role '{role}'[/green]")
            
        elif "group" in selected_action.lower():
            name = Prompt.ask("Enter group name")
            admin = Prompt.ask("Enter admin username (optional)", default="")
            console.print(f"[green]Would create group '{name}'[/green]")
            
        elif "claim" in selected_action.lower():
            content = Prompt.ask("Enter claim content")
            author = Prompt.ask("Enter author username (optional)", default="")
            console.print(f"[green]Would create claim with content: {content[:50]}...[/green]")
            
        elif "validate" in selected_action.lower():
            claim_id = Prompt.ask("Enter claim ID")
            valid = Confirm.ask("Is this claim valid?")
            comment = Prompt.ask("Enter comment (optional)", default="")
            console.print(f"[green]Would validate claim '{claim_id}' as {'valid' if valid else 'invalid'}[/green]")
            
        elif "status" in selected_action.lower():
            console.print("[bold]Network Status[/bold]")
            console.print("[green]✓ Connected to Brim network[/green]")
            console.print("Active peers: 5")
            console.print("Network version: 1.0.0")

    # Health check and monitoring group
    @main_group.group()
    def health():
        """Health check and monitoring commands"""
        pass

    @health.command()
    @handle_errors
    def check():
        """Perform comprehensive health check"""
        checks = [
            ("API Connectivity", "Checking connection to API..."),
            ("Database", "Checking database connection..."),
            ("Network", "Checking network connectivity..."),
            ("Authentication", "Checking authentication service..."),
            ("Storage", "Checking storage availability...")
        ]
        
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            for check_name, description in checks:
                task = progress.add_task(description, total=None)
                time.sleep(1)  # Simulate check
                progress.update(task, description=f"{description} ✓")
                results.append((check_name, True))
        
        console.print("\n[bold]Health Check Results:[/bold]")
        for check_name, status in results:
            status_icon = "✓" if status else "✗"
            status_color = "green" if status else "red"
            console.print(f"[{status_color}]{status_icon}[/{status_color}] {check_name}")

    @health.command()
    @click.option('--interval', default=5, help='Check interval in seconds')
    @click.option('--duration', default=60, help='Monitoring duration in seconds')
    @handle_errors
    def monitor(interval: int, duration: int):
        """Monitor system health continuously"""
        if interval < 1 or interval > 300:
            raise ValidationError("Interval must be between 1 and 300 seconds")
        
        if duration < interval or duration > 3600:
            raise ValidationError("Duration must be between interval and 3600 seconds")
        
        console.print(f"[bold]Monitoring for {duration} seconds (interval: {interval}s)[/bold]")
        console.print("Press Ctrl+C to stop early\n")
        
        start_time = time.time()
        check_count = 0
        
        try:
            while time.time() - start_time < duration:
                check_count += 1
                elapsed = time.time() - start_time
                
                # Simulate health check
                status = "healthy"  # In real implementation, check actual status
                status_color = "green" if status == "healthy" else "red"
                
                console.print(f"[{status_color}][{check_count:03d}][/{status_color}] "
                            f"Status: {status} (elapsed: {elapsed:.1f}s)")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Monitoring stopped by user[/yellow]")
        
        console.print(f"\n[bold]Monitoring completed:[/bold]")
        console.print(f"Total checks: {check_count}")
        console.print(f"Duration: {time.time() - start_time:.1f} seconds")

    return main_group 