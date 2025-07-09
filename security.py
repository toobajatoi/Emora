"""
Security utilities for Mood Journal
Created by Tooba Jatoi
Copyright © 2025 Tooba Jatoi. All rights reserved.
"""

import re
import hashlib
import tempfile
import os
from typing import Dict, Any, Optional, Tuple
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge
import logging

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Security validation utilities"""
    
    @staticmethod
    def validate_text_input(text: str, max_length: int = 10000, min_length: int = 1) -> Tuple[bool, str]:
        """
        Validate text input for security and content
        
        Args:
            text: Input text to validate
            max_length: Maximum allowed length
            min_length: Minimum required length
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if text is None or not isinstance(text, str):
            return False, "Text input is required and must be a string"
        text = text.strip()
        if min_length > 0 and len(text) < min_length:
            return False, f"Text must be at least {min_length} character(s) long"
        
        if len(text) > max_length:
            return False, f"Text must be no more than {max_length} characters long"
        
        # Check for potentially malicious content
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',  # JavaScript protocol
            r'data:text/html',  # Data URLs
            r'vbscript:',  # VBScript
            r'on\w+\s*=',  # Event handlers
            r'<iframe[^>]*>',  # Iframe tags
            r'<object[^>]*>',  # Object tags
            r'<embed[^>]*>',  # Embed tags
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False, "Text contains potentially unsafe content"
        
        return True, ""
    
    @staticmethod
    def validate_audio_file(file_data: bytes, allowed_extensions: set, max_size: int) -> Tuple[bool, str, Optional[str]]:
        """
        Validate uploaded audio file for security
        
        Args:
            file_data: Raw file data
            allowed_extensions: Set of allowed file extensions
            max_size: Maximum file size in bytes
            
        Returns:
            Tuple of (is_valid, error_message, detected_extension)
        """
        if len(file_data) > max_size:
            raise RequestEntityTooLarge(f"File size exceeds maximum allowed size of {max_size} bytes")
        
        if len(file_data) == 0:
            return False, "Empty file not allowed", None
        
        # Simple file type detection based on file headers
        mime_type = None
        if len(file_data) >= 4:
            # Check for common audio file signatures
            if file_data[:4] == b'RIFF' and file_data[8:12] == b'WAVE':
                mime_type = 'audio/wav'
            elif file_data[:3] == b'ID3' or file_data[:2] == b'\xff\xfb':
                mime_type = 'audio/mpeg'
            elif file_data[:4] == b'\x1a\x45\xdf\xa3':
                mime_type = 'video/webm'  # WebM container
            elif file_data[:4] == b'OggS':
                mime_type = 'audio/ogg'
        
        logger.info(f"Detected MIME type: {mime_type}")
        
        # Map MIME types to extensions
        mime_to_ext = {
            'audio/webm': 'webm',
            'video/webm': 'webm',  # Allow video/webm for Chrome/Windows audio
            'audio/wav': 'wav',
            'audio/mpeg': 'mp3',
            'audio/mp4': 'm4a',
            'audio/ogg': 'ogg',
            'audio/x-wav': 'wav',
            'audio/wave': 'wav'
        }
        
        detected_ext = mime_to_ext.get(mime_type)
        
        if not detected_ext:
            return False, "Invalid audio file format", None
        
        if detected_ext not in allowed_extensions:
            return False, f"Audio format '{detected_ext}' not allowed", None
        
        # Additional security checks
        if len(file_data) < 100:  # Suspiciously small for audio
            return False, "File appears to be too small for a valid audio file", None
        
        return True, "", detected_ext
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal attacks"""
        # Remove any path separators
        filename = os.path.basename(filename)
        
        # Remove any potentially dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename
    
    @staticmethod
    def generate_secure_filename() -> str:
        """Generate a secure random filename"""
        return hashlib.sha256(os.urandom(32)).hexdigest()[:16]
    
    @staticmethod
    def validate_json_payload(data: Dict[str, Any], required_fields: list = None) -> Tuple[bool, str]:
        """
        Validate JSON payload structure and content
        
        Args:
            data: JSON data to validate
            required_fields: List of required field names
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(data, dict):
            return False, "Invalid JSON payload format"
        
        if required_fields:
            for field in required_fields:
                if field not in data:
                    return False, f"Missing required field: {field}"
        
        return True, ""
    
    @staticmethod
    def detect_crisis_content(text: str, crisis_keywords: set) -> bool:
        """
        Detect crisis-related content in text
        
        Args:
            text: Text to analyze
            crisis_keywords: Set of crisis-related keywords
            
        Returns:
            True if crisis content is detected
        """
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Check for exact keyword matches
        for keyword in crisis_keywords:
            if keyword.lower() in text_lower:
                return True
        
        # Additional pattern matching for crisis indicators
        crisis_patterns = [
            r'\b(?:want|wish|hope)\s+(?:to\s+)?(?:die|end\s+it|kill\s+myself)\b',
            r'\b(?:no\s+reason\s+to\s+live)\b',
            r'\b(?:better\s+off\s+dead)\b',
            r'\b(?:tired\s+of\s+living)\b',
            r'\b(?:can\'t\s+take\s+it\s+anymore)\b',
            r'\b(?:life\s+is\s+not\s+worth\s+living)\b'
        ]
        
        for pattern in crisis_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    @staticmethod
    def create_secure_temp_file(data: bytes, suffix: str = '.tmp') -> str:
        """
        Create a secure temporary file
        
        Args:
            data: File data to write
            suffix: File extension suffix
            
        Returns:
            Path to the temporary file
        """
        # Create temporary file with secure permissions
        temp_fd, temp_path = tempfile.mkstemp(suffix=suffix)
        
        try:
            # Write data to file
            os.write(temp_fd, data)
            os.close(temp_fd)
            
            # Set restrictive permissions (owner read/write only)
            os.chmod(temp_path, 0o600)
            
            return temp_path
        except Exception as e:
            # Clean up on error
            try:
                os.close(temp_fd)
                os.unlink(temp_path)
            except:
                pass
            raise e

class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    pass

class SecurityError(Exception):
    """Base exception for security-related errors"""
    pass 