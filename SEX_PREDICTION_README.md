# Biological Sex Prediction System

## Overview

This system predicts biological sex based on anthropometric measurements extracted from pose landmarks using MediaPipe. It uses established patterns of sexual dimorphism in human body measurements to make predictions.

## Features

- **Multi-indicator Analysis**: Uses 7 different anthropometric indicators
- **Ratio-based Measurements**: Incorporates body proportion ratios for better accuracy
- **Confidence Scoring**: Provides confidence and certainty scores for predictions
- **Detailed Explanations**: Shows which indicators contributed to the prediction
- **Web Interface**: Integrated into the Easy Mirror web application
- **API Endpoints**: RESTful API for programmatic access

## Methodology

The system uses the following anthropometric indicators:

### Direct Measurements
1. **Shoulder Breadth**: Distance between shoulder landmarks
2. **Standing Height**: Estimated height from head to ankle
3. **Head Circumference**: Estimated from head width

### Calculated Ratios
4. **Shoulder-to-Hip Ratio**: Males typically have broader shoulders relative to hips
5. **Arm Span to Height Ratio**: Males often have longer arm spans relative to height
6. **Head Circumference to Height Ratio**: Males typically have larger heads relative to height
7. **Upper Arm to Forearm Ratio**: Subtle differences in limb proportions

## Scientific Basis

The prediction model is based on well-established patterns of sexual dimorphism in human anthropometry:

- **Shoulder breadth**: Males typically have broader shoulders (>38cm vs <36cm for females)
- **Height**: Males are generally taller (>165cm vs <170cm overlap zone)
- **Head circumference**: Males typically have larger heads (>56cm vs <55cm)
- **Body proportions**: Males often have different limb-to-torso ratios

## Usage

### Web Interface

1. Open the Easy Mirror application
2. Click the "🧬 Sex Prediction" button
3. Click "🔬 Analyze Current Pose" to predict based on current camera view
4. View detailed results including confidence scores and contributing indicators

### API Endpoints

#### GET /api/sex-prediction
Predict sex based on current camera frame:
```bash
curl http://localhost:5000/api/sex-prediction
```

#### POST /api/sex-prediction/from-measurements
Predict sex from provided measurements:
```bash
curl -X POST http://localhost:5000/api/sex-prediction/from-measurements \
  -H "Content-Type: application/json" \
  -d '{
    "shoulder_breadth": 40.0,
    "standing_height": 170.0,
    "head_circumference": 56.0,
    "arm_span": 172.0,
    "waist_circumference": 80.0
  }'
```

#### POST /api/sex-prediction/explanation
Get human-readable explanation of prediction:
```bash
curl -X POST http://localhost:5000/api/sex-prediction/explanation \
  -H "Content-Type: application/json" \
  -d '{"prediction": "male", "confidence": 0.85, ...}'
```

## Response Format

```json
{
  "prediction": "male",
  "confidence": 0.804,
  "certainty": 1.0,
  "scores": {
    "male": 0.804,
    "female": 0.076
  },
  "indicators_used": 7,
  "total_possible_indicators": 7,
  "indicator_details": {
    "shoulder_breadth": {
      "value": 40.0,
      "prediction": "male",
      "confidence": 1.0
    },
    "standing_height": {
      "value": 170.0,
      "prediction": "male",
      "confidence": 0.833
    }
  },
  "ratios_calculated": {
    "shoulder_hip_ratio": 1.75,
    "armspan_height_ratio": 1.012,
    "head_height_ratio": 0.329,
    "upperarm_forearm_ratio": 1.429
  },
  "methodology": "Multi-indicator anthropometric analysis",
  "note": "Prediction based on established patterns of sexual dimorphism in human body measurements"
}
```

## Accuracy and Limitations

### Strengths
- Uses multiple indicators for robust predictions
- Based on established anthropometric research
- Provides confidence scores for reliability assessment
- Handles missing measurements gracefully

### Limitations
- **Individual Variation**: Significant overlap exists between male and female measurements
- **Population Differences**: Thresholds based on general population data
- **Pose Requirements**: Requires clear, full-body pose detection
- **Calibration Dependent**: Accuracy depends on proper camera calibration

### Important Notes
- This system is for **educational and research purposes only**
- Predictions should be interpreted as estimates with inherent uncertainty
- Individual variation means some predictions may be incorrect
- The system cannot account for all biological and genetic variations

## Technical Implementation

### Core Classes

#### `SexPredictor`
Main prediction class with methods:
- `predict_sex(measurements)`: Main prediction method
- `calculate_ratios(measurements)`: Calculate body proportion ratios
- `evaluate_indicator(value, type)`: Evaluate individual indicators
- `get_prediction_explanation(result)`: Generate human-readable explanations

#### Key Methods
```python
from sex_prediction import SexPredictor

predictor = SexPredictor()
result = predictor.predict_sex(measurements)
explanation = predictor.get_prediction_explanation(result)
```

### Integration with Anthropometric Measurements

The system integrates seamlessly with the existing anthropometric measurement system:

```python
from anthropometric_measurements import AnthropometricMeasurements
from sex_prediction import SexPredictor

# Get measurements from camera
measurements_system = AnthropometricMeasurements()
measurements = measurements_system.calculate_all_measurements(frame)

# Predict sex
predictor = SexPredictor()
if measurements.get('pose_detected'):
    result = predictor.predict_sex(measurements)
```

## Testing

Run the test suite:
```bash
python -m unittest tests.test_sex_prediction -v
```

Run the demo:
```bash
python sex_prediction.py
```

## Configuration

### Threshold Adjustment
Thresholds can be adjusted for different populations by modifying the `SexPredictor` initialization:

```python
predictor = SexPredictor()
# Adjust shoulder breadth thresholds
predictor.shoulder_breadth_thresholds['male_min'] = 39.0
predictor.shoulder_breadth_thresholds['female_max'] = 35.0
```

### Weight Adjustment
Indicator weights can be modified to emphasize different measurements:

```python
predictor.indicator_weights['shoulder_breadth'] = 0.30  # Increase weight
predictor.indicator_weights['head_circumference'] = 0.10  # Decrease weight
```

## Ethical Considerations

- **Privacy**: Measurements are processed locally and not stored
- **Bias**: System may have biases based on training population
- **Consent**: Users should be informed about the prediction system
- **Interpretation**: Results should not be used for discriminatory purposes

## Future Improvements

1. **Machine Learning**: Train on larger, more diverse datasets
2. **Population-Specific Models**: Different models for different populations
3. **Additional Indicators**: Include more anthropometric measurements
4. **Uncertainty Quantification**: Better confidence interval estimation
5. **Real-time Calibration**: Automatic calibration based on known references

## References

- ANSUR (Anthropometric Survey of US Army Personnel)
- ISO 7250 standards for anthropometric measurements
- Research on sexual dimorphism in human anthropometry
- MediaPipe pose estimation documentation

## License

This implementation is part of the Easy Mirror project and follows the same licensing terms.