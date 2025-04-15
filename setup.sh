#!/bin/bash

# Automated Zoom Poll Generator - Setup Script
# This script sets up the Automated Zoom Poll Generator application

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print a styled header
print_header() {
    echo -e "\n${BLUE}==================================================================${NC}"
    echo -e "${BLUE}                 Automated Zoom Poll Generator                    ${NC}"
    echo -e "${BLUE}==================================================================${NC}"
    echo -e "${YELLOW}                       Setup Script                             ${NC}"
    echo -e "${BLUE}==================================================================${NC}\n"
}

# Print a section title
print_section() {
    echo -e "\n${GREEN}>>> $1${NC}"
}

# Print an error message
print_error() {
    echo -e "${RED}ERROR: $1${NC}"
}

# Print a success message
print_success() {
    echo -e "${GREEN}$1${NC}"
}

# Detect operating system
detect_os() {
    print_section "Detecting operating system"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="Linux"
        echo "Operating system: Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="MacOS"
        echo "Operating system: macOS"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        OS="Windows"
        echo "Operating system: Windows"
    else
        OS="Unknown"
        echo "Operating system: Unknown ($OSTYPE)"
    fi
}

# Check Python version (requires Python 3.8+)
check_python() {
    print_section "Checking Python version"
    
    if command -v python3 &>/dev/null; then
        PYTHON_CMD=python3
    elif command -v python &>/dev/null; then
        PYTHON_CMD=python
    else
        print_error "Python not found. Please install Python 3.8 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
    echo "Python version: $PYTHON_VERSION"
    
    # Check if Python version is 3.8 or higher
    if [[ $($PYTHON_CMD -c 'import sys; print(sys.version_info.major >= 3 and sys.version_info.minor >= 8)') == "False" ]]; then
        print_error "Python 3.8 or higher is required. Please upgrade your Python installation."
        exit 1
    fi
    
    print_success "Python version check passed"
}

# Install or update pip
setup_pip() {
    print_section "Setting up pip"
    
    # Ensure pip is available and up to date
    $PYTHON_CMD -m pip install --upgrade pip
    
    if [ $? -ne 0 ]; then
        print_error "Failed to set up pip. Please check your Python installation."
        exit 1
    fi
    
    print_success "pip is set up successfully"
}

# Create virtual environment
create_venv() {
    print_section "Creating virtual environment"
    
    # Check if venv already exists
    if [ -d "venv" ]; then
        echo "Virtual environment already exists"
        read -p "Do you want to recreate it? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Removing existing virtual environment..."
            rm -rf venv
        else
            print_success "Using existing virtual environment"
            return
        fi
    fi
    
    # Create venv
    $PYTHON_CMD -m venv venv
    
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment. Please make sure venv module is installed."
        exit 1
    fi
    
    print_success "Virtual environment created successfully"
}

# Activate virtual environment
activate_venv() {
    print_section "Activating virtual environment"
    
    # Activate venv based on OS
    if [ "$OS" = "Windows" ]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    if [ $? -ne 0 ]; then
        print_error "Failed to activate virtual environment"
        exit 1
    fi
    
    print_success "Virtual environment activated"
}

# Install required packages
install_packages() {
    print_section "Installing required packages"
    
    # Install packages from requirements.txt if it exists
    if [ -f "requirements.txt" ]; then
        echo "Installing from requirements.txt..."
        pip install -r requirements.txt
    else
        echo "requirements.txt not found, installing individual packages..."
        
        # Install required packages
        pip install python-dotenv selenium chromedriver-autoinstaller pyautogui pyperclip rich pysimplegui apscheduler pyinstaller flask flask-sqlalchemy gunicorn
    fi
    
    if [ $? -ne 0 ]; then
        print_error "Failed to install some packages. Please check the output above."
        # Continue anyway as some failures might be non-critical
    else
        print_success "All packages installed successfully"
    fi
}

