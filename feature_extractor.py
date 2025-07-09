"""
Created by Tooba Jatoi
Copyright © 2025 Tooba Jatoi. All rights reserved.
"""

import numpy as np
import librosa
import torch

def extract_features(audio_chunk: np.ndarray, sr: int = 16000) -> dict:
    """Extract pitch and energy from a mono audio chunk."""
    y = audio_chunk.flatten()
    
    # Use smaller frame length and hop length for faster processing
    frame_length = 1024  # Reduced from 2048
    hop_length = 256    # Reduced from 512
    
    # RMS energy with optimized parameters
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)
    energy = float(np.mean(rms))

    # Pitch via piptrack with optimized parameters
    pitches, mags = librosa.piptrack(y=y, sr=sr, hop_length=hop_length, fmin=50, fmax=500)
    pitch_vals = pitches[mags > np.median(mags)]
    pitch = float(np.mean(pitch_vals)) if pitch_vals.size > 0 else 0.0

    # Zero crossing rate with optimized parameters
    zcr = librosa.feature.zero_crossing_rate(y=y, frame_length=frame_length, hop_length=hop_length)
    zero_crossing_rate = float(np.mean(zcr))

    # Spectral centroid with optimized parameters
    cent = librosa.feature.spectral_centroid(y=y, sr=sr, n_fft=frame_length, hop_length=hop_length)
    spectral_centroid = float(np.mean(cent))

    return {
        'pitch': pitch,
        'energy': energy,
        'zero_crossing_rate': zero_crossing_rate,
        'spectral_centroid': spectral_centroid,
        'emotion': 'neutral'  # Default emotion since we're not using SpeechBrain
    } 