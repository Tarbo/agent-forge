"""
Application settings and configuration
Loads environment variables and provides configuration values to the app
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
_ = load_dotenv(find_dotenv())

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
EXPORTS_DIR = PROJECT_ROOT / "exports"

# Ensure exports directory exists
EXPORTS_DIR.mkdir(exist_ok=True)

