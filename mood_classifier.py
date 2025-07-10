"""
Voice Journal Mood Classifier
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

def detect_mood(text: str, features: dict) -> dict:
    """
    Returns a dict with 'mood', 'emoji', and 'message'.
    Provides detailed, motivational responses for voice journaling.
    """
    if not text:
        return {
            "mood": "neutral", 
            "emoji": "😐", 
            "message": "I couldn't hear your voice clearly. Please try speaking again, and remember - your voice matters, and your feelings are valid. Take a deep breath and share what's on your mind."
        }

    # Text-based sentiment
    sentiment = _sentiment_pipe(text, top_k=1)[0]
    sentiment_label = sentiment.get("label", "neutral").lower()
    sentiment_score = sentiment.get("score", 0.5)

    # Audio feature heuristics
    pitch = features.get("pitch", 0.0)
    energy = features.get("energy", 1.0)
    zcr = features.get("zero_crossing_rate", 0.0)
    spectral_centroid = features.get("spectral_centroid", 0.0)

    # Enhanced mood detection with detailed motivational responses
    if sentiment_label == "negative":
        if energy < 0.04 and pitch < 150:
            mood = "sad"
            emoji = "😢"
            message = """I can hear the heaviness in your voice, and I want you to know that it's completely okay to feel this way. Sadness is a natural part of being human, and it doesn't make you weak or broken. 

Remember that emotions are like waves - they come and go. This feeling won't last forever, even though it might feel overwhelming right now. 

Consider doing something kind for yourself today - maybe a warm bath, listening to your favorite music, or reaching out to someone who cares about you. Sometimes the bravest thing we can do is simply acknowledge our feelings without trying to fix them immediately.

