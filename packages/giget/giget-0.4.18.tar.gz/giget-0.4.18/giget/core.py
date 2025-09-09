# core.py
import requests
import os
from datetime import datetime

def display_rate_limit_status(response, prefix=""):
    """Display GitHub API rate limit status from response headers."""
    headers = response.headers
    
    # Check if rate limit headers exist
    if 'X-RateLimit-Limit' not in headers:
        print(f"{prefix}⚠️  No rate limit information available")
        return
    
    try:
        limit = int(headers.get('X-RateLimit-Limit', 0))
        remaining = int(headers.get('X-RateLimit-Remaining', 0))
        used = int(headers.get('X-RateLimit-Used', 0))
        reset_timestamp = int(headers.get('X-RateLimit-Reset', 0))
        
        # Calculate percentages
        usage_percent = (used / limit * 100) if limit > 0 else 0
        remaining_percent = (remaining / limit * 100) if limit > 0 else 0
        
        # Convert reset time
        reset_time = datetime.fromtimestamp(reset_timestamp)
        time_until_reset = reset_time - datetime.now()
        minutes_until_reset = max(0, int(time_until_reset.total_seconds() / 60))
        
        # Determine status emoji
        if remaining > limit * 0.5:
            status_emoji = "✅"
            status_text = "GOOD"
        elif remaining > limit * 0.1:
            status_emoji = "⚠️ "
            status_text = "WARNING"
        else:
            status_emoji = "❌"
            status_text = "CRITICAL"
        
        # Display formatted status
        print(f"\n{prefix}📊 GitHub API Rate Limit Status:")
        print(f"{prefix}{'='*45}")
        print(f"{prefix}{status_emoji} Status: {status_text}")
        print(f"{prefix}📈 Usage: {used:,}/{limit:,} requests ({usage_percent:.1f}%)")
        print(f"{prefix}📉 Remaining: {remaining:,}/{limit:,} requests ({remaining_percent:.1f}%)")
        print(f"{prefix}🕒 Resets in: {minutes_until_reset} minutes ({reset_time.strftime('%H:%M:%S')})")
        
        # Additional warnings
        if remaining <= 10:
            print(f"{prefix}🚨 CRITICAL: Only {remaining} requests left!")
        elif remaining <= 100:
            print(f"{prefix}⚠️  LOW: Only {remaining} requests remaining")
        
        print(f"{prefix}{'='*45}\n")
        
        return {
            'remaining': remaining,
            'limit': limit,
            'used': used,
            'reset_time': reset_time,
            'minutes_until_reset': minutes_until_reset,
            'status': status_text.lower()
        }
        
    except (ValueError, KeyError) as e:
        print(f"{prefix}❌ Error parsing rate limit headers: {e}")
        return None

def check_rate_limit_safety(response, min_requests=5):
    """Check if we have enough rate limit for continued operations."""
    headers = response.headers
    
    if 'X-RateLimit-Remaining' not in headers:
        return True  # Can't check, assume it's okay
    
    try:
        remaining = int(headers['X-RateLimit-Remaining'])
        
        if remaining < min_requests:
            reset_timestamp = int(headers.get('X-RateLimit-Reset', 0))
            reset_time = datetime.fromtimestamp(reset_timestamp)
            time_until_reset = reset_time - datetime.now()
            minutes = max(0, int(time_until_reset.total_seconds() / 60))
            
            print(f"🚨 Rate limit too low!")
            print(f"   Remaining: {remaining} requests")
            print(f"   Resets in: {minutes} minutes")
            
            return False
        
        return True
    except (ValueError, KeyError):
        return True  # Can't parse, assume it's okay

