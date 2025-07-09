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
        "Your feelings are valid, and it's okay to not be okay right now. Remember that sadness, like all emotions, is temporary. Consider doing something kind for yourself today - maybe a warm bath, your favorite music, or reaching out to someone who cares about you.",
        "I hear the pain in your words, and I want you to know that you don't have to carry this alone. Sadness can feel overwhelming, but you're stronger than you realize. Sometimes the bravest thing we can do is simply get through the day.",
        "It takes courage to acknowledge when we're feeling down. Your sadness doesn't make you weak - it makes you human. Consider what your body and mind might need right now. Sometimes even small acts of self-care can make a difference."
    ],
    'melancholy': [
        "There's a beautiful depth to your reflection. Melancholy often brings with it wisdom and insight. Honor this contemplative space you're in - it might be preparing you for something meaningful.",
        "Your thoughtful sadness speaks to your sensitivity and depth. These moments of quiet reflection often lead to our most profound realizations. Trust that this feeling has something to teach you.",
        "There's something poetic about the way you're processing your feelings. Melancholy isn't just sadness - it's often a sign of growth and transformation. Be patient with yourself through this process."
    ],
    'angry': [
        "Your anger is telling you something important - it's a signal that something needs to change. Anger can be a powerful force for positive transformation when we learn to channel it constructively. What might your anger be trying to protect you from?",
        "I can feel the intensity of your emotions, and that's completely valid. Anger often masks other feelings like hurt, fear, or disappointment. Try to identify what's beneath the anger - it might help you address the root cause.",
        "Your frustration is understandable. Sometimes anger is our mind's way of saying 'this isn't right' or 'I deserve better.' Consider what boundaries you might need to set or what changes you might need to make."
    ],
    'frustrated': [
        "Frustration is often a sign that you care deeply about something. It shows you have standards and expectations - that's not a bad thing! The challenge is finding constructive ways to channel that energy.",
        "I can hear how much this matters to you. Frustration can be exhausting, but it also shows your commitment to things being better. Sometimes the most productive thing we can do is step back and reassess our approach.",
        "Your frustration is completely valid. When things don't go as planned, it's natural to feel this way. Consider what's within your control and what might need a different approach or perspective."
    ],
    'upset': [
        "It's clear that something has deeply affected you, and that's okay. Being upset shows that you're engaged with life and that things matter to you. Sometimes the best thing we can do is simply acknowledge our feelings without trying to fix them immediately.",
        "Your feelings are important, and it's brave to acknowledge when you're upset. This discomfort you're feeling might be temporary, but it's also real and valid. Consider what support you might need right now.",
        "I can sense the weight of what you're carrying. Being upset doesn't mean you're not handling things well - it means you're human. Sometimes the most healing thing we can do is give ourselves permission to feel exactly as we do."
    ],
    'happy': [
        "Your joy is absolutely radiant! Happiness like this is precious and worth celebrating. These moments of pure contentment are what make life beautiful. Consider what made this possible and how you might create more of these moments.",
        "I can feel your positive energy through your words! Happiness is contagious, and you're spreading it beautifully. These good feelings are well-deserved - enjoy every moment of them.",
        "Your happiness is so genuine and uplifting! When we're truly happy, it shows in everything we do and say. This is the kind of joy that comes from being aligned with what matters most to you."
    ],
    'excited': [
        "Your enthusiasm is absolutely infectious! That spark of excitement you're feeling is precious - it's your passion and energy coming through. When we're excited about something, it often means we're on the right path.",
        "I love the energy you're bringing! Excitement is such a beautiful emotion - it's hope and anticipation combined. This feeling often leads to our most creative and productive moments.",
        "Your excitement is palpable and wonderful! That kind of genuine enthusiasm is rare and valuable. It shows you're engaged with life and open to possibilities. Keep that energy flowing!"
    ],
    'calm': [
        "There's such a peaceful quality to your presence. This inner calm you're experiencing is a beautiful state - it's the foundation for clarity, wisdom, and authentic connection. Cherish this centered feeling.",
        "Your calmness is truly grounding. This peaceful state you're in allows for deeper reflection and more meaningful experiences. It's a sign of inner strength and emotional maturity.",
        "I can feel the serenity in your words. This calm you're experiencing is precious - it's often when we're most open to insights and new perspectives. This peaceful state is worth protecting and nurturing."
    ],
    'content': [
        "You sound genuinely content, and that's a beautiful place to be. Contentment isn't about having everything perfect - it's about being at peace with where you are. This balanced state is often the foundation for lasting happiness.",
        "There's a lovely sense of satisfaction in your tone. Contentment is such an underrated emotion - it's the quiet joy of being okay with yourself and your circumstances. This is a state worth appreciating.",
        "Your contentment is so genuine and refreshing. This feeling of being at ease with yourself and your life is precious. Contentment often comes from accepting what is while still being open to growth."
    ],
    'tired': [
        "Your exhaustion is valid, and it's okay to acknowledge it. Sometimes our bodies and minds need rest more than we realize. Consider what kind of rest would be most restorative for you right now.",
        "I can hear the fatigue in your voice, and that's completely understandable. Being tired doesn't mean you're not doing enough - it might mean you've been doing too much. Give yourself permission to rest.",
        "Your tiredness is telling you something important. Sometimes the most productive thing we can do is rest. Consider what your body and mind might need to feel more energized and refreshed."
    ],
    'anxious': [
        "I can sense the tension you're carrying, and I want you to know that anxiety is a normal human experience. Your body is trying to protect you, even if it feels overwhelming. Consider what might help you feel more grounded right now.",
        "Your anxiety is valid, and it's okay to feel this way. Anxiety often comes from caring deeply about things and wanting to do well. Sometimes the most helpful thing is to acknowledge the feeling without fighting it.",
        "I can hear the worry in your voice, and that's completely understandable. Anxiety can feel isolating, but you're not alone in this experience. Consider what might help you feel more supported and less overwhelmed."
    ],
    'curious': [
        "Your curiosity is such a beautiful quality! That desire to understand and explore is what drives growth and learning. Curiosity keeps us engaged with life and open to new possibilities.",
        "I love the inquisitive energy you're bringing! Curiosity is often the first step toward discovery and growth. That sense of wonder you're feeling is precious - it keeps life interesting and meaningful.",
        "Your curiosity is absolutely wonderful! That desire to learn and understand shows an active, engaged mind. Curiosity often leads to our most interesting discoveries and connections."
    ],
    'neutral': [
        "Sometimes being neutral is exactly where we need to be. It's a balanced state that allows for reflection and observation. Consider what might be beneath the surface of this neutral feeling.",
        "Your neutral state might be a sign of processing or transition. Sometimes we need these balanced moments to integrate our experiences. This calm center can be a good foundation for whatever comes next.",
        "There's wisdom in being able to stay neutral when needed. This balanced state allows you to observe without being overwhelmed by emotions. Consider what this neutrality might be preparing you for."
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
                # Try to use ffmpeg if available, otherwise use direct processing
                try:
                    # Convert audio using ffmpeg with security considerations
                    result = subprocess.run([
                        'ffmpeg', '-y', '-i', temp_file_path, '-ar', '16000', '-ac', '1', wav_temp_file_path
                    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
                    
                    logger.info("Audio converted successfully with ffmpeg")
                    audio_file_for_processing = wav_temp_file_path
                    
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                    logger.info("ffmpeg not available, using direct audio processing")
                    # Use the original file directly if it's already in a supported format
                    audio_file_for_processing = temp_file_path

                # Transcribe and extract features
                transcription = whisper_model.transcribe(audio_file_for_processing)["text"]
                
                # Validate transcribed text
                is_valid, error_msg = SecurityValidator.validate_text_input(
                    transcription, 
                    app.config['MAX_TEXT_LENGTH'], 
                    app.config['MIN_TEXT_LENGTH']
                )
                
                if not is_valid:
                    logger.warning(f"Transcribed text validation failed: {error_msg}")
                    return jsonify({'error': error_msg}), 400
                
                y, sr = librosa.load(audio_file_for_processing, sr=16000)
                features = extract_features(y, sr)
                logger.info("Audio features extracted successfully")
                
            except Exception as e:
                logger.error(f"Audio processing error: {e}")
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
    # Use environment variable for port (Render requirement)
    port = int(os.environ.get('PORT', 5001))
    socketio.run(app, host='0.0.0.0', port=port, debug=False, use_reloader=False) 