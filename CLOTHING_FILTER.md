# Clothing System

## Overview

The Clothing System includes two main features:

1. **Virtual Clothing Filter**: Uses MediaPipe pose detection to overlay virtual clothing items onto the user's body in real-time
2. **Clothing Analysis**: Uses MediaPipe Image Segmentation to detect and analyze real clothing worn by the user

Both features support multiple clothing categories and provide detailed information about garments.

## Features

### Virtual Clothing Filter
- **Real-time Pose Detection**: Uses MediaPipe to detect body landmarks and position clothing accurately
- **Multiple Clothing Categories**: 
  - Shirts (Blue, Green, Red, Yellow T-Shirts)
  - Hats (Black, Blue, Red Caps)
  - Accessories (Glasses)
- **Dynamic Positioning**: Clothing items automatically adjust to body pose and movement
- **Easy Management**: Simple web interface for selecting and clearing clothing items
- **Configurable**: JSON-based configuration for easy addition of new clothing items

### Clothing Analysis
- **Real-time Analysis**: Analyze clothing in the current video frame
- **Garment Type Detection**: Identifies shirts, dresses, blouses, pants, shorts, skirts, etc.
- **Color Recognition**: Detects dominant colors in different body regions
- **Material Analysis**: Estimates fabric types (cotton, denim, silk, wool, etc.)
- **Feature Detection**: Identifies neckline types, sleeve lengths, and other garment features
- **Embellishment Recognition**: Detects buttons, zippers, and other clothing details
- **Confidence Scoring**: Provides confidence levels for analysis results

## Technical Implementation

### Core Components

1. **ClothingOverlay Class** (`clothing_overlay.py`)
   - Handles MediaPipe pose detection
   - Manages clothing item positioning and scaling
   - Applies clothing overlays to video frames

2. **ClothingAnalyzer Class** (`clothing_analysis.py`)
   - Handles MediaPipe Image Segmentation
   - Analyzes real clothing in video frames
   - Provides detailed garment information

3. **Clothing Configuration** (`clothing_config.json`)
   - Defines available clothing items
   - Specifies positioning parameters for each item
   - Configures scaling and offset values

4. **Web Interface Integration**
   - API endpoints for clothing management and analysis
   - Real-time UI updates
   - Category-based clothing selection
   - Interactive analysis results display

### Pose Detection & Image Segmentation

The system uses two MediaPipe models:

1. **MediaPipe Pose** (for virtual clothing overlay):
   - Detects 33 body landmarks
   - **Shoulders**: Used for shirt positioning and scaling
   - **Head**: Used for hat and accessory placement
   - **Body center**: Used for overall clothing alignment

2. **MediaPipe Selfie Segmentation** (for clothing analysis):
   - Segments person from background
   - Identifies clothing regions on the body
   - Enables detailed analysis of real garments

### Clothing Positioning

Each virtual clothing item is positioned based on specific body landmarks:

- **Shirts**: Positioned between shoulders with dynamic width scaling
- **Hats**: Centered on head with appropriate offset
- **Accessories**: Positioned on face landmarks (e.g., glasses on nose)

### Clothing Analysis Process

The analysis system follows these steps:

1. **Person Segmentation**: Isolate the person from the background
2. **Body Region Detection**: Define torso, arms, and legs based on pose landmarks
3. **Color Analysis**: Analyze dominant colors in each body region
4. **Texture Analysis**: Estimate material types based on texture patterns
5. **Garment Classification**: Identify garment types based on coverage patterns
6. **Feature Detection**: Analyze necklines, sleeve lengths, and other features
7. **Embellishment Detection**: Look for buttons, zippers, and other details

## API Endpoints

### Virtual Clothing Management

#### Get Available Clothing
```
GET /api/clothing
```
Returns all available clothing items organized by category.

#### Set Clothing Item
```
POST /api/clothing/{category}/{item_id}
```
Sets a specific clothing item for the given category.

#### Clear All Clothing
```
POST /api/clothing/clear
```
Removes all currently applied clothing items.

### Clothing Analysis

#### Analyze Current Frame
```
POST /api/clothing/analyze
```
Analyzes the clothing in the current video frame and returns detailed information.

#### Get Last Analysis
```
GET /api/clothing/analysis
```
Returns the most recent clothing analysis results.

## Configuration

### Adding New Clothing Items

1. **Add Image File**: Place the clothing image in the appropriate category folder:
   - `static/clothing/shirts/`
   - `static/clothing/hats/`
   - `static/clothing/accessories/`

2. **Update Configuration**: Add the item to `clothing_config.json`:
```json
{
  "category": {
    "new_item": {
      "name": "Display Name",
      "image": "filename.png",
      "scale_factor": 1.0,
      "offset_x": 0,
      "offset_y": 0
    }
  }
}
```

3. **Positioning Parameters**:
   - `scale_factor`: Size multiplier (1.0 = normal size)
   - `offset_x`: Horizontal offset in pixels
   - `offset_y`: Vertical offset in pixels

### Image Requirements

- **Format**: PNG with transparency support recommended
- **Size**: 200-400px width for optimal performance
- **Background**: Transparent or white background
- **Orientation**: Front-facing view

## Usage

1. **Enable Clothing Filter**: Click the "👕 Clothing" filter button
2. **Select Items**: Choose clothing items from each category
3. **Mix and Match**: Combine different items (shirt + hat + accessories)
4. **Clear All**: Use "Clear All" button to remove all clothing

## Performance Considerations

- **Frame Rate**: Pose detection may reduce frame rate on slower devices
- **CPU Usage**: MediaPipe processing is CPU-intensive
- **Memory**: Each clothing item loads into memory when selected

## Troubleshooting

### Common Issues

1. **Clothing Not Appearing**
   - Ensure pose is detected (person visible in frame)
   - Check that clothing filter is active
   - Verify clothing files exist

2. **Poor Positioning**
   - Adjust offset values in configuration
   - Ensure good lighting for pose detection
   - Stand facing camera directly

3. **Performance Issues**
   - Reduce video resolution
   - Close other applications
   - Use fewer clothing items simultaneously

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export CLOTHING_DEBUG=true
```

## Future Enhancements

- **3D Model Support**: Integration with 3D clothing models
- **Custom Uploads**: User-uploaded clothing items
- **Size Adjustment**: Real-time scaling controls
- **Color Customization**: Dynamic color modification
- **Pose-Aware Fitting**: Advanced fitting based on body measurements

## Dependencies

- MediaPipe >= 0.10.0
- OpenCV >= 4.8.0
- PIL (Pillow) >= 9.0.0
- NumPy >= 1.21.0

## License

This feature is part of the Easy Mirror project and follows the same licensing terms.