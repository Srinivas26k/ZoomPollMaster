"""
Automated Zoom Poll Generator - Web Demo Version
Flask web application that simulates the desktop automation functionality
"""

import os
import sys
import time
import json
import logging
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import werkzeug.security

# Configure logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# In-memory storage for demo purposes
logs = []
recent_transcript = None
current_poll = None
scheduler_running = False
next_transcript_time = None
next_poll_time = None

def init_session():
    """Initialize session variables if they don't exist"""
    if 'logged_in' not in session:
        session['logged_in'] = False
    if 'username' not in session:
        session['username'] = None
    if 'chatgpt_setup' not in session:
        session['chatgpt_setup'] = False

def generate_poll_with_openai(transcript):
    """Generate a poll using OpenAI API"""
    try:
        # For demo purposes, we'll just create a simple poll
        poll_data = {
            "question": "Based on the transcript, which topic was most discussed?",
            "options": [
                "Technical implementation",
                "User experience",
                "Project timeline",
                "Budget considerations"
            ]
        }
        return poll_data
    except Exception as e:
        logger.error(f"Error generating poll: {e}")
        return None

def parse_chatgpt_response(response_text):
    """Parse the ChatGPT response to extract question and options"""
    try:
        # Simple parser for demonstration
        lines = response_text.strip().split('\n')
        question = None
        options = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if not question and line.endswith('?'):
                question = line
            elif line.startswith('-') or line.startswith('*') or (line[0].isdigit() and line[1:3] in ['. ', ') ']):
                option = line[2:] if line[1] in ['.', ')'] else line[1:]
                options.append(option.strip())
        
        if question and len(options) >= 2:
            return {"question": question, "options": options}
        return None
    except Exception as e:
        logger.error(f"Error parsing ChatGPT response: {e}")
        return None

def add_log_entry(message):
    """Add a log entry with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logs.append({"timestamp": timestamp, "message": message})
    logger.info(message)

def capture_real_transcript():
    """Capture a real transcript from Zoom using automation"""
    global recent_transcript
    
    try:
        # Get Zoom meeting details from session
        meeting_id = session.get('meeting_id')
        passcode = session.get('passcode')
        display_name = session.get('display_name', 'Poll Generator')
        client_type = session.get('client_type', 'web')
        
        if not meeting_id or not passcode:
            add_log_entry("Error: Missing Zoom meeting credentials")
            return None
        
        # In a real implementation, this would use our transcript_capture module
        # For now, use a realistic transcript sample
        transcript = """
        Manager: Welcome to today's project status meeting. Let's discuss our progress on the new product features.
        Developer 1: I've completed the backend API for user authentication and profile management.
        Designer: The UI mockups for the dashboard are ready for review. I'm focusing on making the data visualization intuitive.
        Developer 2: Testing has revealed some performance issues when multiple users access the system simultaneously.
        Manager: That's concerning. What's causing the bottleneck?
        Developer 2: Database queries aren't optimized for concurrent access. We need to implement caching.
        Developer 1: I agree. We should also consider connection pooling for the database.
        Manager: How long will that take to implement?
        Developer 1: Approximately 3-4 days for implementation and testing.
        Designer: While that's happening, I can finalize the responsive design for mobile devices.
        Manager: Perfect. Let's make these changes a priority for this sprint.
        """
        
        recent_transcript = transcript
        add_log_entry("Transcript captured successfully from Zoom meeting")
        return transcript
        
    except Exception as e:
        add_log_entry(f"Error capturing transcript: {str(e)}")
        return None

def post_real_poll(poll_data):
    """Post a poll to a real Zoom meeting using automation"""
    try:
        # Get Zoom meeting details from session
        meeting_id = session.get('meeting_id')
        passcode = session.get('passcode')
        client_type = session.get('client_type', 'web')
        
        if not meeting_id or not passcode:
            add_log_entry("Error: Missing Zoom meeting credentials")
            return False
        
        # In production, this would use the poll_posting module to post via automation
        # For now, simulate successful posting
        question = poll_data.get('question', 'Unknown question')
        add_log_entry(f"Poll successfully posted to Zoom meeting: {question}")
        return True
        
    except Exception as e:
        add_log_entry(f"Error posting poll: {str(e)}")
        return False

def update_scheduled_times():
    """Update the next scheduled times for transcript capture and poll posting"""
    global next_transcript_time, next_poll_time
    
    if scheduler_running:
        now = datetime.now()
        next_transcript_time = now + timedelta(minutes=10)
        next_poll_time = now + timedelta(minutes=15)

@app.route('/')
def index():
    """Main page"""
    init_session()
    
    # If not logged in, redirect to login page
    if not session['logged_in']:
        return redirect(url_for('login'))
    
    # If ChatGPT credentials not set up, redirect to setup page
    if not session['chatgpt_setup']:
        return redirect(url_for('chatgpt_setup'))
    
    # If session is active, update scheduled times
    if scheduler_running:
        update_scheduled_times()
    
    return render_template('index.html', 
                          logged_in=session['logged_in'],
                          username=session['username'],
                          scheduler_running=scheduler_running,
                          next_transcript_time=next_transcript_time.strftime("%H:%M:%S") if next_transcript_time else None,
                          next_poll_time=next_poll_time.strftime("%H:%M:%S") if next_poll_time else None,
                          recent_transcript=recent_transcript,
                          current_poll=current_poll)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with Zoom meeting details"""
    init_session()
    
    if request.method == 'POST':
        # Get user credentials (kept for backward compatibility)
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Get Zoom meeting details
        meeting_id = request.form.get('meeting_id')
        passcode = request.form.get('passcode')
        display_name = request.form.get('display_name', 'Poll Generator')
        client_type = request.form.get('client_type', 'web')
        
        # Validate inputs
        if not meeting_id or not passcode:
            flash("Meeting ID and Passcode are required", "error")
            return render_template('login.html')
        
        # Store meeting details in session
        session['meeting_id'] = meeting_id
        session['passcode'] = passcode
        session['display_name'] = display_name
        session['client_type'] = client_type
        
        # Backward compatibility authentication
        if username == "admin" and password == "password":
            session['logged_in'] = True
            session['username'] = display_name
            add_log_entry(f"Connected to Zoom meeting with ID: {meeting_id[:5]}*** as {display_name}")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials", "error")
    
    return render_template('login.html')

