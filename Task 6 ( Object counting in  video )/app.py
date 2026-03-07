from flask import Flask, render_template, request, jsonify, send_from_directory, Response, stream_with_context
import cv2
import numpy as np
import os
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import base64
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'static/outputs'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'mkv'}

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    detection_method = request.form.get('detection_method', 'yolo')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'detection_method': detection_method
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/process_stream/<filename>')
def process_stream(filename):
    detection_method = request.args.get('method', 'yolo')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    def generate():
        from object_counter import ObjectCounter
        counter = ObjectCounter(detection_method)
        
        for update in counter.process_video_stream(filepath, app.config['OUTPUT_FOLDER']):
            yield f"data: {json.dumps(update)}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/results')
def results():
    return render_template('results.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
