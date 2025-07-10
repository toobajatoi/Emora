"""
Secure Mood Journal Application
Created by Tooba Jatoi
Copyright © 2025 Tooba Jatoi. All rights reserved.
"""

import os
import logging
import whisper
import numpy as np
from flask import Flask, render_template, request, jsonify, abort, session, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_cors import CORS
from feature_extractor import extract_features
from mood_classifier import detect_mood
from config import config
from security import SecurityValidator, SecurityError
from voice_auth import VoiceAuthenticator
import tempfile
import librosa
import base64
import json
import random
import subprocess
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge
import traceback
import mimetypes
import re

# Set up logging with security considerations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app with security configuration
app = Flask(__name__)
mimetypes.add_type('application/javascript', '.js')
# Force development config for local runs
app.config.from_object(config['development'])

# Set a secret key for session management
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')

# Initialize security extensions
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Comment out Talisman for local development to debug session issues
# talisman = Talisman(
#     app,
#     content_security_policy=app.config['SECURITY_HEADERS']['CONTENT_SECURITY_POLICY'],
#     force_https=False  # Set to True in production
# )

# Initialize CORS
# Restrict CORS to local origins for session cookies
CORS(app, origins=['http://localhost:5001', 'http://127.0.0.1:5001', 'http://192.168.18.10:5001'])

socketio = SocketIO(app, async_mode='threading', cors_allowed_origins='*', logger=True, engineio_logger=True)

# Initialize Voice Authenticator
voice_auth = VoiceAuthenticator()

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

JOURNAL_DIR = 'journals'
if not os.path.exists(JOURNAL_DIR):
    os.makedirs(JOURNAL_DIR)

def normalize_phrase(phrase):
    phrase = phrase.lower()
    phrase = phrase.replace("i'm", "i am")
    phrase = phrase.replace("you're", "you are")
    phrase = phrase.replace("he's", "he is")
    phrase = phrase.replace("she's", "she is")
    phrase = phrase.replace("it's", "it is")
    phrase = phrase.replace("we're", "we are")
    phrase = phrase.replace("they're", "they are")
    phrase = phrase.replace("can't", "cannot")
    phrase = phrase.replace("won't", "will not")
    phrase = phrase.replace("n't", " not")
    phrase = phrase.replace("'re", " are")
    phrase = phrase.replace("'s", " is")
    phrase = phrase.replace("'d", " would")
    phrase = phrase.replace("'ll", " will")
    phrase = phrase.replace("'ve", " have")
    phrase = phrase.replace("'m", " am")
    phrase = re.sub(r"[^a-z0-9 ]", "", phrase)  # remove punctuation
    phrase = phrase.strip()
    return phrase

@app.route('/')
@limiter.limit("100 per minute")
def index():
    """Login page - redirect to login"""
    return render_template('login.html')

@app.route('/journal_page')
@limiter.limit("100 per minute")
def journal_page():
    """Main journal page - requires authentication"""
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user_id = session['user_id']
    # Load user's name from users.json
    name = user_id
    try:
        with open('users.json', 'r') as f:
            users = json.load(f)
        if user_id in users and 'name' in users[user_id]:
            name = users[user_id]['name']
    except Exception:
        pass
    return render_template('index.html', name=name)

@app.route('/logout')
@limiter.limit("100 per minute")
def logout():
    """Logout user and clear session"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/voice-test')
@limiter.limit("100 per minute")
def voice_test():
    """Voice authentication test page"""
    return render_template('voice_test.html')

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

@app.route('/journal', methods=['GET'])
@limiter.limit("100 per minute")
def get_journal():
    """Return the logged-in user's journal entries only"""
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user_id = session['user_id']
    journal_path = os.path.join(JOURNAL_DIR, f"{user_id}.json")
    if os.path.exists(journal_path):
        with open(journal_path, 'r') as f:
            entries = json.load(f)
    else:
        entries = []
    return jsonify({'entries': entries})

