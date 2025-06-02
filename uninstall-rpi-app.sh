#!/bin/bash
# Easy Mirror Raspberry Pi App Uninstaller
# This script removes Easy Mirror desktop application from Raspberry Pi

set -e

# Configuration
APP_NAME="easy-mirror"
APP_DIR="/usr/local/share/$APP_NAME"
BIN_DIR="/usr/local/bin"
DESKTOP_FILE="/usr/share/applications/$APP_NAME.desktop"
SERVICE_FILE="/etc/systemd/system/easy-mirror.service"

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

# Function to stop running services
stop_services() {
    print_status "Stopping Easy Mirror services..."
    
    # Stop systemd service if it exists
    if [ -f "$SERVICE_FILE" ]; then
        systemctl stop easy-mirror.service 2>/dev/null || true
        systemctl disable easy-mirror.service 2>/dev/null || true
        rm -f "$SERVICE_FILE"
        systemctl daemon-reload
        print_success "Systemd service stopped and removed"
    fi
    
    # Kill any running processes
    pkill -f "easy-mirror-launcher" 2>/dev/null || true
    pkill -f "python.*app.py" 2>/dev/null || true
    
    # Clean up user log and pid files
    rm -f /home/*/easy-mirror.log 2>/dev/null || true
    rm -f /home/*/easy-mirror.pid 2>/dev/null || true
}

# Function to remove application files
remove_files() {
    print_status "Removing application files..."
    
    # Remove application directory
    if [ -d "$APP_DIR" ]; then
        rm -rf "$APP_DIR"
        print_success "Application directory removed"
    fi
    
    # Remove launcher script
    if [ -f "$BIN_DIR/easy-mirror-launcher" ]; then
        rm -f "$BIN_DIR/easy-mirror-launcher"
        print_success "Launcher script removed"
    fi
    
    # Remove desktop entry
    if [ -f "$DESKTOP_FILE" ]; then
        rm -f "$DESKTOP_FILE"
        print_success "Desktop entry removed"
    fi
    
    # Update desktop database
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database /usr/share/applications/ 2>/dev/null || true
    fi
}

# Function to ask about removing dependencies
remove_dependencies() {
    echo
    read -p "Do you want to remove system dependencies that were installed? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Removing system dependencies..."
        print_warning "This will remove packages that might be used by other applications!"
        
        read -p "Are you sure you want to continue? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            apt remove --autoremove -y \
                python3-opencv \
                libopencv-dev \
                v4l-utils \
                zenity 2>/dev/null || print_warning "Some packages could not be removed"
            
            print_success "Dependencies removed"
        else
            print_status "Skipping dependency removal"
        fi
    else
        print_status "Keeping system dependencies"
    fi
}

# Function to show completion message
show_completion() {
    print_success "Easy Mirror has been successfully uninstalled!"
    echo
    echo "The following items have been removed:"
    echo "  • Application files from $APP_DIR"
    echo "  • Launcher script from $BIN_DIR"
    echo "  • Desktop entry from Applications menu"
    echo "  • Systemd service (if configured)"
    echo
    echo "User data and logs have been cleaned up."
}

# Main uninstallation function
main() {
    echo "Easy Mirror Raspberry Pi App Uninstaller"
    echo "========================================"
    echo
    
    check_root
    
    print_warning "This will completely remove Easy Mirror from your system."
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Uninstallation cancelled"
        exit 0
    fi
    
    print_status "Starting uninstallation..."
    
    stop_services
    remove_files
    remove_dependencies
    
    show_completion
}

# Run main function
main "$@"