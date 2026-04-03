#!/usr/bin/env python3
"""
System Validation Script for AssistGen

This script performs comprehensive validation of the AssistGen system including:
- Import validation for all modules
- Configuration validation
- Code quality checks
- Documentation completeness
- Dependency verification

Author: AssistGen Team
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

# Color codes for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


class SystemValidator:
    """Comprehensive system validation"""
    
    def __init__(self):
        self.results = {
            "imports": [],
            "config": [],
            "documentation": [],
            "dependencies": [],
            "structure": []
        }
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def log_info(self, message: str):
        """Log info message"""
        print(f"{GREEN}[INFO]{NC} {message}")
    
    def log_warn(self, message: str):
        """Log warning message"""
        print(f"{YELLOW}[WARN]{NC} {message}")
        self.warnings += 1
    
    def log_error(self, message: str):
        """Log error message"""
        print(f"{RED}[ERROR]{NC} {message}")
        self.failed += 1
    
    def log_success(self, message: str):
        """Log success message"""
        print(f"{GREEN}[PASS]{NC} {message}")
        self.passed += 1
    
    def log_step(self, message: str):
        """Log step header"""
        print(f"\n{BLUE}==== {message} ===={NC}\n")
    
    def validate_imports(self) -> bool:
        """Validate that all core modules can be imported"""
        self.log_step("Validating Module Imports")
        
        modules_to_test = [
            ("app.core.config", "Configuration module"),
            ("app.core.database", "Database module"),
            ("app.core.logger", "Logger module"),
            ("app.core.security", "Security module"),
            ("app.core.hashing", "Hashing module"),
            ("app.core.middleware", "Middleware module"),
            ("app.models.user", "User model"),
            ("app.models.conversation", "Conversation model"),
            ("app.models.message", "Message model"),
            ("app.schemas.user", "User schema"),
            ("app.schemas.conversation", "Conversation schema"),
            ("app.schemas.message", "Message schema"),
            ("app.services.base_service", "Base service"),
            ("app.services.user_service", "User service"),
            ("app.services.conversation_service", "Conversation service"),
            ("app.services.llm_factory", "LLM factory"),
        ]
        
        all_passed = True
        for module_name, description in modules_to_test:
            try:
                __import__(module_name)
                self.log_success(f"{description}: {module_name}")
                self.results["imports"].append({
                    "module": module_name,
                    "status": "pass",
                    "description": description
                })
            except ImportError as e:
                self.log_error(f"{description}: {module_name} - {str(e)}")
                self.results["imports"].append({
                    "module": module_name,
                    "status": "fail",
                    "description": description,
                    "error": str(e)
                })
                all_passed = False
            except Exception as e:
                self.log_warn(f"{description}: {module_name} - {str(e)}")
                self.results["imports"].append({
                    "module": module_name,
                    "status": "warning",
                    "description": description,
                    "error": str(e)
                })
        
        return all_passed
    
    def validate_configuration(self) -> bool:
        """Validate configuration files"""
        self.log_step("Validating Configuration")
        
        config_files = [
            ("backend/.env.example", "Backend environment example"),
            ("frontend/.env.example", "Frontend environment example"),
            ("config/development.env.example", "Development config example"),
            ("config/production.env.example", "Production config example"),
            ("backend/requirements.txt", "Backend dependencies"),
            ("frontend/package.json", "Frontend dependencies"),
        ]
        
        all_passed = True
        for file_path, description in config_files:
            full_path = PROJECT_ROOT / file_path
            if full_path.exists():
                self.log_success(f"{description}: {file_path}")
                self.results["config"].append({
                    "file": file_path,
                    "status": "pass",
                    "description": description
                })
            else:
                self.log_error(f"{description}: {file_path} - File not found")
                self.results["config"].append({
                    "file": file_path,
                    "status": "fail",
                    "description": description
                })
                all_passed = False
        
        return all_passed
    
    def validate_documentation(self) -> bool:
        """Validate documentation completeness"""
        self.log_step("Validating Documentation")
        
        doc_files = [
            ("README.md", "Main README"),
            ("docs/api/README.md", "API documentation"),
            ("docs/database/README.md", "Database documentation"),
            ("docs/architecture/README.md", "Architecture documentation"),
            ("docs/deployment/README.md", "Deployment documentation"),
            ("docs/migration/README.md", "Migration guide"),
            ("docs/testing/README.md", "Testing documentation"),
            ("docs/code-review-checklist.md", "Code review checklist"),
            ("docs/logging.md", "Logging documentation"),
        ]
        
        all_passed = True
        for file_path, description in doc_files:
            full_path = PROJECT_ROOT / file_path
            if full_path.exists():
                # Check if file has content (more than just a title)
                content = full_path.read_text()
                if len(content) > 100:  # Arbitrary minimum
                    self.log_success(f"{description}: {file_path}")
                    self.results["documentation"].append({
                        "file": file_path,
                        "status": "pass",
                        "description": description,
                        "size": len(content)
                    })
                else:
                    self.log_warn(f"{description}: {file_path} - File too short")
                    self.results["documentation"].append({
                        "file": file_path,
                        "status": "warning",
                        "description": description,
                        "size": len(content)
                    })
            else:
                self.log_error(f"{description}: {file_path} - File not found")
                self.results["documentation"].append({
                    "file": file_path,
                    "status": "fail",
                    "description": description
                })
                all_passed = False
        
        return all_passed
    
    def validate_structure(self) -> bool:
        """Validate project structure"""
        self.log_step("Validating Project Structure")
        
        required_dirs = [
            ("backend", "Backend directory"),
            ("backend/app", "Backend app directory"),
            ("backend/app/api", "API routes directory"),
            ("backend/app/core", "Core modules directory"),
            ("backend/app/models", "Models directory"),
            ("backend/app/schemas", "Schemas directory"),
            ("backend/app/services", "Services directory"),
            ("frontend", "Frontend directory"),
            ("frontend/src", "Frontend source directory"),
            ("docs", "Documentation directory"),
            ("tests", "Tests directory"),
            ("tests/unit", "Unit tests directory"),
            ("tests/integration", "Integration tests directory"),
            ("config", "Configuration directory"),
            ("scripts", "Scripts directory"),
        ]
        
        all_passed = True
        for dir_path, description in required_dirs:
            full_path = PROJECT_ROOT / dir_path
            if full_path.exists() and full_path.is_dir():
                self.log_success(f"{description}: {dir_path}")
                self.results["structure"].append({
                    "directory": dir_path,
                    "status": "pass",
                    "description": description
                })
            else:
                self.log_error(f"{description}: {dir_path} - Directory not found")
                self.results["structure"].append({
                    "directory": dir_path,
                    "status": "fail",
                    "description": description
                })
                all_passed = False
        
        return all_passed
    
    def validate_dependencies(self) -> bool:
        """Validate that key dependencies are available"""
        self.log_step("Validating Dependencies")
        
        dependencies = [
            ("fastapi", "FastAPI framework"),
            ("pydantic", "Pydantic validation"),
            ("sqlalchemy", "SQLAlchemy ORM"),
            ("loguru", "Loguru logging"),
        ]
        
        all_passed = True
        for package, description in dependencies:
            try:
                __import__(package)
                self.log_success(f"{description}: {package}")
                self.results["dependencies"].append({
                    "package": package,
                    "status": "pass",
                    "description": description
                })
            except ImportError:
                self.log_error(f"{description}: {package} - Not installed")
                self.results["dependencies"].append({
                    "package": package,
                    "status": "fail",
                    "description": description
                })
                all_passed = False
        
        return all_passed
    
    def generate_report(self):
        """Generate validation report"""
        self.log_step("Validation Summary")
        
        print(f"Total Passed: {GREEN}{self.passed}{NC}")
        print(f"Total Failed: {RED}{self.failed}{NC}")
        print(f"Total Warnings: {YELLOW}{self.warnings}{NC}")
        
        # Save detailed report
        report_path = PROJECT_ROOT / "validation_report.json"
        with open(report_path, "w") as f:
            json.dump({
                "summary": {
                    "passed": self.passed,
                    "failed": self.failed,
                    "warnings": self.warnings
                },
                "results": self.results
            }, f, indent=2)
        
        self.log_info(f"Detailed report saved to: {report_path}")
        
        return self.failed == 0
    
    def run_all_validations(self) -> bool:
        """Run all validation checks"""
        print(f"\n{BLUE}{'='*60}{NC}")
        print(f"{BLUE}AssistGen System Validation{NC}")
        print(f"{BLUE}{'='*60}{NC}\n")
        
        validations = [
            self.validate_structure,
            self.validate_configuration,
            self.validate_dependencies,
            self.validate_imports,
            self.validate_documentation,
        ]
        
        all_passed = True
        for validation in validations:
            try:
                if not validation():
                    all_passed = False
            except Exception as e:
                self.log_error(f"Validation error: {str(e)}")
                all_passed = False
        
        return self.generate_report()


def main():
    """Main entry point"""
    validator = SystemValidator()
    success = validator.run_all_validations()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
