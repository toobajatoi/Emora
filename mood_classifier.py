"""
Created by Tooba Jatoi
Copyright © 2025 Tooba Jatoi. All rights reserved.
"""

from transformers import pipeline

# Load a sentiment analysis pipeline once
_sentiment_pipe = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    device=-1
)

# Simple rules for mood detection from audio features

def detect_mood(text: str, features: dict) -> dict:
    """
    Returns a dict with 'mood' and 'message'.
    Mood is one of: angry, sad, happy, neutral, surprised, anxious, excited, etc.
    """
    if not text:
        return {"mood": "neutral", "emoji": "😐", "message": "We couldn't detect your mood. Try speaking again!"}

    # Text-based sentiment
    sentiment = _sentiment_pipe(text, top_k=1)[0]
    sentiment_label = sentiment.get("label", "neutral").lower()
    sentiment_score = sentiment.get("score", 0.5)

    # Audio feature heuristics
    pitch = features.get("pitch", 0.0)
    energy = features.get("energy", 1.0)
    zcr = features.get("zero_crossing_rate", 0.0)
    spectral_centroid = features.get("spectral_centroid", 0.0)

    # Enhanced mood detection with more nuanced analysis
    if sentiment_label == "negative":
        if energy < 0.04 and pitch < 150:
            mood = "sad"
            emoji = "😢"
            message = "I can hear the heaviness in your voice. It's completely normal to feel sad sometimes. Remember, emotions are like waves - they come and go. Be gentle with yourself today."
        elif energy < 0.04 and pitch > 150:
            mood = "melancholy"
            emoji = "😔"
            message = "There's a thoughtful sadness in your tone. Sometimes the most beautiful insights come from these reflective moments. Honor your feelings."
        elif pitch > 200 or zcr > 0.1:
            mood = "angry"
            emoji = "😠"
            message = "I can sense the frustration in your voice. Anger is a valid emotion that often protects us. Try taking a few deep breaths - in for 4, hold for 4, out for 6."
        elif energy > 0.08 and spectral_centroid > 2000:
            mood = "frustrated"
            emoji = "😤"
            message = "You sound frustrated, and that's completely understandable. Sometimes things don't go as planned. What would help you feel better right now?"
        else:
            mood = "upset"
            emoji = "😕"
            message = "I can hear that something's troubling you. Talking about our feelings is one of the bravest things we can do. You're not alone in this."
    elif sentiment_label == "positive":
        if energy > 0.1 and pitch > 180:
            mood = "happy"
            emoji = "😊"
            message = "Your joy is absolutely contagious! I can hear the genuine happiness in your voice. These moments of pure joy are precious - savor them!"
        elif energy > 0.08 and pitch > 160:
            mood = "excited"
            emoji = "🤩"
            message = "You sound so excited! That enthusiasm is wonderful. When we're passionate about something, it shows in every word we speak."
        elif energy < 0.06 and pitch < 180:
            mood = "calm"
            emoji = "🙂"
            message = "There's such a peaceful quality to your voice. You sound centered and grounded. This inner calm is a beautiful state to be in."
        else:
            mood = "content"
            emoji = "😌"
            message = "You sound content and at ease. There's a lovely balance in your tone - not too high, not too low. This is the sound of someone who's doing okay."
    else:
        # Analyze for more subtle emotions
        if energy < 0.03:
            mood = "tired"
            emoji = "😴"
            message = "You sound a bit tired. Sometimes our voice reveals our energy levels before we even realize it. Consider giving yourself permission to rest."
        elif spectral_centroid > 2500 and zcr > 0.08:
            mood = "anxious"
            emoji = "😰"
            message = "I notice some tension in your voice. Anxiety can manifest in subtle ways. Remember, it's okay to feel anxious - it's your body's way of trying to protect you."
        elif pitch > 190 and energy > 0.05:
            mood = "curious"
            emoji = "🤔"
            message = "There's an inquisitive quality to your voice. Curiosity is such a beautiful trait - it keeps us learning and growing."
        else:
            mood = "neutral"
            emoji = "😐"
            message = "You sound balanced and neutral today. Sometimes being in the middle is exactly where we need to be. How are you really feeling beneath the surface?"

    return {"mood": mood, "emoji": emoji, "message": message} 