# Relay - DevOps Tool Provisioning Walkthrough

## Overview
The project has been successfully transformed from "Ratchet" to **Relay**.
Key changes include:
- **Rebranding**: All references updated to Relay.
- **RHEL 8 Support**: `setup.sh` and tool configurations now target RHEL/CentOS 8+ using `dnf`.
- **Airgap Architecture**: The CLI now supports two distinct modes:
    1.  **Download Mode** (`--download`): Fetches RPMs and binaries to a local `downloads/` directory.
    2.  **Install Mode** (`--install`): Installs tools from the local `downloads/` directory without internet access.

## Usage Guide

### 1. Setup
Run the setup script to initialize the environment (requires RHEL/CentOS 8+):
```bash
sudo ./setup.sh
```

### 2. Download Phase (Internet Required)
On a machine with internet access, download the desired tools:
```bash
# Interactive Menu
sudo venv/bin/python3 -m  toolbox.cli --download

# Or select specific tools via menu
```
This will create a `downloads/` directory containing all necessary artifacts.

### 3. Transfer
Copy the entire `devops-tools` directory (including `downloads/`) to your airgapped RHEL 8 server.

### 4. Install Phase (Offline)
On the airgapped machine:
```bash
# Interactive Menu
sudo venv/bin/python3 -m  toolbox.cli --install
```

## Verification Results
- **Simulation**: Verified CLI logic using `venv/bin/python3 -m  toolbox.cli --simulate`.
- **Download Logic**: Confirmed that `dnf install --downloadonly` commands are generated correctly.
- **Install Logic**: Confirmed that `dnf install local/*.rpm` commands are generated correctly.

## Changed Files
- `setup.sh`: Updated for RHEL 8 detection and `dnf` usage.
- `toolbox/cli.py`: Added `--download` and `--install` flags and corresponding logic.
- `toolbox/utils.py`: Added RHEL distro detection.
- `tools/*.json`: Refactored all tool configs to use `download_steps` and `install_steps`.
