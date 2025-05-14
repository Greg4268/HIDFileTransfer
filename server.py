from flask import Flask, request
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    return f'File saved to {filepath}', 200

@app.route('/log', methods=['POST'])
def log_data():
    data = request.json
    with open('log.txt', 'a') as f:
        f.write(str(data) + '\n')
    return 'Logged', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
