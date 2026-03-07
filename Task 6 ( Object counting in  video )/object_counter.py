import cv2
import numpy as np
import os
from collections import defaultdict
import json
import base64

class ObjectCounter:
    def __init__(self, detection_method='yolo'):
        self.detection_method = detection_method
        self.object_counts = defaultdict(int)
        self.frame_counts = []
        
        # Define classes to detect (only persons and vehicles)
        self.target_classes = {
            'person', 'bicycle', 'car', 'motorbike', 'bus', 
            'train', 'truck', 'boat'
        }
        
        # Load YOLO model
        if detection_method == 'yolo':
            self.load_yolo_model()
        
    def load_yolo_model(self):
        """Load YOLO model for object detection"""
        # Using YOLOv3 - you can also use YOLOv4 or YOLOv5
        try:
            # Download these files from: https://pjreddie.com/darknet/yolo/
            self.net = cv2.dnn.readNet('models/yolov3.weights', 'models/yolov3.cfg')
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            
            # Load class names
            with open('models/coco.names', 'r') as f:
                self.classes = [line.strip() for line in f.readlines()]
                
            self.layer_names = self.net.getLayerNames()
            self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            print("Using background subtraction method instead")
            self.detection_method = 'background_subtraction'
    
    def detect_objects_yolo(self, frame):
        """Detect objects using YOLO"""
        height, width = frame.shape[:2]
        
        # Create blob from image
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward(self.output_layers)
        
        # Process detections
        boxes = []
        confidences = []
        class_ids = []
        
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > 0.5:
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # Apply non-maximum suppression
        indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        
        detected_objects = []
        if len(indices) > 0:
            for i in indices.flatten():
                class_name = self.classes[class_ids[i]]
                # Only include persons and vehicles
                if class_name in self.target_classes:
                    detected_objects.append({
                        'box': boxes[i],
                        'confidence': confidences[i],
                        'class_id': class_ids[i],
                        'class_name': class_name
                    })
        
        return detected_objects
    
    def detect_objects_background_subtraction(self, frame, bg_subtractor):
        """Detect objects using background subtraction (fallback method)"""
        # Apply background subtraction
        fg_mask = bg_subtractor.apply(frame)
        
        # Apply morphological operations to clean up the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detected_objects = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:  # Filter small objects
                x, y, w, h = cv2.boundingRect(contour)
                detected_objects.append({
                    'box': [x, y, w, h],
                    'confidence': 1.0,
                    'class_id': 0,
                    'class_name': 'person/vehicle'
                })
        
        return detected_objects
    
    def draw_detections(self, frame, detected_objects):
        """Draw bounding boxes and labels on frame"""
        for obj in detected_objects:
            x, y, w, h = obj['box']
            class_name = obj['class_name']
            confidence = obj['confidence']
            
            # Draw bounding box
            color = (0, 255, 0)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame
    
    def process_video(self, video_path, output_folder):
        """Process video and count objects"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return {'error': 'Could not open video file'}
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Create output video
        output_filename = os.path.basename(video_path).replace('.', '_processed.')
        output_path = os.path.join(output_folder, output_filename)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Initialize background subtractor if needed
        bg_subtractor = None
        if self.detection_method == 'background_subtraction':
            bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        
        frame_number = 0
        object_timeline = []
        max_objects_per_frame = 0
        total_objects_detected = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_number += 1
            
            # Detect objects
            if self.detection_method == 'yolo':
                detected_objects = self.detect_objects_yolo(frame)
            else:
                detected_objects = self.detect_objects_background_subtraction(frame, bg_subtractor)
            
            # Count objects
            object_count = len(detected_objects)
            max_objects_per_frame = max(max_objects_per_frame, object_count)
            total_objects_detected += object_count
            
            # Track object types
            for obj in detected_objects:
                self.object_counts[obj['class_name']] += 1
            
            # Record timeline data (every 10 frames to reduce data)
            if frame_number % 10 == 0:
                object_timeline.append({
                    'frame': frame_number,
                    'count': object_count
                })
            
            # Draw detections
            frame = self.draw_detections(frame, detected_objects)
            
            # Add frame info
            info_text = f"Frame: {frame_number}/{total_frames} | Objects: {object_count}"
            cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Write frame
            out.write(frame)
            
            # Progress update (optional)
            if frame_number % 100 == 0:
                print(f"Processing: {frame_number}/{total_frames} frames")
        
        cap.release()
        out.release()
        
        # Calculate statistics
        avg_objects = total_objects_detected / total_frames if total_frames > 0 else 0
        
        result = {
            'success': True,
            'output_video': output_filename,
            'statistics': {
                'total_frames': total_frames,
                'max_objects_per_frame': max_objects_per_frame,
                'average_objects_per_frame': round(avg_objects, 2),
                'object_counts': dict(self.object_counts),
                'timeline': object_timeline
            }
        }
        
        # Save statistics to JSON
        stats_filename = output_filename.replace('.mp4', '_stats.json')
        stats_path = os.path.join(output_folder, stats_filename)
        with open(stats_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        return result
    
    def process_video_stream(self, video_path, output_folder):
        """Process video and stream updates in real-time"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            yield {'error': 'Could not open video file'}
            return
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Create output video
        output_filename = os.path.basename(video_path).replace('.', '_processed.')
        output_path = os.path.join(output_folder, output_filename)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Initialize background subtractor if needed
        bg_subtractor = None
        if self.detection_method == 'background_subtraction':
            bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        
        frame_number = 0
        object_timeline = []
        max_objects_per_frame = 0
        total_objects_detected = 0
        
        # Send initial info
        yield {
            'type': 'info',
            'total_frames': total_frames,
            'fps': fps
        }
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_number += 1
            
            # Detect objects
            if self.detection_method == 'yolo':
                detected_objects = self.detect_objects_yolo(frame)
            else:
                detected_objects = self.detect_objects_background_subtraction(frame, bg_subtractor)
            
            # Count objects
            object_count = len(detected_objects)
            max_objects_per_frame = max(max_objects_per_frame, object_count)
            total_objects_detected += object_count
            
            # Track object types
            for obj in detected_objects:
                self.object_counts[obj['class_name']] += 1
            
            # Record timeline data
            if frame_number % 10 == 0:
                object_timeline.append({
                    'frame': frame_number,
                    'count': object_count
                })
            
            # Draw detections
            frame_with_boxes = self.draw_detections(frame.copy(), detected_objects)
            
            # Add frame info
            info_text = f"Frame: {frame_number}/{total_frames} | Objects: {object_count}"
            cv2.putText(frame_with_boxes, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Write frame to output video
            out.write(frame_with_boxes)
            
            # Send update every 30 frames or if objects detected
            if frame_number % 30 == 0 or object_count > 0:
                # Encode frame to base64 for preview
                _, buffer = cv2.imencode('.jpg', frame_with_boxes, [cv2.IMWRITE_JPEG_QUALITY, 70])
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                yield {
                    'type': 'progress',
                    'frame': frame_number,
                    'total_frames': total_frames,
                    'objects_current': object_count,
                    'objects_max': max_objects_per_frame,
                    'progress': int((frame_number / total_frames) * 100),
                    'preview': frame_base64,
                    'object_counts': dict(self.object_counts)
                }
        
        cap.release()
        out.release()
        
        # Calculate final statistics
        avg_objects = total_objects_detected / total_frames if total_frames > 0 else 0
        
        # Send final result
        yield {
            'type': 'complete',
            'output_video': output_filename,
            'statistics': {
                'total_frames': total_frames,
                'max_objects_per_frame': max_objects_per_frame,
                'average_objects_per_frame': round(avg_objects, 2),
                'object_counts': dict(self.object_counts),
                'timeline': object_timeline
            }
        }
