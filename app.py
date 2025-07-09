"""
Secure Mood Journal Application
Created by Tooba Jatoi
Copyright © 2025 Tooba Jatoi. All rights reserved.
"""

import os
import logging
import whisper
import numpy as np
from flask import Flask, render_template, request, jsonify, abort
from flask_socketio import SocketIO, emit
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_cors import CORS
from feature_extractor import extract_features
from mood_classifier import detect_mood
from config import config
from security import SecurityValidator, SecurityError
import tempfile
import librosa
import base64
import json
import random
import subprocess
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge
import traceback
import mimetypes

# Set up logging with security considerations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app with security configuration
app = Flask(__name__)
mimetypes.add_type('application/javascript', '.js')
app.config.from_object(config['default'])

# Initialize security extensions
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize Talisman for security headers
talisman = Talisman(
    app,
    content_security_policy=app.config['SECURITY_HEADERS']['CONTENT_SECURITY_POLICY'],
    force_https=False  # Set to True in production
)

# Initialize CORS
CORS(app, origins=app.config['CORS_ORIGINS'])

socketio = SocketIO(app, async_mode='threading', cors_allowed_origins=app.config['CORS_ORIGINS'])

# Initialize Whisper model
logger.info("Loading Whisper model...")
whisper_model = whisper.load_model("base", device="cpu", download_root="./models")
whisper_model.eval()  # Set to evaluation mode
logger.info("Whisper model loaded successfully")

# Supportive messages by mood
SUPPORTIVE_MESSAGES = {
    'sad': [
        "Don’t give up, things can get better.",
        "It’s okay to feel sad. Brighter days are ahead.",
        "You’re not alone. Reach out if you need support."
    ],
    'angry': [
        "Take a deep breath. It’s okay to feel angry sometimes.",
        "Try to let go of what you can’t control.",
        "Channel your anger into something positive."
    ],
    'happy': [
        "That’s wonderful! Keep enjoying the good moments.",
        "Your happiness is contagious!",
        "Celebrate your wins, big or small."
    ],
    'calm': [
        "Thank you for sharing. Journaling is a great habit.",
        "Keep reflecting and taking care of yourself.",
        "Every day is a new opportunity."
    ],
    'neutral': [
        "Thank you for sharing. Journaling is a great habit.",
        "Keep reflecting and taking care of yourself.",
        "Every day is a new opportunity."
    ],
    'upset': [
        "It’s okay to feel upset. Try to talk to someone you trust.",
        "Expressing your feelings is healthy.",
        "You’re stronger than you think."
    ]
}

CRISIS_KEYWORDS = ["suicide", "kill myself", "end my life", "hopeless", "worthless", "life is not worth", "can't go on", "die", "give up"]

@app.route('/')
@limiter.limit("100 per minute")
def index():
    """Main page with rate limiting"""
    return render_template('index.html')

@socketio.on('audio_data')
def handle_audio_data(data):
    """Handle real-time audio data with security validation"""
    try:
        logger.info("Received audio data from WebSocket")
        
        # Validate input data
        if not isinstance(data, dict) or 'audio' not in data:
            logger.warning("Invalid audio data format received")
            emit('error', {'message': 'Invalid audio data format'})
            return
        
        # Validate audio data format
        audio_str = data['audio']
        if not audio_str.startswith('data:audio/'):
            logger.warning("Invalid audio data format")
            emit('error', {'message': 'Invalid audio data format'})
            return
        
        # Decode base64 audio data
        try:
            audio_data = base64.b64decode(audio_str.split(',')[1])
        except Exception as e:
            logger.warning(f"Failed to decode audio data: {e}")
            emit('error', {'message': 'Invalid audio data encoding'})
            return
        
        # Validate audio file
        is_valid, error_msg, _ = SecurityValidator.validate_audio_file(
            audio_data, 
            app.config['ALLOWED_AUDIO_EXTENSIONS'], 
            app.config['MAX_CONTENT_LENGTH']
        )
        
        if not is_valid:
            logger.warning(f"Audio validation failed: {error_msg}")
            emit('error', {'message': error_msg})
            return
        
        # Create secure temporary file
        temp_file_path = SecurityValidator.create_secure_temp_file(audio_data, '.wav')
        
        try:
            # Transcribe audio
            logger.info("Starting audio transcription...")
            transcription = whisper_model.transcribe(temp_file_path)
            text = transcription["text"]
            logger.info(f"Transcription completed: {text[:100]}...")

            # Validate transcribed text
            is_valid, error_msg = SecurityValidator.validate_text_input(
                text, 
                app.config['MAX_TEXT_LENGTH'], 
                app.config['MIN_TEXT_LENGTH']
            )
            
            if not is_valid:
                logger.warning(f"Text validation failed: {error_msg}")
                emit('error', {'message': error_msg})
                return

            # Extract features
            logger.info("Extracting audio features...")
            y, sr = librosa.load(temp_file_path, sr=16000)
            features = extract_features(y, sr)
            logger.info("Audio features extracted successfully")

            # Predict mood
            logger.info("Predicting mood...")
            mood_result = detect_mood(text, features)
            logger.info(f"Mood result: {mood_result['mood']}")

            # Send results back to client
            result = {
                'text': text,
                'mood': mood_result['mood'],
                'emoji': mood_result['emoji'],
                'message': mood_result['message'],
                'features': {
                    'pitch': float(features['pitch']),
                    'energy': float(features['energy']),
                    'zero_crossing_rate': float(features['zero_crossing_rate']),
                    'spectral_centroid': float(features['spectral_centroid'])
                }
            }
            logger.info("Sending analysis results")
            emit('analysis_result', result)

        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
                logger.debug("Temporary file cleaned up")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file: {e}")

    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}", exc_info=True)
        # Don't expose internal errors to client
        emit('error', {'message': 'Audio processing failed. Please try again.'})

