import click
from rich.console import Console
from rich.table import Table
from datetime import datetime
import uuid
import requests
from typing import Optional, Dict, List
from pydantic import BaseModel
import sys

from .errors import (
    handle_errors, ValidationError, AuthenticationError, 
    AuthorizationError, NetworkError, ResourceNotFoundError,
    validate_required, validate_length, validate_choice, validate_uuid
)

# Import advanced commands (optional - uncomment to enable)
# from .advanced_commands import create_advanced_commands

console = Console()

class User(BaseModel):
    id: str
    username: str
    role: str
    groups: List[str]
    created_at: datetime

class Group(BaseModel):
    id: str
    name: str
    admin_id: str
    members: List[str]
    created_at: datetime

class Claim(BaseModel):
    id: str
    content: str
    author_id: str
    status: str
    created_at: datetime
    validated_at: Optional[datetime] = None

@click.group()
def main():
    """Brim network CLI with Veracity Protocol"""
    pass

@main.group()
def users():
    """Manage users"""
    pass

@users.command()
@click.argument('username')
@click.option('--role', type=click.Choice(['user', 'validator', 'group_admin', 'global_admin']), default='user')
@handle_errors
def create(username: str, role: str):
    """Create a new user"""
    validate_required(username, "username")
    validate_length(username, "username", 3, 50)
    validate_choice(role, "role", ['user', 'validator', 'group_admin', 'global_admin'])
    
    # TODO: Implement actual API call
    user = User(
        id=str(uuid.uuid4()),
        username=username,
        role=role,
        groups=[],
        created_at=datetime.now()
    )
    console.print(f"[green]Created user {username} with role {role}[/green]")

@users.command()
@handle_errors
def list():
    """List all users"""
    # TODO: Implement actual API call
    users = [
        User(
            id=str(uuid.uuid4()),
            username="example_user",
            role="user",
            groups=[],
            created_at=datetime.now()
        )
    ]
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("Username")
    table.add_column("Role")
    table.add_column("Groups")
    table.add_column("Created At")
    
    for user in users:
        table.add_row(
            str(user.id),
            user.username,
            user.role,
            ", ".join(user.groups),
            user.created_at.isoformat()
        )
    
    console.print(table)

@users.command()
@click.argument('username')
@click.option('--new-role', type=click.Choice(['user', 'validator', 'group_admin', 'global_admin']))
@click.option('--new-username')
@handle_errors
def update(username: str, new_role: Optional[str], new_username: Optional[str]):
    """Update user information"""
    validate_required(username, "username")
    if not new_role and not new_username:
        raise ValidationError("Must provide at least one field to update (--new-role or --new-username)")
    
    if new_username:
        validate_length(new_username, "new_username", 3, 50)
    
    # TODO: Implement actual API call
    console.print(f"[green]Updated user {username}[/green]")
    if new_role:
        console.print(f"New role: {new_role}")
    if new_username:
        console.print(f"New username: {new_username}")

@users.command()
@click.argument('username')
@click.confirmation_option(prompt='Are you sure you want to delete this user?')
@handle_errors
def delete(username: str):
    """Delete a user"""
    validate_required(username, "username")
    
    # TODO: Implement actual API call
    console.print(f"[green]Deleted user {username}[/green]")

@main.group()
def groups():
    """Manage groups"""
    pass

@groups.command()
@click.argument('name')
@click.option('--admin', help='Username of the group admin')
@handle_errors
def create(name: str, admin: Optional[str]):
    """Create a new group"""
    validate_required(name, "name")
    validate_length(name, "name", 2, 100)
    
    # TODO: Implement actual API call
    group = Group(
        id=str(uuid.uuid4()),
        name=name,
        admin_id=admin or "default_admin",
        members=[],
        created_at=datetime.now()
    )
    console.print(f"[green]Created group {name}[/green]")
    if admin:
        console.print(f"Admin: {admin}")

@groups.command()
@handle_errors
def list():
    """List all groups"""
    # TODO: Implement actual API call
    groups = [
        Group(
            id=str(uuid.uuid4()),
            name="example_group",
            admin_id="example_admin",
            members=["user1", "user2"],
            created_at=datetime.now()
        )
    ]
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Admin")
    table.add_column("Members")
    table.add_column("Created At")
    
    for group in groups:
        table.add_row(
            str(group.id),
            group.name,
            group.admin_id,
            ", ".join(group.members),
            group.created_at.isoformat()
        )
    
    console.print(table)

@groups.command()
@click.argument('group_name')
@click.argument('username')
@handle_errors
def add_member(group_name: str, username: str):
    """Add a user to a group"""
    validate_required(group_name, "group_name")
    validate_required(username, "username")
    
    # TODO: Implement actual API call
    console.print(f"[green]Added {username} to group {group_name}[/green]")