@app.route('/journal', methods=['POST'])
@limiter.limit("30 per minute")
def journal_entry():
    """Handle journal entries with comprehensive security validation and per-user storage"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        user_id = session['user_id']
        # Validate JSON payload
        if not request.is_json:
            logger.warning("Non-JSON request received")
            return jsonify({'error': 'Invalid request format'}), 400
        data = request.get_json()
        if not data:
            logger.warning("Empty JSON payload received")
            return jsonify({'error': 'Empty request payload'}), 400
        # Validate required fields
        is_valid, error_msg = SecurityValidator.validate_json_payload(data, ['text'])
        if not is_valid:
            logger.warning(f"JSON validation failed: {error_msg}")
            return jsonify({'error': error_msg}), 400
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

        # Analyze mood with enhanced emotional analysis
        logger.info(f"Analyzing mood for text: {transcription[:100]}...")
        mood_result = detect_mood(transcription, features)
        mood = mood_result['mood']
        emoji = mood_result['emoji']
        message = mood_result['message']

        # Enhanced crisis detection
        crisis_detected = SecurityValidator.detect_crisis_content(transcription, app.config['CRISIS_KEYWORDS'])
        if crisis_detected:
            message += "\n\nIf you're feeling overwhelmed or hopeless, please consider reaching out to a mental health professional or calling a crisis hotline. You don't have to face this alone."
            logger.warning(f"Crisis content detected in journal entry: {transcription[:200]}...")

        result = {
            'transcription': transcription,
            'mood': mood,
            'emoji': emoji,
            'message': message,
            'features': features
        }
        
        # Save entry to user's journal file
        journal_path = os.path.join(JOURNAL_DIR, f"{user_id}.json")
        if os.path.exists(journal_path):
            with open(journal_path, 'r') as f:
                entries = json.load(f)
        else:
            entries = []
        entry = {
            'text': transcription,
            'mood': mood,
            'emoji': emoji,
            'message': message,
            'features': features,
            'timestamp': str(np.datetime64('now'))
        }
        entries.append(entry)
        with open(journal_path, 'w') as f:
            json.dump(entries, f, indent=2)
        logger.info(f"Journal analysis completed and saved for user {user_id}, mood: {mood}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Unexpected error in journal entry: {str(e)}", exc_info=True)
        return jsonify({'error': 'An unexpected error occurred. Please try again.'}), 500

@app.route('/journal', methods=['DELETE'])
@limiter.limit("10 per minute")
def delete_journal():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    user_id = session['user_id']
    journal_path = os.path.join(JOURNAL_DIR, f"{user_id}.json")
    try:
        if os.path.exists(journal_path):
            os.remove(journal_path)
        return jsonify({'message': 'Journal history deleted.'}), 200
    except Exception as e:
        logger.error(f"Failed to delete journal for {user_id}: {e}")
        return jsonify({'error': 'Failed to delete journal history.'}), 500

# Password Authentication Routes
@app.route('/auth/register', methods=['POST'])
@limiter.limit("10 per minute")
def register_user():
    """Register new user with password"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Invalid request format'}), 400
        
        data = request.get_json()
        user_id = data.get('user_id')
        password = data.get('password')
        name = data.get('name')
        
        if not user_id or not password or not name:
            return jsonify({'error': 'Missing user_id, password, or name'}), 400
        
        # Simple password storage (in production, use proper hashing)
        import hashlib
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Store user data (in production, use a database)
        user_data = {
            'user_id': user_id,
            'password_hash': hashed_password,
            'name': name,
            'created_at': str(np.datetime64('now'))
        }
        
        # Save to file (simple storage)
        import json
        users_file = 'users.json'
        users = {}
        
        try:
            with open(users_file, 'r') as f:
                users = json.load(f)
        except FileNotFoundError:
            pass
        
        if user_id in users:
            return jsonify({'error': 'User already exists'}), 409
        
        users[user_id] = user_data
        
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)
        
        return jsonify({'message': 'User registered successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error in user registration: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/auth/login', methods=['POST'])
@limiter.limit("20 per minute")
def login_user():
    """Login user with password"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Invalid request format'}), 400
        
        data = request.get_json()
        user_id = data.get('user_id')
        password = data.get('password')
        
        if not user_id or not password:
            return jsonify({'error': 'Missing user_id or password'}), 400
        
        # Load user data
        import json
        import hashlib
        
        users_file = 'users.json'
        try:
            with open(users_file, 'r') as f:
                users = json.load(f)
        except FileNotFoundError:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if user_id not in users:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user_data = users[user_id]
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        if user_data['password_hash'] != hashed_password:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        session['user_id'] = user_id
        return jsonify({
            'authenticated': True,
            'message': 'Login successful'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in user login: {e}")
        return jsonify({'error': 'Login failed'}), 500

# Voice Authentication Routes
@app.route('/voice/enroll', methods=['POST'])
@limiter.limit("10 per minute")
def enroll_voice():
    """Enroll user's voice for authentication"""
    try:
        # Validate JSON payload
        if not request.is_json:
            return jsonify({'error': 'Invalid request format'}), 400
        
        data = request.get_json()
        user_id = data.get('user_id')
        audio_b64 = data.get('audio')
        passphrase = data.get('passphrase', 'Hello Emora')
        
        if not user_id or not audio_b64:
            return jsonify({'error': 'Missing user_id or audio data'}), 400
        
        # Validate audio data
        if not audio_b64.startswith('data:audio/'):
            return jsonify({'error': 'Invalid audio data format'}), 400
        
        try:
            audio_data = base64.b64decode(audio_b64.split(',')[1])
        except Exception as e:
            return jsonify({'error': 'Invalid audio data encoding'}), 400
        
        # Always convert to standard WAV for Whisper
        import tempfile
        import uuid
        import subprocess
        import os
        temp_input = f"temp_input_{uuid.uuid4().hex[:8]}"
        temp_wav = f"temp_wav_{uuid.uuid4().hex[:8]}.wav"
        try:
            with open(temp_input, 'wb') as f:
                f.write(audio_data)
            # Use ffmpeg to convert to mono 16kHz WAV
            result = subprocess.run([
                'ffmpeg', '-y', '-i', temp_input, '-ar', '16000', '-ac', '1', temp_wav
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            if not os.path.exists(temp_wav):
                logger.error(f"ffmpeg failed: {result.stderr.decode()}")
                transcription = 'Audio conversion failed (ffmpeg error)'
            else:
                # Transcribe using Whisper
                transcription = whisper_model.transcribe(temp_wav)["text"]
        except Exception as e:
            logger.error(f"Audio conversion/transcription error: {e}")
            transcription = f'Could not transcribe: {e}'
        finally:
            try:
                if os.path.exists(temp_input):
                    os.unlink(temp_input)
                if os.path.exists(temp_wav):
                    os.unlink(temp_wav)
            except Exception as e:
                logger.warning(f"Failed to clean up temp files: {e}")
        
        # Create voice profile (using original audio)
        success = voice_auth.create_voice_profile(user_id, audio_data, passphrase)
        
        if success:
            return jsonify({
                'message': 'Voice profile created successfully',
                'transcription': transcription,
                'passphrase': passphrase,
                'success': True
            }), 200
        else:
            return jsonify({'error': 'Failed to create voice profile'}), 500
            
    except Exception as e:
        logger.error(f"Error in voice enrollment: {e}")
        return jsonify({'error': 'Voice enrollment failed'}), 500

@app.route('/voice/verify', methods=['POST'])
@limiter.limit("20 per minute")
def verify_voice():
    """Verify user's voice for authentication"""
    try:
        # Validate JSON payload
        if not request.is_json:
            logger.warning("Non-JSON request received for voice verification")
            return jsonify({'error': 'Invalid request format'}), 400
        
        data = request.get_json()
        user_id = data.get('user_id')
        audio_b64 = data.get('audio')
        
        logger.info(f"Voice verification request for user: {user_id}")
        
        if not user_id or not audio_b64:
            logger.warning("Missing user_id or audio data in voice verification request")
            return jsonify({'error': 'Missing user_id or audio data'}), 400
        
        # Validate audio data
        if not audio_b64.startswith('data:audio/'):
            logger.warning("Invalid audio data format in voice verification request")
            return jsonify({'error': 'Invalid audio data format'}), 400
        
        try:
            audio_data = base64.b64decode(audio_b64.split(',')[1])
            logger.info(f"Decoded audio data: {len(audio_data)} bytes")
        except Exception as e:
            logger.error(f"Failed to decode audio data: {e}")
            return jsonify({'error': 'Invalid audio data encoding'}), 400
        
        # Verify voice
        logger.info(f"Starting voice verification for user: {user_id}")
        is_authenticated, confidence = voice_auth.verify_voice(user_id, audio_data)
        
        # Transcribe the audio to show what was said
        transcription = "Could not transcribe"
        try:
            import uuid
            temp_path = f"temp_verify_{uuid.uuid4().hex[:8]}.wav"
            with open(temp_path, 'wb') as f:
                f.write(audio_data)
            transcription = whisper_model.transcribe(temp_path)["text"]
            os.unlink(temp_path)
        except Exception as e:
            logger.error(f"Transcription error during verification: {e}")
        
        # Passphrase check
        profile = voice_auth.get_profile_info(user_id)
        expected_phrase = (profile.get('passphrase', '') if profile else '').strip()
        spoken_phrase = transcription.strip()
        expected_phrase_norm = normalize_phrase(expected_phrase)
        spoken_phrase_norm = normalize_phrase(spoken_phrase)
        phrase_match = expected_phrase_norm == spoken_phrase_norm
        if not phrase_match:
            logger.warning(f"Passphrase mismatch: expected '{expected_phrase_norm}', got '{spoken_phrase_norm}'")
        
        logger.info(f"Voice verification result for {user_id}: authenticated={is_authenticated}, confidence={confidence:.3f}, phrase_match={phrase_match}")
        
        if is_authenticated and phrase_match:
            session['user_id'] = user_id
            auth_result = True
        else:
            auth_result = False
        
        return jsonify({
            'authenticated': bool(auth_result),
            'confidence': float(confidence),
            'transcription': transcription,
            'message': 'Voice verified successfully' if auth_result else 'Voice verification failed (voice or phrase did not match)'
        }), 200
            
    except Exception as e:
        logger.error(f"Error in voice verification: {e}")
        import traceback
        logger.error(f"Voice verification traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Voice verification failed'}), 500

@app.route('/voice/profile/<user_id>', methods=['GET'])
@limiter.limit("30 per minute")
def get_voice_profile(user_id):
    """Get user's voice profile information"""
    try:
        profile_info = voice_auth.get_profile_info(user_id)
        
        if profile_info:
            return jsonify(profile_info), 200
        else:
            return jsonify({'error': 'Voice profile not found'}), 404
            
    except Exception as e:
        logger.error(f"Error getting voice profile: {e}")
        return jsonify({'error': 'Failed to get voice profile'}), 500

@app.route('/voice/profile/<user_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
def delete_voice_profile(user_id):
    """Delete user's voice profile"""
    try:
        success = voice_auth.delete_voice_profile(user_id)
        
        if success:
            return jsonify({'message': 'Voice profile deleted successfully'}), 200
        else:
            return jsonify({'error': 'Voice profile not found'}), 404
            
    except Exception as e:
        logger.error(f"Error deleting voice profile: {e}")
        return jsonify({'error': 'Failed to delete voice profile'}), 500

@app.route('/voice/debug/<user_id>', methods=['GET'])
@limiter.limit("10 per minute")
def debug_voice_profile(user_id):
    """Debug voice profile information"""
    try:
        profile_info = voice_auth.get_profile_info(user_id)
        
        if profile_info:
            # Get detailed profile data
            profile_path = os.path.join(voice_auth.storage_path, f"{user_id}.json")
            with open(profile_path, 'r') as f:
                full_profile = json.load(f)
            
            debug_info = {
                'profile_info': profile_info,
                'feature_count': len(full_profile.get('features', {})),
                'feature_names': list(full_profile.get('features', {}).keys()),
                'similarity_threshold': voice_auth.similarity_threshold,
                'storage_path': voice_auth.storage_path
            }
            
            return jsonify(debug_info), 200
        else:
            return jsonify({'error': 'Voice profile not found'}), 404
            
    except Exception as e:
        logger.error(f"Error getting voice profile debug info: {e}")
        return jsonify({'error': 'Failed to get voice profile debug info'}), 500

if __name__ == '__main__':
    logger.info("Starting server...")
    # Use environment variable for port (Render requirement)
    port = int(os.environ.get('PORT', 5001))
    socketio.run(app, host='0.0.0.0', port=port, debug=False, use_reloader=False) 