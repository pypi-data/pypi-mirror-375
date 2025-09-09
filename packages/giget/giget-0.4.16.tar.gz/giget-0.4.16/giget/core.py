# core.py
import requests
import os
from datetime import datetime
import sys

class UIFormatter:
    """Handles clean UI formatting and display."""
    
    @staticmethod
    def print_header(title, width=60):
        """Print a clean header."""
        print(f"\n┌{'─' * (width-2)}┐")
        print(f"│ {title:<{width-4}} │")
        print(f"└{'─' * (width-2)}┘")
    
    @staticmethod
    def print_section(title, width=50):
        """Print a section separator."""
        print(f"\n{'─' * width}")
        print(f"  {title}")
        print(f"{'─' * width}")
    
    @staticmethod
    def print_info(label, value, indent=0):
        """Print formatted info line."""
        spaces = "  " * indent
        print(f"{spaces}{label:<20} {value}")
    
    @staticmethod
    def print_status(message, status="info", indent=0):
        """Print status message with icon."""
        icons = {
            "success": "✅",
            "warning": "⚠️ ",
            "error": "❌",
            "info": "ℹ️ ",
            "download": "⬇️ ",
            "folder": "📁",
            "file": "📄",
            "progress": "🔄"
        }
        spaces = "  " * indent
        icon = icons.get(status, "•")
        print(f"{spaces}{icon} {message}")
    
    @staticmethod
    def print_progress_bar(current, total, width=30):
        """Print a simple progress bar."""
        if total == 0:
            return ""
        
        percent = (current / total) * 100
        filled = int(width * current / total)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {percent:.1f}% ({current}/{total})"

def display_parsed_url(parsed_info):
    """Display parsed URL information cleanly."""
    UIFormatter.print_header("📋 Repository Information")
    UIFormatter.print_info("Owner:", parsed_info["owner"])
    UIFormatter.print_info("Repository:", parsed_info["repo"])
    UIFormatter.print_info("Branch:", parsed_info["branch"])
    UIFormatter.print_info("Path:", parsed_info["path"] or "(root)")
    UIFormatter.print_info("Type:", parsed_info["url_type"])

def display_rate_limit_compact(response):
    """Display rate limit status in a compact, clean format."""
    headers = response.headers
    
    if 'X-RateLimit-Limit' not in headers:
        return
    
    try:
        limit = int(headers.get('X-RateLimit-Limit', 0))
        remaining = int(headers.get('X-RateLimit-Remaining', 0))
        reset_timestamp = int(headers.get('X-RateLimit-Reset', 0))
        
        # Calculate time until reset
        reset_time = datetime.fromtimestamp(reset_timestamp)
        time_until_reset = reset_time - datetime.now()
        minutes = max(0, int(time_until_reset.total_seconds() / 60))
        
        # Determine status
        percent_remaining = (remaining / limit * 100) if limit > 0 else 0
        
        if remaining > limit * 0.5:
            status_icon = "✅"
        elif remaining > limit * 0.2:
            status_icon = "⚠️ "
        else:
            status_icon = "❌"
        
        # Compact single line display
        print(f"{status_icon} Rate Limit: {remaining}/{limit} remaining ({percent_remaining:.0f}%) • Resets in {minutes}m")
        
        # Show warning for low limits
        if remaining <= 10:
            UIFormatter.print_status("CRITICAL: Very low rate limit!", "error")
        
    except (ValueError, KeyError):
        UIFormatter.print_status("Could not parse rate limit info", "warning")

def display_operation_start(operation_type, path):
    """Display operation start message."""
    UIFormatter.print_section(f"🚀 Starting {operation_type}")
    UIFormatter.print_info("Target:", path or "(entire repository)")

def display_download_progress(current, total, current_item):
    """Display download progress in a clean format."""
    progress_bar = UIFormatter.print_progress_bar(current, total)
    print(f"\r🔄 {progress_bar} • {current_item}", end="", flush=True)

def download_single_file(owner, repo, file_path, branch, save_dir=".", force=False, rename=False):
    """Download a single file from GitHub with clean UI."""
    
    display_operation_start("File Download", file_path)
    
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"
    
    UIFormatter.print_status(f"Fetching file info...", "info")
    response = requests.get(url)
    
    # Show compact rate limit
    display_rate_limit_compact(response)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch file: {response.status_code}")
    
    file_info = response.json()
    
    if file_info.get("type") != "file":
        raise Exception(f"Path is not a file: {file_path}")
    
    # Determine save path
    filename = os.path.basename(file_path)
    save_path = os.path.join(save_dir, filename)
    
    # Handle existing file
    if os.path.exists(save_path):
        if force:
            UIFormatter.print_status(f"Overwriting {filename}", "warning")
        elif rename:
            base, ext = os.path.splitext(save_path)
            counter = 1
            new_path = f"{base}_{counter}{ext}"
            while os.path.exists(new_path):
                counter += 1
                new_path = f"{base}_{counter}{ext}"
            save_path = new_path
            filename = os.path.basename(save_path)
            UIFormatter.print_status(f"Renamed to {filename}", "info")
        else:
            raise FileExistsError(f"File exists: {save_path}\nUse --force or --rename")
    
    # Download the file
    UIFormatter.print_status(f"Downloading {filename}...", "download")
    file_data = requests.get(file_info["download_url"]).content
    
    # Create directory if needed
    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
    
    with open(save_path, "wb") as f:
        f.write(file_data)
    
    UIFormatter.print_status(f"Saved: {filename}", "success")

