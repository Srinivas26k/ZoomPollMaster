# Automated Zoom Poll Generator

A full-featured application for automating the creation and posting of polls in Zoom meetings based on real-time transcript analysis.

## Project Overview

The Automated Zoom Poll Generator is a sophisticated application designed to enhance engagement during Zoom meetings by automatically generating and posting relevant polls based on real-time meeting transcript content. It uses UI automation to seamlessly integrate with both Zoom desktop and web clients, as well as ChatGPT.

### Key Features

- **Real-time Transcript Capture**: Automatically captures 10-minute segments of Zoom meeting transcripts
- **Intelligent Poll Generation**: Uses ChatGPT to create contextually relevant polls based on meeting content
- **Seamless Poll Posting**: Automatically posts generated polls to Zoom at specified intervals
- **Multiple Platform Support**: Works with both Zoom desktop client and Zoom web client
- **Secure Credential Handling**: Manages credentials securely with automatic session timeouts
- **User-friendly Interface**: Simple dashboard to monitor and control the automation process
- **Comprehensive Logging**: Detailed activity logs for all operations

## Why This Project Matters

### Problems Solved

1. **Engagement Gap**: Most Zoom meetings lack interactive elements, leading to disengagement
2. **Manual Poll Creation**: Creating polls manually during meetings is time-consuming and distracting
3. **Irrelevant Questions**: Pre-made polls often don't match the actual meeting content
4. **Meeting Flow Disruption**: Manual polling interrupts the natural flow of meetings
5. **Lack of Automation**: No existing tools integrate transcript analysis with automated polling

### Our Solution

The Automated Zoom Poll Generator bridges these gaps by providing a completely hands-free solution that:

- **Operates silently in the background** while you focus on your meeting
- **Creates contextually relevant polls** based on actual discussion topics
- **Posts polls at optimal intervals** without requiring manual intervention
- **Works with existing Zoom infrastructure** without requiring special permissions or API access
- **Maintains privacy** by handling all sensitive information locally

## Installation

### Prerequisites

- Python 3.8 or higher
- Zoom Desktop Client (latest version recommended) or Zoom Web Client access
- Google Chrome browser (for ChatGPT integration)
- Active ChatGPT account

### Installation Steps

#### From GitHub

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/automated-zoom-poll-generator.git
   cd automated-zoom-poll-generator
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch the application:
   ```bash
   python main.py
   ```

#### Desktop Application (Windows/macOS/Linux)

For a standalone desktop application without requiring Python installation:

1. Download the latest release from the [Releases](https://github.com/yourusername/automated-zoom-poll-generator/releases) page
2. Extract the downloaded archive
3. Run the executable file:
   - Windows: `ZoomPollGenerator.exe`
   - macOS: `ZoomPollGenerator.app`
   - Linux: `ZoomPollGenerator`

## Usage

### Initial Setup

1. Launch the application
2. Enter your Zoom meeting credentials when prompted
3. Enter your ChatGPT login credentials when prompted
4. Select your preferred Zoom client (Desktop or Web)

### Operation

1. Click "Start" to begin the automated workflow
2. The application will:
   - Capture transcript data every 10 minutes
   - Generate a poll based on the transcript
   - Post the poll to Zoom every 15 minutes
3. Monitor status and logs in the main interface
4. Click "Stop" to pause the automation

### Manual Controls

- **Capture Now**: Manually trigger a transcript capture
- **Generate Poll**: Force a new poll generation
- **Post Poll**: Immediately post the current poll
- **Export Logs**: Save the application logs for analysis

## Platform-Specific Notes

### Windows

- Requires Windows 10 or higher
- May need to run as administrator for proper UI automation

### macOS

- Requires macOS Catalina (10.15) or higher
- Screen recording permission must be granted in System Preferences

### Linux

- Requires X11 display server
- Additional packages may be needed: `sudo apt-get install python3-tk python3-dev scrot`

## Troubleshooting

### Common Issues

1. **UI automation not working**
   - Ensure Zoom and browser windows are visible and not minimized
   - Check screen scaling settings (recommended: 100%)
   - Try running application as administrator

2. **ChatGPT login issues**
   - Verify your login credentials
   - If using MFA, you may need to generate an app password
   - Check internet connection

3. **Poll posting not working**
   - Ensure you have poll creation permissions in the Zoom meeting
   - Verify the Zoom interface hasn't changed due to updates
   - Try using the web client option if desktop client fails

## Development

### Project Structure

```
automated-zoom-poll-generator/
├── app.py                 # Web application (Flask)
├── assets/                # Images for UI automation
├── chatgpt_integration.py # ChatGPT browser automation
├── config.py              # Configuration settings
├── credential_manager.py  # Secure credential handling
├── docs/                  # Documentation
├── gui.py                 # Desktop GUI implementation
├── logger.py              # Logging functionality
├── main.py                # Application entry point
├── poll_posting.py        # Zoom poll posting automation
├── README.md              # Project overview
├── scheduler.py           # Task scheduling
├── templates/             # Web interface templates
└── transcript_capture.py  # Zoom transcript capture
```

### Contributing

We welcome contributions to improve the Automated Zoom Poll Generator! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The Selenium team for browser automation capabilities
- PyAutoGUI developers for UI automation functionality
- OpenAI for ChatGPT
- Zoom for creating an excellent meeting platform