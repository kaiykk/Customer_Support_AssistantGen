"""
Configuration Validator Module

This module provides validation for application configuration to ensure
all required settings are present and valid before the application starts.
"""

import os
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path


class ConfigValidationError(Exception):
    """Exception raised when configuration validation fails."""
    pass


class ConfigValidator:
    """
    Validates application configuration settings.
    
    This class checks that all required configuration parameters are present
    and have valid values before the application starts.
    """
    
    # Required configuration keys for different services
    REQUIRED_KEYS = {
        "database": ["DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME"],
        "redis": ["REDIS_HOST", "REDIS_PORT"],
        "security": ["SECRET_KEY", "ALGORITHM"],
        "llm": ["CHAT_SERVICE", "REASON_SERVICE"],
    }
    
    # Conditional requirements based on service selection
    CONDITIONAL_REQUIREMENTS = {
        "deepseek": ["DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL", "DEEPSEEK_MODEL"],
        "ollama": ["OLLAMA_BASE_URL", "OLLAMA_CHAT_MODEL"],
    }
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize the configuration validator.
        
        Args:
            env_file: Optional path to .env file to load
        """
        self.env_file = env_file
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self) -> bool:
        """
        Validate all configuration settings.
        
        Returns:
            bool: True if validation passes, False otherwise
            
        Raises:
            ConfigValidationError: If critical configuration is missing or invalid
        """
        self.errors = []
        self.warnings = []
        
        # Validate required keys
        self._validate_required_keys()
        
        # Validate conditional requirements
        self._validate_conditional_requirements()
        
        # Validate value formats
        self._validate_value_formats()
        
        # Validate security settings
        self._validate_security_settings()
        
        # Report results
        if self.errors:
            error_message = "\n".join([
                "Configuration validation failed:",
                *[f"  - {error}" for error in self.errors]
            ])
            raise ConfigValidationError(error_message)
        
        if self.warnings:
            print("Configuration warnings:", file=sys.stderr)
            for warning in self.warnings:
                print(f"  - {warning}", file=sys.stderr)
        
        return True
    
    def _validate_required_keys(self) -> None:
        """Validate that all required configuration keys are present."""
        for category, keys in self.REQUIRED_KEYS.items():
            for key in keys:
                if not os.getenv(key):
                    self.errors.append(
                        f"Missing required {category} configuration: {key}"
                    )
    
    def _validate_conditional_requirements(self) -> None:
        """Validate conditional requirements based on service selection."""
        chat_service = os.getenv("CHAT_SERVICE", "").lower()
        reason_service = os.getenv("REASON_SERVICE", "").lower()
        
        # Check requirements for selected services
        for service in [chat_service, reason_service]:
            if service in self.CONDITIONAL_REQUIREMENTS:
                for key in self.CONDITIONAL_REQUIREMENTS[service]:
                    if not os.getenv(key):
                        self.errors.append(
                            f"Missing required configuration for {service} service: {key}"
                        )
    
    def _validate_value_formats(self) -> None:
        """Validate that configuration values have correct formats."""
        # Validate port numbers
        port_keys = ["DB_PORT", "REDIS_PORT", "PORT"]
        for key in port_keys:
            value = os.getenv(key)
            if value:
                try:
                    port = int(value)
                    if not (1 <= port <= 65535):
                        self.errors.append(
                            f"{key} must be between 1 and 65535, got: {port}"
                        )
                except ValueError:
                    self.errors.append(
                        f"{key} must be a valid integer, got: {value}"
                    )
        
        # Validate boolean values
        bool_keys = ["DEBUG", "RELOAD", "GRAPHRAG_DYNAMIC_COMMUNITY"]
        for key in bool_keys:
            value = os.getenv(key)
            if value and value.lower() not in ["true", "false", "1", "0"]:
                self.warnings.append(
                    f"{key} should be 'true' or 'false', got: {value}"
                )
    
    def _validate_security_settings(self) -> None:
        """Validate security-related configuration settings."""
        secret_key = os.getenv("SECRET_KEY", "")
        
        # Check for default/weak secret keys
        weak_keys = [
            "your-secret-key",
            "dev-secret-key",
            "change-me",
            "secret",
            "password",
        ]
        
        if any(weak in secret_key.lower() for weak in weak_keys):
            if os.getenv("DEBUG", "false").lower() != "true":
                self.errors.append(
                    "SECRET_KEY appears to be a default or weak value. "
                    "Please use a strong random key in production."
                )
            else:
                self.warnings.append(
                    "SECRET_KEY appears to be a default value. "
                    "This is acceptable for development but must be changed for production."
                )
        
        # Check secret key length
        if len(secret_key) < 32:
            self.warnings.append(
                f"SECRET_KEY should be at least 32 characters long, "
                f"current length: {len(secret_key)}"
            )
    
    def get_validation_report(self) -> Dict[str, Any]:
        """
        Get a detailed validation report.
        
        Returns:
            dict: Validation report with errors and warnings
        """
        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "checked_categories": list(self.REQUIRED_KEYS.keys()),
        }


def validate_config(env_file: Optional[str] = None) -> bool:
    """
    Convenience function to validate configuration.
    
    Args:
        env_file: Optional path to .env file
        
    Returns:
        bool: True if validation passes
        
    Raises:
        ConfigValidationError: If validation fails
    """
    validator = ConfigValidator(env_file)
    return validator.validate()


if __name__ == "__main__":
    """Run configuration validation from command line."""
    try:
        validate_config()
        print("✓ Configuration validation passed")
        sys.exit(0)
    except ConfigValidationError as e:
        print(f"✗ Configuration validation failed:\n{e}", file=sys.stderr)
        sys.exit(1)
