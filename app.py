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

# Import demo mode for testing
try:
    from demo_mode import DemoCamera
    DEMO_AVAILABLE = True
except ImportError:
    DEMO_AVAILABLE = False

# Import clothing overlay system
try:
    from clothing_overlay import ClothingOverlay
    CLOTHING_AVAILABLE = True
except ImportError:
    CLOTHING_AVAILABLE = False
    logging.warning("Clothing overlay not available - install mediapipe to enable clothing filters")

# Import anthropometric measurements system
try:
    from anthropometric_measurements import AnthropometricMeasurements
    MEASUREMENTS_AVAILABLE = True
except ImportError:
    MEASUREMENTS_AVAILABLE = False
    logging.warning("Anthropometric measurements not available - install mediapipe to enable measurements")

# Import sex prediction system
try:
    from sex_prediction import SexPredictor
    SEX_PREDICTION_AVAILABLE = True
except ImportError:
    SEX_PREDICTION_AVAILABLE = False
    logging.warning("Sex prediction not available")

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
        
        # Initialize clothing overlay system
        self.clothing_overlay = None
        if CLOTHING_AVAILABLE:
            try:
                self.clothing_overlay = ClothingOverlay()
                logger.info("Clothing overlay system initialized")
            except Exception as e:
                logger.error(f"Failed to initialize clothing overlay: {e}")
        
        # Initialize anthropometric measurements system
        self.anthropometric_measurements = None
        if MEASUREMENTS_AVAILABLE:
            try:
                self.anthropometric_measurements = AnthropometricMeasurements()
                logger.info("Anthropometric measurements system initialized")
            except Exception as e:
                logger.error(f"Failed to initialize anthropometric measurements: {e}")
        
        # Initialize sex prediction system
        self.sex_predictor = None
        if SEX_PREDICTION_AVAILABLE:
            try:
                self.sex_predictor = SexPredictor()
                logger.info("Sex prediction system initialized")
            except Exception as e:
                logger.error(f"Failed to initialize sex prediction: {e}")
        
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
            'warm': self.warm_filter,
            'clothing': self.clothing_filter
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
    
    def clothing_filter(self, frame):
        """Apply clothing overlay filter."""
        if self.clothing_overlay:
            return self.clothing_overlay.apply_clothing_filter(frame)
        return frame
    
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
        'filters_count': len(webcam_filter.get_available_filters()),
        'clothing_available': CLOTHING_AVAILABLE,
        'measurements_available': MEASUREMENTS_AVAILABLE
    })

@app.route('/api/clothing', methods=['GET'])
def get_clothing():
    """Get available clothing items and current selection."""
    if not webcam_filter.clothing_overlay:
        return jsonify({'error': 'Clothing system not available'}), 400
    
    return jsonify({
        'available': webcam_filter.clothing_overlay.get_available_clothing(),
        'current': webcam_filter.clothing_overlay.get_current_clothing()
    })

@app.route('/api/clothing/<category>/<item_id>', methods=['POST'])
def set_clothing_item(category, item_id):
    """Set a clothing item for a specific category."""
    if not webcam_filter.clothing_overlay:
        return jsonify({'error': 'Clothing system not available'}), 400
    
    # Handle 'none' as removing the item
    if item_id.lower() == 'none':
        item_id = None
    
    if webcam_filter.clothing_overlay.set_clothing_item(category, item_id):
        return jsonify({
            'success': True,
            'category': category,
            'item': item_id,
            'current': webcam_filter.clothing_overlay.get_current_clothing()
        })
    else:
        return jsonify({'error': 'Invalid clothing item or category'}), 400

@app.route('/api/clothing/clear', methods=['POST'])
def clear_clothing():
    """Clear all clothing items."""
    if not webcam_filter.clothing_overlay:
        return jsonify({'error': 'Clothing system not available'}), 400
    
    webcam_filter.clothing_overlay.clear_all_clothing()
    return jsonify({
        'success': True,
        'current': webcam_filter.clothing_overlay.get_current_clothing()
    })

