import os
import logging

logger = logging.getLogger(__name__)

def validate_image(file):
    """
    Validate image file
    
    Args:
        file: File object from request
        
    Returns:
        Tuple (is_valid, error_message)
    """
    try:
        # Check file size (max 50MB)
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)
        
        if file_length > 50 * 1024 * 1024:
            return False, "Image file too large (max 50MB)"
        
        if file_length == 0:
            return False, "Empty file"
        
        # Check magic bytes for image formats
        magic_bytes = file.read(4)
        file.seek(0)
        
        valid_signatures = [
            b'\xFF\xD8\xFF',  # JPEG
            b'\x89PNG',        # PNG
            b'GIF8',           # GIF
            b'BM'              # BMP
        ]
        
        is_valid_image = any(magic_bytes.startswith(sig) for sig in valid_signatures)
        
        if not is_valid_image:
            return False, "Invalid image format"
        
        return True, ""
        
    except Exception as e:
        logger.error(f"Image validation error: {str(e)}")
        return False, str(e)

def validate_video(file):
    """
    Validate video file
    
    Args:
        file: File object from request
        
    Returns:
        Tuple (is_valid, error_message)
    """
    try:
        # Check file size (max 500MB)
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)
        
        if file_length > 500 * 1024 * 1024:
            return False, "Video file too large (max 500MB)"
        
        if file_length == 0:
            return False, "Empty file"
        
        # Check magic bytes for video formats
        magic_bytes = file.read(4)
        file.seek(0)
        
        # Common video signatures
        valid_signatures = [
            b'\x00\x00\x00',   # MP4/MOV
            b'RIFF',           # AVI
            b'\x1A\x45',       # MKV
        ]
        
        is_valid_video = any(magic_bytes.startswith(sig) for sig in valid_signatures)
        
        if not is_valid_video:
            return False, "Invalid video format"
        
        return True, ""
        
    except Exception as e:
        logger.error(f"Video validation error: {str(e)}")
        return False, str(e)

def validate_audio(file):
    """
    Validate audio file
    
    Args:
        file: File object from request
        
    Returns:
        Tuple (is_valid, error_message)
    """
    try:
        # Check file size (max 100MB)
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)
        
        if file_length > 100 * 1024 * 1024:
            return False, "Audio file too large (max 100MB)"
        
        if file_length == 0:
            return False, "Empty file"
        
        # Check magic bytes for audio formats
        magic_bytes = file.read(4)
        file.seek(0)
        
        valid_signatures = [
            b'ID3',            # MP3
            b'RIFF',           # WAV
            b'\xFF\xFB',       # MP3 (alternative)
            b'fLaC',           # FLAC
            b'\xFF\xFA',       # MPEG-2 Audio
            b'\x00\x00\x00',   # M4A / MP4 Audio
            b'OggS',           # OGG
            b'ADIF',           # AAC
            b'\xFF\xF1',       # AAC ADTS
            b'\xFF\xF9',       # AAC ADTS
        ]
        
        is_valid_audio = any(magic_bytes.startswith(sig) for sig in valid_signatures)
        
        if not is_valid_audio:
            return False, "Invalid audio format"
        
        return True, ""
        
    except Exception as e:
        logger.error(f"Audio validation error: {str(e)}")
        return False, str(e)
