# User Guide - Automated Zoom Poll Generator

This comprehensive guide will help you get the most out of the Automated Zoom Poll Generator application. It covers setup, daily operation, troubleshooting, and advanced features.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Main Interface](#main-interface)
3. [Setting Up a Meeting](#setting-up-a-meeting)
4. [Automated Workflow](#automated-workflow)
5. [Manual Controls](#manual-controls)
6. [Working with Desktop Zoom Client](#working-with-desktop-zoom-client)
7. [Working with Web Zoom Client](#working-with-web-zoom-client)
8. [Customizing Settings](#customizing-settings)
9. [Log Management](#log-management)
10. [Troubleshooting](#troubleshooting)
11. [Advanced Features](#advanced-features)

## Getting Started

### First Launch

When you first launch the Automated Zoom Poll Generator, you'll be guided through the initial setup process:

1. **Welcome Screen**: Click "Next" to begin setup
2. **Zoom Client Selection**: Choose between Desktop client or Web client
3. **ChatGPT Login**: Enter your ChatGPT credentials
4. **Zoom Credentials**: Enter your Zoom credentials (if using web client)
5. **Final Configuration**: Review and confirm your settings

### Credentials Management

Your credentials are stored securely in memory and never written to disk. For security reasons:

- Credentials are automatically cleared after 30 minutes of inactivity
- You'll need to re-enter credentials after this timeout period
- No API keys or tokens are used or stored

## Main Interface

The application's main interface is divided into several key areas:

### Status Panel
- Displays the current state of the application (Running/Stopped)
- Shows next scheduled actions for transcript capture and poll posting
- Indicates whether you have a current transcript and poll ready

### Control Panel
- **Start/Stop Button**: Begins or ends the automated workflow
- **Manual Action Buttons**: Trigger specific actions immediately
- **Settings Button**: Access configuration options

### Log Display
- Shows real-time application activity
- Color-coded entries by severity level
- Time-stamped operations for audit purposes

### Status Bar
- Quick-reference information
- Current Zoom client mode
- Application version

## Setting Up a Meeting

Before starting the automated workflow, you need to:

1. Join your Zoom meeting as a host or co-host (polling requires these permissions)
2. Position your windows appropriately:
   - For Desktop client: Ensure Zoom is visible on screen
   - For Web client: Keep the Zoom tab accessible to the application
3. Enable meeting transcript in Zoom (required for transcript capture)
4. Make sure you have polling enabled for your Zoom account

### Window Positioning Tips

For optimal performance with the Desktop client:

- Keep the Zoom window visible and unobstructed
- Avoid overlapping windows that might hide Zoom controls
- Don't minimize the Zoom window while the automation is running
- Use a display resolution of at least 1280x720

## Automated Workflow

Once started, the application operates autonomously with this workflow:

1. **Transcript Capture (Every 10 minutes)**
   - Activates the Zoom window
   - Navigates to the transcript area
   - Captures the last 10 minutes of conversation
   - Stores the transcript text in memory

2. **Poll Generation (After transcript capture)**
   - Opens ChatGPT in a browser window
   - Submits the transcript with a specialized prompt
   - Extracts the generated poll question and options
   - Parses and prepares the poll data

3. **Poll Posting (Every 15 minutes)**
   - Activates the Zoom window
   - Navigates to the polling controls
   - Creates a new poll with the generated question and options
   - Launches the poll to all participants

The application handles all window switching and UI navigation automatically, allowing you to focus on your meeting.

## Manual Controls

You can trigger specific actions manually using these controls:

### Capture Transcript Now
- Immediately captures the current meeting transcript
- Useful when an interesting discussion has just occurred

### Generate Poll Now
- Creates a new poll based on the most recent transcript
- Use this if you want a fresh poll before the scheduled time

### Post Poll Now
- Immediately posts the current poll to the meeting
- Helpful when you want to drive engagement at a specific moment

### Export Logs
- Saves the current application logs to a file
- Useful for troubleshooting or record-keeping

## Working with Desktop Zoom Client

When using the Desktop Zoom client mode:

### Requirements
- Zoom must be installed on your computer
- You must be logged in to Zoom
- Your display must be active (not sleeping/locked)

### Recommended Settings
- Enable "Always show meeting controls" in Zoom settings
- Display Zoom in a consistent location on your screen
- Use standard UI scaling (100%) for reliable element detection

### Desktop Client Limitations
- UI automation may be affected by Zoom updates that change the interface
- Heavy CPU usage might occasionally slow down the automation
- Screen recording software may interfere with the automation

## Working with Web Zoom Client

When using the Web Zoom client mode:

### Requirements
- Google Chrome or Chromium browser
- A Zoom account with web client access
- Stable internet connection

### Recommended Settings
- Allow browser notifications if prompted
- Keep the Zoom tab visible (preferably in its own window)
- Use standard zoom level (100%) in the browser

### Web Client Advantages
- More reliable element selection (less affected by OS variations)
- Works well in headless server environments
- Can operate alongside other applications more reliably

## Customizing Settings

You can customize various aspects of the application:

### Scheduling
- Adjust transcript capture interval (default: 10 minutes)
- Modify poll posting interval (default: 15 minutes)
- Set custom schedules for specific meeting patterns

### ChatGPT Prompt
- Edit the prompt template to generate different types of polls
- Customize the instructions for more targeted questions
- Add special directives for formatting or content focus

### UI Automation
- Adjust timing parameters for slower systems
- Modify detection confidence thresholds
- Configure browser window size and position

## Log Management

The application maintains detailed logs of all operations:

### Log Levels
- **INFO**: Normal operations and status changes
- **WARNING**: Non-critical issues that might need attention
- **ERROR**: Problems that prevent normal operation
- **DEBUG**: Detailed technical information (disabled by default)

### Log Export Options
- **Text File**: Plain text log with timestamp and level
- **JSON**: Structured data format for programmatic analysis
- **CSV**: Spreadsheet-compatible format for filtering and sorting

### Log Retention
- Logs are stored for 7 days by default
- Older logs are automatically pruned
- Critical errors are always preserved

## Troubleshooting

### Common Issues and Solutions

#### Application Won't Start
- Check that Python is installed correctly (if running from source)
- Verify that you have the correct permissions
- Look for error messages in the console output

#### ChatGPT Login Fails
- Verify your username and password
- If you use Multi-Factor Authentication, you may need an app password
- Check your internet connection

#### Transcript Capture Not Working
- Ensure the meeting transcript is enabled in Zoom
- Verify that the transcript panel is visible
- Check if the transcript feature is available in your Zoom plan

#### Poll Posting Fails
- Confirm you have host/co-host privileges
- Verify polling is enabled for your Zoom account
- Check if the Zoom interface has been updated recently

#### Automation Seems Slow or Unresponsive
- Reduce other CPU-intensive applications
- Try switching between Desktop and Web client modes
- Adjust the timing parameters in settings

### Diagnostic Tools

#### Log Analysis
- Enable DEBUG level logging for detailed information
- Look for pattern of errors before failure points
- Check timestamps to identify sequence issues

#### Test Mode
- Use the built-in test mode to verify component functionality
- Run individual actions manually to isolate problems
- Verify each step in the workflow independently

## Advanced Features

### Keyboard Shortcuts
- **Ctrl+S**: Start/Stop automation
- **Ctrl+C**: Capture transcript now
- **Ctrl+G**: Generate poll now
- **Ctrl+P**: Post poll now
- **Ctrl+L**: Open log viewer
- **Ctrl+Q**: Quit application

### Command Line Options
- `--headless`: Run without GUI (for server deployments)
- `--debug`: Enable debug logging
- `--config=<path>`: Use custom configuration file
- `--web-mode`: Force web interface mode
- `--desktop-mode`: Force desktop application mode

### Custom Poll Templates
Create specialized poll templates for different meeting types:

1. Create a file named `custom_templates.json`
2. Define templates with custom prompts
3. Select templates from the settings menu

Example template structure:
```json
{
  "templates": [
    {
      "name": "Technical Discussion",
      "prompt": "Based on this technical discussion, create a poll about the most challenging aspect mentioned."
    },
    {
      "name": "Brainstorming",
      "prompt": "From this brainstorming session, create a poll to prioritize the top ideas."
    }
  ]
}
```

### Integration with Meeting Analytics
If you use meeting analytics platforms, you can:

1. Export poll results from Zoom
2. Use the application logs to correlate poll timing with transcript segments
3. Analyze engagement patterns throughout meetings

### Multi-Meeting Support
For advanced users, the application can be configured to:

1. Monitor multiple Zoom meetings simultaneously
2. Use separate browser profiles for different ChatGPT sessions
3. Maintain independent schedules for each meeting