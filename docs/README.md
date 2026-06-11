# Brim Network with Veracity Protocol

A decentralized network implementation with built-in claim validation using the Veracity Protocol.

## Features

- User Management System
  - Role-based access control (GlobalAdmin, GroupAdmin, Validator, User)
  - Group management
- Veracity Protocol Implementation
  - Claim creation and validation
  - Consensus-based validation system
  - Trust scoring mechanism
- Python CLI Interface
  - User and group management
  - Claim validation
  - Rich terminal UI

## Project Structure

```
.
├── rust-node/           # Core Rust implementation
│   ├── Cargo.toml
│   └── src/
│       ├── lib.rs       # Core types and error handling
│       ├── user.rs      # User management
│       └── veracity.rs  # Veracity Protocol implementation
├── python-node/         # Python CLI interface
│   ├── setup.py
│   └── python_node/
│       └── cli.py       # CLI implementation
└── README.md
```

## Installation

### Rust Node

```bash
cd rust-node
cargo build --release
```

### Python CLI

```bash
cd python-node
pip install -e .
```

## Usage

### Command Line Interface

```bash
# User Management
brim users create <username> --role <role>
brim users list

# Group Management
brim groups create <name>
brim groups add-member <group_name> <username>

# Claim Management
brim claims create "<content>"
brim claims validate <claim_id> --valid/--invalid --comment "Optional comment"
```

## Development

### Prerequisites

- Rust 1.70 or later
- Python 3.8 or later
- Cargo and pip package managers

### Building from Source

1. Clone the repository
2. Build the Rust node
3. Install the Python CLI
4. Run tests

## License

MIT License 