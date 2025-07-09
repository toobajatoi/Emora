console.log("App JS loaded!");
/*
Created by Tooba Jatoi
Copyright © 2025 Tooba Jatoi. All rights reserved.
*/

// Theme management
let currentTheme = localStorage.getItem('theme') || 'light';

// Theme functions
function initializeTheme() {
    console.log('Initializing theme...');
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    
    console.log('Theme toggle element:', themeToggle);
    console.log('Theme icon element:', themeIcon);
    
    // Set initial theme
    setTheme(currentTheme);
    
    // Add event listener for theme toggle
    if (themeToggle) {
        // Remove any existing listeners
        themeToggle.removeEventListener('click', themeToggleClickHandler);
        
        // Add new listener
        themeToggle.addEventListener('click', themeToggleClickHandler);
        console.log('Theme toggle event listener added');
    } else {
        console.error('Theme toggle button not found!');
    }
}

// Theme toggle click handler
function themeToggleClickHandler(e) {
    e.preventDefault();
    e.stopPropagation();
    console.log('Theme toggle clicked! Current theme:', currentTheme);
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    console.log('New theme:', currentTheme);
    setTheme(currentTheme);
    localStorage.setItem('theme', currentTheme);
}

function setTheme(theme) {
    console.log('Setting theme to:', theme);
    const themeIcon = document.getElementById('themeIcon');
    
    if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        if (themeIcon) {
            themeIcon.textContent = '☀️';
            themeIcon.setAttribute('aria-label', 'Switch to light mode');
        }
        console.log('Dark theme applied');
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        if (themeIcon) {
            themeIcon.textContent = '🌙';
            themeIcon.setAttribute('aria-label', 'Switch to dark mode');
        }
        console.log('Light theme applied');
    }
}

// Initialize WebSocket connection
const socket = io();

// Audio recording variables
let isRecording = false;
let audioContext;
let analyser;
let dataArray;
let animationFrame;
let recordingStartTime;
let recordingDuration = 0;
let mediaRecorder;
let audioChunks = [];
let audioStream;

// DOM elements
const startBtn = document.getElementById('startRecording');
const stopBtn = document.getElementById('stopRecording');
const statusDiv = document.getElementById('recordingStatus');
const results = document.getElementById('results');
const loading = document.getElementById('loading');
const journalSubmitBtn = document.getElementById('journalSubmit');
const journalText = document.getElementById('journalText');

// Initialize audio context and analyzer
async function initAudio() {
    try {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            showNotification('Microphone access is not supported in this browser. Please use HTTPS or localhost.', 'error');
            return false;
        }
        
        // Request microphone access
        audioStream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
                sampleRate: 44100
            } 
        });
        
        // Create audio context
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        const source = audioContext.createMediaStreamSource(audioStream);
        source.connect(analyser);
        
        analyser.fftSize = 256;
        const bufferLength = analyser.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);
        
        // Setup media recorder with proper MIME type
        const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') 
            ? 'audio/webm;codecs=opus' 
            : 'audio/webm';
        
        mediaRecorder = new MediaRecorder(audioStream, { mimeType });
        setupMediaRecorder();
        
        showNotification('Microphone ready! Click "Start Recording" to begin.', 'success');
        return true;
    } catch (err) {
        console.error('Error accessing microphone:', err);
        showNotification('Error accessing microphone. Please check permissions and try again.', 'error');
        return false;
    }
}

// Show notification
function showNotification(message, type = 'info') {
    if (type === 'error') hideLoading(); // Hide loading on error
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => notification.classList.add('show'), 100);
    
    // Remove after 4 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// Setup media recorder event handlers
