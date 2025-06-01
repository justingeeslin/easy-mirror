// Easy Mirror - Frontend JavaScript

class EasyMirror {
    constructor() {
        this.currentFilter = 'none';
        this.isFullscreen = false;
        this.statusCheckInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadFilters();
        this.startStatusCheck();
        this.hideLoadingOverlay();
    }

    setupEventListeners() {
        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.refreshCamera();
        });

        // Fullscreen button
        document.getElementById('fullscreenBtn').addEventListener('click', () => {
            this.toggleFullscreen();
        });

        // Video stream load events
        const videoStream = document.getElementById('videoStream');
        videoStream.addEventListener('load', () => {
            this.hideLoadingOverlay();
        });

        videoStream.addEventListener('error', () => {
            this.showErrorOverlay();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'f' || e.key === 'F') {
                this.toggleFullscreen();
            } else if (e.key === 'Escape' && this.isFullscreen) {
                this.toggleFullscreen();
            } else if (e.key >= '1' && e.key <= '9') {
                const filterIndex = parseInt(e.key) - 1;
                const filterButtons = document.querySelectorAll('.filter-btn');
                if (filterButtons[filterIndex]) {
                    filterButtons[filterIndex].click();
                }
            }
        });
    }

    async loadFilters() {
        try {
            const response = await fetch('/api/filters');
            const data = await response.json();
            
            if (data.filters) {
                this.renderFilters(data.filters);
                this.currentFilter = data.current || 'none';
                this.updateCurrentFilterDisplay();
            }
        } catch (error) {
            console.error('Error loading filters:', error);
            this.showNotification('Error loading filters', 'error');
        }
    }

    renderFilters(filters) {
        const filterGrid = document.getElementById('filterGrid');
        filterGrid.innerHTML = '';

        // Filter display names
        const filterNames = {
            'none': '🔍 None',
            'blur': '🌫️ Blur',
            'edge': '📐 Edge',
            'grayscale': '⚫ Grayscale',
            'sepia': '🟤 Sepia',
            'invert': '🔄 Invert',
            'emboss': '🎭 Emboss',
            'cartoon': '🎨 Cartoon',
            'vintage': '📷 Vintage',
            'cool': '❄️ Cool',
            'warm': '🔥 Warm'
        };

        filters.forEach((filter, index) => {
            const button = document.createElement('button');
            button.className = 'filter-btn';
            button.textContent = filterNames[filter] || filter;
            button.dataset.filter = filter;
            button.title = `Apply ${filter} filter (${index + 1})`;
            
            if (filter === this.currentFilter) {
                button.classList.add('active');
            }

            button.addEventListener('click', () => {
                this.setFilter(filter, button);
            });

            filterGrid.appendChild(button);
        });
    }

    async setFilter(filterName, buttonElement) {
        try {
            // Visual feedback
            const videoStream = document.getElementById('videoStream');
            videoStream.classList.add('filter-changing');
            
            // Update active button
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            buttonElement.classList.add('active');

            const response = await fetch('/api/filter', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ filter: filterName })
            });

            const data = await response.json();
            
            if (data.success) {
                this.currentFilter = filterName;
                this.updateCurrentFilterDisplay();
                this.showNotification(`Filter changed to ${filterName}`, 'success', filterName);
            } else {
                throw new Error(data.error || 'Failed to set filter');
            }

            // Remove visual feedback
            setTimeout(() => {
                videoStream.classList.remove('filter-changing');
            }, 300);

        } catch (error) {
            console.error('Error setting filter:', error);
            this.showNotification('Error changing filter', 'error');
            
            // Revert button state
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
                if (btn.dataset.filter === this.currentFilter) {
                    btn.classList.add('active');
                }
            });
        }
    }

    async checkStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            const statusElement = document.getElementById('cameraStatus');
            if (data.camera_available) {
                statusElement.textContent = 'Connected';
                statusElement.style.color = '#28a745';
                this.hideErrorOverlay();
            } else {
                statusElement.textContent = 'Disconnected';
                statusElement.style.color = '#dc3545';
                this.showErrorOverlay();
            }
        } catch (error) {
            console.error('Error checking status:', error);
            const statusElement = document.getElementById('cameraStatus');
            statusElement.textContent = 'Error';
            statusElement.style.color = '#dc3545';
        }
    }

    startStatusCheck() {
        this.checkStatus();
        this.statusCheckInterval = setInterval(() => {
            this.checkStatus();
        }, 5000); // Check every 5 seconds
    }

    updateCurrentFilterDisplay() {
        const currentFilterElement = document.getElementById('currentFilter');
        currentFilterElement.textContent = this.currentFilter.charAt(0).toUpperCase() + 
                                         this.currentFilter.slice(1);
    }

    refreshCamera() {
        this.showLoadingOverlay();
        
        // Refresh the video stream by updating the src
        const videoStream = document.getElementById('videoStream');
        const currentSrc = videoStream.src;
        videoStream.src = '';
        
        setTimeout(() => {
            videoStream.src = currentSrc + '?t=' + new Date().getTime();
        }, 500);

        this.showNotification('Camera refreshed', 'info');
    }

    toggleFullscreen() {
        const videoContainer = document.querySelector('.video-container');
        
        if (!this.isFullscreen) {
            videoContainer.classList.add('fullscreen');
            this.isFullscreen = true;
            document.getElementById('fullscreenBtn').textContent = '🔍 Exit Fullscreen';
        } else {
            videoContainer.classList.remove('fullscreen');
            this.isFullscreen = false;
            document.getElementById('fullscreenBtn').textContent = '🔍 Fullscreen';
        }
    }

    showLoadingOverlay() {
        document.getElementById('loadingOverlay').style.display = 'flex';
        document.getElementById('errorOverlay').style.display = 'none';
    }

    hideLoadingOverlay() {
        setTimeout(() => {
            document.getElementById('loadingOverlay').style.display = 'none';
        }, 1000);
    }

    showErrorOverlay() {
        document.getElementById('loadingOverlay').style.display = 'none';
        document.getElementById('errorOverlay').style.display = 'flex';
    }

    hideErrorOverlay() {
        document.getElementById('errorOverlay').style.display = 'none';
    }

    showNotification(message, type = 'info', filterName = null) {
        // Get appropriate icon for the notification
        const icon = this.getNotificationIcon(type, filterName);
        
        // Use the iOS notification component
        IOSNotification.show({
            title: this.getNotificationTitle(type),
            message: message,
            type: type,
            icon: icon,
            duration: 3000
        });
    }

    getNotificationTitle(type) {
        const titles = {
            success: 'Success',
            error: 'Error',
            info: 'Info',
            warning: 'Warning'
        };
        return titles[type] || 'Notification';
    }

    getNotificationIcon(type, filterName = null) {
        // If it's a filter change, use filter-specific icon
        if (filterName) {
            const filterIcons = {
                'none': '🔍',
                'blur': '🌫️',
                'edge': '📐',
                'grayscale': '⚫',
                'sepia': '🟤',
                'invert': '🔄',
                'emboss': '🎭',
                'cartoon': '🎨',
                'vintage': '📷',
                'cool': '❄️',
                'warm': '🔥'
            };
            return filterIcons[filterName] || '🎨';
        }

        // Default icons by type
        const typeIcons = {
            success: '✅',
            error: '❌',
            info: 'ℹ️',
            warning: '⚠️'
        };
        return typeIcons[type] || 'ℹ️';
    }

    destroy() {
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.easyMirror = new EasyMirror();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.easyMirror) {
        window.easyMirror.destroy();
    }
});