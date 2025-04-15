"""
Automated Zoom Poll Generator - Web Demo Version
Flask web application that simulates the desktop automation functionality
"""

import os
import time
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

# Import dotenv for environment variable management
from dotenv import load_dotenv
load_dotenv()

# Try API-based approach if API key is available
try:
    import openai
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    if OPENAI_API_KEY:
        openai.api_key = OPENAI_API_KEY
        USE_API = True
    else:
        USE_API = False
except (ImportError, Exception):
    USE_API = False

# Set up app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Initialize session variables
def init_session():
    if 'logged_in' not in session:
        session['logged_in'] = False
    if 'zoom_client_type' not in session:
        session['zoom_client_type'] = 'web'  # Default to web client
    if 'recent_transcript' not in session:
        session['recent_transcript'] = ''
    if 'current_poll' not in session:
        session['current_poll'] = None
    if 'running' not in session:
        session['running'] = False
    if 'log_entries' not in session:
        session['log_entries'] = []
    if 'next_transcript_time' not in session:
        session['next_transcript_time'] = None
    if 'next_poll_time' not in session:
        session['next_poll_time'] = None

# In-memory log storage
log_entries = []

# Simulated feature flags
HAS_CHATGPT_BROWSER_INTEGRATION = False  # Set to True when implemented
HAS_ZOOM_DESKTOP_INTEGRATION = False     # Set to True when implemented
HAS_ZOOM_WEB_INTEGRATION = True         # Demo mode always supports web simulation

# Check if in demo mode
DEMO_MODE = True  # Set to False in production

# Generate a poll using OpenAI API
def generate_poll_with_openai(transcript):
    """Generate a poll using OpenAI API"""
    if not USE_API:
        return None
        
    try:
        prompt = f"""Based on the transcript below, generate one poll question with four engaging answer options.
Format your response as follows:
Question: [Your question here]
Option 1: [First option]
Option 2: [Second option]
Option 3: [Third option]
Option 4: [Fourth option]

Here's the transcript:
{transcript}
"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates engaging poll questions based on meeting transcripts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        
        if response and response.choices and len(response.choices) > 0:
            poll_text = response.choices[0].message.content
            return parse_chatgpt_response(poll_text)
        else:
            return None
    except Exception as e:
        app.logger.error(f"Error generating poll with OpenAI: {str(e)}")
        return None

# Parse response from ChatGPT to extract question and options
def parse_chatgpt_response(response_text):
    """Parse the ChatGPT response to extract question and options"""
    try:
        # Extract question using regex
        question_match = re.search(r"Question:?\s*(.+?)(?:\n|$)", response_text)
        if not question_match:
            # Try alternative format
            question_match = re.search(r"Poll Question:?\s*(.+?)(?:\n|$)", response_text)
            
        if not question_match:
            app.logger.error("Could not find question in ChatGPT response")
            return None
            
        question = question_match.group(1).strip()
        
        # Extract options using regex
        option_matches = re.findall(r"Option\s*\d+:?\s*(.+?)(?:\n|$)", response_text)
        
        if len(option_matches) < 2:
            # Try alternative format (A, B, C, D)
            option_matches = re.findall(r"[A-D][.):]\s*(.+?)(?:\n|$)", response_text)
        
        if len(option_matches) < 2:
            # Try another format common in ChatGPT responses
            option_matches = re.findall(r"\d+[.):]\s*(.+?)(?:\n|$)", response_text)
            
        if len(option_matches) < 2:
            app.logger.error(f"Not enough options found in ChatGPT response (found {len(option_matches)})")
            return None
            
        # Limit to 4 options
        options = option_matches[:4]
        
        return {
            "question": question,
            "options": options
        }
        
    except Exception as e:
        app.logger.error(f"Error parsing ChatGPT response: {str(e)}")
        return None

# Add a log entry with timestamp
def add_log_entry(message):
    """Add a log entry with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {"timestamp": timestamp, "message": message}
    log_entries.append(log_entry)
    # Keep only the last 100 entries
    if len(log_entries) > 100:
        log_entries.pop(0)
    app.logger.info(message)