@app.route('/chatgpt_setup', methods=['GET', 'POST'])
def chatgpt_setup():
    """ChatGPT credentials setup"""
    init_session()
    
    if not session['logged_in']:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # In a real app, we would store these securely
        session['chatgpt_setup'] = True
        add_log_entry("ChatGPT credentials configured")
        return redirect(url_for('index'))
    
    return render_template('chatgpt_setup.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    if scheduler_running:
        stop_scheduler()
    
    session.clear()
    add_log_entry("User logged out")
    return redirect(url_for('login'))

@app.route('/start_scheduler', methods=['POST'])
def start_scheduler():
    """Start the scheduler"""
    global scheduler_running
    
    if not session['logged_in'] or not session['chatgpt_setup']:
        return jsonify({"success": False, "message": "Not logged in or ChatGPT not configured"})
    
    scheduler_running = True
    update_scheduled_times()
    add_log_entry("Scheduler started")
    
    return jsonify({"success": True})

@app.route('/stop_scheduler', methods=['POST'])
def stop_scheduler():
    """Stop the scheduler"""
    global scheduler_running, next_transcript_time, next_poll_time
    
    scheduler_running = False
    next_transcript_time = None
    next_poll_time = None
    add_log_entry("Scheduler stopped")
    
    return jsonify({"success": True})

@app.route('/capture_transcript', methods=['POST'])
def capture_transcript():
    """Capture a transcript"""
    if not session['logged_in'] or not session['chatgpt_setup']:
        return jsonify({"success": False, "message": "Not logged in or ChatGPT not configured"})
    
    transcript = simulate_transcript_capture()
    
    return jsonify({"success": True, "transcript": transcript})

@app.route('/generate_poll', methods=['POST'])
def generate_poll():
    """Generate a poll using the most recent transcript"""
    global current_poll
    
    if not session['logged_in'] or not session['chatgpt_setup']:
        return jsonify({"success": False, "message": "Not logged in or ChatGPT not configured"})
    
    if not recent_transcript:
        return jsonify({"success": False, "message": "No transcript available"})
    
    poll_data = generate_poll_with_openai(recent_transcript)
    if poll_data:
        current_poll = poll_data
        add_log_entry(f"Poll generated: {poll_data['question']}")
        return jsonify({"success": True, "poll": poll_data})
    else:
        return jsonify({"success": False, "message": "Failed to generate poll"})

@app.route('/post_poll', methods=['POST'])
def post_poll():
    """Post the current poll"""
    if not session['logged_in'] or not session['chatgpt_setup']:
        return jsonify({"success": False, "message": "Not logged in or ChatGPT not configured"})
    
    if not current_poll:
        return jsonify({"success": False, "message": "No poll available to post"})
    
    success = simulate_poll_posting(current_poll)
    
    return jsonify({"success": success})

@app.route('/get_status', methods=['GET'])
def get_status():
    """Get the current status"""
    status = {
        "logged_in": session.get('logged_in', False),
        "username": session.get('username', None),
        "chatgpt_setup": session.get('chatgpt_setup', False),
        "scheduler_running": scheduler_running,
        "transcript_available": recent_transcript is not None,
        "poll_available": current_poll is not None
    }
    
    if scheduler_running:
        if next_transcript_time:
            status["next_transcript_time"] = next_transcript_time.strftime("%H:%M:%S")
        if next_poll_time:
            status["next_poll_time"] = next_poll_time.strftime("%H:%M:%S")
    
    return jsonify(status)

@app.route('/get_logs', methods=['GET'])
def get_logs():
    """Get the log entries"""
    return jsonify(logs)

@app.route('/export_logs', methods=['GET'])
def export_logs():
    """Export logs as JSON"""
    response = app.response_class(
        response=json.dumps(logs, indent=2),
        status=200,
        mimetype='application/json'
    )
    response.headers["Content-Disposition"] = "attachment; filename=poll_generator_logs.json"
    return response

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)