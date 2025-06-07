#!/usr/bin/env python3
"""
Easy Mirror - Modular Web-based Webcam with CV Filters
A Flask application that streams webcam video with real-time computer vision filters.
Uses modular architecture for better maintainability and extensibility.
"""

import cv2
import numpy as np
from flask import Flask, render_template, Response, jsonify, request
from flask_cors import CORS
import threading
import time
import logging
import os

# Import modular components
try:
    from modules.base import CameraManager
    CAMERA_AVAILABLE = True
except ImportError:
    CAMERA_AVAILABLE = False
    logging.warning("Camera management module not available")

try:
    from modules.filters import BasicFilters, ClothingOverlay
    FILTERS_AVAILABLE = True
    CLOTHING_AVAILABLE = True
except ImportError:
    FILTERS_AVAILABLE = False
    CLOTHING_AVAILABLE = False
    logging.warning("Filters modules not available")

try:
    from modules.anthropometric import AnthropometricMeasurements
    MEASUREMENTS_AVAILABLE = True
except ImportError:
    MEASUREMENTS_AVAILABLE = False
    logging.warning("Anthropometric measurements module not available - install mediapipe to enable measurements")

try:
    from modules.prediction import SexPredictor
    SEX_PREDICTION_AVAILABLE = True
except ImportError:
    SEX_PREDICTION_AVAILABLE = False
    logging.warning("Sex prediction module not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


class ModularWebcamFilter:
    """Modular webcam filter system using separate modules for different capabilities."""
    
    def __init__(self):
        self.current_filter = 'none'
        self.is_running = False
        self.frame_lock = threading.Lock()
        self.latest_frame = None
        
        # Initialize camera manager
        self.camera_manager = None
        if CAMERA_AVAILABLE:
            try:
                self.camera_manager = CameraManager()
                logger.info("Camera manager initialized")
            except Exception as e:
                logger.error(f"Failed to initialize camera manager: {e}")
        
        # Initialize basic filters
        self.basic_filters = None
        if FILTERS_AVAILABLE:
            try:
                self.basic_filters = BasicFilters()
                logger.info("Basic filters initialized")
            except Exception as e:
                logger.error(f"Failed to initialize basic filters: {e}")
        
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
        
        # Initialize sex prediction system (depends on anthropometric measurements)
        self.sex_predictor = None
        if SEX_PREDICTION_AVAILABLE and MEASUREMENTS_AVAILABLE:
            try:
                self.sex_predictor = SexPredictor()
                logger.info("Sex prediction system initialized")
            except Exception as e:
                logger.error(f"Failed to initialize sex prediction: {e}")
        elif SEX_PREDICTION_AVAILABLE and not MEASUREMENTS_AVAILABLE:
            logger.warning("Sex prediction available but anthropometric measurements not available - sex prediction disabled")
        
        # Build available filters list
        self.available_filters = ['none']
        if self.basic_filters:
            self.available_filters.extend(self.basic_filters.get_available_filters())
        if self.clothing_overlay:
            self.available_filters.append('clothing')
    
    def get_frame(self):
        """Capture and process a frame."""
        if not self.camera_manager or not self.camera_manager.is_available():
            return None
        
        ret, frame = self.camera_manager.read_frame()
        if not ret:
            return None
        
        # Apply current filter
        try:
            frame = self.apply_current_filter(frame)
        except Exception as e:
            logger.error(f"Error applying filter {self.current_filter}: {e}")
            # Fall back to no filter
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if ret:
            return buffer.tobytes()
        return None
    
    def apply_current_filter(self, frame):
        """Apply the current filter to the frame."""
        if self.current_filter == 'none':
            return frame
        elif self.current_filter == 'clothing' and self.clothing_overlay:
            return self.clothing_overlay.apply_clothing_filter(frame)
        elif self.basic_filters and self.current_filter in self.basic_filters.get_available_filters():
            return self.basic_filters.apply_filter(frame, self.current_filter)
        else:
            logger.warning(f"Unknown filter: {self.current_filter}")
            return frame
    
    def set_filter(self, filter_name):
        """Set the current filter."""
        if filter_name in self.available_filters:
            self.current_filter = filter_name
            logger.info(f"Filter changed to: {filter_name}")
            return True
        return False
    
    def get_available_filters(self):
        """Get list of available filters."""
        return self.available_filters
    
    def cleanup(self):
        """Clean up resources."""
        if self.camera_manager:
            self.camera_manager.cleanup()


# Global webcam filter instance
webcam_filter = ModularWebcamFilter()


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
    camera_available = (webcam_filter.camera_manager is not None and 
                       webcam_filter.camera_manager.is_available())
    return jsonify({
        'camera_available': camera_available,
        'current_filter': webcam_filter.current_filter,
        'filters_count': len(webcam_filter.get_available_filters()),
        'modules': {
            'camera': CAMERA_AVAILABLE,
            'basic_filters': FILTERS_AVAILABLE,
            'clothing': CLOTHING_AVAILABLE,
            'measurements': MEASUREMENTS_AVAILABLE,
            'sex_prediction': SEX_PREDICTION_AVAILABLE
        }
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
    if webcam_filter.camera_manager and webcam_filter.camera_manager.is_available():
        ret, frame = webcam_filter.camera_manager.read_frame()
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
    if webcam_filter.camera_manager and webcam_filter.camera_manager.is_available():
        ret, frame = webcam_filter.camera_manager.read_frame()
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