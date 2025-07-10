"""
Test Voice Authentication
Created by Tooba Jatoi
"""

import requests
import base64
import json
import os

def test_voice_authentication():
    """Test the voice authentication system"""
    
    # Server URL
    base_url = "http://127.0.0.1:5001"
    
    # Test user (use existing profile)
    user_id = "12"
    
    print("🧪 Testing Voice Authentication System")
    print("=" * 50)
    
    # 1. Check if server is running
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Server is running (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Server is not running: {e}")
        return
    
    # 2. Check existing voice profiles
    print(f"\n📋 Checking existing voice profiles...")
    try:
        response = requests.get(f"{base_url}/voice/debug/{user_id}")
        if response.status_code == 200:
            profile_data = response.json()
            print(f"✅ Found existing profile for {user_id}")
            print(f"   Features: {profile_data['feature_count']}")
            print(f"   Feature names: {profile_data['feature_names']}")
            print(f"   Threshold: {profile_data['similarity_threshold']}")
        else:
            print(f"ℹ️  No existing profile for {user_id}")
    except Exception as e:
        print(f"❌ Error checking profile: {e}")
    
    # 3. Test voice enrollment (skip for existing user)
    print(f"\n🎤 Testing voice enrollment...")
    print(f"ℹ️  Skipping enrollment for existing user {user_id}")
    
    # Create a dummy audio file for testing verification
    dummy_audio = b"dummy_audio_data_for_testing" * 100  # Create some dummy data
    audio_b64 = f"data:audio/wav;base64,{base64.b64encode(dummy_audio).decode()}"
    
    # 4. Test voice verification
    print(f"\n🔍 Testing voice verification...")
    
    verification_data = {
        "user_id": user_id,
        "audio": audio_b64
    }
    
    try:
        response = requests.post(f"{base_url}/voice/verify", json=verification_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Voice verification completed")
            print(f"   Authenticated: {result['authenticated']}")
            print(f"   Confidence: {result['confidence']:.3f}")
            print(f"   Message: {result['message']}")
        else:
            print(f"❌ Voice verification failed: {response.json()}")
    except Exception as e:
        print(f"❌ Error during verification: {e}")
    
    # 5. Test password registration
    print(f"\n🔐 Testing password registration...")
    
    password_data = {
        "user_id": user_id,
        "password": "test_password_123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/register", json=password_data)
        if response.status_code == 200:
            print(f"✅ Password registration successful")
        else:
            print(f"ℹ️  Password registration: {response.json()}")
    except Exception as e:
        print(f"❌ Error during password registration: {e}")
    
    # 6. Test password login
    print(f"\n🔑 Testing password login...")
    
    login_data = {
        "user_id": user_id,
        "password": "test_password_123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Password login successful")
            print(f"   Authenticated: {result['authenticated']}")
            print(f"   Message: {result['message']}")
        else:
            print(f"❌ Password login failed: {response.json()}")
    except Exception as e:
        print(f"❌ Error during password login: {e}")
    
    print(f"\n🎯 Test completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_voice_authentication() 