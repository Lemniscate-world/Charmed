"""
verify_build_env.py - Build environment verification script

This script checks that all prerequisites for building Alarmify are installed
and properly configured.

Usage:
    python verify_build_env.py
"""

import sys
import subprocess
import shutil
from pathlib import Path
import platform


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")


def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_info(text):
    """Print info message."""
    print(f"  {text}")


def check_python_version():
    """Check Python version."""
    print("Checking Python version...")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major == 3 and version.minor >= 10:
        print_success(f"Python {version_str} (OK)")
        return True
    else:
        print_error(f"Python {version_str} (Requires Python 3.10+)")
        return False


def check_os():
    """Check operating system."""
    print("\nChecking operating system...")
    
    os_name = platform.system()
    os_version = platform.version()
    
    if os_name == "Windows":
        print_success(f"Windows {os_version} (OK)")
        return True
    else:
        print_warning(f"{os_name} (Build system designed for Windows)")
        return False


def check_python_package(package_name, import_name=None):
    """Check if a Python package is installed."""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print_success(f"{package_name} is installed")
        return True
    except ImportError:
        print_error(f"{package_name} is not installed")
        print_info(f"Install with: pip install {package_name}")
        return False


def check_python_packages():
    """Check required Python packages."""
    print("\nChecking Python packages...")
    
    packages = [
        ("PyQt5", "PyQt5"),
        ("spotipy", "spotipy"),
        ("schedule", "schedule"),
        ("python-dotenv", "dotenv"),
        ("pyinstaller", "PyInstaller"),
        ("pytest", "pytest"),
    ]
    
    all_installed = True
    for package_name, import_name in packages:
        if not check_python_package(package_name, import_name):
            all_installed = False
    
    return all_installed


def check_command(command_name, command_args=None):
    """Check if a command is available."""
    if command_args is None:
        command_args = ["--version"]
    
    try:
        result = subprocess.run(
            [command_name] + command_args,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_git():
    """Check if Git is installed."""
    print("\nChecking Git...")
    
    if check_command("git"):
        result = subprocess.run(["git", "--version"], capture_output=True, text=True)
        version = result.stdout.strip()
        print_success(f"{version} (OK)")
        return True
    else:
        print_warning("Git not found (optional but recommended)")
        print_info("Download from: https://git-scm.com/")
        return False


def check_inno_setup():
    """Check if Inno Setup is installed."""
    print("\nChecking Inno Setup...")
    
    # Common installation paths
    common_paths = [
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 5\ISCC.exe"),
    ]
    
    for path in common_paths:
        if path.exists():
            print_success(f"Inno Setup found at {path}")
            return True
    
    # Check if in PATH
    if check_command("ISCC.exe", ["/?]):
        print_success("Inno Setup found in PATH")
        return True
    
    print_warning("Inno Setup not found (required for installer creation)")
    print_info("Download from: https://jrsoftware.org/isdl.php")
    print_info("Or build executable only with: python build_installer.py --skip-inno")
    return False


def check_project_structure():
    """Check project structure."""
    print("\nChecking project structure...")
    
    project_root = Path(__file__).parent
    
    required_files = [
        "main.py",
        "gui.py",
        "alarm.py",
        "alarmify.spec",
        "installer.iss",
        "build_installer.py",
        "version_manager.py",
        "requirements.txt",
        "README.md",
        "LICENSE",
    ]
    
    all_present = True
    for file_name in required_files:
        file_path = project_root / file_name
        if file_path.exists():
            print_success(f"{file_name}")
        else:
            print_error(f"{file_name} not found")
            all_present = False
    
    return all_present


def check_assets():
    """Check required assets."""
    print("\nChecking assets...")
    
    project_root = Path(__file__).parent
    
    assets = [
        "Logo First Draft.png",
        "spotify_style.qss",
    ]
    
    all_present = True
    for asset in assets:
        asset_path = project_root / asset
        if asset_path.exists():
            print_success(f"{asset}")
        else:
            print_error(f"{asset} not found")
            all_present = False
    
    return all_present


def check_venv():
    """Check if running in virtual environment."""
    print("\nChecking virtual environment...")
    
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print_success("Running in virtual environment")
        return True
    else:
        print_warning("Not running in virtual environment (recommended)")
        print_info("Create venv with: python -m venv .venv")
        print_info("Activate with: .venv\\Scripts\\Activate.ps1")
        return False


def check_disk_space():
    """Check available disk space."""
    print("\nChecking disk space...")
    
    try:
        if platform.system() == "Windows":
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p("."), None, None, ctypes.pointer(free_bytes)
            )
            free_gb = free_bytes.value / (1024 ** 3)
        else:
            import os
            stat = os.statvfs(".")
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024 ** 3)
        
        if free_gb > 1:
            print_success(f"{free_gb:.1f} GB free (OK)")
            return True
        else:
            print_warning(f"{free_gb:.1f} GB free (Low disk space)")
            return False
    except Exception as e:
        print_warning(f"Could not check disk space: {e}")
        return False


def generate_report(results):
    """Generate summary report."""
    print_header("Verification Summary")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed
    
    print(f"Total checks: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
    
    print("\nStatus by category:")
    for category, status in results.items():
        icon = "✓" if status else "✗"
        color = Colors.GREEN if status else Colors.RED
        print(f"{color}{icon} {category}{Colors.RESET}")
    
    print("\n" + "=" * 60)
    
    if all(results.values()):
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All checks passed! Ready to build.{Colors.RESET}\n")
        print("Next steps:")
        print("  1. Build executable: python build_installer.py --skip-inno")
        print("  2. Build installer: python build_installer.py")
        print("  3. Run tests: python -m pytest tests/ -v")
        return True
    else:
        critical_checks = ["Python Version", "Operating System", "Python Packages", "Project Structure"]
        critical_failed = any(not results.get(check, True) for check in critical_checks)
        
        if critical_failed:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ Critical checks failed. Fix issues before building.{Colors.RESET}\n")
        else:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ Some optional checks failed. You can still build with limitations.{Colors.RESET}\n")
            print("Available options:")
            print("  - Build executable only: python build_installer.py --skip-inno")
        
        return not critical_failed


def main():
    """Main verification routine."""
    print_header("Alarmify Build Environment Verification")
    
    results = {}
    
    # Critical checks
    results["Python Version"] = check_python_version()
    results["Operating System"] = check_os()
    results["Python Packages"] = check_python_packages()
    results["Project Structure"] = check_project_structure()
    results["Assets"] = check_assets()
    
    # Optional checks
    results["Virtual Environment"] = check_venv()
    results["Git"] = check_git()
    results["Inno Setup"] = check_inno_setup()
    results["Disk Space"] = check_disk_space()
    
    # Generate report
    success = generate_report(results)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
