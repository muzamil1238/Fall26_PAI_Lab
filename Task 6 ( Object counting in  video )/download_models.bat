@echo off
REM Download YOLO model files for Windows

echo Downloading YOLO model files...
echo This may take a few minutes as the weights file is ~240MB

REM Create models directory if it doesn't exist
if not exist models mkdir models
cd models

REM Download files using PowerShell
echo Downloading yolov3.weights...
powershell -Command "Invoke-WebRequest -Uri 'https://pjreddie.com/media/files/yolov3.weights' -OutFile 'yolov3.weights'"

echo Downloading yolov3.cfg...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg' -OutFile 'yolov3.cfg'"

echo Downloading coco.names...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names' -OutFile 'coco.names'"

cd ..

echo Download complete!
echo YOLO model files are now available in the models/ directory
pause
