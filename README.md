# 🎥 Easy Mirror

A web-based webcam application with real-time computer vision filters, designed for Ubuntu and Raspberry Pi.

## Features

- 📹 **Real-time webcam streaming** via web browser
- 🎨 **11 CV filters**: None, Blur, Edge Detection, Grayscale, Sepia, Invert, Emboss, Cartoon, Vintage, Cool, Warm
- 👕 **Virtual Clothing Filter**: Real-time clothing overlay using MediaPipe pose detection
- 🖥️ **Cross-platform**: Works on Ubuntu, Raspberry Pi, and other Linux systems
- 📱 **Responsive design**: Works on desktop and mobile browsers
- ⌨️ **Keyboard shortcuts**: Number keys (1-9) for quick filter switching, F for fullscreen
- 🔄 **Auto-refresh**: Automatic camera status monitoring
- 🎯 **Easy setup**: Simple installation and configuration

## Screenshots

The application provides a clean, modern interface with:
- Live video stream with applied filters
- Filter selection grid with visual previews
- Status monitoring for camera connection
- Fullscreen mode for immersive viewing

## Installation

### Prerequisites

- Python 3.7 or higher
- USB webcam
- Modern web browser

### Ubuntu/Debian Installation

```bash
# Clone the repository
git clone https://github.com/justingeeslin/easy-mirror.git
cd easy-mirror

# Install system dependencies
sudo apt update
sudo apt install python3-pip python3-venv

# For OpenCV dependencies
sudo apt install python3-opencv libopencv-dev

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Raspberry Pi Installation

```bash
# Clone the repository
git clone https://github.com/justingeeslin/easy-mirror.git
cd easy-mirror

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv python3-opencv

# For better camera support on Raspberry Pi
sudo apt install v4l-utils

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Alternative: Docker Installation

```bash
# Build the Docker image
docker build -t easy-mirror .

# Run with camera access
docker run -p 12000:12000 --device=/dev/video0 easy-mirror
```

## Usage

### Starting the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
python app.py
```

The application will start on `http://localhost:12000`

### Camera Configuration

The application automatically detects available cameras. If you have multiple cameras:

1. Check available cameras:
```bash
v4l2-ctl --list-devices
```

2. Modify the camera index in `app.py` if needed:
```python
# In the initialize_camera method, adjust camera_indices
camera_indices = [0, 1, 2, -1]  # Try different indices
```

### Available Filters

1. **None** - Original video feed
2. **Blur** - Gaussian blur effect
3. **Edge** - Canny edge detection
4. **Grayscale** - Black and white conversion
5. **Sepia** - Vintage sepia tone
6. **Invert** - Color inversion
7. **Emboss** - 3D emboss effect
8. **Cartoon** - Cartoon-style rendering
9. **Vintage** - Aged photo effect
10. **Cool** - Cool color temperature
11. **Warm** - Warm color temperature
12. **Clothing** - Virtual clothing overlay with pose detection

### Keyboard Shortcuts

- `1-9`: Switch to filter by number
- `F`: Toggle fullscreen mode
- `Escape`: Exit fullscreen mode

## API Endpoints

The application provides a REST API for integration:

- `GET /api/filters` - Get available filters and current selection
- `POST /api/filter` - Set current filter
- `GET /api/status` - Get camera and application status
- `GET /video_feed` - Video stream endpoint
- `GET /api/clothing` - Get available clothing items
- `POST /api/clothing/{category}/{item}` - Set clothing item
- `POST /api/clothing/clear` - Clear all clothing

### Example API Usage

```bash
# Get available filters
curl http://localhost:12000/api/filters

# Set blur filter
curl -X POST http://localhost:12000/api/filter \
  -H "Content-Type: application/json" \
  -d '{"filter": "blur"}'

# Check status
curl http://localhost:12000/api/status

# Get available clothing
curl http://localhost:12000/api/clothing

# Set a blue t-shirt
curl -X POST http://localhost:12000/api/clothing/shirts/blue_tshirt

# Clear all clothing
curl -X POST http://localhost:12000/api/clothing/clear
```

## Configuration

### Performance Tuning

For better performance on Raspberry Pi:

1. **Reduce resolution** in `app.py`:
```python
self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
```

2. **Lower frame rate**:
```python
self.camera.set(cv2.CAP_PROP_FPS, 15)
```

3. **Adjust JPEG quality**:
```python
ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
```

### Network Access

To access from other devices on your network:

```bash
# Find your IP address
ip addr show

# The application runs on all interfaces (0.0.0.0)
# Access via: http://YOUR_IP:12000
```

## Troubleshooting

### Camera Issues

1. **Camera not detected**:
```bash
# Check if camera is recognized
lsusb
ls /dev/video*

# Test camera with v4l2
v4l2-ctl --list-formats-ext
```

2. **Permission denied**:
```bash
# Add user to video group
sudo usermod -a -G video $USER
# Logout and login again
```

3. **Camera in use**:
```bash
# Check what's using the camera
sudo lsof /dev/video0
```

### Performance Issues

1. **High CPU usage**: Reduce resolution and frame rate
2. **Slow filters**: Some filters (like cartoon) are computationally intensive
3. **Memory issues**: Restart the application periodically on resource-constrained devices

### Network Issues

1. **Can't access from other devices**: Check firewall settings
2. **Slow streaming**: Reduce video quality or use local network

## Development

### Adding New Filters

1. Add filter method to `WebcamFilter` class in `app.py`:
```python
def my_filter(self, frame):
    # Your OpenCV processing here
    return processed_frame
```

2. Register in the filters dictionary:
```python
self.filters = {
    # ... existing filters
    'my_filter': self.my_filter
}
```

3. Add display name in `static/script.js`:
```javascript
const filterNames = {
    // ... existing names
    'my_filter': '🎯 My Filter'
};
```

### Project Structure

```
easy-mirror/
├── app.py                    # Main Flask application
├── clothing_overlay.py       # Virtual clothing system
├── clothing_config.json      # Clothing item configuration
├── requirements.txt          # Python dependencies
├── templates/
│   └── index.html           # Main web interface
├── static/
│   ├── style.css            # Styling
│   ├── script.js            # Frontend JavaScript
│   └── clothing/            # Clothing assets
│       ├── shirts/          # T-shirt images
│       ├── hats/            # Hat images
│       └── accessories/     # Accessory images
├── README.md                # This file
└── CLOTHING_FILTER.md       # Clothing filter documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on both Ubuntu and Raspberry Pi if possible
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/) and [OpenCV](https://opencv.org/)
- Designed for maker communities and educational use
- Inspired by the need for accessible computer vision tools

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Search existing GitHub issues
3. Create a new issue with system details and error messages

---

**Happy coding! 🚀**