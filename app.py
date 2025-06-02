#!/usr/bin/env python3
"""
Easy Mirror - Web-based Webcam with CV Filters
A Flask application that streams webcam video with real-time computer vision filters.
"""

import cv2
import numpy as np
from flask import Flask, render_template, Response, jsonify, request
from flask_cors import CORS
import threading
import time
import logging
import os
import argparse

# Import demo mode for testing
try:
    from demo_mode import DemoCamera
    DEMO_AVAILABLE = True
except ImportError:
    DEMO_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class WebcamFilter:
    def __init__(self):
        self.camera = None
        self.current_filter = 'none'
        self.is_running = False
        self.frame_lock = threading.Lock()
        self.latest_frame = None
        
        # Available filters
        self.filters = {
            'none': self.no_filter,
            'blur': self.blur_filter,
            'edge': self.edge_filter,
            'grayscale': self.grayscale_filter,
            'sepia': self.sepia_filter,
            'invert': self.invert_filter,
            'emboss': self.emboss_filter,
            'cartoon': self.cartoon_filter,
            'vintage': self.vintage_filter,
            'cool': self.cool_filter,
            'warm': self.warm_filter
        }
        
        self.initialize_camera()
    
    def initialize_camera(self):
        """Initialize the camera with fallback options for different systems."""
        # Check if demo mode is requested
        if os.environ.get('DEMO_MODE', '').lower() in ['true', '1', 'yes']:
            if DEMO_AVAILABLE:
                self.camera = DemoCamera()
                logger.info("Demo mode activated - using simulated camera")
                return
            else:
                logger.warning("Demo mode requested but demo_mode.py not available")
        
        camera_indices = [0, 1, 2, -1]  # Try different camera indices
        
        for idx in camera_indices:
            try:
                self.camera = cv2.VideoCapture(idx)
                if self.camera.isOpened():
                    # Set camera properties for better performance
                    self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    self.camera.set(cv2.CAP_PROP_FPS, 30)
                    
                    # Test if we can read a frame
                    ret, frame = self.camera.read()
                    if ret:
                        logger.info(f"Camera initialized successfully on index {idx}")
                        return
                    else:
                        self.camera.release()
            except Exception as e:
                logger.warning(f"Failed to initialize camera on index {idx}: {e}")
                continue
        
        # If no real camera found, try demo mode as fallback
        if DEMO_AVAILABLE:
            logger.info("No real camera found, falling back to demo mode")
            self.camera = DemoCamera()
            return
        
        logger.error("Could not initialize any camera and demo mode not available")
        self.camera = None
    
    def no_filter(self, frame):
        """No filter applied."""
        return frame
    
    def blur_filter(self, frame):
        """Apply Gaussian blur."""
        return cv2.GaussianBlur(frame, (15, 15), 0)
    
    def edge_filter(self, frame):
        """Apply edge detection."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    def grayscale_filter(self, frame):
        """Convert to grayscale."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    
    def sepia_filter(self, frame):
        """Apply sepia tone effect."""
        sepia_kernel = np.array([[0.272, 0.534, 0.131],
                                [0.349, 0.686, 0.168],
                                [0.393, 0.769, 0.189]])
        return cv2.transform(frame, sepia_kernel)
    
    def invert_filter(self, frame):
        """Invert colors."""
        return cv2.bitwise_not(frame)
    
    def emboss_filter(self, frame):
        """Apply emboss effect."""
        kernel = np.array([[-2, -1, 0],
                          [-1, 1, 1],
                          [0, 1, 2]])
        return cv2.filter2D(frame, -1, kernel)
    
    def cartoon_filter(self, frame):
        """Apply cartoon effect."""
        # Reduce colors
        data = np.float32(frame).reshape((-1, 3))
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(data, 8, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers)
        segmented_data = centers[labels.flatten()]
        segmented_image = segmented_data.reshape(frame.shape)
        
        # Create edge mask
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # Combine
        cartoon = cv2.bitwise_and(segmented_image, edges)
        return cartoon
    
    def vintage_filter(self, frame):
        """Apply vintage effect."""
        # Add noise
        noise = np.random.randint(0, 50, frame.shape, dtype=np.uint8)
        vintage = cv2.add(frame, noise)
        
        # Apply sepia-like color transformation
        vintage = cv2.addWeighted(vintage, 0.8, self.sepia_filter(vintage), 0.2, 0)
        
        # Reduce brightness slightly
        vintage = cv2.convertScaleAbs(vintage, alpha=0.9, beta=-10)
        
        return vintage
    
    def cool_filter(self, frame):
        """Apply cool color temperature."""
        # Increase blue channel, decrease red
        frame_cool = frame.copy()
        frame_cool[:, :, 0] = np.clip(frame_cool[:, :, 0] * 1.2, 0, 255)  # Blue
        frame_cool[:, :, 2] = np.clip(frame_cool[:, :, 2] * 0.8, 0, 255)  # Red
        return frame_cool
    
    def warm_filter(self, frame):
        """Apply warm color temperature."""
        # Increase red channel, decrease blue
        frame_warm = frame.copy()
        frame_warm[:, :, 0] = np.clip(frame_warm[:, :, 0] * 0.8, 0, 255)  # Blue
        frame_warm[:, :, 2] = np.clip(frame_warm[:, :, 2] * 1.2, 0, 255)  # Red
        return frame_warm
    
    def get_frame(self):
        """Capture and process a frame."""
        if not self.camera or not self.camera.isOpened():
            return None
        
        ret, frame = self.camera.read()
        if not ret:
            return None
        
        # Apply current filter
        if self.current_filter in self.filters:
            try:
                frame = self.filters[self.current_filter](frame)
            except Exception as e:
                logger.error(f"Error applying filter {self.current_filter}: {e}")
                # Fall back to no filter
                frame = self.no_filter(frame)
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if ret:
            return buffer.tobytes()
        return None
    
    def set_filter(self, filter_name):
        """Set the current filter."""
        if filter_name in self.filters:
            self.current_filter = filter_name
            logger.info(f"Filter changed to: {filter_name}")
            return True
        return False
    
    def get_available_filters(self):
        """Get list of available filters."""
        return list(self.filters.keys())
    
    def cleanup(self):
        """Clean up camera resources."""
        if self.camera:
            self.camera.release()