function setupMediaRecorder() {
    mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
        audioChunks.push(event.data);
        }
    };

    mediaRecorder.onstop = async () => {
        try {
            if (audioChunks.length === 0) {
                showNotification('No audio recorded. Please try again.', 'error');
                return;
            }
            
            const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType });
        const reader = new FileReader();
            
        reader.onloadend = () => {
                const base64Audio = reader.result.split(',')[1]; // Remove data URL prefix
                submitAudioJournal(base64Audio);
        };
            
            reader.readAsDataURL(audioBlob);
        audioChunks = [];
        } catch (error) {
            console.error('Error processing audio:', error);
            showNotification('Error processing audio. Please try again.', 'error');
        }
    };
    
    mediaRecorder.onerror = (event) => {
        console.error('MediaRecorder error:', event);
        showNotification('Recording error. Please try again.', 'error');
    };
}

// Handle WebSocket events
socket.on('analysis_result', (data) => {
    console.log('Received analysis result:', data);
    hideLoading();
    showResults(data);
});

socket.on('error', (data) => {
    console.error('Socket error:', data);
    hideLoading();
    showNotification(`Error: ${data.message}`, 'error');
});

// Audio recording logic
let spectrogramCanvas = document.getElementById('spectrogram');
let spectrogramCtx = spectrogramCanvas ? spectrogramCanvas.getContext('2d') : null;
let spectrogramAnimationId;

function resizeSpectrogramCanvas() {
    if (!spectrogramCanvas) return;
    const rect = spectrogramCanvas.getBoundingClientRect();
    spectrogramCanvas.width = rect.width;
    spectrogramCanvas.height = rect.height;
}

window.addEventListener('resize', resizeSpectrogramCanvas);

function drawSpectrogram() {
    if (!analyser || !spectrogramCanvas || !spectrogramCtx) return;
    
    const width = spectrogramCanvas.width;
    const height = spectrogramCanvas.height;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyser.getByteFrequencyData(dataArray);

    // Clear canvas with gradient background
    const gradient = spectrogramCtx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, 'rgba(102, 126, 234, 0.1)');
    gradient.addColorStop(1, 'rgba(118, 75, 162, 0.1)');
    spectrogramCtx.fillStyle = gradient;
    spectrogramCtx.fillRect(0, 0, width, height);

    // Draw grid lines
    spectrogramCtx.strokeStyle = 'rgba(102, 126, 234, 0.1)';
    spectrogramCtx.lineWidth = 0.5;
    
    // Horizontal grid lines
    for (let i = 1; i < 4; i++) {
        const y = (height / 4) * i;
        spectrogramCtx.beginPath();
        spectrogramCtx.moveTo(0, y);
        spectrogramCtx.lineTo(width, y);
        spectrogramCtx.stroke();
    }
    
    // Center line (stronger)
    spectrogramCtx.strokeStyle = 'rgba(102, 126, 234, 0.3)';
    spectrogramCtx.lineWidth = 1;
    spectrogramCtx.beginPath();
    spectrogramCtx.moveTo(0, height / 2);
    spectrogramCtx.lineTo(width, height / 2);
    spectrogramCtx.stroke();

    // Draw frequency bars (waveform style)
    const barWidth = Math.max(1, width / bufferLength);
    const centerY = height / 2;
    const time = Date.now() * 0.001; // For subtle animation
    
    for (let i = 0; i < bufferLength; i++) {
        const value = dataArray[i];
        const intensity = value / 255;
        
        // Add subtle animation based on time and position
        const animationOffset = Math.sin(time * 2 + i * 0.1) * 0.1;
        const animatedIntensity = Math.max(0, intensity + animationOffset);
        
        // Calculate bar height based on frequency
        const barHeight = animatedIntensity * (height / 2) * 0.8;
        
        // Create gradient for each bar
        const barGradient = spectrogramCtx.createLinearGradient(0, centerY - barHeight, 0, centerY + barHeight);
        barGradient.addColorStop(0, `rgba(102, 126, 234, ${0.3 + animatedIntensity * 0.7})`);
        barGradient.addColorStop(0.5, `rgba(118, 75, 162, ${0.5 + animatedIntensity * 0.5})`);
        barGradient.addColorStop(1, `rgba(102, 126, 234, ${0.3 + animatedIntensity * 0.7})`);
        
        spectrogramCtx.fillStyle = barGradient;
        
        // Draw top bar with rounded corners effect
        const x = i * barWidth;
        const topY = centerY - barHeight;
        
        // Draw top bar
        spectrogramCtx.fillRect(x, topY, barWidth - 1, barHeight);
        
        // Draw bottom bar (mirror)
        spectrogramCtx.fillRect(x, centerY, barWidth - 1, barHeight);
        
        // Add subtle highlight at the top of each bar
        if (barHeight > 5) {
            const highlightGradient = spectrogramCtx.createLinearGradient(0, topY, 0, topY + 3);
            highlightGradient.addColorStop(0, `rgba(255, 255, 255, ${0.3 * animatedIntensity})`);
            highlightGradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
            spectrogramCtx.fillStyle = highlightGradient;
            spectrogramCtx.fillRect(x, topY, barWidth - 1, 3);
        }
    }
    
    // Add subtle glow effect
    spectrogramCtx.shadowColor = 'rgba(102, 126, 234, 0.3)';
    spectrogramCtx.shadowBlur = 10;
    spectrogramCtx.shadowOffsetX = 0;
    spectrogramCtx.shadowOffsetY = 0;
    
    spectrogramAnimationId = requestAnimationFrame(drawSpectrogram);
}

