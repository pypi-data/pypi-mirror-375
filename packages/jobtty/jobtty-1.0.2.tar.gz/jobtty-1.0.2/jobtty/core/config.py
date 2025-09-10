"""
Configuration management for Jobtty.io
Handles user settings, API keys, and authentication tokens
"""

import os
import json
import keyring
from pathlib import Path
from typing import Dict, Any, Optional

class JobttyConfig:
    """Manages Jobtty configuration and secure storage"""
    
    def __init__(self):
        self.app_name = "jobtty"
        self.config_dir = Path.home() / ".jobtty"
        self.config_file = self.config_dir / "config.json"
        self.ensure_config_dir()
        self.load_config()
    
    def ensure_config_dir(self):
        """Create config directory if it doesn't exist"""
        self.config_dir.mkdir(exist_ok=True)
    
    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self.get_default_config()
            self.save_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "location": "London, UK",
            "currency": "GBP",
            "remote_only": False,
            "salary_min": 0,
            "preferred_sources": ["jobtty"],
            "display_mode": "table",  # table, list, minimal
            "auto_save_searches": True,
            "notifications": True,
            "theme": "cyber"  # cyber, classic, minimal
        }
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all configuration settings"""
        return self.config.copy()
    
    # Authentication methods
    def set_auth_token(self, service: str, token: str):
        """Securely store authentication token"""
        keyring.set_password(self.app_name, f"{service}_token", token)
    
    def get_auth_token(self, service: str) -> Optional[str]:
        """Get authentication token from secure storage"""
        return keyring.get_password(self.app_name, f"{service}_token")
    
    def remove_auth_token(self, service: str):
        """Remove authentication token"""
        try:
            keyring.delete_password(self.app_name, f"{service}_token")
        except keyring.errors.PasswordDeleteError:
            pass
    
    def set_user_info(self, user_data: Dict[str, Any]):
        """Store user information"""
        user_file = self.config_dir / "user.json"
        with open(user_file, 'w') as f:
            json.dump(user_data, f, indent=2)
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get stored user information"""
        user_file = self.config_dir / "user.json"
        if user_file.exists():
            with open(user_file, 'r') as f:
                return json.load(f)
        return {}
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated to JobTTY"""
        return self.get_auth_token('jobtty') is not None
    
    def logout(self):
        """Clear all authentication data"""
        self.remove_auth_token('jobtty')
        
        # Remove user info
        user_file = self.config_dir / "user.json"
        if user_file.exists():
            user_file.unlink()
    
    # API Configuration
    def get_api_endpoints(self) -> Dict[str, str]:
        """Get API endpoints - JobTTY is the single source of truth"""
        # Allow override for development/testing
        api_base = os.getenv("JOBTTY_API_BASE", "https://jobtty.io/api/v1")
        return {
            "jobtty": api_base
        }
    
    def get_stripe_config(self) -> Dict[str, str]:
        """Get Stripe configuration"""
        return {
            "publishable_key": os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_..."),
            "webhook_secret": os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_..."),
            "success_url": "https://jobtty.io/payment/success",
            "cancel_url": "https://jobtty.io/payment/cancel"
        }