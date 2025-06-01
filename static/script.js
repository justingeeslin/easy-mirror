// Easy Mirror - Frontend JavaScript

class EasyMirror {
    constructor() {
        this.currentFilter = 'none';
        this.isFullscreen = false;
        this.statusCheckInterval = null;
        this.clothingAvailable = false;
        this.currentClothing = {};
        this.availableClothing = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadFilters();
        this.loadClothing();
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
            'warm': '🔥 Warm',
            'clothing': '👕 Clothing'
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
                this.showNotification(`Filter changed to ${filterName}`, 'success');
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

    async loadClothing() {
        try {
            const response = await fetch('/api/clothing');
            if (response.ok) {
                const data = await response.json();
                this.availableClothing = data.available;
                this.currentClothing = data.current;
                this.clothingAvailable = true;
                this.renderClothingPanel();
            }
        } catch (error) {
            console.log('Clothing system not available:', error);
            this.clothingAvailable = false;
        }
    }

    renderClothingPanel() {
        if (!this.clothingAvailable) return;

        // Create clothing panel if it doesn't exist
        let clothingPanel = document.getElementById('clothingPanel');
        if (!clothingPanel) {
            clothingPanel = document.createElement('div');
            clothingPanel.id = 'clothingPanel';
            clothingPanel.className = 'clothing-panel';
            clothingPanel.innerHTML = `
                <h3>👕 Virtual Clothing</h3>
                <div class="clothing-categories"></div>
                <button id="clearClothingBtn" class="clear-clothing-btn">Clear All</button>
            `;
            
            // Insert after filter grid
            const filterGrid = document.getElementById('filterGrid');
            filterGrid.parentNode.insertBefore(clothingPanel, filterGrid.nextSibling);
            
            // Add clear button listener
            document.getElementById('clearClothingBtn').addEventListener('click', () => {
                this.clearAllClothing();
            });
        }

        const categoriesContainer = clothingPanel.querySelector('.clothing-categories');
        categoriesContainer.innerHTML = '';

        // Render each category
        Object.keys(this.availableClothing).forEach(category => {
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'clothing-category';
            
            const categoryTitle = document.createElement('h4');
            categoryTitle.textContent = category.charAt(0).toUpperCase() + category.slice(1);
            categoryDiv.appendChild(categoryTitle);
            
            const itemsGrid = document.createElement('div');
            itemsGrid.className = 'clothing-items-grid';
            
            // Add "None" option
            const noneBtn = document.createElement('button');
            noneBtn.className = 'clothing-item-btn';
            noneBtn.textContent = 'None';
            noneBtn.dataset.category = category;
            noneBtn.dataset.item = 'none';
            if (!this.currentClothing[category]) {
                noneBtn.classList.add('active');
            }
            noneBtn.addEventListener('click', () => {
                this.setClothingItem(category, 'none', noneBtn);
            });
            itemsGrid.appendChild(noneBtn);
            
            // Add clothing items
            Object.keys(this.availableClothing[category]).forEach(itemId => {
                const item = this.availableClothing[category][itemId];
                const itemBtn = document.createElement('button');
                itemBtn.className = 'clothing-item-btn';
                itemBtn.textContent = item.name;
                itemBtn.dataset.category = category;
                itemBtn.dataset.item = itemId;
                
                if (this.currentClothing[category] === itemId) {
                    itemBtn.classList.add('active');
                }
                
                itemBtn.addEventListener('click', () => {
                    this.setClothingItem(category, itemId, itemBtn);
                });
                
                itemsGrid.appendChild(itemBtn);
            });
            
            categoryDiv.appendChild(itemsGrid);
            categoriesContainer.appendChild(categoryDiv);
        });
    }

    async setClothingItem(category, itemId, buttonElement) {
        try {
            const response = await fetch(`/api/clothing/${category}/${itemId}`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentClothing = data.current;
                
                // Update button states for this category
                const categoryButtons = document.querySelectorAll(`[data-category="${category}"]`);
                categoryButtons.forEach(btn => btn.classList.remove('active'));
                buttonElement.classList.add('active');
                
                this.showNotification(`${category} updated`, 'success');
            } else {
                throw new Error(data.error || 'Failed to set clothing item');
            }
        } catch (error) {
            console.error('Error setting clothing item:', error);
            this.showNotification('Error updating clothing', 'error');
        }
    }

    async clearAllClothing() {
        try {
            const response = await fetch('/api/clothing/clear', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentClothing = data.current;
                
                // Update all button states
                document.querySelectorAll('.clothing-item-btn').forEach(btn => {
                    btn.classList.remove('active');
                    if (btn.dataset.item === 'none') {
                        btn.classList.add('active');
                    }
                });
                
                this.showNotification('All clothing cleared', 'success');
            }
        } catch (error) {
            console.error('Error clearing clothing:', error);
            this.showNotification('Error clearing clothing', 'error');
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
            
            // Update clothing availability
            if (data.clothing_available && !this.clothingAvailable) {
                this.loadClothing();
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

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '10000',
            opacity: '0',
            transform: 'translateX(100%)',
            transition: 'all 0.3s ease'
        });

        // Set background color based on type
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            info: '#17a2b8',
            warning: '#ffc107'
        };
        notification.style.backgroundColor = colors[type] || colors.info;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
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