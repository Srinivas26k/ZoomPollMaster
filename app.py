"""
Automated Zoom Poll Generator - Web Demo Version
Flask web application that simulates the desktop automation functionality
"""

import os
import time
import json
import logging
import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
import openai
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", os.urandom(24).hex())
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
TRANSCRIPT_CAPTURE_INTERVAL = 10 * 60  # 10 minutes in seconds
POLL_POSTING_INTERVAL = 15 * 60  # 15 minutes in seconds
CHATGPT_PROMPT = """Based on the transcript below, generate one poll question with four engaging answer options. 
Format your response as follows:
Question: [Your question here]
Option 1: [First option]
Option 2: [Second option]
Option 3: [Third option]
Option 4: [Fourth option]

Here's the transcript:
"""

# In-memory storage
credentials = {}
transcripts = []
current_poll = None
scheduler_status = {
    "is_running": False,
    "next_transcript_capture": None,
    "next_poll_posting": None,
    "log_entries": []
}

# OpenAI Integration
def generate_poll_with_openai(transcript):
    """Generate a poll using OpenAI API"""
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.error("OpenAI API key not found")
            add_log_entry("ERROR: OpenAI API key not found")
            return None

        openai.api_key = api_key
        client = openai.Client(api_key=api_key)
        
        # Create the full prompt with transcript
        full_prompt = f"{CHATGPT_PROMPT}\n\n{transcript}"
        
        # Send request to OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=500
        )
        
        # Get the response text
        response_text = response.choices[0].message.content
        
        # Parse the response to extract question and options
        return parse_chatgpt_response(response_text)
    
    except Exception as e:
        logger.error(f"Error generating poll with OpenAI: {str(e)}")
        add_log_entry(f"ERROR: Failed to generate poll - {str(e)}")
        return None

def parse_chatgpt_response(response_text):
    """Parse the ChatGPT response to extract question and options"""
    try:
        lines = response_text.strip().split('\n')
        
        question = None
        options = []
        
        for line in lines:
            if line.startswith('Question:'):
                question = line.replace('Question:', '').strip()
            elif line.startswith('Option '):
                option = line.split(':', 1)[1].strip() if ':' in line else line.strip()
                options.append(option)
        
        if question and len(options) >= 2:
            # Limit to 4 options
            options = options[:4]
            
            poll_data = {
                "question": question,
                "options": options
            }
            
            logger.info(f"Successfully parsed poll: {question}")
            add_log_entry(f"INFO: Successfully generated poll: {question}")
            return poll_data
        else:
            logger.error("Failed to parse poll from OpenAI response")
            add_log_entry("ERROR: Failed to parse poll from OpenAI response")
            return None
            
    except Exception as e:
        logger.error(f"Error parsing OpenAI response: {str(e)}")
        add_log_entry(f"ERROR: Error parsing OpenAI response - {str(e)}")
        return None

