   # Automated Zoom Poll Generator - Setup Script for Windows
# This PowerShell script sets up the Automated Zoom Poll Generator application on Windows

# Function to write colored output
function Write-ColorOutput {
    param (
        [string]$Message,
        [string]$Color = "White"
    )
    
    Write-Host $Message -ForegroundColor $Color
}

# Print a styled header
function Print-Header {
    Write-Host ""
    Write-ColorOutput "=================================================================" "Blue"
    Write-ColorOutput "                 Automated Zoom Poll Generator                    " "Blue"
    Write-ColorOutput "=================================================================" "Blue"
    Write-ColorOutput "                       Setup Script                               " "Yellow"
    Write-ColorOutput "=================================================================" "Blue"
    Write-Host ""
}

# Print a section title
function Print-Section {
    param ([string]$Title)
    
    Write-Host ""
    Write-ColorOutput ">>> $Title" "Green"
}

# Print an error message
function Print-Error {
    param ([string]$Message)
    
    Write-ColorOutput "ERROR: $Message" "Red"
}

# Print a success message
function Print-Success {
    param ([string]$Message)
    
    Write-ColorOutput $Message "Green"
}

# Check Python version (requires Python 3.8+)
function Check-Python {
    Print-Section "Checking Python version"
    
    try {
        $PythonVersion = python --version
        Write-Host "$PythonVersion"
        
        # Extract version numbers
        $VersionMatch = $PythonVersion -match "Python (\d+)\.(\d+)\.(\d+)"
        $Major = [int]$Matches[1]
        $Minor = [int]$Matches[2]
        
        if ($Major -lt 3 -or ($Major -eq 3 -and $Minor -lt 8)) {
            Print-Error "Python 3.8 or higher is required. Please upgrade your Python installation."
            exit 1
        }
        
        Print-Success "Python version check passed"
        return $true
    }
    catch {
        Print-Error "Python not found. Please install Python 3.8 or higher."
        exit 1
    }
}

# Set up pip
function Setup-Pip {
    Print-Section "Setting up pip"
    
    try {
        # Ensure pip is available and up to date
        python -m pip install --upgrade pip
        
        Print-Success "pip is set up successfully"
    }
    catch {
        Print-Error "Failed to set up pip. Please check your Python installation."
        exit 1
    }
}

# Create virtual environment
function Create-Venv {
    Print-Section "Creating virtual environment"
    
    # Check if venv already exists
    if (Test-Path -Path "venv") {
        Write-Host "Virtual environment already exists"
        $Recreate = Read-Host "Do you want to recreate it? (y/n)"
        
        if ($Recreate -eq "y") {
            Write-Host "Removing existing virtual environment..."
            Remove-Item -Recurse -Force "venv"
        }
        else {
            Print-Success "Using existing virtual environment"
            return
        }
    }
    
    # Create venv
    try {
        python -m venv venv
        Print-Success "Virtual environment created successfully"
    }
    catch {
        Print-Error "Failed to create virtual environment. Please make sure venv module is installed."
        exit 1
    }
}

# Activate virtual environment
function Activate-Venv {
    Print-Section "Activating virtual environment"
    
    try {
        # Activate venv
        .\venv\Scripts\Activate.ps1
        Print-Success "Virtual environment activated"
    }
    catch {
        Print-Error "Failed to activate virtual environment"
        Write-Host "You may need to run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
        exit 1
    }
}

# Install required packages
function Install-Packages {
    Print-Section "Installing required packages"
    
    # Install packages from requirements.txt if it exists
    if (Test-Path -Path "requirements.txt") {
        Write-Host "Installing from requirements.txt..."
        pip install -r requirements.txt
    }
    else {
        Write-Host "requirements.txt not found, installing individual packages..."
        
        # Install required packages
        pip install python-dotenv selenium chromedriver-autoinstaller pyautogui pyperclip rich pysimplegui apscheduler pyinstaller flask flask-sqlalchemy gunicorn
    }
    
    if ($LASTEXITCODE -ne 0) {
        Print-Error "Failed to install some packages. Please check the output above."
        # Continue anyway as some failures might be non-critical
    }
    else {
        Print-Success "All packages installed successfully"
    }
}