function startSpectrogram() {
    if (spectrogramCanvas) {
        spectrogramCanvas.classList.add('active');
        resizeSpectrogramCanvas();
        drawSpectrogram();
    }
}

function stopSpectrogram() {
    if (spectrogramCanvas) {
        spectrogramCanvas.classList.remove('active');
        if (spectrogramAnimationId) {
            cancelAnimationFrame(spectrogramAnimationId);
        }
        if (spectrogramCtx) {
            spectrogramCtx.clearRect(0, 0, spectrogramCanvas.width, spectrogramCanvas.height);
        }
    }
}

// Recording button handlers
if (startBtn && stopBtn) {
    startBtn.onclick = async function() {
        try {
            if (!mediaRecorder) {
                const success = await initAudio();
                if (!success) return;
            }
            
            if (mediaRecorder.state === 'recording') return;
            
        audioChunks = [];
            mediaRecorder.start(100); // Collect data every 100ms
            
        startBtn.style.display = 'none';
            stopBtn.style.display = 'inline-flex';
            statusDiv.innerHTML = '<div class="recording-indicator"></div>Recording... Click stop when done.';
            statusDiv.style.color = '#e53e3e';
            startSpectrogram();
            
            showNotification('Recording started! Speak clearly into your microphone.', 'info');
        } catch (err) {
            console.error('Error starting recording:', err);
            showNotification('Error starting recording. Please check microphone permissions.', 'error');
        }
    };
    
    stopBtn.onclick = function() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
            statusDiv.textContent = 'Processing audio...';
            statusDiv.style.color = '#38a169';
            startBtn.style.display = 'inline-flex';
        stopBtn.style.display = 'none';
            stopSpectrogram();
            showNotification('Processing your audio...', 'info');
        }
    };
}

// Show loading state
function showLoading() {
    if (loading) loading.classList.remove('hidden');
    if (results) results.classList.add('hidden');
}

function hideLoading() {
    // Hide all elements with id 'loading'
    document.querySelectorAll('#loading').forEach(el => el.classList.add('hidden'));
    // Hide all elements with class 'loading'
    document.querySelectorAll('.loading').forEach(el => el.classList.add('hidden'));
}