You're not alone in this, and your feelings are valid. Be gentle with yourself today."""
            
        elif energy < 0.04 and pitch > 150:
            mood = "melancholy"
            emoji = "😔"
            message = """There's a thoughtful, reflective quality to your voice that speaks to your depth and sensitivity. This contemplative sadness you're experiencing might actually be preparing you for something meaningful.

Sometimes the most beautiful insights and growth come from these quieter, more reflective moments. Your ability to sit with these feelings shows emotional maturity and wisdom.

Consider what this melancholy might be trying to teach you. Perhaps it's a sign that you need to slow down, reflect, or make some changes in your life. Trust that this feeling has purpose and meaning.

Honor this space you're in - it's part of your journey, and it's making you stronger and more compassionate."""
            
        elif pitch > 200 or zcr > 0.1:
            mood = "angry"
            emoji = "😠"
            message = """I can sense the intensity of your emotions, and I want you to know that your anger is completely valid. Anger often serves as a protective emotion - it's your mind's way of saying that something isn't right or that you deserve better.

Your anger is telling you something important. It might be signaling that boundaries need to be set, that something needs to change, or that you're feeling hurt or disappointed.

Try taking a few deep breaths - inhale for 4 counts, hold for 4, exhale for 6. This can help you find some space to process what's beneath the anger.

Remember that anger can be a powerful force for positive transformation when we learn to channel it constructively. What might your anger be trying to protect you from or motivate you toward?"""
            
        elif energy > 0.08 and spectral_centroid > 2000:
            mood = "frustrated"
            emoji = "😤"
            message = """I can hear your frustration, and it's completely understandable. When things don't go as planned or when we feel stuck, frustration is a natural response. It shows that you care deeply about the outcome.

Your frustration is actually a sign of your commitment and standards - that's not a bad thing! The challenge is finding constructive ways to channel that energy.

Consider what's within your control and what might need a different approach. Sometimes the most productive thing we can do is step back, reassess our strategy, or ask for help.

What would help you feel better right now? Maybe taking a short break, talking to someone, or trying a different approach to whatever is frustrating you?"""
            
        else:
            mood = "upset"
            emoji = "😕"
            message = """I can hear that something has deeply affected you, and I want you to know that it's okay to not be okay right now. Being upset shows that you're engaged with life and that things matter to you.

Sometimes the bravest thing we can do is simply acknowledge our feelings without trying to fix them immediately. You don't have to have all the answers right now.

Consider what support you might need - whether that's talking to a friend, taking some time for yourself, or seeking professional help. You don't have to carry this alone.

Remember that this discomfort you're feeling might be temporary, but it's also real and valid. Be patient with yourself as you work through these feelings."""
            
    elif sentiment_label == "positive":
        if energy > 0.1 and pitch > 180:
            mood = "happy"
            emoji = "😊"
            message = """Your joy is absolutely radiant and contagious! I can hear the genuine happiness in your voice, and it's wonderful to witness. These moments of pure contentment are precious and worth celebrating.

Your happiness shows in every word you speak - there's a lightness and warmth that's truly beautiful. Consider what made this possible and how you might create more of these moments in your life.

These good feelings are well-deserved, and you should enjoy every moment of them. Happiness like this often comes from being aligned with what matters most to you.

Keep spreading that positive energy - it's making the world a better place!"""
            
        elif energy > 0.08 and pitch > 160:
            mood = "excited"
            emoji = "🤩"
            message = """Your enthusiasm is absolutely infectious! That spark of excitement you're feeling is precious - it's your passion and energy coming through in every word.

When we're excited about something, it often means we're on the right path or that we've found something that truly matters to us. This kind of genuine enthusiasm is rare and valuable.

Your excitement shows that you're engaged with life and open to possibilities. This feeling often leads to our most creative and productive moments.

Keep that energy flowing! Your excitement is a beautiful thing, and it's inspiring to hear someone so genuinely passionate about what they're experiencing."""
            
        elif energy < 0.06 and pitch < 180:
            mood = "calm"
            emoji = "🙂"
            message = """There's such a peaceful, centered quality to your voice. You sound grounded and at ease, which is a beautiful state to be in. This inner calm you're experiencing is precious and worth protecting.

This peaceful state allows for deeper reflection, clearer thinking, and more meaningful connections with others. It's often when we're most open to insights and new perspectives.

Your calmness is truly grounding and speaks to your inner strength and emotional maturity. This balanced state is the foundation for wisdom and authentic connection.

Cherish this centered feeling - it's a sign that you're doing well and that you've found a good balance in your life."""
            
        else:
            mood = "content"
            emoji = "😌"
            message = """You sound genuinely content and at ease with yourself and your circumstances. There's a lovely sense of satisfaction in your tone that's so refreshing to hear.

Contentment is such an underrated emotion - it's the quiet joy of being okay with yourself and your life as it is. This balanced state is often the foundation for lasting happiness.

Your contentment shows that you've found a good place in your life, even if everything isn't perfect. It's a sign of emotional maturity and self-acceptance.

This feeling of being at ease with yourself and your life is precious. Contentment often comes from accepting what is while still being open to growth and new experiences."""
            
    else:
        # Analyze for more subtle emotions
        if energy < 0.03:
            mood = "tired"
            emoji = "😴"
            message = """You sound a bit tired, and that's completely understandable. Sometimes our voice reveals our energy levels before we even realize it ourselves.

Being tired doesn't mean you're not doing enough - it might actually mean you've been doing too much. Your body and mind are telling you they need rest.

Consider what kind of rest would be most restorative for you right now. Maybe it's a good night's sleep, a short nap, or simply taking some time to do nothing.

Give yourself permission to rest. Sometimes the most productive thing we can do is take care of ourselves and recharge our energy."""
            
        elif spectral_centroid > 2500 and zcr > 0.08:
            mood = "anxious"
            emoji = "😰"
            message = """I notice some tension in your voice, and I want you to know that anxiety is a normal human experience. Your body is trying to protect you, even if it feels overwhelming right now.

Anxiety often comes from caring deeply about things and wanting to do well. It's your mind's way of trying to keep you safe, even though it might feel uncomfortable.

Try to acknowledge the feeling without fighting it. Sometimes the most helpful thing is to simply notice the anxiety and remind yourself that it's temporary.

Consider what might help you feel more grounded right now - deep breathing, talking to someone you trust, or doing something that helps you feel more present and connected."""
            
        elif pitch > 190 and energy > 0.05:
            mood = "curious"
            emoji = "🤔"
            message = """There's an inquisitive, engaged quality to your voice that's wonderful to hear. Your curiosity is such a beautiful trait - it keeps you learning, growing, and engaged with life.

Curiosity often leads to our most interesting discoveries and connections. That sense of wonder you're feeling is precious and should be nurtured.

Your curiosity shows an active, engaged mind that's open to new possibilities and experiences. This is often the first step toward discovery and growth.

Keep that inquisitive energy flowing! Curiosity is what keeps life interesting and meaningful, and it's a sign of a healthy, engaged mind."""
            
        else:
            mood = "neutral"
            emoji = "😐"
            message = """You sound balanced and neutral today, and sometimes that's exactly where we need to be. Being neutral isn't boring - it's often a sign of emotional stability and processing.

This neutral state might be a sign that you're in a period of transition or integration. Sometimes we need these balanced moments to process our experiences and prepare for what's next.

Consider what might be beneath the surface of this neutral feeling. Sometimes neutrality is actually a sign of inner peace and acceptance.

This calm center can be a good foundation for whatever comes next in your life. Trust that being neutral is a valid and important emotional state."""

    return {"mood": mood, "emoji": emoji, "message": message} 