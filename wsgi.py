"""
WSGI entrypoint for Vercel deployment
"""
import sys
import os

# Add backend folder to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import Flask app from backend
from app import app

if __name__ == '__main__':
    app.run()
