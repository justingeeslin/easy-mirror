/**
 * iOS-style Notification Web Component
 * 
 * Usage:
 * <ios-notification 
 *   title="Notification Title" 
 *   message="Notification message" 
 *   duration="5000" 
 *   action-url="https://example.com"
 *   icon="🔔"
 *   type="info">
 * </ios-notification>
 * 
 * Or programmatically:
 * IOSNotification.show({
 *   title: "Title",
 *   message: "Message",
 *   duration: 5000,
 *   actionUrl: "https://example.com",
 *   icon: "🔔",
 *   type: "success"
 * });
 */

class IOSNotification extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.timeoutId = null;
        this.isVisible = false;
    }

    static get observedAttributes() {
        return ['title', 'message', 'duration', 'action-url', 'icon', 'type', 'auto-show'];
    }

    connectedCallback() {
        this.render();
        if (this.getAttribute('auto-show') !== 'false') {
            this.show();
        }
    }

    disconnectedCallback() {
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
        }
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (oldValue !== newValue) {
            this.render();
        }
    }

    render() {
        const title = this.getAttribute('title') || 'Notification';
        const message = this.getAttribute('message') || '';
        const icon = this.getAttribute('icon') || '🔔';
        const type = this.getAttribute('type') || 'info';
        const actionUrl = this.getAttribute('action-url');

        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 10000;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    transform: translateX(120%);
                    transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                    max-width: 350px;
                    min-width: 280px;
                }

                :host(.show) {
                    transform: translateX(0);
                }

                .notification {
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(20px);
                    -webkit-backdrop-filter: blur(20px);
                    border-radius: 16px;
                    padding: 16px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    cursor: ${actionUrl ? 'pointer' : 'default'};
                    position: relative;
                    overflow: hidden;
                }

                .notification::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 3px;
                    background: var(--accent-color);
                    opacity: 0.8;
                }

                .notification.success {
                    --accent-color: #34C759;
                }

                .notification.error {
                    --accent-color: #FF3B30;
                }

                .notification.warning {
                    --accent-color: #FF9500;
                }

                .notification.info {
                    --accent-color: #007AFF;
                }

                .notification:hover {
                    transform: scale(1.02);
                    transition: transform 0.2s ease;
                }

                .notification:active {
                    transform: scale(0.98);
                }

                .header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 8px;
                }

                .title-section {
                    display: flex;
                    align-items: center;
                    flex: 1;
                }

                .icon {
                    font-size: 20px;
                    margin-right: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 32px;
                    height: 32px;
                    border-radius: 8px;
                    background: rgba(var(--accent-color-rgb), 0.1);
                }

                .success .icon {
                    --accent-color-rgb: 52, 199, 89;
                }

                .error .icon {
                    --accent-color-rgb: 255, 59, 48;
                }

                .warning .icon {
                    --accent-color-rgb: 255, 149, 0;
                }

                .info .icon {
                    --accent-color-rgb: 0, 122, 255;
                }

                .title {
                    font-weight: 600;
                    font-size: 16px;
                    color: #1d1d1f;
                    margin: 0;
                    line-height: 1.2;
                }

                .close-btn {
                    background: none;
                    border: none;
                    font-size: 18px;
                    color: #8e8e93;
                    cursor: pointer;
                    padding: 4px;
                    border-radius: 50%;
                    width: 24px;
                    height: 24px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: background-color 0.2s ease;
                }

                .close-btn:hover {
                    background-color: rgba(0, 0, 0, 0.1);
                }

                .message {
                    color: #6d6d70;
                    font-size: 14px;
                    line-height: 1.4;
                    margin: 0;
                    margin-left: 44px;
                }

                .progress-bar {
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    height: 2px;
                    background: var(--accent-color);
                    transition: width linear;
                    opacity: 0.6;
                }

                @media (max-width: 480px) {
                    :host {
                        right: 10px;
                        left: 10px;
                        max-width: none;
                        min-width: auto;
                    }
                }

                @media (prefers-color-scheme: dark) {
                    .notification {
                        background: rgba(28, 28, 30, 0.95);
                        border: 1px solid rgba(255, 255, 255, 0.1);
                    }

                    .title {
                        color: #f2f2f7;
                    }

                    .message {
                        color: #8e8e93;
                    }

                    .close-btn {
                        color: #8e8e93;
                    }

                    .close-btn:hover {
                        background-color: rgba(255, 255, 255, 0.1);
                    }
                }
            </style>

            <div class="notification ${type}" role="alert" aria-live="polite">
                <div class="header">
                    <div class="title-section">
                        <div class="icon">${icon}</div>
                        <h3 class="title">${title}</h3>
                    </div>
                    <button class="close-btn" aria-label="Close notification">×</button>
                </div>
                ${message ? `<p class="message">${message}</p>` : ''}
                <div class="progress-bar"></div>
            </div>
        `;

        this.setupEventListeners();
    }

    setupEventListeners() {
        const notification = this.shadowRoot.querySelector('.notification');
        const closeBtn = this.shadowRoot.querySelector('.close-btn');
        const actionUrl = this.getAttribute('action-url');

        // Close button
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.hide();
        });

        // Click action
        if (actionUrl) {
            notification.addEventListener('click', () => {
                if (actionUrl.startsWith('javascript:')) {
                    // Execute JavaScript
                    eval(actionUrl.substring(11));
                } else {
                    // Open URL
                    window.open(actionUrl, '_blank');
                }
                this.hide();
            });
        }

        // Swipe to dismiss (touch devices)
        let startX = 0;
        let currentX = 0;
        let isDragging = false;

        notification.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            isDragging = true;
        });

        notification.addEventListener('touchmove', (e) => {
            if (!isDragging) return;
            currentX = e.touches[0].clientX;
            const deltaX = currentX - startX;
            
            if (deltaX > 0) {
                notification.style.transform = `translateX(${deltaX}px)`;
                notification.style.opacity = Math.max(0.3, 1 - deltaX / 200);
            }
        });

        notification.addEventListener('touchend', () => {
            if (!isDragging) return;
            isDragging = false;
            
            const deltaX = currentX - startX;
            if (deltaX > 100) {
                this.hide();
            } else {
                notification.style.transform = '';
                notification.style.opacity = '';
            }
        });
    }

    show() {
        if (this.isVisible) return;
        
        this.isVisible = true;
        this.classList.add('show');
        
        const duration = parseInt(this.getAttribute('duration')) || 5000;
        const progressBar = this.shadowRoot.querySelector('.progress-bar');
        
        // Animate progress bar
        if (duration > 0) {
            progressBar.style.width = '100%';
            progressBar.style.transition = `width ${duration}ms linear`;
            
            requestAnimationFrame(() => {
                progressBar.style.width = '0%';
            });

            this.timeoutId = setTimeout(() => {
                this.hide();
            }, duration);
        }

        // Dispatch custom event
        this.dispatchEvent(new CustomEvent('notification-show', {
            detail: { notification: this },
            bubbles: true
        }));
    }

    hide() {
        if (!this.isVisible) return;
        
        this.isVisible = false;
        this.classList.remove('show');
        
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
            this.timeoutId = null;
        }

        // Dispatch custom event
        this.dispatchEvent(new CustomEvent('notification-hide', {
            detail: { notification: this },
            bubbles: true
        }));

        // Remove from DOM after animation
        setTimeout(() => {
            if (this.parentNode) {
                this.parentNode.removeChild(this);
            }
        }, 300);
    }

    // Static method for programmatic usage
    static show(options = {}) {
        const notification = document.createElement('ios-notification');
        
        if (options.title) notification.setAttribute('title', options.title);
        if (options.message) notification.setAttribute('message', options.message);
        if (options.duration !== undefined) notification.setAttribute('duration', options.duration);
        if (options.actionUrl) notification.setAttribute('action-url', options.actionUrl);
        if (options.icon) notification.setAttribute('icon', options.icon);
        if (options.type) notification.setAttribute('type', options.type);
        
        notification.setAttribute('auto-show', 'true');
        
        document.body.appendChild(notification);
        return notification;
    }

    // Static method for quick notifications
    static success(title, message, options = {}) {
        return this.show({
            title,
            message,
            type: 'success',
            icon: '✅',
            ...options
        });
    }

    static error(title, message, options = {}) {
        return this.show({
            title,
            message,
            type: 'error',
            icon: '❌',
            ...options
        });
    }

    static warning(title, message, options = {}) {
        return this.show({
            title,
            message,
            type: 'warning',
            icon: '⚠️',
            ...options
        });
    }

    static info(title, message, options = {}) {
        return this.show({
            title,
            message,
            type: 'info',
            icon: 'ℹ️',
            ...options
        });
    }
}

// Register the custom element
customElements.define('ios-notification', IOSNotification);

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IOSNotification;
}