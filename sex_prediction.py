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