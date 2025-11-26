#!/usr/bin/env python3
import os
import sys
import json
import argparse
import urllib.request
import urllib.error

def download_file(url, dest_path):
    try:
        print(f"Downloading {url} to {dest_path}...")
        with urllib.request.urlopen(url) as response, open(dest_path, 'wb') as out_file:
            out_file.write(response.read())
        print(f"Successfully downloaded to {dest_path}")
        return True
    except urllib.error.URLError as e:
        print(f"Error downloading {url}: {e}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def get_collection_info(namespace, name):
    api_url = f"https://galaxy.ansible.com/api/v2/collections/{namespace}/{name}/"
    try:
        with urllib.request.urlopen(api_url) as response:
            data = json.loads(response.read().decode())
            return data
    except urllib.error.HTTPError as e:
        print(f"Error fetching info for {namespace}.{name}: {e}")
        return None
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

        latest_version_url = info.get("latest_version", {}).get("href")
        if not latest_version_url:
             # Fallback to finding latest version manually if structure differs
             print("Could not find latest version URL.")
             fail_count += 1
             continue
        
        # The 'latest_version' href usually points to the version details which has the download URL
        # But top level info often has 'download_url' for the latest version directly or inside 'latest_version' object
        # Let's check 'latest_version' object structure from the first response
        download_url = info.get("latest_version", {}).get("download_url")
        
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