@app.route('/api/measurements', methods=['GET'])
def get_measurements():
    """Get anthropometric measurements from current frame."""
    if not webcam_filter.anthropometric_measurements:
        return jsonify({'error': 'Anthropometric measurements system not available'}), 400
    
    # Get current frame
    frame = None
    if webcam_filter.camera and webcam_filter.camera.isOpened():
        ret, frame = webcam_filter.camera.read()
        if not ret:
            return jsonify({'error': 'Could not capture frame from camera'}), 500
    else:
        return jsonify({'error': 'Camera not available'}), 500
    
    # Calculate measurements
    measurements = webcam_filter.anthropometric_measurements.calculate_all_measurements(frame)
    return jsonify(measurements)

@app.route('/api/measurements/descriptions', methods=['GET'])
def get_measurement_descriptions():
    """Get descriptions of all available measurements."""
    if not webcam_filter.anthropometric_measurements:
        return jsonify({'error': 'Anthropometric measurements system not available'}), 400
    
    descriptions = webcam_filter.anthropometric_measurements.get_measurement_descriptions()
    return jsonify(descriptions)

@app.route('/api/measurements/calibrate', methods=['POST'])
def calibrate_measurements():
    """Set calibration for measurements."""
    if not webcam_filter.anthropometric_measurements:
        return jsonify({'error': 'Anthropometric measurements system not available'}), 400
    
    data = request.get_json()
    if not data or 'pixel_to_cm_ratio' not in data:
        return jsonify({'error': 'pixel_to_cm_ratio required'}), 400
    
    ratio = data['pixel_to_cm_ratio']
    if webcam_filter.anthropometric_measurements.set_calibration(ratio):
        return jsonify({
            'success': True,
            'pixel_to_cm_ratio': ratio,
            'message': 'Calibration updated successfully'
        })
    else:
        return jsonify({'error': 'Invalid calibration ratio'}), 400

@app.route('/api/sex-prediction', methods=['GET'])
def predict_sex():
    """Predict biological sex based on current anthropometric measurements."""
    if not webcam_filter.sex_predictor:
        return jsonify({'error': 'Sex prediction system not available'}), 400
    
    if not webcam_filter.anthropometric_measurements:
        return jsonify({'error': 'Anthropometric measurements system not available'}), 400
    
    # Get current frame
    frame = None
    if webcam_filter.camera and webcam_filter.camera.isOpened():
        ret, frame = webcam_filter.camera.read()
        if not ret:
            return jsonify({'error': 'Could not capture frame from camera'}), 500
    else:
        return jsonify({'error': 'Camera not available'}), 500
    
    # Calculate measurements
    measurements = webcam_filter.anthropometric_measurements.calculate_all_measurements(frame)
    
    if not measurements.get('pose_detected', False):
        return jsonify({'error': 'No pose detected in current frame'}), 400
    
    # Predict sex
    prediction_result = webcam_filter.sex_predictor.predict_sex(measurements)
    
    # Add the original measurements for reference
    prediction_result['measurements_used'] = measurements
    
    return jsonify(prediction_result)

@app.route('/api/sex-prediction/from-measurements', methods=['POST'])
def predict_sex_from_measurements():
    """Predict biological sex from provided measurements."""
    if not webcam_filter.sex_predictor:
        return jsonify({'error': 'Sex prediction system not available'}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Measurements data required'}), 400
    
    # Predict sex from provided measurements
    prediction_result = webcam_filter.sex_predictor.predict_sex(data)
    
    return jsonify(prediction_result)

@app.route('/api/sex-prediction/explanation', methods=['POST'])
def get_sex_prediction_explanation():
    """Get human-readable explanation of sex prediction result."""
    if not webcam_filter.sex_predictor:
        return jsonify({'error': 'Sex prediction system not available'}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Prediction result data required'}), 400
    
    explanation = webcam_filter.sex_predictor.get_prediction_explanation(data)
    
    return jsonify({
        'explanation': explanation,
        'prediction_data': data
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    try:
        # Run the Flask app
        app.run(host='0.0.0.0', port=12000, debug=False, threaded=True)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        webcam_filter.cleanup()