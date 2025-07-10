"""
Simple Voice Authentication Test
"""

import requests
import json
import os

def test_voice_auth():
    """Test voice authentication with existing user"""
    
    base_url = "http://127.0.0.1:5001"
    user_id = "12"
    
    print("🔍 Testing Voice Authentication")
    print("=" * 40)
    
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
    
    # 2. Test voice verification with dummy data
    print(f"\n🎤 Testing voice verification...")
    
    # Create dummy audio data
    dummy_audio = b"dummy_audio_data_for_testing" * 100
    audio_b64 = f"data:audio/wav;base64,{dummy_audio.hex()}"
    
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
        else:
            print(f"❌ Voice verification failed:")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error during verification: {e}")
    
    # 3. Test password login
    print(f"\n🔑 Testing password login...")
    
    # Try to find password in users.json
    users_file = "users.json"
    if os.path.exists(users_file):
        with open(users_file, 'r') as f:
            users = json.load(f)
        
        if user_id in users:
            print(f"✅ User {user_id} exists in users.json")
            
            # Try login with a common password
            login_data = {
                "user_id": user_id,
                "password": "password"  # Try common password
            }
            
            try:
                response = requests.post(f"{base_url}/auth/login", json=login_data)
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Password login successful:")
                    print(f"   Authenticated: {result.get('authenticated')}")
                    print(f"   Message: {result.get('message')}")
                else:
                    print(f"❌ Password login failed: {response.json()}")
            except Exception as e:
                print(f"❌ Error during password login: {e}")
        else:
            print(f"ℹ️  User {user_id} not found in users.json")
    else:
        print(f"ℹ️  users.json not found")
    
    print(f"\n🎯 Test completed!")

if __name__ == "__main__":
    test_voice_auth() 