# Simulate capturing a transcript from Zoom
def simulate_transcript_capture():
    """Simulate capturing a transcript from Zoom"""
    add_log_entry("Simulating transcript capture from Zoom")
    
    # Different examples of simulated transcripts for demo purposes
    transcript_examples = [
        "We're discussing the new product launch scheduled for next month. The team has completed the initial market research and we're seeing positive feedback from focus groups. There are still some concerns about production timelines that we need to address in today's meeting.",
        
        "Today's agenda includes reviewing the quarterly financial results and discussing the expansion plans for the Asia-Pacific region. The numbers show we're exceeding expectations in North America but facing challenges in European markets due to regulatory changes.",
        
        "The engineering team has identified some performance issues with the latest software update. We need to decide whether to delay the release or go ahead with a partial rollout. Security testing has already been completed, but there are still concerns about stability under high-load conditions.",
        
        "For the upcoming conference, we need to finalize the speaker list and schedule. Marketing has proposed a new format for the panel discussions that could increase audience engagement. We also need to discuss the budget constraints and make some decisions about the venue options.",
        
        "The customer satisfaction survey results are in, and there are several areas we need to improve. The support response time is the biggest concern, followed by product documentation clarity. On the positive side, our new features have been very well received, especially the collaboration tools."
    ]
    
    # Select a random transcript example
    import random
    transcript = random.choice(transcript_examples)
    
    add_log_entry(f"Captured transcript: {len(transcript)} characters")
    
    # Store the transcript in session
    session['recent_transcript'] = transcript
    
    return transcript

# Simulate posting a poll to Zoom
def simulate_poll_posting(poll_data):
    """Simulate posting a poll to Zoom"""
    if not poll_data:
        add_log_entry("Error: No poll data available for posting")
        return False
        
    add_log_entry(f"Simulating posting poll to Zoom: {poll_data['question']}")
    
    # For demo, just log what would happen in the real version
    add_log_entry(f"Poll question: {poll_data['question']}")
    for idx, option in enumerate(poll_data['options']):
        add_log_entry(f"Option {idx+1}: {option}")
        
    add_log_entry("Poll posted successfully")
    
    # Clear current poll after posting
    session['current_poll'] = None
    
    return True

# Update the next scheduled times for transcript capture and poll posting
def update_scheduled_times():
    """Update the next scheduled times for transcript capture and poll posting"""
    now = datetime.now()
    
    # Schedule next transcript capture for 10 minutes from now
    next_transcript_time = now + timedelta(minutes=10)
    session['next_transcript_time'] = next_transcript_time.strftime("%H:%M:%S")
    
    # Schedule next poll posting for 15 minutes from now
    next_poll_time = now + timedelta(minutes=15)
    session['next_poll_time'] = next_poll_time.strftime("%H:%M:%S")


