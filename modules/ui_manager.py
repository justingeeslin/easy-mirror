"""
UI Manager for Easy Mirror Modular Application

This module manages the collection and rendering of UI components from all modules.
Each module can contribute its own HTML, CSS, and JavaScript to the interface.
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class UIManager:
    """Manages UI components from all modules."""
    
    def __init__(self):
        """Initialize the UI manager."""
        self.modules = {}
        self.module_dependencies = {}
        
    def register_module(self, name: str, module_instance: Any, dependencies: Optional[List[str]] = None):
        """
        Register a module with the UI manager.
        
        Args:
            name: Module name
            module_instance: Instance of the module
            dependencies: List of module names this module depends on
        """
        self.modules[name] = module_instance
        self.module_dependencies[name] = dependencies or []
        logger.info(f"Registered UI module: {name}")
        
    def check_dependencies(self, module_name: str) -> bool:
        """Check if all dependencies for a module are available."""
        dependencies = self.module_dependencies.get(module_name, [])
        for dep in dependencies:
            if dep not in self.modules:
                logger.warning(f"Module {module_name} dependency {dep} not available")
                return False
        return True
        
    def generate_combined_html(self) -> str:
        """Generate combined HTML from all registered modules."""
        html_parts = []
        
        # Add main container
        html_parts.append('<div id="modular-controls">')
        
        for module_name, module in self.modules.items():
            try:
                if hasattr(module, 'generate_ui_html'):
                    # Check dependencies for modules that need them
                    if module_name == 'sex_prediction':
                        measurements_available = 'anthropometric' in self.modules
                        module_html = module.generate_ui_html(measurements_available)
                    else:
                        module_html = module.generate_ui_html()
                    
                    html_parts.append(f'<!-- {module_name.upper()} MODULE -->')
                    html_parts.append(module_html)
                    logger.debug(f"Generated HTML for module: {module_name}")
                else:
                    logger.warning(f"Module {module_name} does not have generate_ui_html method")
            except Exception as e:
                logger.error(f"Error generating HTML for module {module_name}: {e}")
                # Add error placeholder
                html_parts.append(f'''
                <div class="module-section error">
                    <h3>⚠️ {module_name.title()} Module Error</h3>
                    <p>Unable to load module interface.</p>
                </div>
                ''')
        
        html_parts.append('</div>')
        return '\n'.join(html_parts)
    
    def generate_combined_css(self) -> str:
        """Generate combined CSS from all registered modules."""
        css_parts = []
        
        # Add base modular styles
        css_parts.append('''
        /* Base Modular UI Styles */
        #modular-controls {
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .module-section {
            margin-bottom: 30px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 12px;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .module-section h3 {
            margin: 0 0 15px 0;
            color: #333;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 10px;
        }
        
        .module-section.error {
            background: #fff5f5;
            border-color: #fed7d7;
            color: #c53030;
        }
        
        .hidden {
            display: none !important;
        }
        ''')
        
        for module_name, module in self.modules.items():
            try:
                if hasattr(module, 'generate_ui_css'):
                    module_css = module.generate_ui_css()
                    css_parts.append(f'/* {module_name.upper()} MODULE CSS */')
                    css_parts.append(module_css)
                    logger.debug(f"Generated CSS for module: {module_name}")
            except Exception as e:
                logger.error(f"Error generating CSS for module {module_name}: {e}")
        
        return '\n'.join(css_parts)
    
    def generate_combined_javascript(self) -> str:
        """Generate combined JavaScript from all registered modules."""
        js_parts = []
        
        # Add base modular JavaScript
        js_parts.append('''
        // Base Modular UI JavaScript
        
        // Global function to set filter (used by multiple modules)
        function setFilter(filterName) {
            fetch('/set_filter', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({filter: filterName})
            }).catch(error => {
                console.error('Error setting filter:', error);
            });
        }
        
        // Initialize all modules
        function initAllModules() {
            console.log('Initializing all modular UI components...');
        }
        
        // Initialize when DOM is loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initAllModules);
        } else {
            initAllModules();
        }
        ''')
        
        for module_name, module in self.modules.items():
            try:
                if hasattr(module, 'generate_ui_javascript'):
                    module_js = module.generate_ui_javascript()
                    js_parts.append(f'// {module_name.upper()} MODULE JAVASCRIPT')
                    js_parts.append(module_js)
                    logger.debug(f"Generated JavaScript for module: {module_name}")
            except Exception as e:
                logger.error(f"Error generating JavaScript for module {module_name}: {e}")
        
        return '\n'.join(js_parts)
    
    def get_module_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered modules."""
        info = {}
        for module_name, module in self.modules.items():
            info[module_name] = {
                'name': module_name,
                'class': module.__class__.__name__,
                'dependencies': self.module_dependencies.get(module_name, []),
                'dependencies_met': self.check_dependencies(module_name),
                'has_ui_html': hasattr(module, 'generate_ui_html'),
                'has_ui_css': hasattr(module, 'generate_ui_css'),
                'has_ui_javascript': hasattr(module, 'generate_ui_javascript')
            }
        return info
    
    def get_available_modules(self) -> List[str]:
        """Get list of available module names."""
        return list(self.modules.keys())
    
    def get_module(self, name: str) -> Optional[Any]:
        """Get a specific module instance."""
        return self.modules.get(name)