# User Guide - Automated Zoom Poll Generator

This guide explains how to use the Automated Zoom Poll Generator to automatically create and post polls in your Zoom meetings based on meeting content.

## Quick Start

If you're new to the application, follow these steps for a quick start:

1. Launch the application
2. Enter your meeting ID and passcode
3. Click "Join Meeting"
4. Wait for automatic poll generation (approximately 10 minutes into the meeting)
5. Review automatically posted polls (approximately 15 minutes into the meeting)

## Application Interface

The application comes in two versions:

1. **Desktop Application** - A standalone executable with graphical user interface
2. **Terminal Interface** - A command-line interface with rich text display

Both versions provide the same core functionality but with different user interfaces.

### Desktop Application Interface

The desktop application features a simple graphical interface with the following elements:

- **Meeting Connection** section: Join and leave Zoom meetings
- **Automation Control** section: Start and stop the automated poll generation
- **Manual Actions** section: Manually trigger transcript capture, poll generation, or poll posting
- **Status Display**: Shows the current application status
- **Log Display**: Shows recent activity and application logs

### Terminal Interface

The terminal interface provides a rich text-based interface with the following sections:

- **Status Panel**: Shows the current application state
- **Log Panel**: Displays recent activity and application logs
- **Command Input**: Area to enter commands
- **Help Panel**: Shows available commands

## Detailed Usage Instructions

### Joining a Meeting

#### Desktop Application

1. Enter the Zoom meeting ID in the "Meeting ID" field
2. Enter the meeting passcode in the "Passcode" field
3. (Optional) Change your display name in the "Display Name" field
4. Click the "Join Meeting" button
5. Wait for the application to connect to the meeting

#### Terminal Interface

1. Enter the command: `join`
2. When prompted, enter the meeting ID
3. When prompted, enter the meeting passcode
4. (Optional) When prompted, enter your display name
5. Wait for the application to connect to the meeting

### Starting Automated Poll Generation

#### Desktop Application

1. After joining a meeting, click the "Start Automation" button
2. The status display will update to show "Automation: Running"
3. The application will now:
   - Capture meeting transcripts every 10 minutes
   - Generate polls based on transcript content
   - Post polls to the meeting every 15 minutes

#### Terminal Interface

1. After joining a meeting, enter the command: `start`
2. The status panel will update to show "Automation: Running"
3. The log panel will show confirmation that automation has started

### Manual Control

If you want more control over the process, you can manually trigger each step:

#### Desktop Application

1. Click "Capture Transcript" to immediately capture the current meeting transcript
2. Click "Generate Poll" to create a poll based on the most recent transcript
3. Click "Post Poll" to post the current poll to the meeting

#### Terminal Interface

1. Enter `capture` to immediately capture the current meeting transcript
2. Enter `generate` to create a poll based on the most recent transcript
3. Enter `post` to post the current poll to the meeting

### Stopping Automation

#### Desktop Application

1. Click the "Stop Automation" button
2. The status display will update to show "Automation: Stopped"

#### Terminal Interface

1. Enter the command: `stop`
2. The status panel will update to show "Automation: Stopped"

### Leaving a Meeting

#### Desktop Application

1. Click the "Leave Meeting" button
2. The application will disconnect from the meeting

#### Terminal Interface

1. Enter the command: `leave`
2. The application will disconnect from the meeting

## Configuration Options

You can customize the application behavior through the configuration file or through the application interface.

### Key Configuration Options

- **Zoom Client Type**: Choose between "web" for browser-based Zoom or "desktop" for the desktop application
- **Transcript Interval**: How often to capture meeting transcripts (in minutes)
- **Poll Interval**: How often to post polls to the meeting (in minutes)
- **Display Name**: Your name as displayed in Zoom meetings
- **Auto-Start**: Whether to automatically start automation when joining a meeting

### Changing Configuration

#### Desktop Application

1. Click on "Settings" in the menu bar
2. Adjust the settings as needed
3. Click "Save" to apply the changes

#### Terminal Interface

1. Enter the command: `config`
2. Follow the prompts to update each setting
3. The changes will be saved automatically

## Troubleshooting

If you encounter issues while using the application, try these troubleshooting steps:

### Common Issues

#### Cannot Join Meeting

- Verify that the meeting ID and passcode are correct
- Make sure you have a stable internet connection
- Check that the meeting is active and accepting participants

#### No Transcript Captured

- Make sure the meeting has closed captions enabled
- Check that participants are actively speaking in the meeting
- Try manually capturing the transcript with the "Capture Transcript" button

#### Poll Generation Fails

- Ensure there is enough meeting transcript content for meaningful poll generation
- Check your ChatGPT integration settings
- Try manually generating a poll with the "Generate Poll" button

#### Poll Posting Fails

- Verify that you have host or co-host permissions in the meeting
- Make sure polling is enabled for the meeting
- Try manually posting a poll with the "Post Poll" button

### Viewing Logs

For more detailed information about application activity:

#### Desktop Application

1. Click "Export Logs" to save the log file
2. Open the saved log file with a text editor to view detailed information

#### Terminal Interface

1. Enter the command: `status` to see more detailed application state
2. Review the log panel for recent activity
3. For full logs, check the `app.log` file in the application directory

## Best Practices

To get the most out of the Automated Zoom Poll Generator:

1. **Start Early**: Join the meeting a few minutes before it begins to allow the application to set up properly
2. **Enable Captions**: Make sure closed captioning is enabled in the meeting for transcript capture
3. **Active Discussion**: The quality of generated polls depends on the meeting content; more active discussion leads to better polls
4. **Regular Checks**: Occasionally review the application status to ensure it's working as expected
5. **Provide Feedback**: If the generated polls aren't relevant, try adjusting the capture interval or prompt settings

## Advanced Features

### Command Line Options

When launching the application from the command line, you can use these options:

```
python main_app.py --meeting "123456789" --passcode "password" --auto-start
```

- `--meeting`: Automatically join the specified meeting ID
- `--passcode`: Use the specified meeting passcode
- `--auto-start`: Automatically start automation after joining
- `--cli`: Use the terminal interface instead of the graphical interface

### Custom Poll Templates

Advanced users can customize the poll generation prompts in the configuration file:

1. Open `config.json` in a text editor
2. Locate the `poll_generation_prompt` setting
3. Modify the prompt template to suit your needs
4. Save the file and restart the application

## Additional Resources

- [Installation Guide](INSTALLATION.md): Detailed installation instructions
- [GitHub Repository](https://github.com/yourusername/automated-zoom-poll-generator): Source code and latest releases
- [Technical Documentation](TECHNICAL.md): Detailed technical information for developers

## Feedback and Support

If you encounter issues or have suggestions for improvement:

1. Submit an issue on the [GitHub Issues](https://github.com/yourusername/automated-zoom-poll-generator/issues) page
2. Include detailed information about the problem and steps to reproduce it
3. Attach log files if applicable