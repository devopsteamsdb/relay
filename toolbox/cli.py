#!/usr/bin/env python3
"""
Relay - DevOps Tool Provisioning for Airgapped Environments
A CLI tool for downloading and installing DevOps tools offline
"""

import os
import sys
import time
import json # Still needed for potential future json usage, but tool config is external
import subprocess # <--- ADDED THIS IMPORT: Required for subprocess.run()

from colorama import init, Fore, Back, Style

# Import our custom modules
from toolbox.utils import (
    clear_screen, execute_command, get_system_info,
    check_internet_connection, check_disk_space,
    check_command_exists, check_package_manager
)
from toolbox.config import load_tool_configurations

# Initialize colorama for cross-platform colored output
init()

class ToolboxCLI:
    def __init__(self):
        self.installed_tools = set() # This will reflect tools confirmed as installed during runtime
        self.downloaded_tools = set() # Track which tools have been downloaded
        self.tools_config = load_tool_configurations()
        self.system_info = get_system_info()
        self.simulation_mode = False # Add a simulation mode flag
        self.download_mode = False
        self.install_mode = False
        self.downloads_dir = os.path.join(os.getcwd(), "downloads")

        # Pre-check existing tools on startup
        self._check_initial_installed_tools()

    def _check_initial_installed_tools(self):
        """
        On startup, check which tools are already installed on the system
        based on their idempotency_check command.
        """
        print(f"{Fore.MAGENTA}Checking for pre-existing tool installations...{Style.RESET_ALL}")
        for tool in self.tools_config:
            idempotency_cmd = tool.get('idempotency_check')
            if idempotency_cmd:
                try:
                    # Use subprocess.run directly for a silent check, not execute_command
                    # as we don't want to print full output for every check on startup
                    subprocess.run(idempotency_cmd, shell=True, check=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    self.installed_tools.add(tool['name'])
                    print(f"{Fore.GREEN}  ✓ {tool['name']} detected as installed.{Style.RESET_ALL}")
                except (subprocess.CalledProcessError, FileNotFoundError):
                    # Command failed or not found, tool is likely not installed
                    print(f"{Fore.YELLOW}  - {tool['name']} not detected.{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}  Warning: No idempotency check defined for {tool['name']}. Cannot auto-detect.{Style.RESET_ALL}")
        time.sleep(1) # Give user time to see the checks
        
        # Check which tools have been downloaded
        self._check_downloaded_tools()
    
    def _check_downloaded_tools(self):
        """
        Check which tools have their downloads directory present.
        """
        if os.path.exists(self.downloads_dir):
            for tool in self.tools_config:
                tool_download_dir = os.path.join(self.downloads_dir, tool['name'])
                if os.path.exists(tool_download_dir) and os.listdir(tool_download_dir):
                    self.downloaded_tools.add(tool['name'])

    def print_ascii_art(self):
        ascii_art = '''
            ____       _             
            |  _ \ ___| | __ _ _   _ 
            | |_) / _ \ |/ _` | | | |
            |  _ <  __/ | (_| | |_| |
            |_| \_\___|_|\__,_|\__, |
                                |___/ 
                                
DevOps Tool Provisioning for Airgapped Environments
        '''
        print(Fore.CYAN + ascii_art + Style.RESET_ALL)

    def show_disclaimer(self):
        clear_screen()
        print(Fore.YELLOW + "Disclaimer & Terms of Service" + Style.RESET_ALL)
        print("This tool performs system-level changes and requires root privileges.")
        print("By using Relay, you agree to take full responsibility for any changes or damages to your system.")
        print("The creators are not liable for any issues that may arise.")
        print(Fore.CYAN + "Do you agree to these terms? (y/n): " + Style.RESET_ALL, end="")

        response = input().strip().lower()
        if response == 'y':
            return True
        else:
            print(f"{Fore.RED}You must agree to the terms to continue. Exiting.{Style.RESET_ALL}")
            return False

    def show_main_menu(self):
        clear_screen()
        self.print_ascii_art()
        print(Fore.CYAN + "Welcome to Relay - DevOps Tool Provisioning" + Style.RESET_ALL)
        print(f"System detected: {self.system_info['os_version']} | User: {self.system_info['user']} | Python: {self.system_info['python_version']}")
        print("----------------------------------------------------------")
        print(Fore.YELLOW + "Main Menu" + Style.RESET_ALL)

        print("1. Download Tools (Internet Required)")
        print("2. Install Tools (Offline/Airgapped)")
        print("3. Check System Requirements")
        print("4. View Installed Tools (during this session)")
        print("5. Exit")
        print(Fore.CYAN + "Enter your choice: " + Style.RESET_ALL, end="")

    def show_tool_selection_menu(self, action="Install"):
        clear_screen()
        self.print_ascii_art()
        print(Fore.YELLOW + f"{action} DevOps Tools" + Style.RESET_ALL)

        for i, tool in enumerate(self.tools_config, 1):
            status_parts = []
            if tool['name'] in self.installed_tools:
                status_parts.append(f"{Fore.GREEN}[INSTALLED]{Style.RESET_ALL}")
            if tool['name'] in self.downloaded_tools:
                status_parts.append(f"{Fore.YELLOW}[DOWNLOADED]{Style.RESET_ALL}")
            
            status = " ".join(status_parts) if status_parts else ""
            print(f"{i}. {tool['name']} - {tool['description']} {status}")

        print("a. All")
        print("b. Back to Main Menu")
        print("q. Quit")
        print(f"{Fore.CYAN}Select a tool to {action.lower()} by number, or multiple (e.g., 1,3,4): {Style.RESET_ALL}", end="")
        if self.simulation_mode:
            print(f" {Fore.YELLOW}[SIMULATION MODE]{Style.RESET_ALL}")
        else:
            print("") # Newline if not in simulation mode

    def download_tool(self, tool):
        print(f"\n{Fore.YELLOW}Initiating download for: {tool['name']}{Style.RESET_ALL}")
        
        # Ensure tool-specific download directory exists
        tool_download_dir = os.path.join(self.downloads_dir, tool['name'])
        if not self.simulation_mode and not os.path.exists(tool_download_dir):
            os.makedirs(tool_download_dir)
            print(f"Created directory: {tool_download_dir}")

        steps = tool.get('download_steps', [])
        if not steps:
            print(f"{Fore.YELLOW}No download steps defined for {tool['name']}.{Style.RESET_ALL}")
            return True

        success = True
        for step in steps:
            cmd = step.get('command')
            if cmd:
                # Replace placeholders if any (e.g., {download_dir})
                # For now, we assume commands might need to know where to put files.
                # But the plan said commands like: "dnf install ... --downloaddir=./downloads/docker"
                # So we should ensure the command is executed relative to project root or handles paths.
                # We'll rely on the JSON providing correct relative paths or use absolute paths if needed.
                # To make it robust, we can inject the path.
                
                # Simple variable substitution
                cmd = cmd.replace("{download_dir}", tool_download_dir)
                
                if not execute_command(cmd, description=f"Downloading {tool['name']}", simulate=self.simulation_mode):
                    success = False
                    break
        
        if success:
            print(f"{Fore.GREEN}[SUCCESS] {tool['name']} downloaded successfully.{Style.RESET_ALL}")
            self.downloaded_tools.add(tool['name'])
        else:
            print(f"{Fore.RED}[FAILED] {tool['name']} download failed.{Style.RESET_ALL}")
        
        return success

    def install_tool(self, tool):
        if tool['name'] in self.installed_tools:
            print(f"\n{Fore.YELLOW}{tool['name']} is already installed. Skipping.{Style.RESET_ALL}")
            time.sleep(1)
            return True
        
        # Check if tool has been downloaded (skip in simulation mode)
        if not self.simulation_mode and tool['name'] not in self.downloaded_tools:
            print(f"\n{Fore.RED}ERROR: {tool['name']} has not been downloaded yet.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Please run download mode first to fetch this tool.{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return False

        print(f"\n{Fore.YELLOW}Initiating installation for: {tool['name']}{Style.RESET_ALL}")

        steps = tool.get('install_steps', [])
        if not steps:
             # Fallback to old schema for compatibility during migration? 
             # Or just fail. Let's try to support old schema if 'install_steps' is missing but 'installation_steps' exists.
             if 'installation_steps' in tool:
                 print(f"{Fore.YELLOW}Legacy configuration detected. Using old installation method.{Style.RESET_ALL}")
                 return self._install_tool_legacy(tool)
             
             print(f"{Fore.RED}No install steps defined for {tool['name']}.{Style.RESET_ALL}")
             return False

        tool_download_dir = os.path.join(self.downloads_dir, tool['name'])
        success = True
        for step in steps:
            cmd = step.get('command')
            if cmd:
                cmd = cmd.replace("{download_dir}", tool_download_dir)
                if not execute_command(cmd, description=f"Installing {tool['name']}", simulate=self.simulation_mode):
                    success = False
                    break

        if success:
            print(f"{Fore.GREEN}[SUCCESS] {tool['name']} installed successfully.{Style.RESET_ALL}")
            self.installed_tools.add(tool['name'])
        else:
            print(f"{Fore.RED}[FAILED] {tool['name']} installation failed.{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        return success

    def _install_tool_legacy(self, tool):
        # ... (Previous install logic moved here) ...
        steps = [
            ("pre_commands", "PRE-INSTALLATION"),
            ("main_commands", "MAIN INSTALLATION"),
            ("post_commands", "POST-INSTALLATION"),
            ("verification_commands", "VERIFICATION")
        ]

        install_successful = True
        for step_key, step_name in steps:
            commands = tool['installation_steps'].get(step_key, [])
            if commands:
                print(f"\n{Fore.YELLOW}--- {step_name} Steps for {tool['name']} ---{Style.RESET_ALL}")
                for cmd in commands:
                    if not execute_command(cmd, description=f"{tool['name']} {step_name} step", simulate=self.simulation_mode):
                        install_successful = False
                        print(f"{Fore.RED}Installation of {tool['name']} aborted due to failed command.{Style.RESET_ALL}")
                        break # Exit inner loop
                if not install_successful:
                    break # Exit outer loop

        if install_successful:
            print(f"\n{Fore.GREEN}[SUCCESS] {tool['name']} installed successfully.{Style.RESET_ALL}")
            self.installed_tools.add(tool['name'])
        else:
            print(f"\n{Fore.RED}[FAILED] {tool['name']} installation failed.{Style.RESET_ALL}")
        
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        return install_successful


    def check_system_requirements(self):
        clear_screen()
        print(Fore.YELLOW + "System Requirements Check" + Style.RESET_ALL)
        print("---------------------------")

        print(f"{'Operating System':<20} {self.system_info['os_version']:<15} {Fore.GREEN}✓{Style.RESET_ALL}")
        print(f"{'Python Version':<20} {self.system_info['python_version']:<15} {Fore.GREEN}✓{Style.RESET_ALL}")
        print(f"{'Current User':<20} {self.system_info['user']:<15} {Fore.GREEN}✓{Style.RESET_ALL}")

        # Root privileges check
        root_status = self.system_info['is_root']
        status_color = Fore.GREEN if root_status else Fore.RED
        status_char = "✓" if root_status else "✗"
        print(f"{'Root Privileges':<20} {'Enabled' if root_status else 'Disabled':<15} {status_color}{status_char}{Style.RESET_ALL}")

        # Internet connection check
        internet_status = check_internet_connection()
        status_color = Fore.GREEN if internet_status else Fore.RED
        status_char = "✓" if internet_status else "✗"
        print(f"{'Internet Connection':<20} {'Active' if internet_status else 'Inactive':<15} {status_color}{status_char}{Style.RESET_ALL}")

        # Disk space check (example: 50GB required)
        disk_ok, free_space_gb = check_disk_space(required_gb=50)
        status_color = Fore.GREEN if disk_ok else Fore.RED
        status_char = "✓" if disk_ok else "✗"
        print(f"{'Available Disk Space':<20} {f'{free_space_gb:.1f}GB':<15} {status_color}{status_char}{Style.RESET_ALL}")

        # Package manager check
        pm_status = check_package_manager()
        status_color = Fore.GREEN if pm_status else Fore.RED
        status_char = "✓" if pm_status else "✗"
        print(f"{'Package Manager':<20} {'Present' if pm_status else 'Missing':<15} {status_color}{status_char}{Style.RESET_ALL}")

        all_checks_passed = root_status and internet_status and disk_ok and pm_status
        if all_checks_passed:
            print(f"\n{Fore.GREEN}All critical system requirements are met!{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}Some critical system requirements are NOT met. Please review the above.{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def show_installed_tools(self):
        clear_screen()
        self.print_ascii_art() # Display ASCII art here too
        print(Fore.YELLOW + "Installed Tools (Session & Pre-existing)" + Style.RESET_ALL)
        print("---------------------------------------")

        if self.installed_tools:
            # Sort for consistent display
            sorted_tools = sorted(list(self.installed_tools))
            for tool in sorted_tools:
                print(f"{Fore.GREEN}✓ {tool}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}No tools installed yet in this session, and no pre-existing tools detected.{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def run(self):
        # Check for --simulate argument
        if "--simulate" in sys.argv:
            self.simulation_mode = True
            print(f"{Fore.YELLOW}Running in SIMULATION MODE. No actual commands will be executed.{Style.RESET_ALL}")
            time.sleep(2)
        
        # Initial check for root privileges (outside class as it's a hard requirement to even start)
        # Bypass check if in simulation mode
        if not self.system_info['is_root'] and not self.simulation_mode:
            print(f"{Fore.RED}This script must be run as root (use sudo). Exiting.{Style.RESET_ALL}")
            sys.exit(1)
        
        if "--download" in sys.argv:
            self.download_mode = True
        if "--install" in sys.argv:
            self.install_mode = True

        if not self.show_disclaimer():
            return

        if self.download_mode:
             self._run_tool_selection_loop(action="Download")
             return
        
        if self.install_mode:
             self._run_tool_selection_loop(action="Install")
             return

        while True:
            self.show_main_menu()
            choice = input().strip()

            if choice == '1':
                self._run_tool_selection_loop(action="Download")
            elif choice == '2':
                self._run_tool_selection_loop(action="Install")
            elif choice == '3':
                self.check_system_requirements()
            elif choice == '4':
                self.show_installed_tools()
            elif choice == '5':
                print(f"{Fore.CYAN}Exiting Relay. Goodbye!{Style.RESET_ALL}")
                break
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
                time.sleep(1)

    def _run_tool_selection_loop(self, action):
        while True:
            self.show_tool_selection_menu(action=action)
            selection = input().strip().lower()

            if selection == 'b' or selection == 'q':
                break
            
            if selection == 'a':
                # Select all tools
                indices = list(range(len(self.tools_config)))
                for index in indices:
                    tool = self.tools_config[index]
                    if action == "Download":
                        self.download_tool(tool)
                    elif action == "Install":
                        self.install_tool(tool)
                
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                continue

            try:
                if ',' in selection:
                    indices = [int(x.strip()) - 1 for x in selection.split(',')]
                else:
                    indices = [int(selection) - 1]

                valid_indices = [i for i in indices if 0 <= i < len(self.tools_config)]

                if valid_indices:
                    for index in valid_indices:
                        tool = self.tools_config[index]
                        if action == "Download":
                            self.download_tool(tool)
                        elif action == "Install":
                            self.install_tool(tool)
                    
                    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Invalid selection. Please try again.{Style.RESET_ALL}")
                    time.sleep(1)
            except ValueError:
                print(f"{Fore.RED}Invalid input. Please enter numbers separated by commas, 'a' for all, 'b' to go back, or 'q' to quit.{Style.RESET_ALL}")
                time.sleep(1)

if __name__ == "__main__":
    cli = ToolboxCLI()
    cli.run()
