#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def test_detection():
    """Test object detection with YOLO"""
    
    print("=== Test Object Detection ===")
    
    try:
        from ultralytics import YOLO
        import cv2
        import numpy as np
        
        # Load model
        model_path = "models/yolov8n.pt"
        print(f"Loading model: {model_path}")
        model = YOLO(model_path)
        
        # Test with a simple image or video frame
        video_path = "videos/6p-c0.avi"
        print(f"Testing with video: {video_path}")
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"❌ Error: Could not open video {video_path}")
            return
        
        # Read first frame
        ret, frame = cap.read()
        if not ret:
            print("❌ Error: Could not read frame from video")
            cap.release()
            return
        
        print(f"✅ Frame read successfully: {frame.shape}")
        
        # Run detection
        print("Running detection...")
        results = model(frame, conf=0.1, verbose=False)
        
        # Check results
        for i, result in enumerate(results):
            boxes = result.boxes
            if boxes is not None:
                print(f"✅ Detection successful! Found {len(boxes)} objects")
                
                # Print detected objects
                for j, box in enumerate(boxes):
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    coords = box.xyxy[0].cpu().numpy()
                    print(f"  Object {j+1}: Class {cls}, Confidence {conf:.3f}, Coords {coords}")
            else:
                print("❌ No objects detected")
        
        cap.release()
        
        # Test with planes video
        print("\n--- Testing with planes video ---")
        planes_video = "videos/planes_sample.mp4"
        cap = cv2.VideoCapture(planes_video)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ Planes frame read: {frame.shape}")
                results = model(frame, conf=0.1, verbose=False)
                
                for i, result in enumerate(results):
                    boxes = result.boxes
                    if boxes is not None:
                        print(f"✅ Planes detection: Found {len(boxes)} objects")
                        for j, box in enumerate(boxes):
                            cls = int(box.cls[0])
                            conf = float(box.conf[0])
                            coords = box.xyxy[0].cpu().numpy()
                            print(f"  Object {j+1}: Class {cls}, Confidence {conf:.3f}, Coords {coords}")
                    else:
                        print("❌ No objects detected in planes video")
            cap.release()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_detection()

