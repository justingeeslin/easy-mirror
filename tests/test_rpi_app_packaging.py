#!/usr/bin/env python3
"""
Tests for Raspberry Pi app packaging functionality.
"""

import unittest
import os
import tempfile
import shutil
import subprocess
import configparser
from pathlib import Path


class TestRPiAppPackaging(unittest.TestCase):
    """Test cases for Raspberry Pi app packaging."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.app_root = Path(__file__).parent.parent
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_desktop_file_exists(self):
        """Test that the desktop file exists and is valid."""
        desktop_file = self.app_root / "easy-mirror.desktop"
        self.assertTrue(desktop_file.exists(), "Desktop file should exist")
        
        # Parse desktop file
        config = configparser.ConfigParser()
        config.read(desktop_file)
        
        # Check required fields
        self.assertIn('Desktop Entry', config.sections())
        entry = config['Desktop Entry']
        
        required_fields = ['Name', 'Exec', 'Type', 'Categories']
        for field in required_fields:
            self.assertIn(field, entry, f"Desktop file should have {field} field")
        
        # Check specific values
        self.assertEqual(entry['Type'], 'Application')
        self.assertEqual(entry['Name'], 'Easy Mirror')
        self.assertIn('AudioVideo', entry['Categories'])
        self.assertIn('Photography', entry['Categories'])
    
    def test_launcher_script_exists(self):
        """Test that the launcher script exists and is executable."""
        launcher_script = self.app_root / "easy-mirror-launcher"
        self.assertTrue(launcher_script.exists(), "Launcher script should exist")
        
        # Check if it's a shell script
        with open(launcher_script, 'r') as f:
            first_line = f.readline().strip()
            self.assertTrue(first_line.startswith('#!/bin/bash'), 
                          "Launcher should be a bash script")
    
    def test_launcher_script_syntax(self):
        """Test that the launcher script has valid bash syntax."""
        launcher_script = self.app_root / "easy-mirror-launcher"
        
        # Use bash -n to check syntax without executing
        result = subprocess.run(['bash', '-n', str(launcher_script)], 
                              capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, 
                        f"Launcher script has syntax errors: {result.stderr}")
    
    def test_install_script_exists(self):
        """Test that the install script exists."""
        install_script = self.app_root / "install-rpi-app.sh"
        self.assertTrue(install_script.exists(), "Install script should exist")
        
        # Check if it's a shell script
        with open(install_script, 'r') as f:
            first_line = f.readline().strip()
            self.assertTrue(first_line.startswith('#!/bin/bash'), 
                          "Install script should be a bash script")
    
    def test_install_script_syntax(self):
        """Test that the install script has valid bash syntax."""
        install_script = self.app_root / "install-rpi-app.sh"
        
        # Use bash -n to check syntax without executing
        result = subprocess.run(['bash', '-n', str(install_script)], 
                              capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, 
                        f"Install script has syntax errors: {result.stderr}")
    
    def test_uninstall_script_exists(self):
        """Test that the uninstall script exists."""
        uninstall_script = self.app_root / "uninstall-rpi-app.sh"
        self.assertTrue(uninstall_script.exists(), "Uninstall script should exist")
        
        # Check if it's a shell script
        with open(uninstall_script, 'r') as f:
            first_line = f.readline().strip()
            self.assertTrue(first_line.startswith('#!/bin/bash'), 
                          "Uninstall script should be a bash script")
    
    def test_uninstall_script_syntax(self):
        """Test that the uninstall script has valid bash syntax."""
        uninstall_script = self.app_root / "uninstall-rpi-app.sh"
        
        # Use bash -n to check syntax without executing
        result = subprocess.run(['bash', '-n', str(uninstall_script)], 
                              capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, 
                        f"Uninstall script has syntax errors: {result.stderr}")
    
    def test_app_supports_command_line_args(self):
        """Test that the main app supports command line arguments."""
        app_file = self.app_root / "app.py"
        
        # Check if app.py contains argparse
        with open(app_file, 'r') as f:
            content = f.read()
            self.assertIn('import argparse', content, 
                         "App should import argparse for command line arguments")
            self.assertIn('--port', content, 
                         "App should support --port argument")
            self.assertIn('--host', content, 
                         "App should support --host argument")
    
    def test_app_help_output(self):
        """Test that the app shows help when requested."""
        app_file = self.app_root / "app.py"
        
        # Test help output
        result = subprocess.run(['python3', str(app_file), '--help'], 
                              capture_output=True, text=True, cwd=self.app_root)
        self.assertEqual(result.returncode, 0, "App should show help without errors")
        self.assertIn('Easy Mirror', result.stdout, "Help should mention Easy Mirror")
        self.assertIn('--port', result.stdout, "Help should show --port option")
        self.assertIn('--host', result.stdout, "Help should show --host option")
    
    def test_launcher_script_functions(self):
        """Test that launcher script contains required functions."""
        launcher_script = self.app_root / "easy-mirror-launcher"
        
        with open(launcher_script, 'r') as f:
            content = f.read()
            
        required_functions = [
            'cleanup()',
            'wait_for_server()',
            'find_browser()',
            'get_browser_args()',
            'main()'
        ]
        
        for func in required_functions:
            self.assertIn(func, content, 
                         f"Launcher script should contain {func} function")
    
    def test_launcher_script_handles_signals(self):
        """Test that launcher script sets up signal handlers."""
        launcher_script = self.app_root / "easy-mirror-launcher"
        
        with open(launcher_script, 'r') as f:
            content = f.read()
            
        self.assertIn('trap cleanup', content, 
                     "Launcher should set up signal handlers")
        self.assertIn('EXIT INT TERM', content, 
                     "Launcher should handle EXIT, INT, and TERM signals")
    
    def test_install_script_checks_root(self):
        """Test that install script checks for root privileges."""
        install_script = self.app_root / "install-rpi-app.sh"
        
        with open(install_script, 'r') as f:
            content = f.read()
            
        self.assertIn('check_root()', content, 
                     "Install script should check for root privileges")
        self.assertIn('EUID', content, 
                     "Install script should check effective user ID")
    
    def test_desktop_file_categories(self):
        """Test that desktop file has appropriate categories."""
        desktop_file = self.app_root / "easy-mirror.desktop"
        
        config = configparser.ConfigParser()
        config.read(desktop_file)
        
        categories = config['Desktop Entry']['Categories']
        expected_categories = ['AudioVideo', 'Photography']
        
        for category in expected_categories:
            self.assertIn(category, categories, 
                         f"Desktop file should include {category} category")
    
    def test_desktop_file_keywords(self):
        """Test that desktop file has relevant keywords."""
        desktop_file = self.app_root / "easy-mirror.desktop"
        
        config = configparser.ConfigParser()
        config.read(desktop_file)
        
        if 'Keywords' in config['Desktop Entry']:
            keywords = config['Desktop Entry']['Keywords']
            expected_keywords = ['webcam', 'camera', 'mirror', 'filters']
            
            for keyword in expected_keywords:
                self.assertIn(keyword, keywords.lower(), 
                             f"Desktop file should include {keyword} keyword")


class TestAppFunctionality(unittest.TestCase):
    """Test cases for app functionality related to packaging."""
    
    def setUp(self):
        """Set up test environment."""
        self.app_root = Path(__file__).parent.parent
    
    def test_app_imports_successfully(self):
        """Test that the app can be imported without errors."""
        import sys
        sys.path.insert(0, str(self.app_root))
        
        try:
            # This should not raise any import errors
            import app
            self.assertTrue(hasattr(app, 'WebcamFilter'), 
                          "App should have WebcamFilter class")
            self.assertTrue(hasattr(app, 'app'), 
                          "App should have Flask app instance")
        except ImportError as e:
            self.fail(f"App import failed: {e}")
    
    def test_demo_mode_available(self):
        """Test that demo mode is available for testing."""
        demo_file = self.app_root / "demo_mode.py"
        if demo_file.exists():
            import sys
            sys.path.insert(0, str(self.app_root))
            
            try:
                import demo_mode
                self.assertTrue(hasattr(demo_mode, 'DemoCamera'), 
                              "Demo mode should have DemoCamera class")
            except ImportError as e:
                self.fail(f"Demo mode import failed: {e}")


if __name__ == '__main__':
    unittest.main()