# Routes
@app.route('/')
def index():
    """Main page"""
    init_session()
    return render_template(
        'index.html',
        logged_in=session.get('logged_in', False),
        zoom_client_type=session.get('zoom_client_type', 'web'),
        running=session.get('running', False),
        has_transcript=bool(session.get('recent_transcript', '')),
        has_poll=bool(session.get('current_poll')),
        next_transcript_time=session.get('next_transcript_time'),
        next_poll_time=session.get('next_poll_time'),
        demo_mode=DEMO_MODE
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    init_session()
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        client_type = request.form.get('client_type', 'web')
        
        # For demo, accept any non-empty credentials
        if username and password:
            session['logged_in'] = True
            session['zoom_client_type'] = client_type
            add_log_entry(f"Logged in successfully. Using {client_type} Zoom client.")
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/chatgpt_setup', methods=['GET', 'POST'])
def chatgpt_setup():
    """ChatGPT credentials setup"""
    init_session()
    
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        chatgpt_email = request.form.get('chatgpt_email')
        chatgpt_password = request.form.get('chatgpt_password')
        
        # For demo, accept any non-empty credentials
        if chatgpt_email and chatgpt_password:
            add_log_entry("ChatGPT credentials stored securely (not saved to disk)")
            flash('ChatGPT credentials stored successfully!', 'success')
            
            # Direct to browser integration if implemented, otherwise use API
            if HAS_CHATGPT_BROWSER_INTEGRATION:
                add_log_entry("Using ChatGPT browser integration")
            elif USE_API:
                add_log_entry("Using ChatGPT API integration")
            else:
                add_log_entry("Using demo mode for ChatGPT integration")
                
            return redirect(url_for('index'))
        else:
            flash('Please provide valid ChatGPT credentials', 'error')
    
    return render_template('chatgpt_setup.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    # Stop scheduler if running
    if session.get('running', False):
        session['running'] = False
        add_log_entry("Scheduler stopped on logout")
    
    # Clear session
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

# API Routes
@app.route('/api/start_scheduler', methods=['POST'])
def start_scheduler():
    """Start the scheduler"""
    init_session()
    
    if not session.get('logged_in', False):
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    if session.get('running', False):
        return jsonify({"success": False, "message": "Scheduler already running"}), 400
    
    session['running'] = True
    update_scheduled_times()
    add_log_entry("Scheduler started")
    
    return jsonify({"success": True, "message": "Scheduler started successfully"})

@app.route('/api/stop_scheduler', methods=['POST'])
def stop_scheduler():
    """Stop the scheduler"""
    init_session()
    
    if not session.get('logged_in', False):
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    if not session.get('running', False):
        return jsonify({"success": False, "message": "Scheduler not running"}), 400
    
    session['running'] = False
    add_log_entry("Scheduler stopped")
    
    return jsonify({"success": True, "message": "Scheduler stopped successfully"})

@app.route('/api/capture_transcript', methods=['POST'])
def capture_transcript():
    """Capture a transcript"""
    init_session()
    
    if not session.get('logged_in', False):
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    # Capture transcript
    transcript = simulate_transcript_capture()
    
    if transcript:
        # Update next scheduled transcript time
        now = datetime.now()
        next_transcript_time = now + timedelta(minutes=10)
        session['next_transcript_time'] = next_transcript_time.strftime("%H:%M:%S")
        
        return jsonify({
            "success": True, 
            "message": "Transcript captured successfully",
            "transcript_length": len(transcript),
            "next_transcript_time": session['next_transcript_time']
        })
    else:
        return jsonify({"success": False, "message": "Failed to capture transcript"}), 500

@app.route('/api/generate_poll', methods=['POST'])
def generate_poll():
    """Generate a poll using the most recent transcript"""
    init_session()
    
    if not session.get('logged_in', False):
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    transcript = session.get('recent_transcript', '')
    
    if not transcript:
        return jsonify({"success": False, "message": "No transcript available"}), 400
    
    # Use OpenAI API if available, otherwise use demo data
    if USE_API:
        poll_data = generate_poll_with_openai(transcript)
    else:
        # Demo poll data
        poll_data = {
            "question": "What is the most important topic to discuss next?",
            "options": [
                "Product timeline",
                "Budget concerns",
                "Market research findings",
                "Team resources"
            ]
        }
    
    if poll_data:
        session['current_poll'] = poll_data
        add_log_entry(f"Poll generated: {poll_data['question']}")
        return jsonify({
            "success": True, 
            "message": "Poll generated successfully",
            "poll_data": poll_data
        })
    else:
        return jsonify({"success": False, "message": "Failed to generate poll"}), 500

@app.route('/api/post_poll', methods=['POST'])
def post_poll():
    """Post the current poll"""
    init_session()
    
    if not session.get('logged_in', False):
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    poll_data = session.get('current_poll')
    
    if not poll_data:
        return jsonify({"success": False, "message": "No poll available to post"}), 400
    
    success = simulate_poll_posting(poll_data)
    
    if success:
        # Update next scheduled poll time
        now = datetime.now()
        next_poll_time = now + timedelta(minutes=15)
        session['next_poll_time'] = next_poll_time.strftime("%H:%M:%S")
        
        return jsonify({
            "success": True, 
            "message": "Poll posted successfully",
            "next_poll_time": session['next_poll_time']
        })
    else:
        return jsonify({"success": False, "message": "Failed to post poll"}), 500

@app.route('/api/get_status', methods=['GET'])
def get_status():
    """Get the current status"""
    init_session()
    
    if not session.get('logged_in', False):
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    status = {
        "logged_in": session.get('logged_in', False),
        "zoom_client_type": session.get('zoom_client_type', 'web'),
        "running": session.get('running', False),
        "has_transcript": bool(session.get('recent_transcript', '')),
        "has_poll": bool(session.get('current_poll')),
        "next_transcript_time": session.get('next_transcript_time'),
        "next_poll_time": session.get('next_poll_time'),
        "demo_mode": DEMO_MODE,
        "api_available": USE_API
    }
    
    return jsonify({"success": True, "status": status})

@app.route('/api/get_logs', methods=['GET'])
def get_logs():
    """Get the log entries"""
    init_session()
    
    if not session.get('logged_in', False):
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    return jsonify({"success": True, "logs": log_entries})

@app.route('/api/export_logs', methods=['GET'])
def export_logs():
    """Export logs as JSON"""
    init_session()
    
    if not session.get('logged_in', False):
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    export_data = {
        "application": "Zoom Poll Generator",
        "export_time": datetime.now().isoformat(),
        "logs": log_entries
    }
    
    return jsonify(export_data)

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 5000))
    
    # Add initial log entry
    add_log_entry("Application started")
    
    # Run app
    app.run(host='0.0.0.0', port=port, debug=True)