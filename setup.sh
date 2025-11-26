#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Check for root privileges ---
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root. Please use sudo."
   echo "Example: sudo bash setup.sh"
   exit 1
fi

echo "🚀 Starting Relay setup..."

# --- Navigate to the script's directory ---
# This ensures that all relative paths work correctly.
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
cd "$SCRIPT_DIR"

echo "Current working directory: $(pwd)"

# --- Check for RHEL/CentOS 8+ ---
if [ -f /etc/redhat-release ]; then
    echo "Red Hat based system detected."
else
    echo "⚠️  Warning: This script is optimized for RHEL/CentOS 8+. Proceeding with caution..."
fi

# --- Install python3-venv if not present ---
echo "Checking for python3-venv..."
# On RHEL 8, python3 is usually installed, but we might need platform-python-devel or similar if compiling extensions.
# For venv, it's often built-in or in python3-libs.
# We'll try to install it using dnf to be sure.

if command -v dnf &> /dev/null; then
    PKG_MANAGER="dnf"
elif command -v yum &> /dev/null; then
    PKG_MANAGER="yum"
else
    echo "Error: neither dnf nor yum found. Is this a RHEL-based system?"
    exit 1
fi

echo "Using package manager: $PKG_MANAGER"

# Ensure python3 is present
if ! command -v python3 &> /dev/null; then
    echo "python3 not found. Installing..."
    $PKG_MANAGER install -y python3
fi

# --- Create and activate virtual environment ---
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment '$VENV_DIR'..."
    python3 -m  venv "$VENV_DIR"
    echo "Virtual environment created."
else
    echo "Virtual environment '$VENV_DIR' already exists."
fi

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"
echo "Virtual environment activated."

# --- Install Python dependencies ---
echo "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt
echo "Python dependencies installed successfully."

# --- Final instructions ---
echo ""
echo "🎉 Setup complete!"
echo "You can now run the Relay CLI using:"
echo "  sudo venv/bin/python3 -m  toolbox.cli"
echo ""
echo "To download tools for offline use:"
echo "  sudo venv/bin/python3 -m  toolbox.cli --download"
echo ""
echo "To install tools (offline mode):"
echo "  sudo venv/bin/python3 -m  toolbox.cli --install"
echo ""
echo "Remember to run the main application with 'sudo'."

# Deactivate venv (optional, as sudo will re-evaluate environment for the main app)
# deactivate
