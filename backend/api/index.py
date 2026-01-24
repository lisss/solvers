import sys
import os

# Add parent directory to path so we can import main
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app

# This is required for Vercel serverless functions
app = app
