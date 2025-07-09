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
    Mood is one of: angry, sad, happy, neutral, surprised, etc.
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

    # Mood logic
    if sentiment_label == "negative":
        if energy < 0.04:
            mood = "sad"
            emoji = "😢"
            message = "You sound sad. Remember, it's okay to feel down sometimes. Take care of yourself!"
        elif pitch > 200 or zcr > 0.1:
            mood = "angry"
            emoji = "😠"
            message = "You sound angry. Take a deep breath and try to relax."
        else:
            mood = "upset"
            emoji = "😕"
            message = "You sound upset. Try to talk to someone you trust."
    elif sentiment_label == "positive":
        if energy > 0.1 and pitch > 180:
            mood = "happy"
            emoji = "😊"
            message = "You sound happy! Keep spreading positivity."
        else:
            mood = "calm"
            emoji = "🙂"
            message = "You sound calm and relaxed."
    else:
        mood = "neutral"
        emoji = "😐"
        message = "You sound neutral. Hope you're having a good day!"

    return {"mood": mood, "emoji": emoji, "message": message} 