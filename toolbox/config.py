import json
import os
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
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
                    tool_data = _apply_latest_version(tool_data)
                    tools_config.append(tool_data)
            except json.JSONDecodeError:
                print(f"{Fore.RED}Error: Invalid JSON in {filename}. Skipping.{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Error loading {filename}: {e}. Skipping.{Style.RESET_ALL}")
    
    # Sort tools by name for consistent menu display
    tools_config.sort(key=lambda x: x.get('name', ''))
    return tools_config


def _apply_latest_version(tool: Dict[str, Any]) -> Dict[str, Any]:
    """
    If the tool declares version: \"{{latest_version}}\" and provides a version_source,
    resolve the latest version from the upstream source.
    """
    version = tool.get("version")
    version_source = tool.get("version_source")

    if isinstance(version, str) and version.strip() == "{{latest_version}}" and version_source:
        latest = _fetch_latest_version(version_source)
        if latest:
            tool["version"] = latest
        else:
            print(f"{Fore.YELLOW}Warning: Could not resolve latest version for {tool.get('name', 'Unknown tool')}. Using placeholder.{Style.RESET_ALL}")

    return tool


def _fetch_latest_version(source: Dict[str, Any]) -> Optional[str]:
    """
    Fetch the latest version string based on the specified source configuration.
    Supported sources:
      - type: github_release, repo: \"org/name\"
      - type: hashicorp_checkpoint, product: \"terraform\" (etc.)
    """
    source_type = source.get("type")

    try:
        if source_type == "github_release":
            repo = source.get("repo")
            if not repo:
                return None
            url = f"https://api.github.com/repos/{repo}/releases/latest"
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                tag = data.get("tag_name") or data.get("name")
                return tag.lstrip("v") if tag else None

        if source_type == "hashicorp_checkpoint":
            product = source.get("product")
            if not product:
                return None
            url = f"https://checkpoint-api.hashicorp.com/v1/check/{product}"
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("current_version")
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        print(f"{Fore.YELLOW}Version lookup failed ({source_type}): {e}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.YELLOW}Unexpected error during version lookup: {e}{Style.RESET_ALL}")

    return None
