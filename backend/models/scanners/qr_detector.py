"""QR Code Detection Module

Detects QR codes from images and extracts URLs for analysis.
Uses OpenCV QRCodeDetector for QR code detection and decoding.
"""

import io
import logging
from typing import Optional, List, Dict, Any
from PIL import Image
import cv2
import numpy as np

logger = logging.getLogger(__name__)


def detect_qr_codes(image_data: bytes) -> List[str]:
    """
    Detect QR codes from image bytes and extract their data.
    
    Args:
        image_data: Raw image bytes (PNG, JPG, etc.)
        
    Returns:
        List of decoded QR code strings (typically URLs)
        
    Raises:
        ValueError: If image cannot be processed
    """
    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert PIL Image to numpy array (OpenCV format)
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Initialize QR Code detector
        qr_detector = cv2.QRCodeDetector()
        
        qr_data = []
        
        # Try detectAndDecodeMulti first (for multiple QR codes)
        try:
            result = qr_detector.detectAndDecodeMulti(cv_image)
            if result is not None and len(result) >= 2:
                data = result[0]
                if data is not None and len(data) > 0:
                    for qr_text in data:
                        if qr_text:
                            qr_data.append(qr_text)
                            logger.info(f"QR code detected: {qr_text[:100]}...")
        except (AttributeError, ValueError, TypeError):
            # detectAndDecodeMulti not available or failed, use detectAndDecode
            data, points, straight_qr = qr_detector.detectAndDecode(cv_image)
            if data and data.strip():
                qr_data.append(data)
                logger.info(f"QR code detected: {data[:100]}...")
        
        if not qr_data:
            logger.warning("No QR codes detected in the image")
            return []
        
        return qr_data
        
    except Exception as e:
        logger.error(f"Error detecting QR codes: {e}")
        raise ValueError(f"Failed to process image: {str(e)}")


def validate_url(data: str) -> Optional[str]:
    """
    Validate if QR code data is a valid URL.
    
    Args:
        data: String extracted from QR code
        
    Returns:
        The URL if valid, None otherwise
    """
    data = data.strip()
    
    # Check if it starts with common URL schemes
    if data.startswith(('http://', 'https://', 'ftp://')):
        return data
    
    # Check if it looks like a URL (contains protocol or domain pattern)
    if '://' in data:
        return data
    
    # Check for common domain patterns (e.g., example.com)
    if '.' in data and not data.startswith('/'):
        # Likely a domain, add https prefix
        return f"https://{data}"
    
    # Check for UPI URLs
    if data.startswith('upi://'):
        return data
    
    return None


def extract_url_from_qr(image_data: bytes) -> Optional[str]:
    """
    Detect QR codes and extract the first valid URL.
    
    Args:
        image_data: Raw image bytes
        
    Returns:
        First valid URL found in QR codes, or None
    """
    try:
        qr_codes = detect_qr_codes(image_data)
        
        for qr_data in qr_codes:
            url = validate_url(qr_data)
            if url:
                logger.info(f"Extracted URL from QR: {url}")
                return url
        
        logger.warning("No valid URLs extracted from QR codes")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting URL from QR: {e}")
        raise


def scan_qr_image(image_data: bytes) -> Dict[str, Any]:
    """
    Scan QR code image and return detailed detection results.
    
    Args:
        image_data: Raw image bytes
        
    Returns:
        Dictionary with detection results:
        {
            "detected": bool,
            "qr_count": int,
            "urls": List[str],
            "primary_url": Optional[str],
            "raw_data": List[str]
        }
    """
    try:
        qr_codes = detect_qr_codes(image_data)
        
        urls = []
        for qr_data in qr_codes:
            url = validate_url(qr_data)
            if url:
                urls.append(url)
        
        return {
            "detected": len(qr_codes) > 0,
            "qr_count": len(qr_codes),
            "urls": urls,
            "primary_url": urls[0] if urls else None,
            "raw_data": qr_codes
        }
        
    except Exception as e:
        logger.error(f"Error scanning QR: {e}")
        raise ValueError(f"Failed to scan QR code: {str(e)}")