@groups.command()
@click.argument('group_name')
@click.argument('username')
@click.confirmation_option(prompt='Are you sure you want to remove this member?')
@handle_errors
def remove_member(group_name: str, username: str):
    """Remove a user from a group"""
    validate_required(group_name, "group_name")
    validate_required(username, "username")
    
    # TODO: Implement actual API call
    console.print(f"[green]Removed {username} from group {group_name}[/green]")

@main.group()
def claims():
    """Manage claims"""
    pass

@claims.command()
@click.argument('content')
@click.option('--author', help='Username of the claim author')
@handle_errors
def create(content: str, author: Optional[str]):
    """Create a new claim"""
    validate_required(content, "content")
    validate_length(content, "content", 10, 1000)
    
    # TODO: Implement actual API call
    claim_id = str(uuid.uuid4())
    console.print(f"[green]Created claim {claim_id}[/green]")
    console.print(f"Content: {content}")
    if author:
        console.print(f"Author: {author}")

@claims.command()
@handle_errors
def list():
    """List all claims"""
    # TODO: Implement actual API call
    claims = [
        Claim(
            id=str(uuid.uuid4()),
            content="Example claim content",
            author_id="example_user",
            status="pending",
            created_at=datetime.now()
        )
    ]
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("Content")
    table.add_column("Author")
    table.add_column("Status")
    table.add_column("Created At")
    
    for claim in claims:
        table.add_row(
            str(claim.id),
            claim.content[:50] + "..." if len(claim.content) > 50 else claim.content,
            claim.author_id,
            claim.status,
            claim.created_at.isoformat()
        )
    
    console.print(table)

@claims.command()
@click.argument('claim_id')
@click.option('--valid/--invalid', default=True)
@click.option('--comment', default=None)
@handle_errors
def validate(claim_id: str, valid: bool, comment: Optional[str]):
    """Validate a claim"""
    validate_required(claim_id, "claim_id")
    validate_uuid(claim_id, "claim_id")
    
    # TODO: Implement actual API call
    status = "valid" if valid else "invalid"
    console.print(f"[green]Marked claim {claim_id} as {status}[/green]")
    if comment:
        console.print(f"Comment: {comment}")

@claims.command()
@click.argument('claim_id')
@handle_errors
def show(claim_id: str):
    """Show detailed information about a claim"""
    validate_required(claim_id, "claim_id")
    validate_uuid(claim_id, "claim_id")
    
    # TODO: Implement actual API call
    console.print(f"[bold]Claim Details[/bold]")
    console.print(f"ID: {claim_id}")
    console.print(f"Content: Example claim content")
    console.print(f"Author: example_user")
    console.print(f"Status: pending")
    console.print(f"Created: {datetime.now().isoformat()}")

# New command group for network operations
@main.group()
def network():
    """Network operations"""
    pass

@network.command()
@handle_errors
def status():
    """Show network status"""
    # TODO: Implement actual API call
    console.print("[bold]Network Status[/bold]")
    console.print("[green]✓ Connected to Brim network[/green]")
    console.print("Active peers: 5")
    console.print("Network version: 1.0.0")

@network.command()
@click.argument('peer_id')
@handle_errors
def connect(peer_id: str):
    """Connect to a specific peer"""
    validate_required(peer_id, "peer_id")
    
    # TODO: Implement actual API call
    console.print(f"[green]Connected to peer {peer_id}[/green]")

@network.command()
@handle_errors
def peers():
    """List connected peers"""
    # TODO: Implement actual API call
    peers = [
        {"id": "peer1", "address": "127.0.0.1:8080", "status": "connected"},
        {"id": "peer2", "address": "127.0.0.1:8081", "status": "connected"}
    ]
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Peer ID")
    table.add_column("Address")
    table.add_column("Status")
    
    for peer in peers:
        table.add_row(peer["id"], peer["address"], peer["status"])
    
    console.print(table)

# New command group for configuration
@main.group()
def config():
    """Configuration management"""
    pass

@config.command()
@click.option('--key', required=True, help='Configuration key')
@click.option('--value', required=True, help='Configuration value')
@handle_errors
def set(key: str, value: str):
    """Set a configuration value"""
    validate_required(key, "key")
    validate_required(value, "value")
    
    # TODO: Implement actual API call
    console.print(f"[green]Set {key} = {value}[/green]")

@config.command()
@click.option('--key', required=True, help='Configuration key')
@handle_errors
def get(key: str):
    """Get a configuration value"""
    validate_required(key, "key")
    
    # TODO: Implement actual API call
    console.print(f"{key} = example_value")

@config.command()
@handle_errors
def list():
    """List all configuration values"""
    # TODO: Implement actual API call
    configs = {
        "api_endpoint": "http://localhost:8080",
        "timeout": "30",
        "max_retries": "3"
    }
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Key")
    table.add_column("Value")
    
    for key, value in configs.items():
        table.add_row(key, value)
    
    console.print(table)

if __name__ == '__main__':
    # Uncomment the following line to enable advanced commands
    # create_advanced_commands(main)
    main() 