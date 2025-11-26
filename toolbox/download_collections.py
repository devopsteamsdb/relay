#!/usr/bin/env python3
import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from tqdm import tqdm

def download_file(url, dest_path):
    try:
        print(f"Downloading {url} to {dest_path}...")
        with urllib.request.urlopen(url) as response, open(dest_path, 'wb') as out_file:
            total_size = int(response.info().get('Content-Length', 0))
            block_size = 1024 # 1 Kibibyte
            
            with tqdm(total=total_size, unit='iB', unit_scale=True, desc=os.path.basename(dest_path)) as t:
                while True:
                    data = response.read(block_size)
                    if not data:
                        break
                    t.update(len(data))
                    out_file.write(data)
                    
        print(f"Successfully downloaded to {dest_path}")
        return True
    except urllib.error.URLError as e:
        print(f"Error downloading {url}: {e}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def get_collection_info(namespace, name):
    # Try v3 API first as it's the current standard for Galaxy NG
    api_url_v3 = f"https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/index/{namespace}/{name}/"
    
    # Fallback to v2 if v3 fails (legacy Galaxy)
    api_url_v2 = f"https://galaxy.ansible.com/api/v2/collections/{namespace}/{name}/"
    
    for api_url in [api_url_v3, api_url_v2]:
        try:
            # Create a request with a User-Agent to avoid 403s or blocks
            req = urllib.request.Request(
                api_url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            )
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                return data
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue # Try next API version
            print(f"Error fetching info for {namespace}.{name} from {api_url}: {e}")
        except Exception as e:
            print(f"Error: {e}")
            
    return None

def main():
    parser = argparse.ArgumentParser(description="Download Ansible collections from Galaxy API")
    parser.add_argument("--output-dir", required=True, help="Directory to save downloaded collections")
    parser.add_argument("collections", nargs="+", help="List of collections to download (namespace.name)")
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    success_count = 0
    fail_count = 0

    for collection in args.collections:
        if "." not in collection:
            print(f"Invalid collection name: {collection}. Must be namespace.name")
            fail_count += 1
            continue

        namespace, name = collection.split(".", 1)
        print(f"\nProcessing {collection}...")
        
        info = get_collection_info(namespace, name)
        if not info:
            fail_count += 1
            continue
            
        # DEBUG: Print keys to understand structure
        # print(f"DEBUG: Keys in info: {list(info.keys())}")
        
        download_url = None
        
        # Strategy: Use 'versions_url' to list versions, find the highest/latest, and get its download link
        versions_url = info.get("versions_url")
        highest_version = info.get("highest_version", {}).get("version")
        
        if versions_url and highest_version:
            print(f"Found highest version: {highest_version}. Fetching version details...")
            # The versions_url usually lists versions. We might need to append the version number or filter.
            # Let's try constructing the version-specific URL directly if we know the pattern
            # Pattern v3: .../versions/{version}/
            # Pattern v2: .../versions/{version}/
            
            # Try to fetch the specific version directly using the versions_url base
            # If versions_url is .../versions/, we append {version}/
            
            # Handle relative URLs
            if versions_url.startswith("/"):
                versions_url = f"https://galaxy.ansible.com{versions_url}"
            
            target_version_url = f"{versions_url.rstrip('/')}/{highest_version}/"
            
            try:
                req = urllib.request.Request(
                    target_version_url, 
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                )
                with urllib.request.urlopen(req) as response:
                    version_data = json.loads(response.read().decode())
                    download_url = version_data.get("download_url")
            except Exception as e:
                print(f"Error fetching version details from {target_version_url}: {e}")
                # Fallback: List all versions and find the match
                try:
                    req = urllib.request.Request(
                        versions_url, 
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                    )
                    with urllib.request.urlopen(req) as response:
                        versions_data = json.loads(response.read().decode())
                        # versions_data might be a list or a paginated dict
                        results = versions_data.get("results", []) if isinstance(versions_data, dict) else versions_data
                        for v in results:
                            if v.get("version") == highest_version:
                                download_url = v.get("download_url")
                                break
                except Exception as e2:
                    print(f"Error listing versions: {e2}")

        if not download_url:
             print(f"Could not find download URL for {collection}")
             fail_count += 1
             continue

        filename = os.path.basename(download_url)
        dest_path = os.path.join(args.output_dir, filename)
        
        if download_file(download_url, dest_path):
            success_count += 1
        else:
            fail_count += 1

    print(f"\nDownload Summary: {success_count} successful, {fail_count} failed.")
    if fail_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