def download_github_dir(owner, repo, path, branch="main", save_dir=".", flat=False, force=False, rename=False, _is_recursive=False):
    """Download a GitHub directory with clean UI."""
    
    if not _is_recursive:
        display_operation_start("Directory Download", path)
    
    # Build URL
    if not path:
        url = f"https://api.github.com/repos/{owner}/{repo}/contents?ref={branch}"
    else:
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    
    if not _is_recursive:
        UIFormatter.print_status("Scanning directory structure...", "info")
    
    response = requests.get(url)
    
    # Show rate limit only for main call
    if not _is_recursive:
        display_rate_limit_compact(response)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch directory: {response.status_code}")
    
    response_data = response.json()
    
    if isinstance(response_data, dict) and response_data.get("message"):
        raise Exception(f"GitHub API error: {response_data['message']}")
    
    if not isinstance(response_data, list):
        raise Exception(f"Expected directory contents, got: {type(response_data)}")

    # Process items
    total_items = len(response_data)
    files_downloaded = 0
    dirs_processed = 0
    
    if not _is_recursive and total_items > 0:
        print(f"\n📊 Found {total_items} items to process")
    
    for i, item in enumerate(response_data, 1):
        item_name = item['name']
        
        if item["type"] == "file":
            # Show progress for files
            if not _is_recursive:
                display_download_progress(i, total_items, f"Downloading {item_name}")
            
            # Determine save path
            if flat:
                item_path = os.path.join(save_dir, os.path.basename(item["path"]))
            else:
                if path:
                    relative_path = item["path"]
                    if relative_path.startswith(path + "/"):
                        relative_path = relative_path[len(path) + 1:]
                    elif relative_path == path:
                        relative_path = os.path.basename(path)
                    item_path = os.path.join(save_dir, relative_path)
                else:
                    item_path = os.path.join(save_dir, item["path"])
                
                # Create parent directories
                parent_dir = os.path.dirname(item_path)
                if parent_dir:
                    os.makedirs(parent_dir, exist_ok=True)

            # Handle existing file
            if os.path.exists(item_path):
                if force:
                    pass  # Will overwrite
                elif rename:
                    base, ext = os.path.splitext(item_path)
                    counter = 1
                    new_path = f"{base}_{counter}{ext}"
                    while os.path.exists(new_path):
                        counter += 1
                        new_path = f"{base}_{counter}{ext}"
                    item_path = new_path
                else:
                    if not _is_recursive:
                        print()  # New line after progress bar
                    UIFormatter.print_status(f"Skipped {item_name} (already exists)", "warning")
                    continue

            # Download file
            file_data = requests.get(item["download_url"]).content
            with open(item_path, "wb") as f:
                f.write(file_data)
            
            files_downloaded += 1

        elif item["type"] == "dir":
            if not _is_recursive:
                print()  # New line after progress bar
                UIFormatter.print_status(f"Entering directory: {item_name}", "folder")
            
            if flat:
                # Recurse without creating directory structure
                download_github_dir(owner, repo, item["path"], branch, save_dir, flat, force, rename, _is_recursive=True)
            else:
                # Calculate directory path
                if path:
                    relative_path = item["path"]
                    if relative_path.startswith(path + "/"):
                        relative_path = relative_path[len(path) + 1:]
                    dir_path = os.path.join(save_dir, relative_path)
                else:
                    dir_path = os.path.join(save_dir, item["path"])

                # Handle existing directory
                if os.path.exists(dir_path):
                    if rename:
                        counter = 1
                        new_path = f"{dir_path}_{counter}"
                        while os.path.exists(new_path):
                            counter += 1
                            new_path = f"{base}_{counter}"
                        dir_path = new_path

                os.makedirs(dir_path, exist_ok=True)

                # Recurse into subdirectory
                download_github_dir(owner, repo, item["path"], branch, save_dir, flat, force, rename, _is_recursive=True)
            
            dirs_processed += 1
    
    # Summary for main call
    if not _is_recursive:
        print()  # New line after progress
        UIFormatter.print_section("📊 Download Summary")
        UIFormatter.print_info("Files downloaded:", files_downloaded)
        UIFormatter.print_info("Directories processed:", dirs_processed)
        UIFormatter.print_status("Download completed successfully!", "success")
        
        # Final rate limit check
        try:
            final_response = requests.get(f"https://api.github.com/repos/{owner}/{repo}")
            print()
            display_rate_limit_compact(final_response)
        except:
            pass  # Don't fail if we can't get final rate limit