# Check for additional dependencies based on OS
check_dependencies() {
    print_section "Checking additional dependencies"
    
    if [ "$OS" = "Linux" ]; then
        echo "Checking Linux dependencies..."
        
        # Check for X11 dependencies for GUI automation
        if ! command -v xdpyinfo &>/dev/null; then
            echo "xdpyinfo not found. You may need to install X11 development packages:"
            echo "  sudo apt-get install x11-utils"
        fi
        
        # Check for Tkinter for PySimpleGUI
        $PYTHON_CMD -c "import tkinter" 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "Tkinter not found. You may need to install it:"
            echo "  sudo apt-get install python3-tk"
        fi
        
        # Check for dependencies for PyAutoGUI
        echo "You may need additional dependencies for PyAutoGUI:"
        echo "  sudo apt-get install scrot python3-xlib python3-dev"
    elif [ "$OS" = "MacOS" ]; then
        echo "Checking macOS dependencies..."
        
        # Check for Accessibility permissions
        echo "Note: PyAutoGUI requires Accessibility permissions on macOS."
        echo "You'll need to grant these permissions in System Preferences > Security & Privacy > Privacy > Accessibility"
    fi
    
    # Check for browser for ChatGPT automation
    if command -v google-chrome &>/dev/null || command -v chromium-browser &>/dev/null || [ -d "/Applications/Google Chrome.app" ] || [ -d "C:/Program Files/Google/Chrome" ]; then
        echo "Chrome/Chromium browser found. Will use for ChatGPT automation."
    else
        echo "Warning: Chrome or Chromium browser not found. You'll need to install it for ChatGPT automation."
    fi
}

# Create config file if it doesn't exist
create_config() {
    print_section "Creating configuration"
    
    if [ ! -f "config.json" ]; then
        echo "Creating default config.json..."
        
        # Create default config
        cat > config.json << EOL
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
EOL
        print_success "Default configuration created"
    else
        echo "Using existing config.json"
    fi
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        echo "Creating .env file for environment variables..."
        
        # Create default .env
        cat > .env << EOL
# Automated Zoom Poll Generator - Environment Variables

# OpenAI API Key (optional, only needed if using API integration)
# OPENAI_API_KEY=your_api_key_here

# Session secret for web interface
SESSION_SECRET=change_this_to_a_random_string
EOL
        print_success ".env file created. You can edit it to add any required API keys."
    else
        echo "Using existing .env file"
    fi
    
    # Create directories
    mkdir -p assets
    mkdir -p transcripts
}

# Run a quick test
run_test() {
    print_section "Running quick system test"
    
    # Test Python imports
    echo "Testing Python imports..."
    IMPORT_TEST=$($PYTHON_CMD -c "
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
")
    
    echo "$IMPORT_TEST"
    
    if [[ "$IMPORT_TEST" != *"All critical imports successful"* ]]; then
        print_error "Some imports failed. Please check the output above."
    else
        print_success "All critical imports are working"
    fi
}

# Print final instructions
print_instructions() {
    print_section "Setup complete"
    
    echo -e "${GREEN}The Automated Zoom Poll Generator has been set up successfully!${NC}"
    echo 
    echo -e "To run the application with GUI:"
    echo -e "  ${YELLOW}${PYTHON_CMD} main_app.py${NC}"
    echo 
    echo -e "To run the application with CLI:"
    echo -e "  ${YELLOW}${PYTHON_CMD} main_app.py --cli${NC}"
    echo 
    echo -e "To join a meeting automatically on startup:"
    echo -e "  ${YELLOW}${PYTHON_CMD} main_app.py --meeting \"meeting_id\" --passcode \"passcode\"${NC}"
    echo 
    echo -e "For more information, please refer to the documentation in the docs folder."
    echo 
    echo -e "${BLUE}Thank you for using Automated Zoom Poll Generator!${NC}"
}

# Main function
main() {
    print_header
    detect_os
    check_python
    setup_pip
    create_venv
    activate_venv
    install_packages
    check_dependencies
    create_config
    run_test
    print_instructions
}

# Execute main function
main