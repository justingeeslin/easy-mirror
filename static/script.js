// Easy Mirror - Frontend JavaScript

class EasyMirror {
    constructor() {
        this.currentFilter = 'none';
        this.isFullscreen = false;
        this.statusCheckInterval = null;
        this.clothingAvailable = false;
        this.currentClothing = {};
        this.availableClothing = {};
        this.measurementsAvailable = false;
        this.measurementDescriptions = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadFilters();
        this.loadClothing();
        this.loadMeasurements();
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

        // Measurements button
        document.getElementById('measurementsBtn').addEventListener('click', () => {
            this.toggleMeasurementsPanel();
        });

        // Take measurement button
        document.getElementById('takeMeasurementBtn').addEventListener('click', () => {
            this.takeMeasurement();
        });

        // Calibrate button
        document.getElementById('calibrateBtn').addEventListener('click', () => {
            this.toggleCalibrationPanel();
        });

        // Set calibration button
        document.getElementById('setCalibrateBtn').addEventListener('click', () => {
            this.setCalibration();
        });

        // Sex prediction button
        document.getElementById('sexPredictionBtn').addEventListener('click', () => {
            this.toggleSexPredictionPanel();
        });

        // Predict sex button
        document.getElementById('predictSexBtn').addEventListener('click', () => {
            this.predictSex();
        });

        // Show methodology button
        document.getElementById('showMethodologyBtn').addEventListener('click', () => {
            this.toggleMethodologyPanel();
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
            
            // Update measurements availability
            if (data.measurements_available && !this.measurementsAvailable) {
                this.loadMeasurements();
                document.getElementById('measurementsBtn').style.display = 'inline-block';
            } else if (!data.measurements_available) {
                document.getElementById('measurementsBtn').style.display = 'none';
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
        notification.className = `glass notification notification-${type}`;
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
            success: 'rgba(40, 167, 69, 0.5)',
            error: 'rgba(220, 53, 69, 0.2)',
            info: 'rgba(23, 162, 184, 0.2)',
            warning: 'rgba(255, 193, 7, 0.2)'
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

    // Measurements functionality
    async loadMeasurements() {
        try {
            const response = await fetch('/api/measurements/descriptions');
            if (response.ok) {
                this.measurementDescriptions = await response.json();
                this.measurementsAvailable = true;
            }
        } catch (error) {
            console.log('Measurements not available:', error);
            this.measurementsAvailable = false;
        }
    }

    toggleMeasurementsPanel() {
        const panel = document.getElementById('measurementsPanel');
        const isVisible = panel.style.display !== 'none';
        panel.style.display = isVisible ? 'none' : 'block';
        
        if (!isVisible && this.measurementsAvailable) {
            this.showMeasurementsInfo();
        }
    }

    toggleCalibrationPanel() {
        const panel = document.getElementById('calibrationPanel');
        const isVisible = panel.style.display !== 'none';
        panel.style.display = isVisible ? 'none' : 'block';
    }

    async takeMeasurement() {
        const resultsDiv = document.getElementById('measurementsResults');
        const button = document.getElementById('takeMeasurementBtn');
        
        // Show loading state
        button.disabled = true;
        button.textContent = '📐 Measuring...';
        resultsDiv.innerHTML = '<p class="measurements-info">Analyzing pose and calculating measurements...</p>';
        
        try {
            const response = await fetch('/api/measurements');
            const data = await response.json();
            
            if (response.ok) {
                this.displayMeasurements(data);
                this.showNotification('Measurements calculated successfully!', 'success');
            } else {
                this.displayMeasurementError(data.error || 'Failed to get measurements');
                this.showNotification('Failed to calculate measurements', 'error');
            }
        } catch (error) {
            console.error('Error taking measurement:', error);
            this.displayMeasurementError('Network error occurred');
            this.showNotification('Network error occurred', 'error');
        } finally {
            button.disabled = false;
            button.textContent = '📐 Take Measurement';
        }
    }

    displayMeasurements(data) {
        const resultsDiv = document.getElementById('measurementsResults');
        
        if (!data.pose_detected) {
            this.displayMeasurementError(data.error || 'No pose detected in frame');
            return;
        }
        
        let html = '<div class="measurements-data">';
        
        // Group measurements by category
        const categories = {
            'Basic Measurements': ['shoulder_breadth', 'standing_height', 'arm_span'],
            'Upper Body': ['left_upper_arm_length', 'right_upper_arm_length', 'left_forearm_length', 'right_forearm_length'],
            'Lower Body': ['left_thigh_length', 'right_thigh_length', 'left_lower_leg_length', 'right_lower_leg_length'],
            'Circumferences (Estimated)': ['chest_circumference', 'waist_circumference', 'head_circumference']
        };
        
        for (const [category, measurements] of Object.entries(categories)) {
            const categoryMeasurements = measurements.filter(m => data[m] !== undefined);
            if (categoryMeasurements.length > 0) {
                html += `<div class="measurement-category">${category}</div>`;
                
                for (const measurement of categoryMeasurements) {
                    const value = data[measurement];
                    const label = this.formatMeasurementLabel(measurement);
                    html += `
                        <div class="measurement-item">
                            <span class="measurement-label">${label}</span>
                            <span class="measurement-value">${value.toFixed(1)}<span class="measurement-unit">cm</span></span>
                        </div>
                    `;
                }
            }
        }
        
        html += '</div>';
        
        // Add calibration note if present
        if (data.calibration_note) {
            html += `<div class="measurement-note">${data.calibration_note}</div>`;
        }
        
        resultsDiv.innerHTML = html;
    }

    displayMeasurementError(error) {
        const resultsDiv = document.getElementById('measurementsResults');
        resultsDiv.innerHTML = `
            <div class="measurements-error">
                <strong>Error:</strong> ${error}
                <br><br>
                <strong>Tips:</strong>
                <ul>
                    <li>Stand facing the camera with your full body visible</li>
                    <li>Ensure good lighting</li>
                    <li>Keep arms slightly away from your body</li>
                    <li>Stand in a neutral pose</li>
                </ul>
            </div>
        `;
    }

    showMeasurementsInfo() {
        const resultsDiv = document.getElementById('measurementsResults');
        resultsDiv.innerHTML = `
            <p class="measurements-info">
                Click "Take Measurement" to analyze your pose and calculate body measurements.
                <br><br>
                <strong>Available measurements:</strong>
                <ul style="text-align: left; margin-top: 10px;">
                    <li>Shoulder breadth, standing height, arm span</li>
                    <li>Upper and lower arm lengths (both sides)</li>
                    <li>Thigh and lower leg lengths (both sides)</li>
                    <li>Estimated circumferences (chest, waist, head)</li>
                </ul>
            </p>
        `;
    }

    formatMeasurementLabel(measurement) {
        const labels = {
            'shoulder_breadth': 'Shoulder Breadth',
            'standing_height': 'Standing Height',
            'arm_span': 'Arm Span',
            'left_upper_arm_length': 'Left Upper Arm',
            'right_upper_arm_length': 'Right Upper Arm',
            'left_forearm_length': 'Left Forearm',
            'right_forearm_length': 'Right Forearm',
            'left_thigh_length': 'Left Thigh',
            'right_thigh_length': 'Right Thigh',
            'left_lower_leg_length': 'Left Lower Leg',
            'right_lower_leg_length': 'Right Lower Leg',
            'chest_circumference': 'Chest Circumference',
            'waist_circumference': 'Waist Circumference',
            'head_circumference': 'Head Circumference'
        };
        return labels[measurement] || measurement.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    async setCalibration() {
        const knownValue = parseFloat(document.getElementById('knownMeasurement').value);
        const measurementType = document.getElementById('measurementType').value;
        
        if (!knownValue || knownValue <= 0) {
            this.showNotification('Please enter a valid measurement value', 'error');
            return;
        }
        
        // First, take a measurement to get the current pixel value
        try {
            const response = await fetch('/api/measurements');
            const data = await response.json();
            
            if (!response.ok || !data.pose_detected || !data[measurementType]) {
                this.showNotification('Cannot calibrate: measurement not available in current pose', 'error');
                return;
            }
            
            const currentPixelValue = data[measurementType];
            const newRatio = knownValue / currentPixelValue * 0.1; // Current ratio is 0.1
            
            // Set the new calibration
            const calibrateResponse = await fetch('/api/measurements/calibrate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    pixel_to_cm_ratio: newRatio
                })
            });
            
            if (calibrateResponse.ok) {
                this.showNotification('Calibration updated successfully!', 'success');
                document.getElementById('calibrationPanel').style.display = 'none';
                document.getElementById('knownMeasurement').value = '';
            } else {
                this.showNotification('Failed to update calibration', 'error');
            }
            
        } catch (error) {
            console.error('Error setting calibration:', error);
            this.showNotification('Error setting calibration', 'error');
        }
    }

    toggleSexPredictionPanel() {
        const panel = document.getElementById('sexPredictionPanel');
        const isVisible = panel.style.display !== 'none';
        
        // Hide other panels
        document.getElementById('measurementsPanel').style.display = 'none';
        
        panel.style.display = isVisible ? 'none' : 'block';
    }

    toggleMethodologyPanel() {
        const panel = document.getElementById('methodologyPanel');
        const isVisible = panel.style.display !== 'none';
        panel.style.display = isVisible ? 'none' : 'block';
    }

    async predictSex() {
        const resultsDiv = document.getElementById('sexPredictionResults');
        const predictBtn = document.getElementById('predictSexBtn');
        
        try {
            predictBtn.disabled = true;
            predictBtn.textContent = '🔬 Analyzing...';
            
            resultsDiv.innerHTML = '<div class="loading">Analyzing pose and calculating measurements...</div>';

            const response = await fetch('/api/sex-prediction');
            const data = await response.json();

            if (response.ok) {
                this.displaySexPredictionResults(data);
            } else {
                resultsDiv.innerHTML = `<div class="error">Error: ${data.error}</div>`;
            }

        } catch (error) {
            console.error('Error predicting sex:', error);
            resultsDiv.innerHTML = '<div class="error">Error connecting to server</div>';
        } finally {
            predictBtn.disabled = false;
            predictBtn.textContent = '🔬 Analyze Current Pose';
        }
    }

    displaySexPredictionResults(data) {
        const resultsDiv = document.getElementById('sexPredictionResults');
        
        if (data.prediction === 'error') {
            resultsDiv.innerHTML = `<div class="error">Error: ${data.error}</div>`;
            return;
        }

        if (data.prediction === 'insufficient_data') {
            resultsDiv.innerHTML = `
                <div class="warning">
                    <h4>⚠️ Insufficient Data</h4>
                    <p>Not enough anthropometric measurements available for reliable prediction.</p>
                    <p>Please ensure you are clearly visible in the camera with good lighting.</p>
                </div>
            `;
            return;
        }

        const prediction = data.prediction.toUpperCase();
        const confidence = (data.confidence * 100).toFixed(1);
        const certainty = (data.certainty * 100).toFixed(1);
        const maleScore = (data.scores.male * 100).toFixed(1);
        const femaleScore = (data.scores.female * 100).toFixed(1);

        let predictionClass = 'prediction-result';
        if (data.prediction === 'male') {
            predictionClass += ' prediction-male';
        } else if (data.prediction === 'female') {
            predictionClass += ' prediction-female';
        } else {
            predictionClass += ' prediction-uncertain';
        }

        let html = `
            <div class="${predictionClass}">
                <h4>🧬 Prediction Results</h4>
                <div class="prediction-summary">
                    <div class="prediction-main">
                        <span class="prediction-label">Predicted Sex:</span>
                        <span class="prediction-value">${prediction}</span>
                    </div>
                    <div class="prediction-confidence">
                        <span class="confidence-label">Confidence:</span>
                        <span class="confidence-value">${confidence}%</span>
                    </div>
                    <div class="prediction-certainty">
                        <span class="certainty-label">Certainty:</span>
                        <span class="certainty-value">${certainty}%</span>
                    </div>
                </div>
                
                <div class="score-breakdown">
                    <h5>Score Breakdown:</h5>
                    <div class="score-bars">
                        <div class="score-bar">
                            <span class="score-label">Male:</span>
                            <div class="score-bar-container">
                                <div class="score-bar-fill male-score" style="width: ${maleScore}%"></div>
                                <span class="score-value">${maleScore}%</span>
                            </div>
                        </div>
                        <div class="score-bar">
                            <span class="score-label">Female:</span>
                            <div class="score-bar-container">
                                <div class="score-bar-fill female-score" style="width: ${femaleScore}%"></div>
                                <span class="score-value">${femaleScore}%</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="indicators-used">
                    <h5>Indicators Used (${data.indicators_used}/${data.total_possible_indicators}):</h5>
                    <div class="indicators-list">
        `;

        // Add indicator details
        for (const [indicator, details] of Object.entries(data.indicator_details)) {
            const indicatorName = indicator.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            let value = details.value;
            const prediction = details.prediction;
            const confidence = (details.confidence * 100).toFixed(0);
            
            let unit = 'cm';
            if (indicator.includes('ratio')) {
                unit = '';
                value = value.toFixed(3);
            } else {
                value = value.toFixed(1);
            }
            
            html += `
                <div class="indicator-item">
                    <span class="indicator-name">${indicatorName}:</span>
                    <span class="indicator-value">${value}${unit}</span>
                    <span class="indicator-prediction ${prediction}">${prediction} (${confidence}%)</span>
                </div>
            `;
        }

        html += `
                    </div>
                </div>
                
                <div class="prediction-note">
                    <p><strong>Note:</strong> This prediction is based on established patterns of sexual dimorphism in human anthropometry. Individual variation exists and predictions should be interpreted as estimates only. This tool is for educational and research purposes.</p>
                </div>
            </div>
        `;

        resultsDiv.innerHTML = html;
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