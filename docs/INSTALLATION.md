# Installation Guide - Automated Zoom Poll Generator

This document provides detailed installation instructions for the Automated Zoom Poll Generator on different operating systems.

## System Requirements

### Minimum Hardware Requirements
- **CPU**: Dual-core processor, 2.0 GHz or higher
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 250 MB of free disk space
- **Display**: 1280x720 resolution or higher
- **Internet**: Broadband connection (5 Mbps or faster)

### Software Requirements
- **Operating System**: 
  - Windows 10/11
  - macOS 10.15 (Catalina) or higher
  - Ubuntu 20.04 or higher / Other Linux distributions with X11
- **Browser**: Google Chrome or Chromium (latest version)
- **Zoom**: Latest version of Zoom desktop client or web client access
- **Python**: Version 3.8 or higher (if installing from source)

## Installation Methods

### Method 1: Pre-built Binaries (Recommended for Non-technical Users)

#### Windows
1. Download the latest Windows installer (.exe) from the [Releases page](https://github.com/yourusername/automated-zoom-poll-generator/releases)
2. Run the installer and follow the on-screen instructions
3. Allow the application to install required dependencies
4. Launch the application from the desktop shortcut or Start menu

#### macOS
1. Download the latest macOS disk image (.dmg) from the [Releases page](https://github.com/yourusername/automated-zoom-poll-generator/releases)
2. Open the disk image and drag the application to your Applications folder
3. Right-click on the application and select "Open" (this is necessary the first time to bypass Gatekeeper)
4. Grant the necessary permissions when prompted (Screen Recording, Accessibility)

#### Linux
1. Download the latest AppImage from the [Releases page](https://github.com/yourusername/automated-zoom-poll-generator/releases)
2. Make the AppImage executable: `chmod +x ZoomPollGenerator-x.x.x.AppImage`
3. Run the AppImage: `./ZoomPollGenerator-x.x.x.AppImage`
4. Follow the on-screen instructions to complete setup

### Method 2: Installation from Source

#### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning the repository)

#### Windows
1. Open Command Prompt or PowerShell
2. Clone the repository or download and extract the source code:
   ```
   git clone https://github.com/yourusername/automated-zoom-poll-generator.git
   cd automated-zoom-poll-generator
   ```
3. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run the application:
   ```
   python main.py
   ```

#### macOS/Linux
1. Open Terminal
2. Clone the repository or download and extract the source code:
   ```
   git clone https://github.com/yourusername/automated-zoom-poll-generator.git
   cd automated-zoom-poll-generator
   ```
3. Create a virtual environment (optional but recommended):
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run the application:
   ```
   python main.py
   ```

### Method 3: Web Application Deployment

The Automated Zoom Poll Generator can also be deployed as a web application for server environments.

#### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- A web server (e.g., Nginx, Apache)

#### Deployment Steps
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/automated-zoom-poll-generator.git
   cd automated-zoom-poll-generator
   ```
2. Create a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Configure the web server to proxy requests to the Flask application
5. Start the application with Gunicorn or similar WSGI server:
   ```
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

## Post-Installation Configuration

### Required Permissions

#### Windows
1. Allow the application through Windows Firewall
2. For UI automation to work correctly, ensure the application has permission to control other applications
3. If running from source, ensure Python has permission to access the internet

#### macOS
1. Open System Preferences > Security & Privacy > Privacy
2. Grant the following permissions to the application:
   - Screen Recording
   - Accessibility
   - Automation (if prompted)
3. Restart the application after granting permissions

#### Linux
1. Ensure your user has appropriate permissions for UI automation: 
   ```
   sudo apt-get install python3-dev python3-tk python3-xlib scrot
   ```
2. For headless environments, ensure X11 is properly configured if needed for browser automation

### First Run Setup

1. Launch the application
2. You will be prompted to:
   - Enter your ChatGPT login credentials
   - Select your preferred Zoom client (desktop or web)
   - Configure polling intervals (optional)
3. For the Zoom desktop client, the application will guide you through positioning your windows correctly
4. For the Zoom web client, you'll need to provide your Zoom login credentials

## Troubleshooting Common Installation Issues

### Windows-specific Issues

#### "Chrome driver not found" Error
1. Ensure you have the latest version of Google Chrome installed
2. The application will attempt to download the correct chromedriver version automatically
3. If automatic download fails, download the appropriate chromedriver manually from [chromedriver.chromium.org](https://chromedriver.chromium.org/) and place it in the application directory

#### UI Automation Not Working
1. Try running the application as Administrator
2. Verify that your display scaling is set to 100% (in Display Settings)
3. Ensure Zoom is updated to the latest version

### macOS-specific Issues

#### Permission Dialogs Not Appearing
1. macOS may block permission dialogs. Open System Preferences manually
2. Go to Security & Privacy > Privacy
3. Add the application to Screen Recording and Accessibility sections

#### Unable to Start Application from Finder
1. If Gatekeeper blocks the application, right-click and select "Open"
2. If that doesn't work, go to System Preferences > Security & Privacy > General
3. Look for a message about the application being blocked and click "Open Anyway"

### Linux-specific Issues

#### Missing Dependencies
1. Install required system packages:
   ```
   sudo apt-get update
   sudo apt-get install -y python3-tk python3-dev scrot xvfb libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-xinerama0 libxcb-xkb1 libxkbcommon-x11-0
   ```

#### Browser Automation Issues
1. For headless environments, install and configure Xvfb:
   ```
   sudo apt-get install xvfb
   Xvfb :99 -screen 0 1280x1024x24 &
   export DISPLAY=:99
   ```
2. Add these lines to your startup script if needed

## Updating the Application

### Automatic Updates
The application will check for updates on startup. If an update is available, you will be prompted to install it.

### Manual Updates
1. For binary installations, download and install the latest version from the Releases page
2. For source installations, pull the latest changes:
   ```
   git pull
   pip install -r requirements.txt
   ```

## Uninstallation

### Windows
1. Go to Control Panel > Programs > Uninstall a Program
2. Find "Automated Zoom Poll Generator" and select Uninstall
3. Follow the uninstallation wizard

### macOS
1. Drag the application from the Applications folder to the Trash
2. Empty the Trash

### Linux
1. If using the AppImage, simply delete the AppImage file
2. If installed from source, delete the directory and remove any created shortcuts

### Removing Configuration Data
1. The application stores configuration data in:
   - Windows: `%APPDATA%\ZoomPollGenerator`
   - macOS: `~/Library/Application Support/ZoomPollGenerator`
   - Linux: `~/.config/ZoomPollGenerator`
2. Delete these directories to completely remove all application data