#!/bin/bash
# Build script for Render deployment
# Installs system dependencies required for audio processing libraries

set -e

echo "Installing system dependencies..."
apt-get update
apt-get install -y \
    portaudio19-dev \
    libportaudio2

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Build complete!"
