#!/bin/bash
# Easy Mirror Raspberry Pi App Installer
# This script installs Easy Mirror as a desktop application on Raspberry Pi

set -e

# Configuration
APP_NAME="easy-mirror"
APP_DIR="/usr/local/share/$APP_NAME"
BIN_DIR="/usr/local/bin"
DESKTOP_FILE="/usr/share/applications/$APP_NAME.desktop"
ICON_DIR="/usr/local/share/$APP_NAME"
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Function to detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
    else
        print_error "Cannot detect operating system"
        exit 1
    fi
    
    print_status "Detected OS: $OS $VERSION"
    
    # Check if it's a Raspberry Pi
    if [ -f /proc/device-tree/model ] && grep -q "Raspberry Pi" /proc/device-tree/model; then
        print_status "Raspberry Pi detected"
        IS_RPI=true
    else
        print_warning "Not running on Raspberry Pi, but continuing anyway"
        IS_RPI=false
    fi
}

# Function to install system dependencies
install_dependencies() {
    print_status "Installing system dependencies..."
    
    # Update package list
    apt update
    
    # Install required packages
    apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-opencv \
        libopencv-dev \
        v4l-utils \
        curl \
        netstat-nat \
        chromium-browser \
        zenity
    
    # Install additional packages for Raspberry Pi
    if [ "$IS_RPI" = true ]; then
        print_status "Installing Raspberry Pi specific packages..."
        apt install -y \
            libraspberrypi-bin \
            python3-picamera2 || print_warning "picamera2 not available, continuing..."
    fi
    
    print_success "System dependencies installed"
}

# Function to create application directory
create_app_directory() {
    print_status "Creating application directory..."
    
    # Create directories
    mkdir -p "$APP_DIR"
    mkdir -p "$ICON_DIR"
    
    # Copy application files
    cp -r "$CURRENT_DIR"/* "$APP_DIR/"
    
    # Set permissions
    chmod +x "$APP_DIR/easy-mirror-launcher"
    chmod +x "$APP_DIR/start.sh"
    
    print_success "Application directory created at $APP_DIR"
}

# Function to create virtual environment
create_virtual_environment() {
    print_status "Creating Python virtual environment..."
    
    cd "$APP_DIR"
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate and install dependencies
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    print_success "Virtual environment created and dependencies installed"
}

# Function to create application icon
create_icon() {
    print_status "Creating application icon..."
    
    # Create a simple SVG icon if none exists
    cat > "$ICON_DIR/icon.svg" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#4CAF50;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#2196F3;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="64" height="64" rx="8" fill="url(#grad1)"/>
  <circle cx="32" cy="32" r="20" fill="none" stroke="white" stroke-width="3"/>
  <circle cx="32" cy="32" r="12" fill="none" stroke="white" stroke-width="2"/>
  <circle cx="32" cy="32" r="4" fill="white"/>
  <text x="32" y="52" text-anchor="middle" fill="white" font-family="Arial" font-size="8">MIRROR</text>
</svg>
EOF
    
    # Convert SVG to PNG if possible
    if command -v rsvg-convert >/dev/null 2>&1; then
        rsvg-convert -w 64 -h 64 "$ICON_DIR/icon.svg" -o "$ICON_DIR/icon.png"
    elif command -v convert >/dev/null 2>&1; then
        convert "$ICON_DIR/icon.svg" -resize 64x64 "$ICON_DIR/icon.png"
    else
        # Use SVG directly
        cp "$ICON_DIR/icon.svg" "$ICON_DIR/icon.png"
        print_warning "Could not convert SVG to PNG, using SVG as icon"
    fi
    
    print_success "Application icon created"
}

# Function to install launcher script
install_launcher() {
    print_status "Installing launcher script..."
    
    # Copy launcher to bin directory
    cp "$APP_DIR/easy-mirror-launcher" "$BIN_DIR/"
    chmod +x "$BIN_DIR/easy-mirror-launcher"
    
    print_success "Launcher script installed to $BIN_DIR"
}

# Function to install desktop entry
install_desktop_entry() {
    print_status "Installing desktop entry..."
    
    # Update desktop file with correct paths
    sed "s|/usr/local/share/easy-mirror/icon.png|$ICON_DIR/icon.png|g" \
        "$APP_DIR/easy-mirror.desktop" > "$DESKTOP_FILE"
    
    chmod 644 "$DESKTOP_FILE"
    
    # Update desktop database
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database /usr/share/applications/
    fi
    
    print_success "Desktop entry installed"
}

# Function to configure autostart (optional)
configure_autostart() {
    read -p "Do you want Easy Mirror to start automatically on boot? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Configuring autostart..."
        
        # Create systemd service
        cat > /etc/systemd/system/easy-mirror.service << EOF
[Unit]
Description=Easy Mirror Webcam Application
After=graphical-session.target

[Service]
Type=simple
User=pi
Environment=DISPLAY=:0
ExecStart=$BIN_DIR/easy-mirror-launcher
Restart=on-failure
RestartSec=5

[Install]
WantedBy=graphical-session.target
EOF
        
        systemctl daemon-reload
        systemctl enable easy-mirror.service
        
        print_success "Autostart configured"
    fi
}

# Function to test installation
test_installation() {
    print_status "Testing installation..."
    
    # Check if files exist
    if [ ! -f "$BIN_DIR/easy-mirror-launcher" ]; then
        print_error "Launcher script not found"
        return 1
    fi
    
    if [ ! -f "$DESKTOP_FILE" ]; then
        print_error "Desktop entry not found"
        return 1
    fi
    
    if [ ! -d "$APP_DIR/venv" ]; then
        print_error "Virtual environment not found"
        return 1
    fi
    
    # Test if Python dependencies are installed
    cd "$APP_DIR"
    source venv/bin/activate
    python3 -c "import flask, cv2, numpy; print('Dependencies OK')" || {
        print_error "Python dependencies test failed"
        return 1
    }
    
    print_success "Installation test passed"
}

# Function to show completion message
show_completion() {
    print_success "Easy Mirror has been successfully installed!"
    echo
    echo "You can now:"
    echo "  • Find 'Easy Mirror' in your Applications menu"
    echo "  • Run it from command line: easy-mirror-launcher"
    echo "  • Access the web interface at: http://localhost:12000"
    echo
    echo "The application will run in fullscreen mode when launched from the menu."
    echo "Press Alt+F4 or close the browser window to exit."
    echo
    if [ "$IS_RPI" = true ]; then
        echo "Raspberry Pi specific notes:"
        echo "  • Make sure your camera is connected and enabled"
        echo "  • Use 'sudo raspi-config' to enable the camera if needed"
        echo "  • The app will automatically detect USB and Pi cameras"
    fi
}

# Main installation function
main() {
    echo "Easy Mirror Raspberry Pi App Installer"
    echo "======================================"
    echo
    
    check_root
    detect_os
    
    print_status "Starting installation..."
    
    install_dependencies
    create_app_directory
    create_virtual_environment
    create_icon
    install_launcher
    install_desktop_entry
    configure_autostart
    test_installation
    
    show_completion
}

# Run main function
main "$@"