def download_single_file(owner, repo, file_path, branch, save_dir=".", force=False, rename=False):
    """Download a single file from GitHub."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"
    
    print(f"🔍 Fetching file info: {url}")
    response = requests.get(url)
    
    # Display rate limit status immediately after request
    rate_info = display_rate_limit_status(response, "   ")
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch file: {response.status_code} - {response.text}")
    
    file_info = response.json()
    
    if file_info.get("type") != "file":
        raise Exception(f"The specified path is not a file: {file_path}")
    
    # Determine save path
    filename = os.path.basename(file_path)
    save_path = os.path.join(save_dir, filename)
    
    # Handle existing file
    if os.path.exists(save_path):
        if force:
            print(f"⚠️ Overwriting {save_path}")
        elif rename:
            base, ext = os.path.splitext(save_path)
            counter = 1
            new_path = f"{base}_{counter}{ext}"
            while os.path.exists(new_path):
                counter += 1
                new_path = f"{base}_{counter}{ext}"
            save_path = new_path
            print(f"📄 Renamed and saving as {save_path}")
        else:
            raise FileExistsError(
                f"❌ File already exists: {save_path}\n"
                f"Use --force to overwrite or --rename to save with a new name."
            )
    
    # Download the file (this doesn't count against API rate limit)
    print(f"⬇️  Downloading {file_info['download_url']}")
    file_data = requests.get(file_info["download_url"]).content
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
    
    with open(save_path, "wb") as f:
        f.write(file_data)
    
    print(f"✅ File saved: {save_path}")

def download_github_dir(owner, repo, path, branch="main", save_dir=".", flat=False, force=False, rename=False, show_rate_limit=True):
    """Download a GitHub folder recursively with overwrite/rename options."""
    
    # Handle empty path (root directory)
    if not path:
        url = f"https://api.github.com/repos/{owner}/{repo}/contents?ref={branch}"
    else:
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    
    print(f"🔍 Fetching directory: {url}")
    response = requests.get(url)
    
    # Display rate limit status
    if show_rate_limit:
        rate_info = display_rate_limit_status(response, "   ")
        
        # Check if we should continue
        if not check_rate_limit_safety(response, min_requests=5):
            user_input = input("Continue anyway? [y/N]: ")
            if user_input.lower() not in ['y', 'yes']:
                print("❌ Operation cancelled due to low rate limit")
                return
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch directory: {response.status_code} - {response.text}")
    
    response_data = response.json()
    
    if isinstance(response_data, dict) and response_data.get("message"):
        raise Exception(f"GitHub API error: {response_data['message']}")
    
    if not isinstance(response_data, list):
        raise Exception(f"Expected directory contents, got: {type(response_data)}")

    total_items = len(response_data)
    processed_items = 0

    for item in response_data:
        processed_items += 1
        print(f"\n📁 Processing {processed_items}/{total_items}: {item['name']}")
        
        if item["type"] == "file":
            if flat:
                item_path = os.path.join(save_dir, os.path.basename(item["path"]))
            else:
                # For non-flat mode, preserve the relative structure from the requested path
                if path:
                    # Remove the requested path prefix to get relative path
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
                    print(f"   ⚠️ Overwriting {item_path}")
                elif rename:
                    base, ext = os.path.splitext(item_path)
                    counter = 1
                    new_path = f"{base}_{counter}{ext}"
                    while os.path.exists(new_path):
                        counter += 1
                        new_path = f"{base}_{counter}{ext}"
                    item_path = new_path
                    print(f"   📄 Renamed and saving as {item_path}")
                else:
                    raise FileExistsError(
                        f"❌ File already exists: {item_path}\n"
                        f"Use --force to overwrite or --rename to save with a new name."
                    )

            print(f"   ⬇️  Downloading {item['download_url']}")
            file_data = requests.get(item["download_url"]).content
            with open(item_path, "wb") as f:
                f.write(file_data)
            print(f"   ✅ Saved: {item_path}")

        elif item["type"] == "dir":
            if flat:
                # Skip making directories in flat mode, just recurse inside
                download_github_dir(owner, repo, item["path"], branch, save_dir, flat, force, rename, show_rate_limit=False)  # Don't show rate limit in recursive calls
            else:
                # Calculate the relative directory path
                if path:
                    relative_path = item["path"]
                    if relative_path.startswith(path + "/"):
                        relative_path = relative_path[len(path) + 1:]
                    dir_path = os.path.join(save_dir, relative_path)
                else:
                    dir_path = os.path.join(save_dir, item["path"])

                # Handle existing directory
                if os.path.exists(dir_path):
                    if force:
                        print(f"   ⚠️ Directory exists: {dir_path}")
                    elif rename:
                        counter = 1
                        new_path = f"{dir_path}_{counter}"
                        while os.path.exists(new_path):
                            counter += 1
                            new_path = f"{dir_path}_{counter}"
                        dir_path = new_path
                        print(f"   📂 Renamed directory to {dir_path}")
                    else:
                        print(f"   📂 Directory exists: {dir_path}")

                os.makedirs(dir_path, exist_ok=True)
                print(f"   📁 Created directory: {dir_path}")

                # Recurse into subdirectory
                download_github_dir(owner, repo, item["path"], branch, save_dir, flat, force, rename, show_rate_limit=False)  # Don't show rate limit in recursive calls
    
    # Show final rate limit status for main call
    if show_rate_limit:
        print(f"\n🎉 Completed processing {total_items} items")
        # Make a lightweight request to get current rate limit status
        try:
            final_response = requests.get(f"https://api.github.com/repos/{owner}/{repo}")
            print("\n📊 Final Rate Limit Status:")
            display_rate_limit_status(final_response, "   ")
        except:
            print("   ⚠️ Could not fetch final rate limit status")