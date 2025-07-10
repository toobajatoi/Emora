"""
Test Voice Authentication with Real Audio Data
"""

import requests
import json
import os
import numpy as np
import wave
import tempfile
import base64

def create_test_audio(duration=2.0, frequency=440, sample_rate=16000):
    """Create a simple sine wave audio for testing"""
    # Generate sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(2 * np.pi * frequency * t)
    
    # Convert to 16-bit PCM
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Create WAV file in memory
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    # Write to WAV file
    with wave.open(temp_filename, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    # Read the file as bytes
    with open(temp_filename, 'rb') as f:
        wav_bytes = f.read()
    
    # Clean up temp file
    os.unlink(temp_filename)
    
    return wav_bytes

def test_voice_auth_with_real_audio():
    """Test voice authentication with real audio data"""
    
    base_url = "http://127.0.0.1:5001"
    user_id = "12"
    
    print("🎤 Testing Voice Authentication with Real Audio")
    print("=" * 55)
    
    # 1. Check if profile exists
    profile_path = f"voice_profiles/{user_id}.json"
    if os.path.exists(profile_path):
        print(f"✅ Profile file exists: {profile_path}")
        with open(profile_path, 'r') as f:
            profile = json.load(f)
        print(f"   Features: {len(profile.get('features', {}))}")
        print(f"   Feature names: {list(profile.get('features', {}).keys())}")
    else:
        print(f"❌ Profile file not found: {profile_path}")
        return
    
    # 2. Create real audio data
    print(f"\n🎵 Creating test audio...")
    try:
        audio_data = create_test_audio(duration=3.0, frequency=440)
        audio_b64 = f"data:audio/wav;base64,{base64.b64encode(audio_data).decode()}"
        print(f"✅ Created test audio: {len(audio_data)} bytes")
    except Exception as e:
        print(f"❌ Failed to create test audio: {e}")
        return
    
    # 3. Test voice verification with real audio
    print(f"\n🔍 Testing voice verification...")
    
    verification_data = {
        "user_id": user_id,
        "audio": audio_b64
    }
    
    try:
        response = requests.post(f"{base_url}/voice/verify", json=verification_data)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Voice verification response:")
            print(f"   Authenticated: {result.get('authenticated')}")
            print(f"   Confidence: {result.get('confidence', 0):.3f}")
            print(f"   Message: {result.get('message')}")
            
            if result.get('authenticated'):
                print(f"🎉 SUCCESS! Voice verification is working!")
            else:
                print(f"⚠️  Voice verification failed with confidence {result.get('confidence', 0):.3f}")
        else:
            print(f"❌ Voice verification failed:")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error during verification: {e}")
    
    # 4. Test with different audio (should still work)
    print(f"\n🎵 Testing with different frequency...")
    try:
        audio_data2 = create_test_audio(duration=3.0, frequency=880)  # Different frequency
        audio_b64_2 = f"data:audio/wav;base64,{base64.b64encode(audio_data2).decode()}"
        
        verification_data2 = {
            "user_id": user_id,
            "audio": audio_b64_2
        }
        
        response = requests.post(f"{base_url}/voice/verify", json=verification_data2)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Second test response:")
            print(f"   Authenticated: {result.get('authenticated')}")
            print(f"   Confidence: {result.get('confidence', 0):.3f}")
        else:
            print(f"❌ Second test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error during second test: {e}")
    
    print(f"\n🎯 Test completed!")

if __name__ == "__main__":
    test_voice_auth_with_real_audio() 