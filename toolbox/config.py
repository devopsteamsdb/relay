import json
import os
from typing import List, Dict, Any
from colorama import Fore, Style

def load_tool_configurations(tools_dir: str = 'tools') -> List[Dict[str, Any]]:
    """
    Loads tool configurations from JSON files in the specified directory.
    """
    tools_config = []
    # Get the directory of the current script (toolbox/config.py)
    # Then navigate up to the project root and into the 'tools' directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '..') # Go up one level from 'toolbox' to 'devops-toolbox'
    full_tools_path = os.path.join(project_root, tools_dir)

    if not os.path.isdir(full_tools_path):
        print(f"{Fore.RED}Error: Tools configuration directory not found at {full_tools_path}{Style.RESET_ALL}")
        return []

    for filename in os.listdir(full_tools_path):
        if filename.endswith('.json'):
            filepath = os.path.join(full_tools_path, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    tool_data = json.load(f)
                    tools_config.append(tool_data)
            except json.JSONDecodeError:
                print(f"{Fore.RED}Error: Invalid JSON in {filename}. Skipping.{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Error loading {filename}: {e}. Skipping.{Style.RESET_ALL}")
    
    # Sort tools by name for consistent menu display
    tools_config.sort(key=lambda x: x.get('name', ''))
    return tools_config