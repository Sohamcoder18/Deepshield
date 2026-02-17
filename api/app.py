"""
API entrypoint for Vercel deployment
Imports Flask app from backend folder
"""
import sys
import os

# Add backend folder to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import Flask app from backend
from app import app

# Export WSGI app for Vercel
__all__ = ['app']
