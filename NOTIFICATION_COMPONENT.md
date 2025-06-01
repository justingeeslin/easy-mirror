# iOS-Style Notification Component

A custom web component that creates beautiful, semi-transparent notifications similar to iOS notifications. Perfect for modern web applications that need elegant user feedback.

## Features

- 🎨 **iOS-style Design**: Beautiful blur effects and modern styling
- ⏰ **Auto-dismiss**: Configurable duration with progress bar animation
- 👆 **Manual Dismiss**: Close button and swipe-to-dismiss on touch devices
- 🔗 **Click Actions**: Support for URLs and JavaScript execution
- 📱 **Responsive**: Works perfectly on desktop and mobile
- 🌙 **Dark Mode**: Automatic dark mode support
- ♿ **Accessible**: Keyboard navigation and screen reader support
- 🎯 **Multiple Types**: Success, error, warning, and info variants
- 🔧 **Customizable**: Custom icons, colors, and durations

## Quick Start

### 1. Include the Component

```html
<script src="ios-notification.js"></script>
```

### 2. Show Notifications Programmatically

```javascript
// Simple notifications
IOSNotification.success('Success!', 'Operation completed successfully');
IOSNotification.error('Error!', 'Something went wrong');
IOSNotification.warning('Warning!', 'Please check your input');
IOSNotification.info('Info', 'Here is some information');

// Custom notification
IOSNotification.show({
    title: 'Custom Notification',
    message: 'This is a custom notification with action',
    type: 'info',
    icon: '🎉',
    duration: 5000,
    actionUrl: 'https://example.com'
});
```

### 3. Use as HTML Element

```html
<ios-notification 
    title="Welcome!" 
    message="Thanks for visiting our app" 
    type="success"
    icon="👋"
    duration="4000">
</ios-notification>
```

## API Reference

### Static Methods

#### `IOSNotification.show(options)`

Creates and shows a notification with custom options.

**Parameters:**
- `options` (Object): Configuration object
  - `title` (String): Notification title
  - `message` (String): Notification message
  - `type` (String): Notification type ('success', 'error', 'warning', 'info')
  - `icon` (String): Emoji or text icon
  - `duration` (Number): Auto-dismiss duration in milliseconds (0 = no auto-dismiss)
  - `actionUrl` (String): URL to open on click or JavaScript code (prefix with 'javascript:')

**Returns:** IOSNotification element

#### Quick Methods

```javascript
IOSNotification.success(title, message, options)
IOSNotification.error(title, message, options)
IOSNotification.warning(title, message, options)
IOSNotification.info(title, message, options)
```

### HTML Attributes

When using as an HTML element:

- `title`: Notification title
- `message`: Notification message
- `type`: Notification type
- `icon`: Emoji or text icon
- `duration`: Auto-dismiss duration in milliseconds
- `action-url`: URL to open on click
- `auto-show`: Whether to show automatically (default: true)

### Instance Methods

#### `show()`
Shows the notification with animation.

#### `hide()`
Hides the notification with animation and removes from DOM.

### Events

The component dispatches custom events:

```javascript
// Listen for notification events
document.addEventListener('notification-show', (e) => {
    console.log('Notification shown:', e.detail.notification);
});

document.addEventListener('notification-hide', (e) => {
    console.log('Notification hidden:', e.detail.notification);
});
```

## Styling

The component uses CSS custom properties for theming:

```css
ios-notification {
    --accent-color: #007AFF; /* Custom accent color */
}
```

### Type Colors

- **Success**: `#34C759` (Green)
- **Error**: `#FF3B30` (Red)
- **Warning**: `#FF9500` (Orange)
- **Info**: `#007AFF` (Blue)

## Examples

### Basic Usage

```javascript
// Show a simple success message
IOSNotification.success('Saved!', 'Your changes have been saved');

// Show an error with custom duration
IOSNotification.error('Failed to save', 'Please try again', {
    duration: 8000
});
```

### With Actions

```javascript
// Open URL on click
IOSNotification.show({
    title: 'Update Available',
    message: 'Click to download the latest version',
    type: 'info',
    icon: '⬇️',
    actionUrl: 'https://example.com/download'
});

// Execute JavaScript on click
IOSNotification.show({
    title: 'Debug Mode',
    message: 'Click to open developer tools',
    type: 'warning',
    icon: '🔧',
    actionUrl: 'javascript:console.log("Debug mode activated")'
});
```

### Persistent Notifications

```javascript
// Notification that doesn't auto-dismiss
const notification = IOSNotification.show({
    title: 'Important',
    message: 'This message will stay until manually dismissed',
    type: 'warning',
    duration: 0 // No auto-dismiss
});

// Manually hide it later
setTimeout(() => {
    notification.hide();
}, 10000);
```

### Multiple Notifications

```javascript
// Show multiple notifications with staggered timing
IOSNotification.info('Step 1', 'Starting process...');

setTimeout(() => {
    IOSNotification.info('Step 2', 'Processing data...');
}, 1000);

setTimeout(() => {
    IOSNotification.success('Complete', 'Process finished successfully!');
}, 3000);
```

## Touch Gestures

On touch devices, users can:
- **Swipe right** to dismiss notifications
- **Tap** to trigger actions (if configured)
- **Tap close button** to dismiss

## Keyboard Accessibility

- Notifications are announced to screen readers
- Close button is keyboard accessible
- Proper ARIA labels and roles

## Browser Support

- Modern browsers with ES6 support
- Custom Elements v1 support
- CSS backdrop-filter support (graceful degradation)

## Integration with Easy Mirror

The notification component is integrated into the Easy Mirror webcam application to provide elegant feedback for:

- Filter changes
- Camera status updates
- Error messages
- Success confirmations

Example from Easy Mirror:

```javascript
// When a filter is applied
IOSNotification.show({
    title: 'Filter Applied',
    message: `${filterName} filter activated`,
    type: 'success',
    icon: getFilterIcon(filterName),
    duration: 3000
});
```

## Demo

Visit `/notification-demo` in the Easy Mirror application to see all notification types and features in action.