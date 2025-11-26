# Relay Technology Stack

## Overview
Relay is a CLI-based DevOps tool provisioning system designed for airgapped environments. It manages the download and offline installation of various DevOps tools (e.g., Docker, Kubernetes, Ansible) on RHEL 8+ systems.

## Core Technology
- **Language:** Python 3
- **Shell Scripting:** Bash (for setup and bootstrapping)

## Dependencies
- **Python Packages:**
  - `colorama` (>=0.4.6): For cross-platform colored terminal output.
- **System Requirements:**
  - Linux-based OS (uses `apt-get`, `dpkg`)
  - Root privileges (required for installation commands)
  - `python3-venv` (for virtual environment management)

## Architecture
- **Entry Point:** `ratchet/cli.py`
- **Configuration:** Tool definitions are stored as JSON files in the `tools/` directory. Each JSON file defines installation steps (pre, main, post, verification) and idempotency checks.
- **Execution:** Uses Python's `subprocess` module to execute system commands defined in the JSON configurations.
- **User Interface:** Interactive CLI with menu-based navigation using standard input/output.

## Key Files
- `setup.sh`: Bootstraps the environment, installs dependencies, and creates a virtual environment.
- `requirements.txt`: Lists Python dependencies.
- `ratchet/cli.py`: Main application logic.
- `ratchet/config.py`: Handles loading of tool configurations.
- `ratchet/utils.py`: Utility functions for system checks and command execution.
