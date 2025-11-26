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
  - **OS:** RHEL 8+, CentOS 8+, or compatible RPM-based distros
  - **Package Manager:** `dnf` (or `yum`)
  - **Root Privileges:** Required for installation commands
  - **Python:** Python 3.6+ with `venv` module

## Architecture
- **Entry Point:** `toolbox/cli.py`
- **Configuration:** Tool definitions are stored as JSON files in the `tools/` directory. Each JSON file defines:
    - `download_steps`: Commands to fetch artifacts (online phase)
    - `install_steps`: Commands to install from local artifacts (offline phase)
    - `idempotency_check`: Command to verify installation
- **Execution:** Uses Python's `subprocess` module to execute system commands.
- **Workflow:**
    1. **Download Phase:** Fetches RPMs/binaries to `downloads/{tool_name}/`
    2. **Transfer:** User copies project to airgapped system
    3. **Install Phase:** Installs from local `downloads/` directory
- **User Interface:** Interactive CLI with menu-based navigation and color-coded status (`[INSTALLED]`, `[DOWNLOADED]`).

## Key Files
- `setup.sh`: Bootstraps the environment, checks for RHEL/CentOS, and creates a virtual environment.
- `requirements.txt`: Lists Python dependencies.
- `toolbox/cli.py`: Main application logic, menu system, and workflow orchestration.
- `toolbox/config.py`: Handles loading of tool configurations.
- `toolbox/utils.py`: Utility functions for system checks, package manager detection, and command execution.
- `tools/*.json`: Individual tool configuration files.
