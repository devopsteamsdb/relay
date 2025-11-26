import subprocess
import os
import sys
import platform
import shutil
import socket # For internet connectivity check
from colorama import Fore, Style

def execute_command(command: str, description: str = "", simulate: bool = False) -> bool:
    """
    Executes a shell command and prints its output.
    Returns True if the command was successful, False otherwise.
    """
    if description:
        print(f"{Fore.BLUE}Executing: {description}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}$ {command}{Style.RESET_ALL}")

    if simulate:
        print(f"{Fore.YELLOW}[SIMULATION] Skipping actual command execution.{Style.RESET_ALL}")
        return True

    try:
        # Using shell=True for convenience with piping and complex commands
        # In a real-world product, carefully consider shlex.split and direct execution
        # to avoid shell injection if commands were user-provided. Here, they are hardcoded.
        result = subprocess.run(
            command,
            shell=True,
            check=True,  # Raises CalledProcessError for non-zero exit codes
            capture_output=True,
            text=True,   # Capture output as text (decoded)
            encoding='utf-8' # Ensure proper decoding
        )

        if result.stdout:
            print(f"{Fore.WHITE}Output:\n{result.stdout.strip()}{Style.RESET_ALL}")
        if result.stderr:
            print(f"{Fore.YELLOW}Error Output (if any):\n{result.stderr.strip()}{Style.RESET_ALL}")

        print(f"{Fore.GREEN}Command successful.{Style.RESET_ALL}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}ERROR: Command failed with exit code {e.returncode}{Style.RESET_ALL}")
        print(f"{Fore.RED}Command: {e.cmd}{Style.RESET_ALL}")
        if e.stdout:
            print(f"{Fore.RED}Stdout:\n{e.stdout.strip()}{Style.RESET_ALL}")
        if e.stderr:
            print(f"{Fore.RED}Stderr:\n{e.stderr.strip()}{Style.RESET_ALL}")
        return False
    except FileNotFoundError:
        print(f"{Fore.RED}ERROR: Command '{command.split()[0]}' not found.{Style.RESET_ALL}")
        return False
    except Exception as e:
        print(f"{Fore.RED}AN UNEXPECTED ERROR OCCURRED: {e}{Style.RESET_ALL}")
        return False


def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_system_info():
    """Gathers basic system information."""
    os_name = platform.system()
    os_version = platform.version()
    distro_name = "Unknown"
    
    # Try to get more specific distro info for Linux
    if os_name == "Linux":
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        os_version = line.split("=")[1].strip().strip('"')
                    elif line.startswith("ID="):
                        distro_name = line.split("=")[1].strip().strip('"')
        except FileNotFoundError:
            pass # Fallback to platform.version() if file not found

    python_version = sys.version.split(' ')[0]
    try:
        user = os.getenv('SUDO_USER') or os.getlogin()
    except OSError:
        # os.getlogin() fails in Docker containers without a controlling terminal
        user = os.getenv('USER') or os.getenv('USERNAME') or 'unknown'
    
    try:
        is_root = os.geteuid() == 0
    except AttributeError:
        # Windows does not have geteuid
        is_root = False # Assume not root on Windows for safety, or check Admin if needed.
        pass

    return {
        "os_name": os_name,
        "os_version": os_version,
        "distro_name": distro_name,
        "python_version": python_version,
        "user": user,
        "is_root": is_root,
        "package_manager": "apt" if distro_name.lower() in ["ubuntu", "debian", "kali"] else "dnf" if distro_name.lower() in ["rhel", "centos", "fedora", "rocky", "almalinux"] else "unknown"
    }

def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    """Check for internet connectivity by trying to connect to a known host."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

def check_disk_space(path='/', required_gb=10):
    """Check available disk space at a given path in GB."""
    try:
        total, used, free = shutil.disk_usage(path)
        free_gb = free / (1024**3) # Convert bytes to gigabytes
        return free_gb >= required_gb, free_gb
    except Exception:
        return False, 0.0

def check_command_exists(command: str) -> bool:
    """Checks if a command exists in the system's PATH."""
    return shutil.which(command) is not None
    
def check_package_manager(pm_name: str = None) -> bool:
    """
    Checks if a specific package manager exists.
    If pm_name is None, checks for common ones (dnf, yum, apt).
    """
    if pm_name:
        return check_command_exists(pm_name)
    
    # Auto-detect
    for pm in ['dnf', 'yum', 'apt', 'zypper']:
        if check_command_exists(pm):
            return True
    return False