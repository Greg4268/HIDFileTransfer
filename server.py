from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import time
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__, template_folder='templates')
auth = HTTPBasicAuth()

# Configuration
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', '/tmp/uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_FILE_SIZE', 32 * 1024 * 1024))  # 16MB default
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_testing')

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Add basic authentication
users = {
    os.environ.get('AUTH_USERNAME', "admin"): generate_password_hash(os.environ.get('AUTH_PASSWORD', "change_this_password"))
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None

# Simple test route that doesn't require auth
@app.route('/ping')
def ping():
    return "Server is running!"

# Home page
@app.route('/')
@auth.login_required
def index():
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
        return f"Error: {str(e)}", 500

# File upload endpoint
@app.route('/upload', methods=['POST'])
def upload_file():
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
        return jsonify({'error': str(e)}), 500

# File download endpoint
@app.route('/files/<filename>')
@auth.login_required
def get_file(filename):
    logger.debug(f"Download requested for: {filename}")
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# File delete endpoint
@app.route('/delete/<filename>', methods=['POST'])
@auth.login_required
def delete_file(filename):
    logger.debug(f"Delete requested for: {filename}")
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
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
        return jsonify({'error': str(e)}), 500

#Delete all files endpoint
@app.route('/delete_all', methods=['POST'])
@auth.login_required
def delete_all_files():
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
        return jsonify({'error': str(e)}), 500

# File list endpoint
@app.route('/files', methods=['GET'])
@auth.login_required
def list_files():
    logger.debug("Listing files")
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
        return jsonify(files)
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port)