@app.route('/journal', methods=['POST'])
@limiter.limit("30 per minute")
def journal_entry():
    """Handle journal entries with comprehensive security validation"""
    try:
        # Validate JSON payload
        if not request.is_json:
            logger.warning("Non-JSON request received")
            return jsonify({'error': 'Invalid request format'}), 400
        
        data = request.get_json()
        print("DEBUG: Received JSON payload:", data)
        if not data:
            logger.warning("Empty JSON payload received")
            return jsonify({'error': 'Empty request payload'}), 400
        
        # Validate required fields
        is_valid, error_msg = SecurityValidator.validate_json_payload(data, ['text'])
        if not is_valid:
            logger.warning(f"JSON validation failed: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        # Validate text input
        text = data.get('text', '').strip()
        is_valid, error_msg = SecurityValidator.validate_text_input(
            text,
            app.config['MAX_TEXT_LENGTH'],
            0  # Allow empty string for audio
        )
        
        if not is_valid:
            logger.warning(f"Text validation failed: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        audio_b64 = data.get('audio', None)
        transcription = text
        features = {'pitch': 0, 'energy': 0, 'zero_crossing_rate': 0, 'spectral_centroid': 0}

        # Process audio if provided
        if audio_b64:
            logger.info("Processing audio data for journal entry")
            
            # Validate audio data format
            if not isinstance(audio_b64, str) or not audio_b64.startswith('data:audio/'):
                logger.warning("Invalid audio data format")
                return jsonify({'error': 'Invalid audio data format'}), 400
            
            try:
                audio_data = base64.b64decode(audio_b64.split(',')[1])
            except Exception as e:
                logger.warning(f"Failed to decode audio data: {e}")
                return jsonify({'error': 'Invalid audio data encoding'}), 400
            
            # Validate audio file
            is_valid, error_msg, detected_ext = SecurityValidator.validate_audio_file(
                audio_data, 
                app.config['ALLOWED_AUDIO_EXTENSIONS'], 
                app.config['MAX_CONTENT_LENGTH']
            )
            
            if not is_valid:
                logger.warning(f"Audio validation failed: {error_msg}")
                return jsonify({'error': error_msg}), 400
            
            # Create secure temporary files
            temp_file_path = SecurityValidator.create_secure_temp_file(audio_data, f'.{detected_ext}')
            wav_temp_file_path = SecurityValidator.create_secure_temp_file(b'', '.wav')
            
            try:
                # Convert audio using ffmpeg with security considerations
                result = subprocess.run([
                    'ffmpeg', '-y', '-i', temp_file_path, '-ar', '16000', '-ac', '1', wav_temp_file_path
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
                
                logger.info("Audio converted successfully")

                # Transcribe and extract features
                transcription = whisper_model.transcribe(wav_temp_file_path)["text"]
                
                # Validate transcribed text
                is_valid, error_msg = SecurityValidator.validate_text_input(
                    transcription, 
                    app.config['MAX_TEXT_LENGTH'], 
                    app.config['MIN_TEXT_LENGTH']
                )
                
                if not is_valid:
                    logger.warning(f"Transcribed text validation failed: {error_msg}")
                    return jsonify({'error': error_msg}), 400
                
                y, sr = librosa.load(wav_temp_file_path, sr=16000)
                features = extract_features(y, sr)
                logger.info("Audio features extracted successfully")
                
            except subprocess.TimeoutExpired:
                logger.error("Audio conversion timed out")
                return jsonify({'error': 'Audio processing timed out. Please try again.'}), 408
            except subprocess.CalledProcessError as e:
                logger.error(f"Audio conversion failed: {e}")
                return jsonify({'error': 'Audio processing failed. Please try again.'}), 500
            except Exception as e:
                logger.error(f"Audio processing error: {e}", exc_info=True)
                return jsonify({'error': 'Audio processing failed. Please try again.'}), 500
            finally:
                # Clean up temporary files
                for temp_path in [temp_file_path, wav_temp_file_path]:
                    try:
                        os.unlink(temp_path)
                    except Exception as e:
                        logger.warning(f"Failed to clean up temporary file {temp_path}: {e}")

        # Analyze mood
        logger.info(f"Analyzing mood for text: {transcription[:100]}...")
        mood_result = detect_mood(transcription, features)
        mood = mood_result['mood']
        emoji = mood_result['emoji']

        # Create summary
        summary = f"You shared that you felt {mood} today."
        if len(transcription.split()) > 10:
            summary = f"You talked about: {transcription[:120]}{'...' if len(transcription) > 120 else ''}"

        # Get supportive message
        supportive_message = random.choice(SUPPORTIVE_MESSAGES.get(mood, SUPPORTIVE_MESSAGES['neutral']))

        # Enhanced crisis detection
        crisis_detected = SecurityValidator.detect_crisis_content(transcription, app.config['CRISIS_KEYWORDS'])
        if crisis_detected:
            supportive_message += " If you're feeling overwhelmed or hopeless, please consider reaching out to a mental health professional or calling a crisis hotline."
            logger.warning(f"Crisis content detected in journal entry: {transcription[:200]}...")

        result = {
            'transcription': transcription,
            'mood': mood,
            'emoji': emoji,
            'summary': summary,
            'message': supportive_message,
            'features': features
        }
        
        logger.info(f"Journal analysis completed successfully for mood: {mood}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Unexpected error in journal entry: {str(e)}", exc_info=True)
        return jsonify({'error': 'An unexpected error occurred. Please try again.'}), 500

if __name__ == '__main__':
    logger.info("Starting server...")
    socketio.run(app, host='0.0.0.0', port=5001, debug=False, use_reloader=False) 