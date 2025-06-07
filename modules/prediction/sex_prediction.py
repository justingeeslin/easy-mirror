#!/usr/bin/env python3
"""
Biological Sex Prediction System for Easy Mirror
Predicts biological sex based on anthropometric measurements using established sexual dimorphism patterns.
"""

import numpy as np
import logging
from typing import Dict, Optional, Tuple, List

logger = logging.getLogger(__name__)

class SexPredictor:
    """
    Predicts biological sex based on anthropometric measurements.
    
    Uses established patterns of sexual dimorphism in human body measurements
    including ratios and absolute measurements to make predictions.
    """
    
    def __init__(self):
        """Initialize the sex prediction system with anthropometric thresholds."""
        
        # Thresholds based on anthropometric literature and ANSUR data
        # These are approximate values and may need calibration for specific populations
        
        # Shoulder breadth thresholds (cm)
        self.shoulder_breadth_thresholds = {
            'male_min': 38.0,    # Typical male minimum
            'female_max': 36.0,  # Typical female maximum
            'overlap_zone': (34.0, 40.0)  # Overlap zone where sex is less certain
        }
        
        # Height thresholds (cm)
        self.height_thresholds = {
            'male_min': 165.0,   # Typical male minimum
            'female_max': 170.0, # Typical female maximum
            'overlap_zone': (155.0, 180.0)
        }
        
        # Head circumference thresholds (cm)
        self.head_circumference_thresholds = {
            'male_min': 56.0,    # Typical male minimum
            'female_max': 55.0,  # Typical female maximum
            'overlap_zone': (53.0, 58.0)
        }
        
        # Ratio thresholds
        self.ratio_thresholds = {
            # Shoulder to hip width ratio
            'shoulder_hip_ratio': {
                'male_min': 1.35,     # Males typically > 1.35
                'female_max': 1.25,   # Females typically < 1.25
                'overlap_zone': (1.20, 1.40)
            },
            
            # Arm span to height ratio
            'armspan_height_ratio': {
                'male_typical': 1.03,  # Males often slightly > 1.0
                'female_typical': 1.00, # Females often closer to 1.0
                'overlap_zone': (0.95, 1.08)
            },
            
            # Head circumference to height ratio
            'head_height_ratio': {
                'male_typical': 0.33,  # Males typically higher ratio
                'female_typical': 0.31, # Females typically lower ratio
                'overlap_zone': (0.30, 0.35)
            },
            
            # Upper arm to forearm ratio
            'upperarm_forearm_ratio': {
                'male_typical': 1.45,  # Males often have longer upper arms
                'female_typical': 1.40, # Females often have more proportional arms
                'overlap_zone': (1.35, 1.50)
            }
        }
        
        # Weights for different indicators (sum should equal 1.0)
        self.indicator_weights = {
            'shoulder_breadth': 0.25,
            'standing_height': 0.15,
            'head_circumference': 0.15,
            'shoulder_hip_ratio': 0.20,
            'armspan_height_ratio': 0.10,
            'head_height_ratio': 0.10,
            'upperarm_forearm_ratio': 0.05
        }
    
    def calculate_hip_width_estimate(self, measurements: Dict) -> Optional[float]:
        """
        Estimate hip width from available measurements.
        Uses the distance between hip landmarks if available.
        """
        # This would need to be calculated from hip landmark positions
        # For now, we'll estimate based on waist circumference if available
        waist_circ = measurements.get('waist_circumference')
        if waist_circ:
            # Rough estimate: hip width ≈ waist circumference / 3.5
            return waist_circ / 3.5
        return None
    
    def calculate_ratios(self, measurements: Dict) -> Dict[str, Optional[float]]:
        """Calculate various anthropometric ratios for sex prediction."""
        ratios = {}
        
        # Shoulder to hip ratio
        shoulder_breadth = measurements.get('shoulder_breadth')
        hip_width = self.calculate_hip_width_estimate(measurements)
        if shoulder_breadth and hip_width:
            ratios['shoulder_hip_ratio'] = shoulder_breadth / hip_width
        else:
            ratios['shoulder_hip_ratio'] = None
        
        # Arm span to height ratio
        arm_span = measurements.get('arm_span')
        height = measurements.get('standing_height')
        if arm_span and height:
            ratios['armspan_height_ratio'] = arm_span / height
        else:
            ratios['armspan_height_ratio'] = None
        
        # Head circumference to height ratio
        head_circ = measurements.get('head_circumference')
        if head_circ and height:
            ratios['head_height_ratio'] = head_circ / height
        else:
            ratios['head_height_ratio'] = None
        
        # Upper arm to forearm ratio (using left side, fallback to right)
        left_upper = measurements.get('left_upper_arm_length')
        left_forearm = measurements.get('left_forearm_length')
        right_upper = measurements.get('right_upper_arm_length')
        right_forearm = measurements.get('right_forearm_length')
        
        if left_upper and left_forearm:
            ratios['upperarm_forearm_ratio'] = left_upper / left_forearm
        elif right_upper and right_forearm:
            ratios['upperarm_forearm_ratio'] = right_upper / right_forearm
        else:
            ratios['upperarm_forearm_ratio'] = None
        
        return ratios
    
    def evaluate_indicator(self, value: float, indicator_type: str) -> Tuple[str, float]:
        """
        Evaluate a single indicator and return prediction and confidence.
        
        Returns:
            Tuple of (prediction, confidence) where prediction is 'male'/'female'/'uncertain'
            and confidence is between 0.0 and 1.0
        """
        if indicator_type == 'shoulder_breadth':
            thresholds = self.shoulder_breadth_thresholds
            if value >= thresholds['male_min']:
                confidence = min(1.0, (value - thresholds['male_min']) / 5.0 + 0.6)
                return 'male', confidence
            elif value <= thresholds['female_max']:
                confidence = min(1.0, (thresholds['female_max'] - value) / 5.0 + 0.6)
                return 'female', confidence
            else:
                return 'uncertain', 0.3
        
        elif indicator_type == 'standing_height':
            thresholds = self.height_thresholds
            if value >= thresholds['male_min']:
                confidence = min(1.0, (value - thresholds['male_min']) / 15.0 + 0.5)
                return 'male', confidence
            elif value <= thresholds['female_max']:
                confidence = min(1.0, (thresholds['female_max'] - value) / 15.0 + 0.5)
                return 'female', confidence
            else:
                return 'uncertain', 0.3
        
        elif indicator_type == 'head_circumference':
            thresholds = self.head_circumference_thresholds
            if value >= thresholds['male_min']:
                confidence = min(1.0, (value - thresholds['male_min']) / 3.0 + 0.6)
                return 'male', confidence
            elif value <= thresholds['female_max']:
                confidence = min(1.0, (thresholds['female_max'] - value) / 3.0 + 0.6)
                return 'female', confidence
            else:
                return 'uncertain', 0.3
        
        elif indicator_type in self.ratio_thresholds:
            thresholds = self.ratio_thresholds[indicator_type]
            
            if indicator_type == 'shoulder_hip_ratio':
                if value >= thresholds['male_min']:
                    confidence = min(1.0, (value - thresholds['male_min']) / 0.2 + 0.6)
                    return 'male', confidence
                elif value <= thresholds['female_max']:
                    confidence = min(1.0, (thresholds['female_max'] - value) / 0.2 + 0.6)
                    return 'female', confidence
                else:
                    return 'uncertain', 0.3
            
            elif indicator_type == 'armspan_height_ratio':
                male_typical = thresholds['male_typical']
                female_typical = thresholds['female_typical']
                
                male_distance = abs(value - male_typical)
                female_distance = abs(value - female_typical)
                
                if male_distance < female_distance:
                    confidence = max(0.5, 1.0 - male_distance / 0.05)
                    return 'male', confidence
                else:
                    confidence = max(0.5, 1.0 - female_distance / 0.05)
                    return 'female', confidence
            
            elif indicator_type == 'head_height_ratio':
                male_typical = thresholds['male_typical']
                female_typical = thresholds['female_typical']
                
                if value >= (male_typical + female_typical) / 2:
                    confidence = min(1.0, (value - female_typical) / 0.02 + 0.5)
                    return 'male', confidence
                else:
                    confidence = min(1.0, (male_typical - value) / 0.02 + 0.5)
                    return 'female', confidence
            
            elif indicator_type == 'upperarm_forearm_ratio':
                male_typical = thresholds['male_typical']
                female_typical = thresholds['female_typical']
                
                if value >= (male_typical + female_typical) / 2:
                    confidence = min(1.0, (value - female_typical) / 0.1 + 0.5)
                    return 'male', confidence
                else:
                    confidence = min(1.0, (male_typical - value) / 0.1 + 0.5)
                    return 'female', confidence
        
        return 'uncertain', 0.0
    
    def predict_sex(self, measurements: Dict) -> Dict:
        """
        Predict biological sex based on anthropometric measurements.
        
        Args:
            measurements: Dictionary of anthropometric measurements
            
        Returns:
            Dictionary containing prediction results with confidence scores
        """
        try:
            # Calculate ratios
            ratios = self.calculate_ratios(measurements)
            
            # Evaluate each available indicator
            indicators = {}
            weighted_scores = {'male': 0.0, 'female': 0.0}
            total_weight = 0.0
            
            # Direct measurements
            for measurement_name in ['shoulder_breadth', 'standing_height', 'head_circumference']:
                value = measurements.get(measurement_name)
                if value is not None:
                    prediction, confidence = self.evaluate_indicator(value, measurement_name)
                    indicators[measurement_name] = {
                        'value': value,
                        'prediction': prediction,
                        'confidence': confidence
                    }
                    
                    weight = self.indicator_weights[measurement_name]
                    if prediction == 'male':
                        weighted_scores['male'] += weight * confidence
                    elif prediction == 'female':
                        weighted_scores['female'] += weight * confidence
                    total_weight += weight
            
            # Ratio measurements
            for ratio_name in ['shoulder_hip_ratio', 'armspan_height_ratio', 'head_height_ratio', 'upperarm_forearm_ratio']:
                value = ratios.get(ratio_name)
                if value is not None:
                    prediction, confidence = self.evaluate_indicator(value, ratio_name)
                    indicators[ratio_name] = {
                        'value': value,
                        'prediction': prediction,
                        'confidence': confidence
                    }
                    
                    weight = self.indicator_weights[ratio_name]
                    if prediction == 'male':
                        weighted_scores['male'] += weight * confidence
                    elif prediction == 'female':
                        weighted_scores['female'] += weight * confidence
                    total_weight += weight
            
            # Calculate final prediction
            if total_weight > 0:
                # Normalize scores
                male_score = weighted_scores['male'] / total_weight
                female_score = weighted_scores['female'] / total_weight
                
                # Determine prediction
                if male_score > female_score:
                    final_prediction = 'male'
                    confidence = male_score
                elif female_score > male_score:
                    final_prediction = 'female'
                    confidence = female_score
                else:
                    final_prediction = 'uncertain'
                    confidence = 0.5
                
                # Calculate certainty based on score difference
                score_difference = abs(male_score - female_score)
                certainty = min(1.0, score_difference + 0.5)
                
            else:
                final_prediction = 'insufficient_data'
                confidence = 0.0
                certainty = 0.0
                male_score = 0.0
                female_score = 0.0
            
            # Prepare detailed results
            result = {
                'prediction': final_prediction,
                'confidence': round(confidence, 3),
                'certainty': round(certainty, 3),
                'scores': {
                    'male': round(male_score, 3),
                    'female': round(female_score, 3)
                },
                'indicators_used': len(indicators),
                'total_possible_indicators': len(self.indicator_weights),
                'indicator_details': indicators,
                'ratios_calculated': ratios,
                'methodology': 'Multi-indicator anthropometric analysis',
                'note': 'Prediction based on established patterns of sexual dimorphism in human body measurements'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in sex prediction: {e}")
            return {
                'prediction': 'error',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def get_prediction_explanation(self, prediction_result: Dict) -> str:
        """
        Generate a human-readable explanation of the prediction.
        
        Args:
            prediction_result: Result from predict_sex method
            
        Returns:
            String explanation of the prediction
        """
        if prediction_result.get('prediction') == 'error':
            return f"Error in prediction: {prediction_result.get('error', 'Unknown error')}"
        
        if prediction_result.get('prediction') == 'insufficient_data':
            return "Insufficient anthropometric data available for reliable sex prediction."
        
        prediction = prediction_result['prediction']
        confidence = prediction_result['confidence']
        certainty = prediction_result['certainty']
        indicators_used = prediction_result['indicators_used']
        
        explanation = f"Prediction: {prediction.upper()}\n"
        explanation += f"Confidence: {confidence:.1%}\n"
        explanation += f"Certainty: {certainty:.1%}\n"
        explanation += f"Based on {indicators_used} anthropometric indicators\n\n"
        
        explanation += "Key indicators:\n"
        for indicator, details in prediction_result['indicator_details'].items():
            value = details['value']
            pred = details['prediction']
            conf = details['confidence']
            
            if indicator.endswith('_ratio'):
                explanation += f"• {indicator.replace('_', ' ').title()}: {value:.3f} → {pred} ({conf:.1%})\n"
            else:
                explanation += f"• {indicator.replace('_', ' ').title()}: {value:.1f}cm → {pred} ({conf:.1%})\n"
        
        explanation += f"\nNote: This prediction is based on established patterns of sexual dimorphism "
        explanation += f"in human anthropometry and should be interpreted as an estimate only."
        
        return explanation

    def estimate_bust_circumference_range(self, measurements: Dict) -> Optional[Tuple[float, float]]:
        """
        Estimate a plausible range for bust circumference (in cm) based on available measurements.

        Uses shoulder breadth, waist circumference, height, and optionally predicted sex.

        Returns:
            Tuple of (min_cm, max_cm) if enough data is available, else None.
        """
        shoulder_breadth = measurements.get('shoulder_breadth')
        waist_circ = measurements.get('waist_circumference')
        height = measurements.get('standing_height')

        # Require at least shoulder breadth and one other measurement
        if not shoulder_breadth or not (waist_circ or height):
            return None

        # Start with shoulder-based base estimate
        # These multipliers are derived from ANSUR regression approximations
        base_bust = shoulder_breadth * 2.2  # Rough linear scale from shoulder width

        # Adjust based on waist and height if available
        if waist_circ:
            # Adjust upward for higher waist—tends to correlate with larger bust
            base_bust += (waist_circ - 70) * 0.25  # scaling factor
        if height:
            # Normalize for torso proportion (shorter stature sometimes means relatively larger bust)
            base_bust += (160 - height) * 0.15  # more weight to height differences below 160

        # Generate a ± range to reflect natural variation
        bust_min = base_bust * 0.95
        bust_max = base_bust * 1.05

        return round(bust_min, 1), round(bust_max, 1)

    def generate_ui_html(self, measurements_available=True):
        """Generate HTML for sex prediction UI controls."""
        if not measurements_available:
            return '''
            <div class="module-section" id="sex-prediction-section">
                <h3>🧬 Biological Sex Prediction</h3>
                <div class="dependency-warning">
                    <p>⚠️ This module requires anthropometric measurements to be available.</p>
                    <p>Please ensure the measurements module is enabled.</p>
                </div>
            </div>
            '''
        
        return '''
        <div class="module-section" id="sex-prediction-section">
            <h3>🧬 Biological Sex Prediction</h3>
            <div class="prediction-controls">
                <button id="predict-sex-btn" class="action-btn">
                    <span class="btn-icon">🔮</span>
                    Predict from Camera
                </button>
                <button id="predict-from-manual-btn" class="action-btn secondary">
                    <span class="btn-icon">📝</span>
                    Manual Input
                </button>
                <button id="show-methodology-btn" class="action-btn secondary">
                    <span class="btn-icon">📚</span>
                    Methodology
                </button>
            </div>
            
            <div id="manual-input-panel" class="panel hidden">
                <h4>Manual Measurement Input</h4>
                <div class="input-grid">
                    <div class="input-group">
                        <label>Height (cm):</label>
                        <input type="number" id="manual-height" placeholder="175" step="0.1">
                    </div>
                    <div class="input-group">
                        <label>Shoulder Breadth (cm):</label>
                        <input type="number" id="manual-shoulder" placeholder="42" step="0.1">
                    </div>
                    <div class="input-group">
                        <label>Head Circumference (cm):</label>
                        <input type="number" id="manual-head" placeholder="57" step="0.1">
                    </div>
                </div>
                <div class="panel-actions">
                    <button id="predict-manual-btn" class="action-btn">Predict</button>
                    <button id="cancel-manual-btn" class="action-btn secondary">Cancel</button>
                </div>
            </div>
            
            <div id="prediction-results" class="results-panel hidden">
                <h4>Prediction Results</h4>
                <div id="prediction-data"></div>
            </div>
            
            <div id="methodology-panel" class="panel hidden">
                <h4>Prediction Methodology</h4>
                <p>This system uses established patterns of sexual dimorphism in human body measurements to make predictions.</p>
                <ul>
                    <li><strong>Shoulder Breadth:</strong> Males typically have broader shoulders</li>
                    <li><strong>Height:</strong> Males are typically taller on average</li>
                    <li><strong>Head Circumference:</strong> Males typically have larger head circumference</li>
                    <li><strong>Body Ratios:</strong> Various body proportions show sexual dimorphism</li>
                </ul>
                <p><em>Note: These are statistical patterns and individual variation exists. Predictions are for research/educational purposes.</em></p>
            </div>
        </div>
        '''
    
    def generate_ui_css(self):
        """Generate CSS for sex prediction UI."""
        return '''
        .prediction-controls {
            display: flex;
            gap: 10px;
            margin-top: 10px;
            flex-wrap: wrap;
        }
        
        .dependency-warning {
            padding: 15px;
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            color: #856404;
            margin-top: 10px;
        }
        
        .input-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        
        .input-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
        }
        
        .prediction-result {
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        
        .prediction-result.male {
            background: #e3f2fd;
            border: 2px solid #2196f3;
        }
        
        .prediction-result.female {
            background: #fce4ec;
            border: 2px solid #e91e63;
        }
        
        .prediction-result.unknown {
            background: #f5f5f5;
            border: 2px solid #9e9e9e;
        }
        
        .prediction-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .prediction-sex {
            font-size: 18px;
            font-weight: bold;
        }
        
        .prediction-confidence {
            font-size: 14px;
            opacity: 0.8;
        }
        
        .contributing-factors {
            margin-top: 10px;
        }
        
        .factor-item {
            padding: 5px 0;
            border-bottom: 1px solid rgba(0,0,0,0.1);
        }
        
        .factor-item:last-child {
            border-bottom: none;
        }
        '''
    
    def generate_ui_javascript(self):
        """Generate JavaScript for sex prediction UI."""
        return '''
        // Sex Prediction Module JavaScript
        function initSexPredictionModule() {
            const predictBtn = document.getElementById('predict-sex-btn');
            const manualBtn = document.getElementById('predict-from-manual-btn');
            const methodologyBtn = document.getElementById('show-methodology-btn');
            const manualPanel = document.getElementById('manual-input-panel');
            const resultsPanel = document.getElementById('prediction-results');
            const methodologyPanel = document.getElementById('methodology-panel');
            
            // Predict from camera
            if (predictBtn) {
                predictBtn.addEventListener('click', async function() {
                    this.disabled = true;
                    this.innerHTML = '<span class="btn-icon">⏳</span> Predicting...';
                    
                    try {
                        const response = await fetch('/api/sex-prediction');
                        const data = await response.json();
                        
                        if (response.ok) {
                            displayPredictionResults(data);
                            resultsPanel.classList.remove('hidden');
                        } else {
                            alert('Error: ' + data.error);
                        }
                    } catch (error) {
                        alert('Error getting prediction: ' + error.message);
                    } finally {
                        this.disabled = false;
                        this.innerHTML = '<span class="btn-icon">🔮</span> Predict from Camera';
                    }
                });
            }
            
            // Manual input
            if (manualBtn) {
                manualBtn.addEventListener('click', function() {
                    manualPanel.classList.toggle('hidden');
                    methodologyPanel.classList.add('hidden');
                });
            }
            
            // Predict from manual input
            const predictManualBtn = document.getElementById('predict-manual-btn');
            if (predictManualBtn) {
                predictManualBtn.addEventListener('click', async function() {
                    const height = document.getElementById('manual-height').value;
                    const shoulder = document.getElementById('manual-shoulder').value;
                    const head = document.getElementById('manual-head').value;
                    
                    if (!height || !shoulder || !head) {
                        alert('Please fill in all measurement fields');
                        return;
                    }
                    
                    const measurements = {
                        pose_detected: true,
                        height_cm: parseFloat(height),
                        shoulder_breadth_cm: parseFloat(shoulder),
                        head_circumference_cm: parseFloat(head),
                        shoulder_to_hip_ratio: 1.2, // Default estimate
                        head_to_shoulder_ratio: 0.25, // Default estimate
                        arm_span_to_height_ratio: 1.0 // Default estimate
                    };
                    
                    try {
                        const response = await fetch('/api/sex-prediction/from-measurements', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify(measurements)
                        });
                        
                        const data = await response.json();
                        if (response.ok) {
                            displayPredictionResults(data);
                            resultsPanel.classList.remove('hidden');
                            manualPanel.classList.add('hidden');
                        } else {
                            alert('Error: ' + data.error);
                        }
                    } catch (error) {
                        alert('Error getting prediction: ' + error.message);
                    }
                });
            }
            
            // Cancel manual input
            const cancelManualBtn = document.getElementById('cancel-manual-btn');
            if (cancelManualBtn) {
                cancelManualBtn.addEventListener('click', function() {
                    manualPanel.classList.add('hidden');
                });
            }
            
            // Show methodology
            if (methodologyBtn) {
                methodologyBtn.addEventListener('click', function() {
                    methodologyPanel.classList.toggle('hidden');
                    manualPanel.classList.add('hidden');
                });
            }
        }
        
        function displayPredictionResults(data) {
            const container = document.getElementById('prediction-data');
            if (!container) return;
            
            const prediction = data.predicted_sex || data.prediction || 'Unknown';
            const confidence = data.confidence || data.certainty || 0;
            const factors = data.contributing_factors || [];
            
            let resultClass = 'unknown';
            if (prediction.toLowerCase().includes('male') && !prediction.toLowerCase().includes('female')) {
                resultClass = 'male';
            } else if (prediction.toLowerCase().includes('female')) {
                resultClass = 'female';
            }
            
            let html = `
                <div class="prediction-result ${resultClass}">
                    <div class="prediction-header">
                        <span class="prediction-sex">Predicted: ${prediction}</span>
                        <span class="prediction-confidence">Confidence: ${(confidence * 100).toFixed(1)}%</span>
                    </div>
            `;
            
            if (factors.length > 0) {
                html += '<div class="contributing-factors"><strong>Contributing Factors:</strong>';
                factors.forEach(factor => {
                    html += `<div class="factor-item">${factor}</div>`;
                });
                html += '</div>';
            }
            
            html += '</div>';
            
            // Add explanation if available
            if (data.explanation) {
                html += `<div class="explanation-text">${data.explanation}</div>`;
            }
            
            container.innerHTML = html;
        }
        
        // Initialize when DOM is loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initSexPredictionModule);
        } else {
            initSexPredictionModule();
        }
        '''


def create_sex_prediction_demo():
    """Create a demonstration of the sex prediction system."""
    
    # Sample measurements for demonstration
    sample_measurements_male = {
        'shoulder_breadth': 42.5,
        'standing_height': 175.0,
        'arm_span': 180.0,
        'head_circumference': 58.0,
        'waist_circumference': 85.0,
        'left_upper_arm_length': 32.0,
        'left_forearm_length': 22.0,
        'pose_detected': True
    }
    
    sample_measurements_female = {
        'shoulder_breadth': 34.0,
        'standing_height': 162.0,
        'arm_span': 162.0,
        'head_circumference': 54.0,
        'waist_circumference': 70.0,
        'left_upper_arm_length': 28.0,
        'left_forearm_length': 20.5,
        'pose_detected': True
    }
    
    predictor = SexPredictor()
    
    print("=== Sex Prediction Demo ===\n")
    
    print("Sample 1 - Typical Male Measurements:")
    result1 = predictor.predict_sex(sample_measurements_male)
    print(predictor.get_prediction_explanation(result1))
    print("\n" + "="*50 + "\n")
    
    print("Sample 2 - Typical Female Measurements:")
    result2 = predictor.predict_sex(sample_measurements_female)
    print(predictor.get_prediction_explanation(result2))
    
    return predictor


if __name__ == "__main__":
    # Run demonstration
    demo_predictor = create_sex_prediction_demo()