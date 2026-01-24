import sys
import os

# Add parent directory to path so we can import main
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app
from mangum import Mangum


handler = Mangum(app, lifespan="off")
