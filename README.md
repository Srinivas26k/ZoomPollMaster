# Automated Zoom Poll Generator

A desktop application that automates the process of generating and posting polls in Zoom meetings using transcript analysis via ChatGPT.

## Features

- **Transcript Capture**: Automatically captures 10-minute segments of Zoom meeting transcripts
- **Poll Generation**: Uses ChatGPT to generate relevant poll questions based on meeting content
- **Automated Posting**: Posts the generated polls directly to the Zoom meeting
- **Scheduling**: Automatically runs every 10 minutes (configurable)
- **Secure Credential Handling**: Securely manages Zoom and ChatGPT credentials
- **Comprehensive Logging**: Maintains detailed logs of all operations

## Requirements

- Python 3.8 or higher
- Zoom Desktop Client
- Chrome Browser (for ChatGPT integration)
- Active ChatGPT account

## Dependencies

- PyAutoGUI: For UI automation
- Selenium: For browser automation
- APScheduler: For task scheduling
- tkinter: For GUI components (included with Python)
- pyperclip: For clipboard operations
- chromedriver-autoinstaller: For automatic webdriver management

## Installation

1. Install Python 3.8 or higher if not already installed
2. Install the required dependencies:
   