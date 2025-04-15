# GitHub Release Guide

This document explains how to create a GitHub release for the Automated Zoom Poll Generator and includes instructions for building executable versions.

## Initial Setup

### 1. Create a GitHub Repository

1. Sign in to GitHub and navigate to your profile
2. Click "New" to create a new repository
3. Name it `automated-zoom-poll-generator` (or a name of your choice)
4. Add a description for the repository: "Automated Zoom Poll Generator - A tool for generating and posting polls in Zoom meetings based on transcript content"
5. Choose whether the repository should be Public or Private
6. Select "Add a README file"
7. Click "Create repository"

### 2. Clone the Repository Locally

```bash
git clone https://github.com/yourusername/automated-zoom-poll-generator.git
cd automated-zoom-poll-generator
```

### 3. Push Project Files to GitHub

1. Copy all project files to the cloned repository folder
2. Add all files to Git:

```bash
git add .
git commit -m "Initial commit - project files"
git push origin main
```

## Building Executables

The Automated Zoom Poll Generator can be distributed as standalone executables for Windows, macOS, and Linux using PyInstaller. Follow these steps to create the executables.

### Prerequisites

- Make sure you have PyInstaller installed:
  ```
  pip install pyinstaller
  ```
- Ensure you have activated your project's virtual environment
- Make sure all dependencies are installed

### Building Windows Executable

```powershell
# Navigate to project directory
cd path/to/automated-zoom-poll-generator

# Activate virtual environment
.\venv\Scripts\activate

# Run PyInstaller
pyinstaller --name="ZoomPollGenerator" --windowed --onefile --icon=assets/icon.ico main_app.py
```

Additional Windows options:
- Add `--uac-admin` to request admin privileges if needed
- Add `--add-data "assets;assets"` to include assets folder

### Building macOS App

```bash
# Navigate to project directory
cd path/to/automated-zoom-poll-generator

# Activate virtual environment
source venv/bin/activate

# Run PyInstaller
pyinstaller --name="ZoomPollGenerator" --windowed --onefile --icon=assets/icon.icns main_app.py
```

Additional macOS options:
- Add `--add-data "assets:assets"` to include assets folder
- For code signing, see PyInstaller documentation

### Building Linux Executable

```bash
# Navigate to project directory
cd path/to/automated-zoom-poll-generator

# Activate virtual environment
source venv/bin/activate

# Run PyInstaller
pyinstaller --name="ZoomPollGenerator" --windowed --onefile --icon=assets/icon.png main_app.py
```

The executables will be created in the `dist` directory.

## Creating a GitHub Release

GitHub Releases allow you to package software and release notes together. Follow these steps to create a release.

### 1. Create a Tag

A tag marks a specific point in your repository's history. You can create a tag through the GitHub interface or using Git commands.

Using Git commands:
```bash
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0
```

### 2. Create a Release from the Tag

1. Go to your GitHub repository
2. Click on "Releases" in the right-side panel
3. Click "Draft a new release"
4. Select the tag you created (e.g., "v1.0.0")
5. Title the release (e.g., "Version 1.0.0")
6. Add a description of the release, including:
   - New features
   - Bug fixes
   - Known issues
   - Installation instructions
7. If you have executable files, drag and drop them into the release assets section:
   - `ZoomPollGenerator.exe` (Windows)
   - `ZoomPollGenerator.app.zip` (macOS, zip the .app folder)
   - `ZoomPollGenerator` (Linux)
8. If the release is ready for production, select "This is a pre-release" if appropriate
9. Click "Publish release"

### Example Release Description

```markdown
# Automated Zoom Poll Generator v1.0.0

First public release of the Automated Zoom Poll Generator.

## Features
- Automatic transcript capture from Zoom meetings
- Intelligent poll generation based on meeting content
- Automatic poll posting to Zoom
- Support for both desktop and web Zoom clients
- Simple and intuitive user interface

## Installation

### Windows
1. Download `ZoomPollGenerator.exe`
2. Double-click to run the application
3. Make sure you have Chrome installed for ChatGPT integration

### macOS
1. Download `ZoomPollGenerator.app.zip`
2. Extract the zip file
3. Right-click on `ZoomPollGenerator.app` and select "Open"
4. If prompted about an unidentified developer, go to System Preferences > Security & Privacy and click "Open Anyway"

### Linux
1. Download `ZoomPollGenerator`
2. Make the file executable: `chmod +x ZoomPollGenerator`
3. Run the application: `./ZoomPollGenerator`

## Source Code Installation
Alternatively, you can install from source code:
1. Clone the repository
2. Run the setup script:
   - Linux/macOS: `./setup.sh`
   - Windows: Run `setup.ps1` in PowerShell
3. Run the application: `python main_app.py`

## Known Issues
- Limited support for Zoom Enterprise features
- Requires Chrome browser for ChatGPT integration

## Feedback and Contributions
Please open an issue on GitHub if you encounter any problems or have suggestions for improvements.
```

## Updating the Release

To update a release:

1. Make your code changes
2. Update the version number in appropriate files
3. Create a new tag (e.g., "v1.0.1")
4. Push the tag to GitHub
5. Create a new release following the steps above

## GitHub Pages Documentation (Optional)

You can also set up GitHub Pages to host the project documentation:

1. Go to your repository's "Settings" tab
2. Scroll down to "GitHub Pages" section
3. Select the source branch (usually "main")
4. Choose the "/docs" folder as the source
5. Click "Save"

Your documentation will be available at `https://yourusername.github.io/automated-zoom-poll-generator/`.

## Continuous Integration (Optional)

For more advanced users, consider setting up GitHub Actions to automatically build and release your application:

1. Create a `.github/workflows/release.yml` file
2. Set up the workflow to build the application on each tag
3. Configure it to automatically create releases with build artifacts

This is beyond the scope of this document, but GitHub has excellent documentation on GitHub Actions.

## Conclusion

By following these steps, you'll have a professional GitHub release for the Automated Zoom Poll Generator that users can easily download and install on their systems.