# Global webcam filter instance
webcam_filter = WebcamFilter()

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route."""
    def generate():
        while True:
            frame = webcam_filter.get_frame()
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                # If no frame available, wait a bit
                time.sleep(0.1)
    
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/filters', methods=['GET'])
def get_filters():
    """Get available filters."""
    return jsonify({
        'filters': webcam_filter.get_available_filters(),
        'current': webcam_filter.current_filter
    })

@app.route('/api/filter', methods=['POST'])
def set_filter():
    """Set the current filter."""
    data = request.get_json()
    if not data or 'filter' not in data:
        return jsonify({'error': 'Filter name required'}), 400
    
    filter_name = data['filter']
    if webcam_filter.set_filter(filter_name):
        return jsonify({'success': True, 'filter': filter_name})
    else:
        return jsonify({'error': 'Invalid filter name'}), 400

@app.route('/api/status')
def get_status():
    """Get camera and application status."""
    camera_available = webcam_filter.camera is not None and webcam_filter.camera.isOpened()
    return jsonify({
        'camera_available': camera_available,
        'current_filter': webcam_filter.current_filter,
        'filters_count': len(webcam_filter.get_available_filters())
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Easy Mirror - Webcam with CV Filters')
    parser.add_argument('--port', type=int, default=12000, help='Port to run the server on (default: 12000)')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    try:
        # Run the Flask app
        logger.info(f"Starting Easy Mirror on {args.host}:{args.port}")
        app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        webcam_filter.cleanup()