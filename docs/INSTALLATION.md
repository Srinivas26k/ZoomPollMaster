# Installation Guide for Automated Zoom Poll Generator

This document provides detailed installation and setup instructions for the Automated Zoom Poll Generator application on various platforms.

## Prerequisites

Before installing the Automated Zoom Poll Generator, ensure that your system meets the following requirements:

### System Requirements

- Operating System: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+ recommended)
- Processor: Dual-core 2GHz or better
- Memory: At least 4GB RAM
- Disk Space: At least 500MB of free disk space
- Internet Connection: Required for ChatGPT integration

### Software Requirements

- Python 3.8 or higher
- Google Chrome or Chromium browser (required for ChatGPT integration)
- Zoom Desktop Client or Zoom Web Client access

## Installation Methods

There are three ways to install the Automated Zoom Poll Generator:

1. **Pre-built executable** (recommended for end users)
2. **Setup script** (recommended for developers)
3. **Manual installation** (for advanced users)

## Method 1: Pre-built Executable

This is the simplest method for end users who don't need to modify the application code.

### Windows

1. Download the latest `ZoomPollGenerator-Windows.zip` from the [GitHub Releases](https://github.com/yourusername/automated-zoom-poll-generator/releases) page
2. Extract the ZIP file to a location of your choice
3. Double-click `ZoomPollGenerator.exe` to run the application

### macOS

1. Download the latest `ZoomPollGenerator-macOS.zip` from the [GitHub Releases](https://github.com/yourusername/automated-zoom-poll-generator/releases) page
2. Extract the ZIP file to a location of your choice
3. Right-click on `ZoomPollGenerator.app` and select "Open"
4. If you see a security warning, go to System Preferences > Security & Privacy and click "Open Anyway"

### Linux

1. Download the latest `ZoomPollGenerator-Linux.zip` from the [GitHub Releases](https://github.com/yourusername/automated-zoom-poll-generator/releases) page
2. Extract the ZIP file to a location of your choice
3. Open a terminal in the extracted directory
4. Make the executable file runnable: `chmod +x ZoomPollGenerator`
5. Run the application: `./ZoomPollGenerator`

## Method 2: Setup Script

This method is recommended for developers who want to modify or contribute to the application.

### Windows

1. Ensure Python 3.8+ is installed and available in your PATH
2. Clone or download the repository: `git clone https://github.com/yourusername/automated-zoom-poll-generator.git`
3. Navigate to the project directory: `cd automated-zoom-poll-generator`
4. Run the setup script using PowerShell:
   ```powershell
   .\setup.ps1
   ```
5. Follow the on-screen instructions to complete the setup

### macOS/Linux

1. Ensure Python 3.8+ is installed and available in your PATH
2. Clone or download the repository: `git clone https://github.com/yourusername/automated-zoom-poll-generator.git`
3. Navigate to the project directory: `cd automated-zoom-poll-generator`
4. Make the setup script executable: `chmod +x setup.sh`
5. Run the setup script:
   ```bash
   ./setup.sh
   ```
6. Follow the on-screen instructions to complete the setup

## Method 3: Manual Installation

This method is for advanced users who need more control over the installation process.

1. Ensure Python 3.8+ is installed and available in your PATH
2. Clone or download the repository: `git clone https://github.com/yourusername/automated-zoom-poll-generator.git`
3. Navigate to the project directory: `cd automated-zoom-poll-generator`
4. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   ```
5. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
6. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
7. Create necessary directories:
   ```bash
   mkdir -p assets transcripts
   ```
8. Create a `.env` file with required environment variables (see Configuration section below)
9. Create a `config.json` file with application settings (see Configuration section below)

## Configuration

### .env File

Create a `.env` file in the project root directory with the following content:

```
# Automated Zoom Poll Generator - Environment Variables

# OpenAI API Key (optional, only needed if using API integration)
# OPENAI_API_KEY=your_api_key_here

# Session Secret for Web Version (change this to a random string)
SESSION_SECRET=change_this_to_a_random_string
```

### config.json File

Create a `config.json` file in the project root directory with the following content:

```json
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
```

Adjust these settings according to your preferences:

- `zoom_client_type`: Use "web" for Zoom Web Client or "desktop" for Zoom Desktop Client
- `transcript_interval`: Time between transcript captures in minutes
- `poll_interval`: Time between poll postings in minutes
- `display_name`: Your display name in Zoom meetings
- `auto_enable_captions`: Automatically enable closed captions when joining a meeting
- `auto_start`: Automatically start automation when the application launches
- `chatgpt_integration_method`: Use "browser" for browser automation or "api" for API integration
- `check_interval`: How often to check for scheduled tasks in seconds
- `save_transcripts`: Whether to save meeting transcripts to files
- `transcripts_folder`: Folder to save transcripts in

## Troubleshooting

### Common Issues

#### Application won't start

- Make sure you have Python 3.8+ installed
- Check that all dependencies are installed
- On Linux, ensure you have X11 and required libraries installed

#### ChatGPT integration fails

- Make sure Chrome or Chromium browser is installed
- Check your internet connection
- Verify that your ChatGPT credentials are correct

#### Zoom automation issues

- Make sure Zoom is installed (for desktop client mode)
- Check that you have proper permissions for screen capture and automation

### Getting Help

If you encounter issues not covered in this guide:

1. Check the [GitHub Issues](https://github.com/yourusername/automated-zoom-poll-generator/issues) page for known problems
2. Submit a new issue with details about your problem
3. Include information about your operating system, Python version, and application logs

## Next Steps

After installing the Automated Zoom Poll Generator, refer to the [User Guide](USER_GUIDE.md) for instructions on how to use the application.