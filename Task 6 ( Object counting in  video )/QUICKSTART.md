# Quick Start Guide

## Installation Steps

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Download YOLO models** (Optional - for better accuracy):
   
   **For Windows**:
   ```bash
   download_models.bat
   ```
   
   **For Linux/Mac**:
   ```bash
   chmod +x download_models.sh
   ./download_models.sh
   ```

   Or skip this step to use the faster motion detection method.

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser**:
   Navigate to http://localhost:5000

## Quick Test

1. Upload a video file (MP4, AVI, MOV, or MKV)
2. Choose detection method:
   - **YOLO**: More accurate, detects specific objects (person, car, etc.)
   - **Motion Detection**: Faster, detects any moving objects
3. Click "Analyze Video" and wait for processing
4. View results with statistics and processed video

## Sample Videos

You can test with any video containing:
- People walking
- Cars driving
- Animals moving
- Sports activities
- Any scene with moving objects

## Troubleshooting

- If YOLO doesn't work, the app automatically uses motion detection
- For large videos, consider using motion detection for faster processing
- Ensure video file is under 100MB
