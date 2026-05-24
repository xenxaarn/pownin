import os
import sys
import subprocess
import shutil

def get_linux_package_manager():
    """Detects the available package manager on Linux."""
    if shutil.which("apt-get"):
        return "apt"
    elif shutil.which("pacman"):
        return "pacman"
    elif shutil.which("dnf"):
        return "dnf"
    return None

def install_system_deps():
    """Detects OS and installs required system tools (portaudio, swig, build tools)."""
    print(f"📦 Detecting OS and system dependencies... (Platform: {sys.platform})")
    
    # 1. WINDOWS SETUP
    if sys.platform.startswith("win32"):
        print("🪟 Windows detected. System packages must be installed manually or via winget/choco.")
        print("💡 Note: If PyAudio or PocketSphinx fail to install later, you may need Visual Studio Build Tools.")
        return

    # 2. MACOS SETUP
    elif sys.platform.startswith("darwin"):
        print("🍎 macOS detected. Checking for Homebrew...")
        if not shutil.which("brew"):
            print("❌ Homebrew is required on macOS to install portaudio and swig. Please install it first.")
            sys.exit(1)
        
        print("Installing portaudio and swig via Homebrew...")
        try:
            subprocess.check_call(["brew", "install", "portaudio", "swig"])
        except subprocess.CalledProcessError:
            print("😓 Failed to install macOS dependencies via Homebrew.")
            sys.exit(1)

    # 3. LINUX SETUP
    elif sys.platform.startswith("linux"):
        pkg_manager = get_linux_package_manager()
        
        if pkg_manager == "apt":
            print("🐧 Ubuntu/Debian detected. Installing via apt...")
            cmd = "sudo apt-get update && sudo apt-get install -y build-essential portaudio19-dev swig python3-dev python3-venv"
        elif pkg_manager == "pacman":
            print("🐧 Arch Linux detected. Installing via pacman...")
            cmd = "sudo pacman -S --noconfirm --needed base-devel portaudio swig"
        elif pkg_manager == "dnf":
            print("🐧 Fedora/RHEL detected. Installing via dnf...")
            cmd = "sudo dnf groupinstall -y 'Development Tools' && sudo dnf install -y portaudio-devel swig python3-devel"
        else:
            print("⚠️ Unknown Linux distribution. Skipping system package installation.")
            print("👉 Please manually install: portaudio development headers, swig, and C/C++ build tools.")
            return

        try:
            subprocess.check_call(cmd, shell=True)
        except subprocess.CalledProcessError:
            print("😓 System package installation failed.")
            sys.exit(1)

def main():
    # Step 1: Install system packages first
    install_system_deps()

    # Determine paths based on OS structure
    if sys.platform.startswith("win32"):
        pip_path = os.path.join("venv", "Scripts", "pip.exe")
        run_msg = "venv\\Scripts\\python server.py"
    else:
        pip_path = os.path.join("venv", "bin", "pip")
        run_msg = "./venv/bin/python server.py"

    # Step 2: Aggressively purge any pre-existing venv folder to resolve broken symlinks
    if os.path.exists("venv") or os.path.islink("venv"):
        print("🧹 Cleaning up the existing venv environment folder to ensure a fresh build...")
        try:
            if os.path.islink("venv"):
                os.unlink("venv")
            else:
                shutil.rmtree("venv")
        except Exception as e:
            print(f"🔥 Warning during environment cleanup: {e}")

    # create a environment with fixed python3-venv installation
    print("🌐 Creating a fresh local python isolation environment (venv)...")
    try:
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
    except subprocess.CalledProcessError as e:
        print(f"😓 Failed to create virtual environment: {e}")
        sys.exit(1)

    # Step 3: Install Python dependencies
    print("📥 Installing python dependencies inside the isolated environment...")
    dependencies = ["websockets", "speechrecognition", "pyaudio", "pocketsphinx", "edge-tts", "aiohttp"]

    try:
        subprocess.check_call([pip_path, "install", "--upgrade", "pip", "setuptools", "wheel"])
        subprocess.check_call([pip_path, "install", *dependencies])
        print(f"\n😁 Setup complete! Run your project using: {run_msg}")
    except subprocess.CalledProcessError as e:
        print(f"\n😓 Python package installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()