// Show results
function showResults(data) {
    hideLoading(); // Always hide loading before showing results
    if (results) results.classList.remove('hidden');
    
    // Update mood, emoji, and message
    const moodEmoji = document.getElementById('moodEmoji');
    const moodLabel = document.getElementById('moodLabel');
    const moodMessage = document.getElementById('moodMessage');
    const journalSummary = document.getElementById('journalSummary');
    const journalTranscription = document.getElementById('journalTranscription');
    
    if (moodEmoji) moodEmoji.textContent = data.emoji || '😊';
    if (moodLabel) moodLabel.textContent = (data.mood || 'neutral').charAt(0).toUpperCase() + (data.mood || 'neutral').slice(1);
    if (moodMessage) moodMessage.textContent = data.message || 'Thank you for sharing your thoughts.';
    if (journalSummary) journalSummary.textContent = data.summary || 'Your journal entry has been analyzed.';
    if (journalTranscription) journalTranscription.textContent = data.transcription || 'No transcription available.';

    // Animate feature values
    const features = ['pitch', 'energy', 'zero_crossing_rate', 'spectral_centroid'];
    features.forEach(feature => {
        const element = document.getElementById(`${feature}Value`);
        if (element && data.features && data.features[feature] !== undefined) {
            const targetValue = data.features[feature] || 0;
            animateValue(element, 0, targetValue, 1000);
        }
    });
    
    // Store entry in localStorage
    saveJournalEntry({
        date: new Date().toLocaleString(),
        mood: data.mood || 'neutral',
        emoji: data.emoji || '😊',
        summary: data.summary || '',
        message: data.message || '',
        transcription: data.transcription || '',
        features: data.features || {}
    });
    
    loadJournalHistory();
    
    // Clear form
    if (journalText) journalText.value = '';
}

