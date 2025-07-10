"""
Debug Voice Authentication System
"""

import requests
import json
import os
import base64
import numpy as np
import wave
import tempfile

def create_simple_audio():
    """Create a very simple audio file for testing"""
    # Create a simple sine wave
    sample_rate = 16000
    duration = 2.0
    frequency = 440
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(2 * np.pi * frequency * t)
    
    # Convert to 16-bit PCM
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Create WAV file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    with wave.open(temp_filename, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    # Read the file as bytes
    with open(temp_filename, 'rb') as f:
        wav_bytes = f.read()
    
    # Clean up
    os.unlink(temp_filename)
    
    return wav_bytes

def test_voice_system():
    """Test the voice authentication system step by step"""
    
    base_url = "http://127.0.0.1:5001"
    user_id = "12"
    
    print("🔍 Debugging Voice Authentication System")
    print("=" * 50)
    
    # 1. Check if server is running
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Server is running (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Server is not running: {e}")
        return
    
    # 2. Check voice profile
    profile_path = f"voice_profiles/{user_id}.json"
    if os.path.exists(profile_path):
        print(f"✅ Voice profile exists: {profile_path}")
        with open(profile_path, 'r') as f:
            profile = json.load(f)
        print(f"   Features: {len(profile.get('features', {}))}")
        print(f"   Sample features: {dict(list(profile.get('features', {}).items())[:3])}")
    else:
        print(f"❌ Voice profile not found: {profile_path}")
        return
    
    # 3. Create test audio
    print(f"\n🎵 Creating test audio...")
    try:
        audio_data = create_simple_audio()
        audio_b64 = f"data:audio/wav;base64,{base64.b64encode(audio_data).decode()}"
        print(f"✅ Created test audio: {len(audio_data)} bytes")
        print(f"   Base64 length: {len(audio_b64)} characters")
    except Exception as e:
        print(f"❌ Failed to create test audio: {e}")
        return
    
    # 4. Test voice verification with detailed error handling
    print(f"\n🔍 Testing voice verification...")
    
    verification_data = {
        "user_id": user_id,
        "audio": audio_b64
    }
    
    try:
        print(f"   Sending request to {base_url}/voice/verify")
        print(f"   User ID: {user_id}")
        print(f"   Audio data length: {len(audio_data)} bytes")
        
        response = requests.post(f"{base_url}/voice/verify", json=verification_data, timeout=30)
        
        print(f"   Response status: {response.status_code}")
        print(f"   Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Voice verification successful:")
            print(f"   Authenticated: {result.get('authenticated')}")
            print(f"   Confidence: {result.get('confidence', 0):.3f}")
            print(f"   Message: {result.get('message')}")
            
            if result.get('authenticated'):
                print(f"🎉 SUCCESS! Voice verification is working!")
            else:
                print(f"⚠️  Voice verification failed with confidence {result.get('confidence', 0):.3f}")
                
        elif response.status_code == 500:
            print(f"❌ Server error (500):")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out")
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error - server might not be running")
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
    
    # 5. Test with a different user ID (should fail)
    print(f"\n🔍 Testing with non-existent user...")
    try:
        verification_data_fail = {
            "user_id": "nonexistent_user",
            "audio": audio_b64
        }
        
        response = requests.post(f"{base_url}/voice/verify", json=verification_data_fail)
        
        if response.status_code == 200:
            result = response.json()
            if not result.get('authenticated'):
                print(f"✅ Correctly failed for non-existent user")
            else:
                print(f"❌ Unexpectedly succeeded for non-existent user")
        else:
            print(f"❌ Unexpected response for non-existent user: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing non-existent user: {e}")
    
    print(f"\n🎯 Debug completed!")

if __name__ == "__main__":
    test_voice_system() 