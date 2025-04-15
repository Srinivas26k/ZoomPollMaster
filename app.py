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

def simulate_transcript_capture():
    """Simulate capturing a transcript from Zoom"""
    global recent_transcript
    
    transcript = """
    Person A: Welcome to the meeting everyone. Today we'll be discussing the progress on the automated poll generator project.
    Person B: Thanks for organizing this. I've been working on the user interface, and I think we've made good progress.
    Person A: That's great to hear. What are the key features you've implemented so far?
    Person B: We've got the transcript capture functionality working, and the integration with ChatGPT is almost complete.
    Person C: I have a concern about the poll posting feature. Are we sure it will work with both web and desktop Zoom clients?
    Person A: That's a valid point. We've been testing it with the web client primarily, but we need to ensure compatibility.
    Person D: I can help with testing the desktop client integration. I've got some experience with that from previous projects.
    Person B: That would be very helpful. The scheduler component also needs some attention - it's not reliably triggering the poll posting.
    Person A: Let's prioritize fixing that issue. What about the credential management system?
    Person C: It's secure but we could improve the user experience a bit. Right now it's not very intuitive.
    Person A: Agreed. Let's schedule a design review for that component.
    """
    
    recent_transcript = transcript
    add_log_entry("Transcript captured successfully")
    return transcript

def simulate_poll_posting(poll_data):
    """Simulate posting a poll to Zoom"""
    add_log_entry(f"Poll posted: {poll_data['question']}")
    return True

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
    """Login page"""
    init_session()
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple authentication for demonstration
        if username == "admin" and password == "password":
            session['logged_in'] = True
            session['username'] = username
            add_log_entry(f"User {username} logged in")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password", "error")
    
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