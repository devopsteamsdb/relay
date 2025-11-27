# Relay

**DevOps Tool Provisioning for Airgapped Environments**

Relay is a CLI-based tool designed to simplify the deployment of DevOps tools in airgapped (offline) RHEL 8+ environments. It separates the provisioning process into two phases: downloading packages on an internet-connected machine and installing them on isolated systems.

## Features

- **Two-Phase Workflow**: Download tools online, install them offline
- **RHEL 8+ Support**: Optimized for Red Hat Enterprise Linux and CentOS 8+
- **Airgap-Ready**: No internet required during installation phase
- **Multiple Tools**: Pre-configured support for Docker, Kubernetes, Ansible, Terraform, and more
- **Simulation Mode**: Test commands without executing them

## Supported Tools

- Docker & Docker Compose
- Kubernetes (kubectl)
- Ansible
- Terraform
- Helm
- Git
- And more...

## Quick Start

### Prerequisites

- RHEL/CentOS 8+ system
- Python 3.6+
- Root/sudo privileges

### Installation

1. Clone the repository:
```bash
git clone https://github.com/devopsteamsdb/relay.git
cd relay
```

2. Run the setup script:
```bash
sudo chmod +x setup.sh
sudo ./setup.sh
```

## Usage

### Download Phase (Internet-Connected Machine)

Download tools to a local directory:
```bash
sudo venv/bin/python3 -m  toolbox.cli --download
```

Or use the interactive menu:
```bash
sudo venv/bin/python3 -m  toolbox.cli
# Select option 1: Download Tools
```

### Transfer Phase

Copy the entire project directory (including the `downloads/` folder) to your airgapped machine.

### Install Phase (Airgapped Machine)

Install tools from local files:
```bash
sudo venv/bin/python3 -m  toolbox.cli --install
```

Or use the interactive menu:
```bash
sudo venv/bin/python3 -m  toolbox.cli
# Select option 2: Install Tools
```

## Simulation Mode

Test the tool without making actual changes:
```bash
sudo venv/bin/python3 -m  toolbox.cli --simulate
```

## Testing

- Run all unit tests: `python -m unittest discover -s tests`
- Last local run: passing (Python 3.x)

## Project Structure

```
relay/
Γö£ΓöÇΓöÇ toolbox/           # Main Python package
Γöé   Γö£ΓöÇΓöÇ cli.py        # CLI interface
Γöé   Γö£ΓöÇΓöÇ config.py     # Configuration loader
Γöé   ΓööΓöÇΓöÇ utils.py      # Utility functions
Γö£ΓöÇΓöÇ tools/            # Tool configuration files (JSON)
Γö£ΓöÇΓöÇ downloads/        # Downloaded packages (created during download phase)
Γö£ΓöÇΓöÇ setup.sh          # Setup script
ΓööΓöÇΓöÇ requirements.txt  # Python dependencies
```

## Adding New Tools

To add a new tool, create a JSON configuration file in the `tools/` directory:

```json
{
    "name": "ToolName",
    "description": "Tool description",
    "download_steps": [
        {
            "type": "shell",
            "command": "dnf install -y --downloadonly --downloaddir={download_dir} package-name"
        }
    ],
    "install_steps": [
        {
            "type": "shell",
            "command": "dnf install -y {download_dir}/*.rpm"
        }
    ],
    "idempotency_check": "tool-name --version"
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Designed for enterprise RHEL environments
- Built to support secure, airgapped infrastructure deployments
