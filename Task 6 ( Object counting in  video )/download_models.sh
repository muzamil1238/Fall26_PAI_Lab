#!/bin/bash

# Download YOLO model files
echo "Downloading YOLO model files..."
echo "This may take a few minutes as the weights file is ~240MB"

# Create models directory if it doesn't exist
mkdir -p models
cd models

# Download yolov3.weights
echo "Downloading yolov3.weights..."
wget -c https://pjreddie.com/media/files/yolov3.weights

# Download yolov3.cfg
echo "Downloading yolov3.cfg..."
wget -c https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg

# Download coco.names (already included but download for backup)
echo "Downloading coco.names..."
wget -c https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names

cd ..

echo "Download complete!"
echo "YOLO model files are now available in the models/ directory"