# Logging functions
def add_log_entry(message):
    """Add a log entry with timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - {message}"
    scheduler_status["log_entries"].append(log_entry)
    # Keep log size manageable
    if len(scheduler_status["log_entries"]) > 100:
        scheduler_status["log_entries"] = scheduler_status["log_entries"][-100:]
    return log_entry

# Simulated functionality
def simulate_transcript_capture():
    """Simulate capturing a transcript from Zoom"""
    add_log_entry("INFO: Capturing transcript from Zoom")
    
    # Generate a simulated transcript
    sample_transcripts = [
        "We're discussing the new product features today. The main focus is on improving user experience and reducing load times. We need to prioritize which features to implement first.",
        "The marketing team presented their Q2 results. We saw a 15% increase in engagement when we launched the email campaign. Social media metrics were also strong.",
        "Today's meeting is about the upcoming conference. We need volunteers for the booth and speakers for three workshop sessions. Please let me know if you're interested.",
        "We need to address the customer feedback about the checkout process. Several users reported it's too complicated. Let's simplify it in our next sprint."
    ]
    
    import random
    transcript = random.choice(sample_transcripts)
    
    # Add some randomization to make it seem different each time
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    transcript = f"[{current_time}] {transcript}"
    
    # Store the transcript
    transcripts.append(transcript)
    if len(transcripts) > 5:
        transcripts.pop(0)  # Keep only the 5 most recent transcripts
    
    add_log_entry(f"INFO: Transcript captured ({len(transcript)} characters)")
    
    return transcript

def simulate_poll_posting(poll_data):
    """Simulate posting a poll to Zoom"""
    if not poll_data:
        add_log_entry("ERROR: No poll data available to post")
        return False
    
    add_log_entry(f"INFO: Posting poll to Zoom: {poll_data['question']}")
    time.sleep(1)  # Simulate some processing time
    
    # In a real app, this would use PyAutoGUI to navigate Zoom UI
    add_log_entry("INFO: Poll successfully posted to Zoom")
    
    return True

# Update scheduled times
def update_scheduled_times():
    """Update the next scheduled times for transcript capture and poll posting"""
    now = datetime.datetime.now()
    
    if scheduler_status["is_running"]:
        # Set next transcript capture time
        scheduler_status["next_transcript_capture"] = (now + datetime.timedelta(seconds=TRANSCRIPT_CAPTURE_INTERVAL)).strftime("%Y-%m-%d %H:%M:%S")
        
        # Set next poll posting time
        scheduler_status["next_poll_posting"] = (now + datetime.timedelta(seconds=POLL_POSTING_INTERVAL)).strftime("%Y-%m-%d %H:%M:%S")
    else:
        scheduler_status["next_transcript_capture"] = None
        scheduler_status["next_poll_posting"] = None

# Routes
@app.route('/')
def index():
    """Main page"""
    # Check if logged in
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    return render_template('index.html', 
                           scheduler_status=scheduler_status,
                           transcripts=transcripts,
                           current_poll=current_poll)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    error = None
    
    if request.method == 'POST':
        # Simulate Zoom credentials validation
        zoom_meeting_id = request.form.get('zoom_meeting_id')
        zoom_passcode = request.form.get('zoom_passcode')
        
        # Simple validation
        if zoom_meeting_id and zoom_passcode:
            # Store credentials in memory
            credentials['zoom'] = {
                'meeting_id': zoom_meeting_id,
                'passcode': zoom_passcode
            }
            
            session['logged_in'] = True
            add_log_entry("INFO: User logged in with Zoom credentials")
            return redirect(url_for('index'))
        else:
            error = "Please provide both Meeting ID and Passcode"
    
    return render_template('login.html', error=error)

@app.route('/chatgpt_setup', methods=['GET', 'POST'])
def chatgpt_setup():
    """ChatGPT credentials setup"""
    error = None
    
    if request.method == 'POST':
        # Check if we already have API key in environment
        if os.environ.get("OPENAI_API_KEY"):
            add_log_entry("INFO: Using existing OpenAI API key from environment")
            return redirect(url_for('index'))
        
        # Get API key from form
        api_key = request.form.get('api_key')
        
        if api_key:
            # In a production app, store securely - here we're just using env var
            os.environ["OPENAI_API_KEY"] = api_key
            add_log_entry("INFO: OpenAI API key configured")
            return redirect(url_for('index'))
        else:
            error = "Please provide a valid API key"
    
    # Check if we already have API key
    has_api_key = bool(os.environ.get("OPENAI_API_KEY"))
    
    return render_template('chatgpt_setup.html', error=error, has_api_key=has_api_key)

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/start', methods=['POST'])
def start_scheduler():
    """Start the scheduler"""
    global scheduler_status
    
    # Check if OpenAI API key is configured
    if not os.environ.get("OPENAI_API_KEY"):
        return jsonify({
            "success": False,
            "message": "OpenAI API key not configured. Please set it up first."
        })
    
    scheduler_status["is_running"] = True
    update_scheduled_times()
    add_log_entry("INFO: Scheduler started")
    
    return jsonify({
        "success": True,
        "message": "Scheduler started successfully"
    })

@app.route('/api/stop', methods=['POST'])
def stop_scheduler():
    """Stop the scheduler"""
    global scheduler_status
    
    scheduler_status["is_running"] = False
    update_scheduled_times()
    add_log_entry("INFO: Scheduler stopped")
    
    return jsonify({
        "success": True,
        "message": "Scheduler stopped successfully"
    })

@app.route('/api/capture_transcript', methods=['POST'])
def capture_transcript():
    """Capture a transcript"""
    transcript = simulate_transcript_capture()
    
    return jsonify({
        "success": True,
        "message": "Transcript captured successfully",
        "transcript": transcript
    })

@app.route('/api/generate_poll', methods=['POST'])
def generate_poll():
    """Generate a poll using the most recent transcript"""
    global current_poll
    
    # Get the most recent transcript
    if not transcripts:
        # If no transcript available, capture one
        transcript = simulate_transcript_capture()
    else:
        transcript = transcripts[-1]
    
    add_log_entry("INFO: Generating poll from transcript")
    
    # Generate poll
    current_poll = generate_poll_with_openai(transcript)
    
    if current_poll:
        return jsonify({
            "success": True,
            "message": "Poll generated successfully",
            "poll": current_poll
        })
    else:
        return jsonify({
            "success": False,
            "message": "Failed to generate poll"
        })

@app.route('/api/post_poll', methods=['POST'])
def post_poll():
    """Post the current poll"""
    global current_poll
    
    if not current_poll:
        return jsonify({
            "success": False,
            "message": "No poll available to post"
        })
    
    # Simulate posting poll
    success = simulate_poll_posting(current_poll)
    
    if success:
        # Clear current poll after posting
        poll_data = current_poll
        current_poll = None
        
        return jsonify({
            "success": True,
            "message": "Poll posted successfully",
            "poll": poll_data
        })
    else:
        return jsonify({
            "success": False,
            "message": "Failed to post poll"
        })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get the current status"""
    return jsonify({
        "scheduler_status": scheduler_status,
        "has_transcript": len(transcripts) > 0,
        "current_poll": current_poll,
        "recent_transcripts": transcripts
    })

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get the log entries"""
    return jsonify({
        "logs": scheduler_status["log_entries"]
    })

@app.route('/api/export_logs', methods=['GET'])
def export_logs():
    """Export logs as JSON"""
    log_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "logs": scheduler_status["log_entries"]
    }
    
    from flask import Response
    return Response(
        json.dumps(log_data, indent=2),
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment;filename=zoom_poll_generator_logs.json'}
    )

if __name__ == '__main__':
    # Generate a unique session ID
    if not app.secret_key:
        app.secret_key = os.urandom(24).hex()
    
    # Add initial log entry
    add_log_entry("INFO: Application started")
    
    app.run(host='0.0.0.0', port=5000, debug=True)