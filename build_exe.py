"""
Build script for creating executable versions of the Automated Zoom Poll Generator.
This script uses PyInstaller to create standalone executables for multiple platforms.
"""

import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

# Set up the console for rich output
console = Console()

# Define the application metadata
APP_NAME = "ZoomPollGenerator"
APP_VERSION = "1.0.0"
MAIN_SCRIPT = "main_app.py"
ICON_PATH = "assets/app_icon"  # Base path without extension


def check_environment():
    """Check if the environment is properly set up for building."""
    console.print(Panel("Checking environment", style="blue"))
    
    # Check Python version
    py_version = platform.python_version()
    console.print(f"Python version: {py_version}")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        console.print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        console.print("[bold red]PyInstaller not found. Installing...[/bold red]")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        console.print("[green]PyInstaller installed successfully.[/green]")
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        console.print("[yellow]Warning: Not running in a virtual environment.[/yellow]")
        console.print("It's recommended to build in a virtual environment to control dependencies.")
        
        if console.input("Continue anyway? [y/N]: ").lower() != 'y':
            console.print("Aborting. Please run in a virtual environment.")
            sys.exit(1)
    
    # Check for icon files
    os_type = platform.system()
    if os_type == "Windows":
        icon_file = f"{ICON_PATH}.ico"
    elif os_type == "Darwin":  # macOS
        icon_file = f"{ICON_PATH}.icns"
    else:  # Linux
        icon_file = f"{ICON_PATH}.png"
    
    if not os.path.exists(icon_file):
        console.print(f"[yellow]Warning: Icon file {icon_file} not found.[/yellow]")
        console.print("Building without an icon.")
        icon_file = None
    else:
        console.print(f"Using icon: {icon_file}")
    
    return icon_file


def build_executable(icon_file):
    """Build the executable for the current platform."""
    os_type = platform.system()
    console.print(Panel(f"Building executable for {os_type}", style="blue"))
    
    # Prepare build arguments
    pyinstaller_args = [
        "pyinstaller",
        f"--name={APP_NAME}",
        "--windowed",
        "--onefile",
    ]
    
    # Add icon if available
    if icon_file:
        pyinstaller_args.append(f"--icon={icon_file}")
    
    # Add platform-specific arguments
    if os_type == "Windows":
        # pyinstaller_args.append("--uac-admin")  # Uncomment to request admin privileges
        pass
    elif os_type == "Darwin":  # macOS
        pyinstaller_args.append("--osx-bundle-identifier=com.yourdomain.zoompollgenerator")
        pass
    
    # Add data files
    pyinstaller_args.append("--add-data=assets:assets")
    
    # Add the main script
    pyinstaller_args.append(MAIN_SCRIPT)
    
    # Run PyInstaller
    console.print("Running PyInstaller with the following arguments:")
    console.print(" ".join(pyinstaller_args))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Building executable...", total=None)
        
        # Execute PyInstaller
        result = subprocess.run(pyinstaller_args, capture_output=True, text=True)
        
        progress.update(task, completed=True, total=1)
    
    # Check if build was successful
    if result.returncode != 0:
        console.print("[bold red]Build failed![/bold red]")
        console.print(result.stderr)
        return False
    
    console.print("[bold green]Build completed successfully![/bold green]")
    
    # Show the location of the executable
    dist_path = Path("dist")
    exe_path = None
    
    if os_type == "Windows":
        exe_path = dist_path / f"{APP_NAME}.exe"
    elif os_type == "Darwin":  # macOS
        exe_path = dist_path / f"{APP_NAME}.app"
    else:  # Linux
        exe_path = dist_path / APP_NAME
    
    if exe_path and exe_path.exists():
        console.print(f"Executable created at: [cyan]{exe_path}[/cyan]")
    
    return True


def create_distribution_package():
    """Create a distribution package with the executable and necessary files."""
    os_type = platform.system()
    console.print(Panel("Creating distribution package", style="blue"))
    
    # Create a directory for the distribution
    dist_dir = Path(f"dist/{APP_NAME}-{APP_VERSION}-{os_type.lower()}")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Copy necessary files to the distribution directory
    files_to_copy = [
        "README.md",
        "LICENSE",
        "config.json",
        ".env.example",  # Example environment file
    ]
    
    for file in files_to_copy:
        if Path(file).exists():
            shutil.copy2(file, dist_dir)
    
    # Copy docs folder
    if Path("docs").exists():
        shutil.copytree("docs", dist_dir / "docs")
    
    # Copy executable
    exe_source = None
    if os_type == "Windows":
        exe_source = Path(f"dist/{APP_NAME}.exe")
        exe_dest = dist_dir / f"{APP_NAME}.exe"
    elif os_type == "Darwin":  # macOS
        exe_source = Path(f"dist/{APP_NAME}.app")
        exe_dest = dist_dir / f"{APP_NAME}.app"
    else:  # Linux
        exe_source = Path(f"dist/{APP_NAME}")
        exe_dest = dist_dir / APP_NAME
    
    if exe_source and exe_source.exists():
        if os_type == "Darwin":  # For macOS, copy the entire .app bundle
            shutil.copytree(exe_source, exe_dest)
        else:
            shutil.copy2(exe_source, exe_dest)
    
    # Create a zip file of the distribution
    shutil.make_archive(f"{APP_NAME}-{APP_VERSION}-{os_type.lower()}", 'zip', "dist", f"{APP_NAME}-{APP_VERSION}-{os_type.lower()}")
    
    console.print(f"Distribution package created: [cyan]{APP_NAME}-{APP_VERSION}-{os_type.lower()}.zip[/cyan]")
    return True


def main():
    """Main function to build executables."""
    console.print(Panel.fit(
        f"[bold cyan]{APP_NAME} [white]v{APP_VERSION}[/white][/bold cyan]\n"
        "Executable Build Script",
        title="Automated Zoom Poll Generator", subtitle="Build Process"
    ))
    
    # Check environment
    icon_file = check_environment()
    
    # Clean previous builds
    if Path("dist").exists():
        console.print("Cleaning previous builds...")
        shutil.rmtree("dist")
    if Path("build").exists():
        shutil.rmtree("build")
    if Path(f"{APP_NAME}.spec").exists():
        os.remove(f"{APP_NAME}.spec")
    
    # Build executable
    if build_executable(icon_file):
        # Create distribution package
        create_distribution_package()
        console.print("[bold green]Build process completed successfully![/bold green]")
    else:
        console.print("[bold red]Build process failed![/bold red]")
        return 1
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Build process interrupted by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]An error occurred during the build process:[/bold red] {e}")
        sys.exit(1)