// Animate numeric values
function animateValue(element, start, end, duration) {
    const startTime = performance.now();
    const difference = end - start;
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = start + (difference * progress);
        element.textContent = current.toFixed(2);
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// Store journal entry in localStorage
function saveJournalEntry(entry) {
    let entries = JSON.parse(localStorage.getItem('journalEntries') || '[]');
    entries.unshift(entry);
    localStorage.setItem('journalEntries', JSON.stringify(entries));
}

// Load and display journal history
function loadJournalHistory() {
    const container = document.getElementById('journalHistory');
    if (!container) return;
    
    let entries = JSON.parse(localStorage.getItem('journalEntries') || '[]');
    
    if (entries.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📝</div>
                <p>No journal entries yet</p>
                <p>Start by writing or recording your first entry!</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = entries.map((entry, idx) => `
        <div class="journal-entry" onclick="openJournalModal(${idx})">
            <div class="journal-entry-header">
                <div class="journal-entry-info">
                    <span class="journal-entry-emoji">${entry.emoji || '📝'}</span>
                    <span class="journal-entry-mood">${entry.mood ? entry.mood.charAt(0).toUpperCase() + entry.mood.slice(1) : 'Unknown'}</span>
                </div>
                <div class="journal-entry-date">${entry.date || ''}</div>
                <button class="btn btn-danger btn-small delete-entry-btn" onclick="event.stopPropagation(); deleteJournalEntry(${idx});" aria-label="Delete this journal entry">🗑️</button>
            </div>
            <div class="journal-entry-content">
                <div class="journal-entry-message">${entry.message || ''}</div>
                <div class="journal-entry-summary">${entry.summary || ''}</div>
            </div>
            </div>
        `).join('');
}

// Modal functions
window.openJournalModal = function(idx) {
    let entries = JSON.parse(localStorage.getItem('journalEntries') || '[]');
    const entry = entries[idx];
    if (!entry) return;
    
    const modal = document.getElementById('journalModal');
    const modalDate = document.getElementById('modalDate');
    const modalEmoji = document.getElementById('modalEmoji');
    const modalMood = document.getElementById('modalMood');
    const modalMessage = document.getElementById('modalMessage');
    const modalSummary = document.getElementById('modalSummary');
    const modalTranscription = document.getElementById('modalTranscription');
    const modalFeatures = document.getElementById('modalFeatures');
    
    if (modalDate) modalDate.textContent = entry.date || '';
    if (modalEmoji) modalEmoji.textContent = entry.emoji || '📝';
    if (modalMood) modalMood.textContent = entry.mood ? entry.mood.charAt(0).toUpperCase() + entry.mood.slice(1) : 'Unknown';
    if (modalMessage) modalMessage.textContent = entry.message || '';
    if (modalSummary) modalSummary.textContent = entry.summary || '';
    if (modalTranscription) modalTranscription.textContent = entry.transcription || '';
    
    // Features
    if (modalFeatures && entry.features) {
        const featuresText = Object.entries(entry.features)
            .map(([key, value]) => {
                let num = Number(value);
                return `${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}: ${isFinite(num) ? num.toFixed(2) : '0.00'}`;
            })
            .join(', ');
        modalFeatures.textContent = featuresText;
    } else if (modalFeatures) {
        modalFeatures.textContent = '';
    }

    // Add navigation buttons
    let navContainer = document.getElementById('modalNav');
    if (!navContainer) {
        navContainer = document.createElement('div');
        navContainer.id = 'modalNav';
        navContainer.style.display = 'flex';
        navContainer.style.justifyContent = 'space-between';
        navContainer.style.marginTop = '2rem';
        modal.querySelector('.modal-content').appendChild(navContainer);
    }
    navContainer.innerHTML = `
        <button class="btn btn-secondary btn-small" id="prevJournalBtn" ${idx === entries.length - 1 ? 'disabled' : ''}>&larr; Previous</button>
        <button class="btn btn-secondary btn-small" id="nextJournalBtn" ${idx === 0 ? 'disabled' : ''}>Next &rarr;</button>
    `;
    document.getElementById('prevJournalBtn').onclick = function(e) {
        e.stopPropagation();
        if (idx < entries.length - 1) window.openJournalModal(idx + 1);
    };
    document.getElementById('nextJournalBtn').onclick = function(e) {
        e.stopPropagation();
        if (idx > 0) window.openJournalModal(idx - 1);
    };

    modal.classList.add('active');
}

window.closeJournalModal = function() {
    document.getElementById('journalModal').classList.remove('active');
}

// Delete journal entry
function deleteJournalEntry(idx) {
    let entries = JSON.parse(localStorage.getItem('journalEntries') || '[]');
    entries.splice(idx, 1);
    localStorage.setItem('journalEntries', JSON.stringify(entries));
    loadJournalHistory();
}

// Journal submit handler
function submitJournal() {
    const text = journalText ? journalText.value.trim() : '';
    if (!text) {
        showNotification('Please write about your day or record your voice.', 'error');
        return;
    }
    
    showLoading();
    
    fetch('/journal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
    })
    .then(res => {
        if (!res.ok) throw new Error('Network response was not ok');
        return res.json();
    })
    .then(data => showResults(data))
    .catch(error => {
        console.error('Error:', error);
        hideLoading();
        showNotification('Error analyzing your journal. Please try again.', 'error');
    });
}

// Send audio to server
function submitAudioJournal(audioB64) {
    showLoading();
    let textValue = "";
    if (typeof journalText !== "undefined" && journalText && typeof journalText.value === "string") {
        textValue = journalText.value.trim();
    }
    fetch("/journal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            text: textValue, // Always a string
            audio: "data:audio/webm;base64," + audioB64
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.error) {
            showNotification(data.error, "error");
        } else {
            showResults(data);
            saveJournalEntry(data);
        }
    })
    .catch(error => {
        hideLoading();
        showNotification("Error analyzing your audio. Please try again.", "error");
        console.error("Error:", error);
    });
}

// Attach submit handler to button
if (journalSubmitBtn) {
    journalSubmitBtn.onclick = submitJournal;
}

// Initialize when page loads
window.onload = function() {
    console.log('Page loaded, initializing...');
    initializeTheme();
    initAudio();
    loadJournalHistory();
    
    // Hide results initially
    if (results) results.classList.add('hidden');
    if (loading) loading.classList.add('hidden');
};

// Also initialize theme when DOM is ready (fallback)
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');
    // Apply theme immediately
    setTheme(currentTheme);
    
    // Try to initialize theme again if not already done
    setTimeout(() => {
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle && !themeToggle.hasAttribute('data-initialized')) {
            console.log('Re-initializing theme...');
            initializeTheme();
            themeToggle.setAttribute('data-initialized', 'true');
        }
    }, 100);
}); 