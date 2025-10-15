import os
import sys
import platform
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path

def get_platform():
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    elif system == "darwin":
        return "macos"
    return "unknown"

def check_nodejs():
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js found: {version}")
            return True
    except FileNotFoundError:
        pass
    print("❌ Node.js not found")
    return False

def download_cloudflared():
    system = get_platform()
    base_dir = Path(__file__).parent
    bin_dir = base_dir / "bin"
    bin_dir.mkdir(exist_ok=True)
    
    urls = {
        "windows": "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe",
        "linux": "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64",
        "macos": "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64"
    }
    
    if system not in urls:
        print(f"❌ Unsupported platform: {system}")
        return None
    
    cloudflared_name = "cloudflared.exe" if system == "windows" else "cloudflared"
    cloudflared_path = bin_dir / cloudflared_name
    
    if cloudflared_path.exists():
        print(f"✅ cloudflared already exists: {cloudflared_path}")
        return str(cloudflared_path)
    
    print(f"📥 Downloading cloudflared for {system}...")
    try:
        urllib.request.urlretrieve(urls[system], cloudflared_path)
        
        if system != "windows":
            os.chmod(cloudflared_path, 0o755)
        
        print(f"✅ cloudflared downloaded: {cloudflared_path}")
        return str(cloudflared_path)
    except Exception as e:
        print(f"❌ Failed to download cloudflared: {e}")
        return None

def download_nodejs_portable():
    system = get_platform()
    base_dir = Path(__file__).parent
    node_dir = base_dir / "nodejs_portable"
    
    if (node_dir / ("node.exe" if system == "windows" else "bin/node")).exists():
        print(f"✅ Portable Node.js already exists: {node_dir}")
        return str(node_dir)
    
    print(f"📥 Downloading portable Node.js for {system}...")
    
    urls = {
        "windows": "https://nodejs.org/dist/v20.11.0/node-v20.11.0-win-x64.zip",
        "linux": "https://nodejs.org/dist/v20.11.0/node-v20.11.0-linux-x64.tar.xz",
        "macos": "https://nodejs.org/dist/v20.11.0/node-v20.11.0-darwin-x64.tar.gz"
    }
    
    if system not in urls:
        print(f"❌ Unsupported platform: {system}")
        return None
    
    try:
        temp_file = base_dir / f"nodejs_temp.{'zip' if system == 'windows' else 'tar.xz'}"
        
        print("⏳ Downloading... (this may take a while)")
        urllib.request.urlretrieve(urls[system], temp_file)
        
        print("📦 Extracting...")
        if system == "windows":
            with zipfile.ZipFile(temp_file, 'r') as zip_ref:
                zip_ref.extractall(base_dir)
            extracted_dir = base_dir / f"node-v20.11.0-win-x64"
        else:
            import tarfile
            with tarfile.open(temp_file) as tar:
                tar.extractall(base_dir)
            extracted_dir = base_dir / f"node-v20.11.0-{'darwin' if system == 'macos' else 'linux'}-x64"
        
        extracted_dir.rename(node_dir)
        temp_file.unlink()
        
        print(f"✅ Portable Node.js installed: {node_dir}")
        return str(node_dir)
    except Exception as e:
        print(f"❌ Failed to download Node.js: {e}")
        if temp_file.exists():
            temp_file.unlink()
        return None

def setup_all():
    print("=" * 60)
    print("Setting up dependencies...")
    print("=" * 60)
    
    # Check Node.js
    has_nodejs = check_nodejs()
    node_path = None
    
    if not has_nodejs:
        print("\n⚠️  Node.js not found. Downloading portable version...")
        node_path = download_nodejs_portable()
    
    # Download cloudflared
    print()
    cloudflared_path = download_cloudflared()
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)
    
    return {
        "nodejs_path": node_path,
        "cloudflared_path": cloudflared_path,
        "has_system_nodejs": has_nodejs
    }

if __name__ == "__main__":
    setup_all()