# Check for additional dependencies
function Check-Dependencies {
    Print-Section "Checking additional dependencies"
    
    # Check for Chrome browser
    $ChromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
    $ChromePathX86 = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    
    if (Test-Path -Path $ChromePath -PathType Leaf) {
        Write-Host "Google Chrome found at: $ChromePath"
    }
    elseif (Test-Path -Path $ChromePathX86 -PathType Leaf) {
        Write-Host "Google Chrome found at: $ChromePathX86"
    }
    else {
        Write-Host "Warning: Google Chrome not found. You'll need to install it for ChatGPT automation."
    }
    
    # Check for Zoom
    $ZoomPath = "$env:APPDATA\Zoom\bin\Zoom.exe"
    
    if (Test-Path -Path $ZoomPath -PathType Leaf) {
        Write-Host "Zoom Desktop Client found at: $ZoomPath"
    }
    else {
        Write-Host "Warning: Zoom Desktop Client not found. You may need to install it for full desktop client support."
    }
}

# Create config file if it doesn't exist
function Create-Config {
    Print-Section "Creating configuration"
    
    if (-not (Test-Path -Path "config.json")) {
        Write-Host "Creating default config.json..."
        
        # Create default config
        @"
{
    "zoom_client_type": "web",
    "transcript_interval": 10,
    "poll_interval": 15,
    "display_name": "Poll Generator",
    "auto_enable_captions": true,
    "auto_start": false,
    "chatgpt_integration_method": "browser",
    "check_interval": 30,
    "save_transcripts": true,
    "transcripts_folder": "./transcripts"
}
"@ | Out-File -FilePath "config.json" -Encoding utf8
        
        Print-Success "Default configuration created"
    }
    else {
        Write-Host "Using existing config.json"
    }
    
    # Create .env file if it doesn't exist
    if (-not (Test-Path -Path ".env")) {
        Write-Host "Creating .env file for environment variables..."
        
        # Create default .env
        @"
# Automated Zoom Poll Generator - Environment Variables

# OpenAI API Key (optional, only needed if using API integration)
# OPENAI_API_KEY=your_api_key_here

# Session secret for web interface
SESSION_SECRET=change_this_to_a_random_string
"@ | Out-File -FilePath ".env" -Encoding utf8
        
        Print-Success ".env file created. You can edit it to add any required API keys."
    }
    else {
        Write-Host "Using existing .env file"
    }
    
    # Create directories
    if (-not (Test-Path -Path "assets")) {
        New-Item -Path "assets" -ItemType Directory | Out-Null
    }
    
    if (-not (Test-Path -Path "transcripts")) {
        New-Item -Path "transcripts" -ItemType Directory | Out-Null
    }
}

# Run a quick test
function Run-Test {
    Print-Section "Running quick system test"
    
    # Test Python imports
    Write-Host "Testing Python imports..."
    
    try {
        python -c "
try:
    import selenium
    import pyautogui
    import rich
    import PySimpleGUI
    import dotenv
    print('All critical imports successful')
except ImportError as e:
    print(f'Import error: {e}')
    exit(1)
"
        Print-Success "All critical imports are working"
    }
    catch {
        Print-Error "Some imports failed. Please check the output above."
    }
}

# Print final instructions
function Print-Instructions {
    Print-Section "Setup complete"
    
    Print-Success "The Automated Zoom Poll Generator has been set up successfully!"
    Write-Host ""
    Write-Host "To run the application with GUI:"
    Write-ColorOutput "  python main_app.py" "Yellow"
    Write-Host ""
    Write-Host "To run the application with CLI:"
    Write-ColorOutput "  python main_app.py --cli" "Yellow"
    Write-Host ""
    Write-Host "To join a meeting automatically on startup:"
    Write-ColorOutput "  python main_app.py --meeting `"meeting_id`" --passcode `"passcode`"" "Yellow"
    Write-Host ""
    Write-Host "For more information, please refer to the documentation in the docs folder."
    Write-Host ""
    Write-ColorOutput "Thank you for using Automated Zoom Poll Generator!" "Blue"
}

# Main function
function Main {
    Print-Header
    Check-Python
    Setup-Pip
    Create-Venv
    Activate-Venv
    Install-Packages
    Check-Dependencies
    Create-Config
    Run-Test
    Print-Instructions
}

# Execute main function
Main