#!/usr/bin/env python3
"""
Clothing Overlay System for Easy Mirror
Handles pose detection and clothing overlay using MediaPipe and OpenCV.
"""

import cv2
import numpy as np
import mediapipe as mp
from PIL import Image, ImageDraw
import json
import os
import logging

logger = logging.getLogger(__name__)

class ClothingOverlay:
    def __init__(self, config_path="clothing_config.json"):
        """Initialize the clothing overlay system."""
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.clothing_config = self.load_clothing_config(config_path)
        self.clothing_cache = {}
        self.current_clothing = {
            'shirts': None,
            'hats': None,
            'accessories': None
        }
        
        # MediaPipe pose landmark indices
        self.landmark_indices = {
            'nose': 0,
            'left_eye_inner': 1,
            'left_eye': 2,
            'left_eye_outer': 3,
            'right_eye_inner': 4,
            'right_eye': 5,
            'right_eye_outer': 6,
            'left_ear': 7,
            'right_ear': 8,
            'mouth_left': 9,
            'mouth_right': 10,
            'left_shoulder': 11,
            'right_shoulder': 12,
            'left_elbow': 13,
            'right_elbow': 14,
            'left_wrist': 15,
            'right_wrist': 16,
            'left_pinky': 17,
            'right_pinky': 18,
            'left_index': 19,
            'right_index': 20,
            'left_thumb': 21,
            'right_thumb': 22,
            'left_hip': 23,
            'right_hip': 24
        }
    
    def load_clothing_config(self, config_path):
        """Load clothing configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading clothing config: {e}")
            return {"clothing_items": {}}
    
    def load_clothing_image(self, clothing_item):
        """Load and cache a clothing image."""
        file_path = clothing_item['file']
        
        if file_path in self.clothing_cache:
            return self.clothing_cache[file_path]
        
        try:
            if os.path.exists(file_path):
                # Load image with PIL to handle transparency
                pil_image = Image.open(file_path).convert('RGBA')
                # Convert to OpenCV format
                cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGBA2BGRA)
                self.clothing_cache[file_path] = cv_image
                return cv_image
            else:
                logger.warning(f"Clothing file not found: {file_path}")
                return None
        except Exception as e:
            logger.error(f"Error loading clothing image {file_path}: {e}")
            return None
    
    def get_landmark_position(self, landmarks, landmark_name, frame_width, frame_height):
        """Get the pixel position of a landmark."""
        if landmark_name not in self.landmark_indices:
            return None
        
        landmark_idx = self.landmark_indices[landmark_name]
        if landmark_idx < len(landmarks.landmark):
            landmark = landmarks.landmark[landmark_idx]
            if landmark.visibility > 0.5:  # Only use visible landmarks
                x = int(landmark.x * frame_width)
                y = int(landmark.y * frame_height)
                return (x, y)
        return None
    
    def calculate_clothing_position(self, landmarks, clothing_item, frame_width, frame_height):
        """Calculate where to place a clothing item based on pose landmarks."""
        anchor_points = clothing_item.get('anchor_points', ['nose'])
        offset = clothing_item.get('offset', [0, 0])
        scale_factor = clothing_item.get('scale_factor', 1.0)
        
        # Get positions of anchor points
        positions = []
        for anchor in anchor_points:
            pos = self.get_landmark_position(landmarks, anchor, frame_width, frame_height)
            if pos:
                positions.append(pos)
        
        if not positions:
            return None
        
        # Calculate center position
        if len(positions) == 1:
            center_x, center_y = positions[0]
        else:
            # Average position of multiple anchor points
            center_x = sum(pos[0] for pos in positions) // len(positions)
            center_y = sum(pos[1] for pos in positions) // len(positions)
        
        # Apply offset
        center_x += offset[0]
        center_y += offset[1]
        
        # Calculate scale based on shoulder distance for better fitting
        if len(positions) >= 2 and 'shoulder' in anchor_points[0]:
            shoulder_distance = abs(positions[1][0] - positions[0][0])
            scale_factor *= max(0.5, min(2.0, shoulder_distance / 100.0))
        
        return {
            'center': (center_x, center_y),
            'scale': scale_factor
        }
    
    def overlay_clothing_item(self, frame, clothing_image, position_info):
        """Overlay a clothing item on the frame."""
        if clothing_image is None or position_info is None:
            return frame
        
        center_x, center_y = position_info['center']
        scale = position_info['scale']
        
        # Resize clothing image
        height, width = clothing_image.shape[:2]
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        if new_width <= 0 or new_height <= 0:
            return frame
        
        resized_clothing = cv2.resize(clothing_image, (new_width, new_height))
        
        # Calculate position to center the clothing item
        start_x = center_x - new_width // 2
        start_y = center_y - new_height // 2
        
        # Ensure the clothing item fits within the frame
        frame_height, frame_width = frame.shape[:2]
        
        # Clip to frame boundaries
        src_start_x = max(0, -start_x)
        src_start_y = max(0, -start_y)
        src_end_x = min(new_width, frame_width - start_x)
        src_end_y = min(new_height, frame_height - start_y)
        
        dst_start_x = max(0, start_x)
        dst_start_y = max(0, start_y)
        dst_end_x = dst_start_x + (src_end_x - src_start_x)
        dst_end_y = dst_start_y + (src_end_y - src_start_y)
        
        if src_end_x <= src_start_x or src_end_y <= src_start_y:
            return frame
        
        # Extract the region to overlay
        clothing_region = resized_clothing[src_start_y:src_end_y, src_start_x:src_end_x]
        
        if clothing_region.shape[2] == 4:  # BGRA
            # Handle transparency
            alpha = clothing_region[:, :, 3] / 255.0
            alpha = np.expand_dims(alpha, axis=2)
            
            # Blend the clothing with the background
            frame_region = frame[dst_start_y:dst_end_y, dst_start_x:dst_end_x]
            clothing_rgb = clothing_region[:, :, :3]
            
            blended = frame_region * (1 - alpha) + clothing_rgb * alpha
            frame[dst_start_y:dst_end_y, dst_start_x:dst_end_x] = blended.astype(np.uint8)
        else:
            # No transparency, direct overlay
            frame[dst_start_y:dst_end_y, dst_start_x:dst_end_x] = clothing_region
        
        return frame
    
    def apply_clothing_filter(self, frame):
        """Apply clothing overlay to a frame."""
        try:
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)
            
            if results.pose_landmarks:
                frame_height, frame_width = frame.shape[:2]
                
                # Apply clothing items in order: shirts, hats, accessories
                for category in ['shirts', 'hats', 'accessories']:
                    if self.current_clothing[category]:
                        clothing_item = self.clothing_config['clothing_items'][category][self.current_clothing[category]]
                        clothing_image = self.load_clothing_image(clothing_item)
                        
                        if clothing_image is not None:
                            position_info = self.calculate_clothing_position(
                                results.pose_landmarks, clothing_item, frame_width, frame_height
                            )
                            frame = self.overlay_clothing_item(frame, clothing_image, position_info)
            
            return frame
            
        except Exception as e:
            logger.error(f"Error applying clothing filter: {e}")
            return frame
    
    def set_clothing_item(self, category, item_id):
        """Set a clothing item for a specific category."""
        if category in self.current_clothing:
            if item_id in self.clothing_config['clothing_items'].get(category, {}):
                self.current_clothing[category] = item_id
                logger.info(f"Set {category} to {item_id}")
                return True
            elif item_id is None:
                self.current_clothing[category] = None
                logger.info(f"Removed {category}")
                return True
        return False
    
    def get_current_clothing(self):
        """Get current clothing configuration."""
        return self.current_clothing.copy()
    
    def get_available_clothing(self):
        """Get all available clothing items."""
        return self.clothing_config['clothing_items']
    
    def clear_all_clothing(self):
        """Remove all clothing items."""
        for category in self.current_clothing:
            self.current_clothing[category] = None
    
    def generate_ui_html(self):
        """Generate HTML for clothing overlay UI controls."""
        html = '''
        <div class="module-section" id="clothing-section">
            <h3>👕 Virtual Clothing</h3>
            <div class="clothing-controls">
                <button id="clear-clothing-btn" class="action-btn secondary">
                    <span class="btn-icon">🧹</span>
                    Clear All
                </button>
                <button id="clothing-filter-btn" class="filter-btn" data-filter="clothing" data-module="clothing">
                    <span class="filter-icon">👔</span>
                    <span class="filter-name">Clothing Filter</span>
                </button>
            </div>
        '''
        
        # Generate clothing categories
        for category, items in self.clothing_config['clothing_items'].items():
            category_display = category.replace('_', ' ').title()
            html += f'''
            <div class="clothing-category">
                <h4>{category_display}</h4>
                <div class="clothing-items">
                    <button class="clothing-item-btn" data-category="{category}" data-item="none">
                        <span class="item-icon">❌</span>
                        <span class="item-name">None</span>
                    </button>
            '''
            
            for item_id, item_config in items.items():
                active_class = 'active' if self.current_clothing.get(category) == item_id else ''
                html += f'''
                    <button class="clothing-item-btn {active_class}" 
                            data-category="{category}" 
                            data-item="{item_id}"
                            title="{item_config.get('description', item_config['name'])}">
                        <span class="item-icon">{item_config.get('icon', '👔')}</span>
                        <span class="item-name">{item_config['name']}</span>
                    </button>
                '''
            
            html += '''
                </div>
            </div>
            '''
        
        html += '''
        </div>
        '''
        return html
    
    def generate_ui_css(self):
        """Generate CSS for clothing overlay UI."""
        return '''
        .clothing-controls {
            display: flex;
            gap: 10px;
            margin-top: 10px;
            flex-wrap: wrap;
        }
        
        .clothing-category {
            margin-top: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: #f8f9fa;
        }
        
        .clothing-category h4 {
            margin: 0 0 10px 0;
            color: #495057;
        }
        
        .clothing-items {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
        }
        
        .clothing-item-btn {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 8px;
            background: white;
            cursor: pointer;
            transition: all 0.3s ease;
            min-height: 70px;
        }
        
        .clothing-item-btn:hover {
            border-color: #17a2b8;
            background: #f8f9fa;
            transform: translateY(-2px);
        }
        
        .clothing-item-btn.active {
            border-color: #17a2b8;
            background: #e1f5fe;
            box-shadow: 0 2px 8px rgba(23,162,184,0.3);
        }
        
        .item-icon {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .item-name {
            font-size: 12px;
            font-weight: 500;
            text-align: center;
        }
        '''
    
    def generate_ui_javascript(self):
        """Generate JavaScript for clothing overlay UI."""
        return '''
        // Clothing Overlay Module JavaScript
        function initClothingModule() {
            const clearBtn = document.getElementById('clear-clothing-btn');
            const clothingFilterBtn = document.getElementById('clothing-filter-btn');
            const clothingItemBtns = document.querySelectorAll('.clothing-item-btn');
            
            // Clear all clothing
            if (clearBtn) {
                clearBtn.addEventListener('click', async function() {
                    try {
                        const response = await fetch('/api/clothing/clear', {
                            method: 'POST'
                        });
                        
                        const data = await response.json();
                        if (response.ok) {
                            // Update UI to show no items selected
                            clothingItemBtns.forEach(btn => {
                                btn.classList.remove('active');
                                if (btn.dataset.item === 'none') {
                                    btn.classList.add('active');
                                }
                            });
                        } else {
                            alert('Error: ' + data.error);
                        }
                    } catch (error) {
                        alert('Error clearing clothing: ' + error.message);
                    }
                });
            }
            
            // Clothing filter toggle
            if (clothingFilterBtn) {
                clothingFilterBtn.addEventListener('click', function() {
                    const isActive = this.classList.contains('active');
                    
                    // Remove active from all filter buttons
                    document.querySelectorAll('.filter-btn').forEach(btn => {
                        btn.classList.remove('active');
                    });
                    
                    if (!isActive) {
                        this.classList.add('active');
                        setFilter('clothing');
                    } else {
                        setFilter('none');
                    }
                });
            }
            
            // Clothing item selection
            clothingItemBtns.forEach(btn => {
                btn.addEventListener('click', async function() {
                    const category = this.dataset.category;
                    const itemId = this.dataset.item;
                    
                    try {
                        const response = await fetch(`/api/clothing/${category}/${itemId}`, {
                            method: 'POST'
                        });
                        
                        const data = await response.json();
                        if (response.ok) {
                            // Update UI for this category
                            const categoryBtns = document.querySelectorAll(`[data-category="${category}"]`);
                            categoryBtns.forEach(categoryBtn => {
                                categoryBtn.classList.remove('active');
                            });
                            this.classList.add('active');
                            
                            // Automatically enable clothing filter if an item is selected
                            if (itemId !== 'none' && clothingFilterBtn) {
                                document.querySelectorAll('.filter-btn').forEach(filterBtn => {
                                    filterBtn.classList.remove('active');
                                });
                                clothingFilterBtn.classList.add('active');
                                setFilter('clothing');
                            }
                        } else {
                            alert('Error: ' + data.error);
                        }
                    } catch (error) {
                        alert('Error setting clothing item: ' + error.message);
                    }
                });
            });
        }
        
        // Initialize when DOM is loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initClothingModule);
        } else {
            initClothingModule();
        }
        '''