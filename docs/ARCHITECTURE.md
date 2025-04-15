# Automated Zoom Poll Generator - Architecture

This document outlines the architecture and component interactions of the Automated Zoom Poll Generator application.

## Architecture Overview

The application follows a modular architecture with clearly defined components that handle specific aspects of the automation workflow:

```
[User Interface Layer]
     |      ^
     v      |
[Application Logic Layer]
     |      ^
     v      |
[Automation Layer]
     |      ^
     v      |
[External Services]
```

## Component Breakdown

### 1. User Interface Layer

#### Desktop GUI (`gui.py`)
- Provides a native desktop interface with real-time status display
- Exposes controls for manual operation and settings configuration
- Displays logs and operation status

#### Web Interface (`app.py`, `templates/`)
- Offers browser-based alternative for headless environments
- Provides functionality similar to desktop UI via Flask web application
- Allows remote monitoring and control

### 2. Application Logic Layer

#### Main Application Controller (`main.py`)
- Orchestrates the workflow between all components
- Handles application lifecycle
- Manages state transitions between different operations

#### Scheduler (`scheduler.py`)
- Controls timing of automated operations
- Maintains scheduled tasks for transcript capture and poll posting
- Provides hooks for custom scheduling logic

#### Credential Manager (`credential_manager.py`)
- Securely handles user credentials
- Manages timeout and security policies
- Provides credential prompting UI

#### Logger (`logger.py`)
- Centralized logging facility
- Handles log file rotation and export
- Provides different logging levels

### 3. Automation Layer

#### Transcript Capture (`transcript_capture.py`)
- Automates interaction with Zoom transcript features
- Extracts text content from zoom meetings
- Processes and cleans transcript data

#### ChatGPT Integration (`chatgpt_integration.py`)
- Manages browser automation for ChatGPT interaction
- Handles ChatGPT login and session management
- Submits prompts and extracts responses

#### Poll Posting (`poll_posting.py`)
- Automates interaction with Zoom polling interface
- Handles poll creation and launch
- Adapts to different Zoom client UIs

### 4. External Services

- **Zoom Client**: Either desktop application or web client
- **ChatGPT Web Interface**: Used for generating polls from transcripts
- **Web Browser**: Chrome/Chromium for ChatGPT interaction

## Data Flow

1. **Transcript Capture Cycle**:
   ```
   Zoom Client -> TranscriptCapture -> Main Controller -> Storage
   ```

2. **Poll Generation Cycle**:
   ```
   Storage -> Main Controller -> ChatGPTIntegration -> ChatGPT -> Response Parsing -> Storage
   ```

3. **Poll Posting Cycle**:
   ```
   Storage -> Main Controller -> PollPosting -> Zoom Client
   ```

## Key Interfaces

### Zoom Desktop Client Interface
- Uses PyAutoGUI for UI automation
- Image recognition to locate UI elements
- Clipboard interactions for text extraction

### Zoom Web Client Interface
- Uses Selenium for browser automation
- XPath and CSS selectors to interact with elements
- JavaScript execution for complex interactions

### ChatGPT Web Interface
- Uses Selenium for browser automation
- Form interactions for login and prompt submission
- DOM traversal for response extraction

## Module Dependencies

- **PyAutoGUI**: For desktop UI automation
- **Selenium**: For web browser automation
- **Chrome WebDriver**: For browser control
- **APScheduler**: For task scheduling
- **Flask**: For web interface (optional)

## Configuration System

The application uses a centralized configuration (`config.py`) with settings for:

- Application modes (web/desktop)
- Timing parameters
- UI element identifiers
- URL endpoints
- Prompt templates
- Logging preferences

## Security Considerations

1. **Credential Security**:
   - Credentials stored in memory only, never written to disk
   - Automatic memory clearing after timeout
   - No API keys stored or transmitted

2. **Browser Security**:
   - Isolated Chrome instance for ChatGPT interactions
   - No extension loading
   - Reduced attack surface configuration

3. **Operating System Permissions**:
   - Minimal permission requirements
   - Isolation from other system processes

## Extension Points

The architecture provides several extension points for future enhancements:

1. **Alternative AI Services**:
   - The ChatGPT integration can be extended to support other LLMs
   - Adapter pattern used to abstract specific service details

2. **Additional Meeting Platforms**:
   - The automation layer can be extended for other platforms like Microsoft Teams or Google Meet
   - Common interface for transcript and polling operations

3. **Enhanced Analytics**:
   - Poll results collection and analysis
   - Meeting engagement metrics
   - Reporting capabilities

## Error Handling Strategy

The application implements a robust error handling strategy:

1. **Graceful Degradation**:
   - Operations continue even if some components fail
   - Fallback mechanisms for critical functions

2. **Automatic Recovery**:
   - Self-healing for common error conditions
   - Retry logic with exponential backoff

3. **Comprehensive Logging**:
   - Detailed error information for troubleshooting
   - Operation audit trail

## Testing Approach

The codebase supports multiple testing approaches:

1. **Unit Tests**:
   - Component-level testing with mocked dependencies
   - Coverage of core business logic

2. **Integration Tests**:
   - Testing of component interactions
   - Validation of workflow correctness

3. **UI Automation Tests**:
   - Verification of UI interaction patterns
   - Confirmation of element selection logic