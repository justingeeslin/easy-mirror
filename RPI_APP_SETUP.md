# Raspberry Pi App Setup Guide

This guide explains how to install Easy Mirror as a desktop application on Raspberry Pi that can be launched from the Applications menu and run in fullscreen mode.

## Quick Installation

For a quick installation, run the automated installer:

```bash
# Clone the repository
git clone https://github.com/justingeeslin/easy-mirror.git
cd easy-mirror

# Make the installer executable and run it
chmod +x install-rpi-app.sh
sudo ./install-rpi-app.sh
```

The installer will:
- Install all required system dependencies
- Set up a Python virtual environment
- Create the desktop application entry
- Install the launcher script
- Optionally configure autostart

## Manual Installation Steps

If you prefer to install manually or understand what the installer does:

### 1. Install System Dependencies

```bash
sudo apt update
sudo apt install -y \
    python3 python3-pip python3-venv python3-opencv \
    libopencv-dev v4l-utils curl netstat-nat \
    chromium-browser zenity
```

### 2. Set Up Application Directory

```bash
# Create application directory
sudo mkdir -p /usr/local/share/easy-mirror

# Copy application files
sudo cp -r * /usr/local/share/easy-mirror/

# Set permissions
sudo chmod +x /usr/local/share/easy-mirror/easy-mirror-launcher
```

### 3. Create Virtual Environment

```bash
cd /usr/local/share/easy-mirror
sudo python3 -m venv venv
sudo venv/bin/pip install -r requirements.txt
```

### 4. Install Launcher Script

```bash
sudo cp easy-mirror-launcher /usr/local/bin/
sudo chmod +x /usr/local/bin/easy-mirror-launcher
```

### 5. Install Desktop Entry

```bash
sudo cp easy-mirror.desktop /usr/share/applications/
sudo update-desktop-database /usr/share/applications/
```

## Usage

### Launching from Applications Menu

1. Open the Applications menu (usually in the top-left corner)
2. Navigate to "Sound & Video" or "Graphics" category
3. Click on "Easy Mirror"

The application will:
- Start the Flask server in the background
- Open a web browser in fullscreen/kiosk mode
- Display the webcam feed with filter controls

### Launching from Command Line

```bash
easy-mirror-launcher
```

### Exiting the Application

- Press `Alt+F4` to close the browser window
- Press `Escape` to exit fullscreen mode (then close normally)
- The Flask server will automatically shut down when the browser closes

## Features

### Fullscreen Mode

The application automatically launches in fullscreen/kiosk mode using:
- Chromium: `--kiosk` mode for true fullscreen
- Firefox: `-kiosk` mode
- Other browsers: Regular fullscreen

### Automatic Camera Detection

The launcher automatically detects and configures:
- USB webcams
- Raspberry Pi camera module
- Multiple camera setups

### Error Handling

The launcher includes robust error handling:
- Automatic port selection if default port is busy
- Browser detection and fallback options
- Camera initialization with multiple attempts
- Graceful cleanup on exit

## Configuration

### Changing Default Port

Edit the launcher script to change the default port:

```bash
sudo nano /usr/local/bin/easy-mirror-launcher
# Change: PORT=12000
# To:     PORT=8080
```

### Camera Configuration

For multiple cameras or specific camera selection:

```bash
# List available cameras
v4l2-ctl --list-devices

# Edit app.py to specify camera index
sudo nano /usr/local/share/easy-mirror/app.py
# Modify the camera_indices list in initialize_camera method
```

### Browser Selection

The launcher tries browsers in this order:
1. chromium-browser (preferred for kiosk mode)
2. chromium
3. google-chrome
4. firefox-esr
5. firefox

To force a specific browser, edit the launcher script.

## Autostart Configuration

To start Easy Mirror automatically on boot:

```bash
# Enable the systemd service (if configured during installation)
sudo systemctl enable easy-mirror.service
sudo systemctl start easy-mirror.service

# Or add to user autostart
mkdir -p ~/.config/autostart
cp /usr/share/applications/easy-mirror.desktop ~/.config/autostart/
```

## Troubleshooting

### Camera Not Detected

```bash
# Check if camera is recognized
lsusb
ls /dev/video*

# For Raspberry Pi camera
sudo raspi-config
# Enable camera in Interface Options

# Check camera permissions
sudo usermod -a -G video $USER
# Logout and login again
```

### Browser Issues

```bash
# Install additional browsers
sudo apt install firefox-esr

# For older Raspberry Pi models, use lighter browsers
sudo apt install midori
```

### Performance Issues

For better performance on older Raspberry Pi models:

1. **Reduce resolution** in `/usr/local/share/easy-mirror/app.py`:
```python
self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
```

2. **Lower frame rate**:
```python
self.camera.set(cv2.CAP_PROP_FPS, 15)
```

3. **Use lighter filters**: Avoid computationally intensive filters like "cartoon"

### Port Conflicts

If port 12000 is already in use:

```bash
# Check what's using the port
sudo netstat -tulpn | grep :12000

# The launcher will automatically try port 12001 as fallback
```

## Uninstallation

To completely remove Easy Mirror:

```bash
sudo ./uninstall-rpi-app.sh
```

This will remove:
- Application files
- Desktop entry
- Launcher script
- Systemd service (if configured)
- Optionally remove system dependencies

## File Locations

After installation, files are located at:

- **Application**: `/usr/local/share/easy-mirror/`
- **Launcher**: `/usr/local/bin/easy-mirror-launcher`
- **Desktop Entry**: `/usr/share/applications/easy-mirror.desktop`
- **Icon**: `/usr/local/share/easy-mirror/icon.png`
- **Logs**: `~/.easy-mirror.log`
- **Service**: `/etc/systemd/system/easy-mirror.service` (if configured)

## Development

### Testing the Installation

Run the test suite to verify everything is working:

```bash
cd /usr/local/share/easy-mirror
python3 -m pytest tests/test_rpi_app_packaging.py -v
```

### Modifying the Application

To modify the application after installation:

```bash
# Edit the main application
sudo nano /usr/local/share/easy-mirror/app.py

# Edit the launcher
sudo nano /usr/local/bin/easy-mirror-launcher

# Restart if running as service
sudo systemctl restart easy-mirror.service
```

## Support

For issues specific to the Raspberry Pi app packaging:

1. Check the log file: `~/.easy-mirror.log`
2. Test the components individually:
   ```bash
   # Test Flask app
   cd /usr/local/share/easy-mirror
   source venv/bin/activate
   python3 app.py
   
   # Test browser launch
   chromium-browser --kiosk http://localhost:12000
   ```
3. Verify all files are in place:
   ```bash
   ls -la /usr/local/bin/easy-mirror-launcher
   ls -la /usr/share/applications/easy-mirror.desktop
   ls -la /usr/local/share/easy-mirror/
   ```

## License

This packaging system is part of Easy Mirror and is licensed under the same MIT License as the main project.