# AI-Powered Object Counter 🎥

A unique AI-powered web application that uses OpenCV and Flask to count and track objects in videos. Upload a video, select a detection method, and get detailed analytics with visual results!

## 🌟 Features

- **Real-time Object Detection**: Uses YOLO deep learning model or motion-based detection
- **Video Analysis**: Processes videos and counts objects frame by frame
- **Interactive Web Interface**: Beautiful, responsive Flask-based frontend
- **Detailed Analytics**: 
  - Total frame count
  - Maximum objects per frame
  - Average objects per frame
  - Object type breakdown
  - Timeline visualization
- **Processed Video Output**: Download the analyzed video with bounding boxes
- **Multiple Detection Methods**:
  - YOLO (Accurate - detects specific object types like people, cars, etc.)
  - Motion Detection (Fast - detects any moving objects)

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Webcam or video files to analyze

## 🚀 Installation

1. **Clone or download this repository**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download YOLO model files** (Optional - for YOLO detection method):
   
   Create a `models` folder and download these files:
   - [yolov3.weights](https://pjreddie.com/media/files/yolov3.weights) (~240MB)
   - [yolov3.cfg](https://github.com/pjreddie/darknet/blob/master/cfg/yolov3.cfg)
   - [coco.names](https://github.com/pjreddie/darknet/blob/master/data/coco.names)

   ```bash
   mkdir models
   cd models
   # Download the files manually or use wget/curl:
   wget https://pjreddie.com/media/files/yolov3.weights
   wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg
   wget https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names
   cd ..
   ```

   **Note**: If you don't download YOLO models, the application will automatically fall back to the motion detection method.

## 🎯 Usage

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Open your web browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **Upload a video**:
   - Click "Choose a video file" button
   - Select a video file (MP4, AVI, MOV, or MKV)
   - Choose detection method (YOLO or Motion Detection)
   - Click "Analyze Video"

4. **View results**:
   - See detailed statistics
   - Watch the processed video with object detections
   - View timeline chart of object counts
   - Download the processed video

## 📁 Project Structure

```
unique powered application/
├── app.py                      # Flask application and routes
├── object_counter.py           # Object detection and counting logic
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── templates/
│   └── index.html             # Main web interface
├── static/
│   ├── css/
│   │   └── style.css          # Application styles
│   ├── js/
│   │   └── app.js             # Frontend JavaScript
│   └── outputs/               # Processed videos and stats (auto-created)
├── uploads/                    # Uploaded videos (auto-created)
└── models/                     # YOLO model files (optional)
    ├── yolov3.weights
    ├── yolov3.cfg
    └── coco.names
```

## 🔧 Configuration

Edit `app.py` to change settings:

```python
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Max file size (100MB)
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'mkv'}
```

## 🎨 Detection Methods

### YOLO (Recommended for Accuracy)
- Detects specific object types (80 classes including person, car, bicycle, etc.)
- More accurate but slower
- Requires model files (~240MB download)
- Best for: Counting specific object types

### Motion Detection (Fast)
- Detects any moving objects
- Faster processing
- No model files required
- Best for: Quick analysis of movement

## 📊 Output

The application generates:
1. **Processed Video**: Video with bounding boxes around detected objects
2. **Statistics JSON**: Detailed analytics saved as JSON file
3. **Visual Dashboard**: Interactive web interface with charts and metrics

## 🐛 Troubleshooting

### YOLO Model Not Loading
- Ensure all three YOLO files are in the `models/` folder
- Application will automatically use motion detection if YOLO fails

### Video Upload Fails
- Check file size (must be under 100MB)
- Ensure video format is supported (MP4, AVI, MOV, MKV)

### Slow Processing
- Use motion detection method for faster results
- Reduce video resolution before uploading
- Use shorter video clips for testing

## 🚀 Future Enhancements

- Real-time webcam analysis
- Custom object detection models
- Multiple video format support
- Batch video processing
- Cloud storage integration
- Advanced tracking algorithms (SORT, DeepSORT)

## 📝 License

This project is open source and available for educational purposes.

## 👨‍💻 Developer

Created with ❤️ using Flask, OpenCV, and modern web technologies.

## 🙏 Credits

- **OpenCV**: Computer vision library
- **YOLO**: Object detection algorithm by Joseph Redmon
- **Flask**: Python web framework
- **Chart.js**: JavaScript charting library
