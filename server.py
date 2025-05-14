from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import time
from datetime import datetime

# Create Flask application
app = Flask(__name__, template_folder='templates')
auth = HTTPBasicAuth()

# Configuration
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_FILE_SIZE', 16 * 1024 * 1024))  # 16MB default
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))

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

# Home page
@app.route('/')
@auth.login_required
def index():
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
    return render_template('index.html', files=files)

# File upload endpoint
@app.route('/upload', methods=['POST'])
def upload_file():
    # For API uploads (no auth required - compatible with your existing script)
    if request.content_type and 'multipart/form-data' in request.content_type:
        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        # If user does not select file
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Save the file with secure filename
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        unique_filename = f"{timestamp}_{filename}"
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        return jsonify({
            'message': 'File uploaded successfully', 
            'filename': unique_filename
        }), 201
    else:
        # Require auth for browser-based uploads
        if not auth.current_user():
            return auth.login_required(lambda: None)()
        
        # Rest of upload handling (same as above)
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        unique_filename = f"{timestamp}_{filename}"
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Redirect back to the index page after uploading
        return redirect(url_for('index'))

# File download endpoint
@app.route('/files/<filename>')
@auth.login_required
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# File list endpoint
@app.route('/files', methods=['GET'])
@auth.login_required
def list_files():
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
    return jsonify(files)

# For running directly
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)