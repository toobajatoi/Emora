"""
Secure Configuration for Mood Journal
Created by Tooba Jatoi
Copyright © 2025 Tooba Jatoi. All rights reserved.
"""

import os
import secrets
from datetime import timedelta

class Config:
    """Base configuration class with security defaults"""
    
    # Generate a secure secret key if not provided
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_urlsafe(32)
    
    # Security headers
    SECURITY_HEADERS = {
        'STRICT_TRANSPORT_SECURITY': {
            'max_age': 31536000,
            'include_subdomains': True,
            'preload': True
        },
        'CONTENT_SECURITY_POLICY': {
            'default-src': ["'self'"],
            'script-src': ["'self'", "'unsafe-inline'"],
            'style-src': ["'self'", "'unsafe-inline'"],
            'img-src': ["'self'", "data:", "https:"],
            'font-src': ["'self'"],
            'connect-src': ["'self'"],
            'media-src': ["'self'", "blob:"],
            'object-src': ["'none'"],
            'base-uri': ["'self'"],
            'form-action': ["'self'"]
        },
        'X_CONTENT_TYPE_OPTIONS': 'nosniff',
        'X_FRAME_OPTIONS': 'DENY',
        'X_XSS_PROTECTION': '1; mode=block',
        'REFERRER_POLICY': 'strict-origin-when-cross-origin'
    }
    
    # Rate limiting
    RATELIMIT_DEFAULT = "100 per minute"
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    
    # File upload security
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    ALLOWED_AUDIO_EXTENSIONS = {'webm', 'wav', 'mp3', 'm4a', 'ogg'}
    MAX_AUDIO_DURATION = 300  # 5 minutes max
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5001,http://127.0.0.1:5001').split(',')
    
    # Input validation
    MAX_TEXT_LENGTH = 10000  # 10KB max text input
    MIN_TEXT_LENGTH = 1
    
    # Crisis detection keywords (case insensitive)
    CRISIS_KEYWORDS = {
        "suicide", "kill myself", "end my life", "hopeless", "worthless", 
        "life is not worth", "can't go on", "die", "give up", "no reason to live",
        "better off dead", "want to die", "tired of living", "end it all"
    }
    
    # Session security
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Development settings
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    
    @staticmethod
    def init_app(app):
        """Initialize security configurations"""
        pass

class DevelopmentConfig(Config):
    """Development configuration with relaxed security for local development"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    CORS_ORIGINS = ['http://localhost:5001', 'http://127.0.0.1:5001']

class ProductionConfig(Config):
    """Production configuration with strict security"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 