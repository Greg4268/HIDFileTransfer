from flask import Flask, request, abort, jsonify, render_template, redirect, url_for, send_from_directory
from flask_httpauth import HTTPBasicAuth
from flask_limiter import Limiter
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from pathlib import Path
import os
import time
import sys
import logging
from datetime import datetime

env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("API_KEY")

# Validate API key is set
if not api_key:
    raise ValueError("API_KEY must be set in environment variables")

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__, template_folder='../templates')
auth = HTTPBasicAuth()

# Create limiter AFTER app is defined
limiter = Limiter(
    app,
    default_limits=["200 per day", "50 per hour"]
)

# Configuration
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', '/tmp/uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_FILE_SIZE', 4 * 1024 * 1024))  # 4MB default
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
api_key = app.config['SECRET_KEY']
if not api_key: 
    raise ValueError("NOT API KEY. CHeck environment configs")

username = os.environ.get('AUTH_USERNAME')
password = os.environ.get('AUTH_PASSWORD')
if not username or not password: 
    raise ValueError("AUTH_USERNAME and AUTH_PASSWORD must be set")
users = {username: generate_password_hash(password)}

# Approved file extensions
approved_files = ('.png', '.jpg', '.jpeg', '.img', '.svg', '.mp3', '.mp4', '.txt', '.xlsx', '.docx')

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def check_api_key():
    """Check if API key is valid"""
    client_key = request.headers.get('X-API-Key')
    if not client_key or not api_key or client_key != api_key:
        logger.warning(f"API key check failed. Client key: {client_key[:10] + '...' if client_key else 'None'}")
        abort(403)

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None

# Home page - only requires HTTP Basic Auth (for web interface)
@app.route('/')
@auth.login_required
def index():
    # No API key check for web interface
    logger.debug("Accessing index page")
    try:
        files = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(path):
                size = os.path.getsize(path)
                modified = datetime.fromtimestamp(os.path.getmtime(path))
                files.append({
                    'name': filename,
                    'size': size,
                    'modified': modified.strftime('%Y-%m-%d %H:%M:%S')
                })
        logger.debug(f"Found {len(files)} files")
        return render_template('index.html', files=files)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# File upload endpoint
@app.route('/upload', methods=['POST'])
@limiter.limit("5 per minute")
def upload_file():
    check_api_key()  # Check API key
    
    logger.debug("Upload endpoint called")
    
    # Check if the post request has the file part
    if 'file' not in request.files:
        logger.error("No file part in request")
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    logger.debug(f"File received: {file.filename}")
    
    # If user does not select file
    if file.filename == '':
        logger.error("Empty filename")
        return jsonify({'error': 'No selected file'}), 400

    # Check file extension
    if not file.filename.lower().endswith(approved_files):
        logger.debug("Unwanted file type sent for upload. Rejecting")
        return jsonify({'error': 'Unwanted file type'}), 400

    # Check file size
    if file.content_length and file.content_length > app.config['MAX_CONTENT_LENGTH']:
        logger.error("File too big, ignoring")
        return jsonify({'error': 'File too large'}), 413
    
    try:
        # Save the file with secure filename
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        unique_filename = f"{timestamp}_{filename}"
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        logger.debug(f"Saving file to: {file_path}")
        file.save(file_path)
        
        logger.debug("File saved successfully")
        return jsonify({
            'message': 'File uploaded successfully', 
            'filename': unique_filename
        }), 201
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# File download endpoint - only requires HTTP Basic Auth (for web interface)
@app.route('/files/<filename>')
@auth.login_required
def get_file(filename):
    # No API key check for web interface downloads
    logger.debug(f"Download requested for: {filename}")
    
    # Validate filename
    if not filename.lower().endswith(approved_files):
        abort(400)
    
    # Check for path traversal
    if '..' in filename or '/' in filename:
        abort(400)

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Ensure file is within upload directory
    if not os.path.commonpath([file_path, app.config['UPLOAD_FOLDER']]) == app.config['UPLOAD_FOLDER']:
        abort(400)
    
    # Check if file exists
    if not os.path.exists(file_path):
        abort(404)
        
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# File delete endpoint - only requires HTTP Basic Auth (for web interface)
@app.route('/delete/<filename>', methods=['POST'])
@auth.login_required
def delete_file(filename):
    # No API key check for web interface
    logger.debug(f"Delete requested for: {filename}")
    
    # Validate filename
    if '..' in filename or '/' in filename:
        abort(400)
    
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Ensure file is within upload directory
        if not os.path.commonpath([file_path, app.config['UPLOAD_FOLDER']]) == app.config['UPLOAD_FOLDER']:
            abort(400)
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return jsonify({'error': 'File not found'}), 404
            
        # Delete the file
        os.remove(file_path)
        logger.info(f"File deleted: {filename}")
        
        # Redirect back to the index page
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Delete all files endpoint - only requires HTTP Basic Auth (for web interface)
@app.route('/delete_all', methods=['POST'])
@auth.login_required
def delete_all_files():
    # No API key check for web interface
    logger.debug("Delete all files requested")
    try:
        count = 0
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                count += 1
                
        logger.info(f"Deleted {count} files")
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error deleting all files: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Add security headers
@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# Error handlers
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden'}), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port)