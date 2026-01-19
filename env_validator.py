#!/usr/bin/env python3
"""
DailyNewsBot - Environment Validator
=====================================
Validates all environment variables and configuration before startup.
Run this before launching the bot to catch issues early.

Usage: python env_validator.py
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    name: str
    passed: bool
    message: str
    severity: str = "ERROR"  # ERROR, WARNING, INFO


class EnvironmentValidator:
    """Validates environment configuration for DailyNewsBot."""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
    
    def validate_all(self) -> bool:
        """
        Run all validation checks.
        
        Returns:
            True if all critical checks passed
        """
        self.results.clear()
        
        # Required variables
        self._check_gemini_key()
        self._check_whatsapp_number()
        
        # Optional but recommended
        self._check_news_api_key()
        self._check_gnews_key()
        
        # Directories
        self._check_directories()
        
        # Python version
        self._check_python_version()
        
        # Dependencies
        self._check_dependencies()
        
        return self.all_passed()
    
    def _check_gemini_key(self):
        """Validate GEMINI_API_KEY."""
        key = os.getenv("GEMINI_API_KEY", "")
        
        if not key:
            self.results.append(ValidationResult(
                "GEMINI_API_KEY",
                False,
                "Missing! Get one at: https://aistudio.google.com/app/apikey"
            ))
        elif "YOUR_" in key.upper():
            self.results.append(ValidationResult(
                "GEMINI_API_KEY",
                False,
                "Contains placeholder 'YOUR_' - replace with real key"
            ))
        elif len(key) < 30:
            self.results.append(ValidationResult(
                "GEMINI_API_KEY",
                False,
                f"Key looks too short ({len(key)} chars). Valid keys are 39+ characters"
            ))
        else:
            self.results.append(ValidationResult(
                "GEMINI_API_KEY",
                True,
                f"Valid format ({len(key)} chars)"
            ))
    
    def _check_whatsapp_number(self):
        """Validate WHATSAPP_NUMBER."""
        number = os.getenv("WHATSAPP_NUMBER", "")
        
        if not number:
            self.results.append(ValidationResult(
                "WHATSAPP_NUMBER",
                False,
                "Missing! Add your WhatsApp number with country code (e.g., +923001234567)"
            ))
        else:
            # Clean and validate
            clean = re.sub(r'[\s\-\(\)]', '', number)
            clean = clean.lstrip('+')
            
            if not clean.isdigit():
                self.results.append(ValidationResult(
                    "WHATSAPP_NUMBER",
                    False,
                    f"Invalid format: '{number}' - use only digits and optional +"
                ))
            elif len(clean) < 10:
                self.results.append(ValidationResult(
                    "WHATSAPP_NUMBER",
                    False,
                    f"Too short: '{number}' - include country code"
                ))
            elif len(clean) > 15:
                self.results.append(ValidationResult(
                    "WHATSAPP_NUMBER",
                    False,
                    f"Too long: '{number}' - check for extra digits"
                ))
            else:
                self.results.append(ValidationResult(
                    "WHATSAPP_NUMBER",
                    True,
                    f"Valid: {number}"
                ))
    
    def _check_news_api_key(self):
        """Validate NEWS_API_KEY (optional)."""
        key = os.getenv("NEWS_API_KEY", "")
        
        if not key:
            self.results.append(ValidationResult(
                "NEWS_API_KEY",
                True,
                "Not configured (optional - get one at newsapi.org)",
                severity="INFO"
            ))
        elif "YOUR_" in key.upper():
            self.results.append(ValidationResult(
                "NEWS_API_KEY",
                False,
                "Contains placeholder - replace with real key",
                severity="WARNING"
            ))
        else:
            self.results.append(ValidationResult(
                "NEWS_API_KEY",
                True,
                "Configured"
            ))
    
    def _check_gnews_key(self):
        """Validate GNEWS_API_KEY (optional)."""
        key = os.getenv("GNEWS_API_KEY", "")
        
        if not key:
            self.results.append(ValidationResult(
                "GNEWS_API_KEY",
                True,
                "Not configured (optional - get one at gnews.io)",
                severity="INFO"
            ))
        elif "YOUR_" in key.upper():
            self.results.append(ValidationResult(
                "GNEWS_API_KEY",
                False,
                "Contains placeholder - replace with real key",
                severity="WARNING"
            ))
        else:
            self.results.append(ValidationResult(
                "GNEWS_API_KEY",
                True,
                "Configured"
            ))
    
    def _check_directories(self):
        """Check required directories exist or can be created."""
        dirs = ["cache", "logs", "logs/health_reports"]
        
        for dir_name in dirs:
            path = Path(dir_name)
            try:
                path.mkdir(parents=True, exist_ok=True)
                self.results.append(ValidationResult(
                    f"Directory: {dir_name}",
                    True,
                    "Exists or created",
                    severity="INFO"
                ))
            except PermissionError:
                self.results.append(ValidationResult(
                    f"Directory: {dir_name}",
                    False,
                    "Permission denied"
                ))
            except Exception as e:
                self.results.append(ValidationResult(
                    f"Directory: {dir_name}",
                    False,
                    f"Error: {e}"
                ))
    
    def _check_python_version(self):
        """Check Python version."""
        major, minor = sys.version_info[:2]
        
        if major < 3 or (major == 3 and minor < 8):
            self.results.append(ValidationResult(
                "Python Version",
                False,
                f"Python {major}.{minor} - requires 3.8+"
            ))
        else:
            self.results.append(ValidationResult(
                "Python Version",
                True,
                f"Python {major}.{minor}"
            ))
    
    def _check_dependencies(self):
        """Check required packages are installed."""
        required = [
            ("google.generativeai", "google-generativeai"),
            ("pywhatkit", "pywhatkit"),
            ("feedparser", "feedparser"),
            ("requests", "requests"),
            ("dotenv", "python-dotenv"),
            ("bs4", "beautifulsoup4"),
        ]
        
        missing = []
        for import_name, pip_name in required:
            try:
                __import__(import_name)
            except ImportError:
                missing.append(pip_name)
        
        if missing:
            self.results.append(ValidationResult(
                "Dependencies",
                False,
                f"Missing: {', '.join(missing)}. Run: pip install {' '.join(missing)}"
            ))
        else:
            self.results.append(ValidationResult(
                "Dependencies",
                True,
                "All required packages installed"
            ))
    
    def all_passed(self) -> bool:
        """Check if all ERROR-level checks passed."""
        return all(
            r.passed 
            for r in self.results 
            if r.severity == "ERROR"
        )
    
    def print_results(self):
        """Print validation results to console."""
        print("\n" + "=" * 60)
        print("  ENVIRONMENT VALIDATION RESULTS")
        print("=" * 60 + "\n")
        
        for result in self.results:
            if result.passed:
                status = "[OK]  "
            elif result.severity == "WARNING":
                status = "[WARN]"
            elif result.severity == "INFO":
                status = "[INFO]"
            else:
                status = "[FAIL]"
            
            print(f"{status} {result.name}")
            print(f"       {result.message}\n")
        
        print("=" * 60)
        if self.all_passed():
            print("  RESULT: ALL CRITICAL CHECKS PASSED")
        else:
            print("  RESULT: SOME CHECKS FAILED - Fix issues above")
        print("=" * 60 + "\n")
    
    def get_summary(self) -> Dict:
        """Get validation summary as dict."""
        return {
            "passed": self.all_passed(),
            "total": len(self.results),
            "errors": len([r for r in self.results if not r.passed and r.severity == "ERROR"]),
            "warnings": len([r for r in self.results if not r.passed and r.severity == "WARNING"]),
            "checks": [
                {"name": r.name, "passed": r.passed, "message": r.message}
                for r in self.results
            ]
        }


def main():
    """Run validation and exit with appropriate code."""
    validator = EnvironmentValidator()
    validator.validate_all()
    validator.print_results()
    
    sys.exit(0 if validator.all_passed() else 1)


if __name__ == "__main__":
    main()
