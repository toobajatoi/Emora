/*
Login Page JavaScript for Emora
Created by Tooba Jatoi
*/

// Theme management
let currentTheme = localStorage.getItem('theme') || 'light';

// Initialize theme
function initializeTheme() {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    
    setTheme(currentTheme);
    
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            currentTheme = currentTheme === 'light' ? 'dark' : 'light';
            setTheme(currentTheme);
            localStorage.setItem('theme', currentTheme);
        });
    }
}

function setTheme(theme) {
    const themeIcon = document.getElementById('themeIcon');
    
    if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        if (themeIcon) {
            themeIcon.textContent = '☀️';
            themeIcon.setAttribute('aria-label', 'Switch to light mode');
        }
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        if (themeIcon) {
            themeIcon.textContent = '🌙';
            themeIcon.setAttribute('aria-label', 'Switch to dark mode');
        }
    }
}

// Login System
class LoginSystem {
    constructor() {
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.audioStream = null;
        this.audioContext = null;
        this.analyser = null;
        this.dataArray = null;
        this.animationFrame = null;
        
        this.initializeLoginSystem();
    }
    
    async initializeLoginSystem() {
        // Initialize tab switching
        this.initializeTabs();
        
        // Initialize voice recording
        await this.initializeVoiceRecording();
        
        // Initialize event listeners
        this.initializeEventListeners();
        
        // Check if user is already logged in
        this.checkLoginStatus();
    }
    
    initializeTabs() {
        const tabs = document.querySelectorAll('.login-tab');
        const contents = document.querySelectorAll('.login-content');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetTab = tab.getAttribute('data-tab');
                
                // Update active tab
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Update active content
                contents.forEach(content => {
                    content.classList.remove('active');
                    if (content.id === `${targetTab}-tab`) {
                        content.classList.add('active');
                    }
                });
            });
        });
    }
    
    async initializeVoiceRecording() {
        const spectrograms = ['voiceSpectrogram', 'enrollSpectrogram'];
        
        try {
            // Request microphone access
            this.audioStream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    sampleRate: 44100
                } 
            });
            
            // Create audio context
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioContext.createAnalyser();
            const source = this.audioContext.createMediaStreamSource(this.audioStream);
            source.connect(this.analyser);
            
            this.analyser.fftSize = 256;
            const bufferLength = this.analyser.frequencyBinCount;
            this.dataArray = new Uint8Array(bufferLength);
            
            // Setup media recorder
            const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') 
                ? 'audio/webm;codecs=opus' 
                : 'audio/webm';
            
            this.mediaRecorder = new MediaRecorder(this.audioStream, { mimeType });
            this.setupMediaRecorder();
            
            // Setup spectrograms
            spectrograms.forEach(id => {
                const canvas = document.getElementById(id);
                if (canvas) {
                    this.setupSpectrogram(canvas);
                }
            });
            
        } catch (err) {
            console.error('Error accessing microphone:', err);
            this.showNotification('Microphone access denied. Please check permissions.', 'error');
        }
    }
    
    setupMediaRecorder() {
        this.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                this.audioChunks.push(event.data);
            }
        };

        this.mediaRecorder.onstop = async () => {
            try {
                if (this.audioChunks.length === 0) {
                    this.showNotification('No audio recorded. Please try again.', 'error');
                    return;
                }
                
                const audioBlob = new Blob(this.audioChunks, { type: this.mediaRecorder.mimeType });
                
                // Show audio playback for enrollment
                if (this.currentRecordingType === 'enroll') {
                    const audioElement = document.getElementById('enrollRecordedAudio');
                    const playbackDiv = document.getElementById('enrollAudioPlayback');
                    const retakeBtn = document.getElementById('enrollRetakeRecording');
                    
                    if (audioElement && playbackDiv && retakeBtn) {
                        audioElement.src = URL.createObjectURL(audioBlob);
                        playbackDiv.style.display = 'block';
                        retakeBtn.style.display = 'inline-block';
                    }
                }
                
                const reader = new FileReader();
                
                reader.onloadend = () => {
                    const base64Audio = reader.result;
                    this.handleAudioData(base64Audio);
                };
                
                reader.readAsDataURL(audioBlob);
                this.audioChunks = [];
            } catch (error) {
                console.error('Error processing audio:', error);
                this.showNotification('Error processing audio. Please try again.', 'error');
            }
        };
        
        this.mediaRecorder.onerror = (event) => {
            console.error('MediaRecorder error:', event);
            this.showNotification('Recording error. Please try again.', 'error');
        };
    }
    
    setupSpectrogram(canvas) {
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        
        const drawSpectrogram = () => {
            if (!this.analyser || !this.dataArray) return;
            
            this.analyser.getByteFrequencyData(this.dataArray);
            
            ctx.clearRect(0, 0, width, height);
            
            const barWidth = width / this.dataArray.length;
            const barMaxHeight = height / 2;
            
            for (let i = 0; i < this.dataArray.length; i++) {
                const barHeight = (this.dataArray[i] / 255) * barMaxHeight;
                const x = i * barWidth;
                const y = height / 2 - barHeight;
                
                // Create gradient
                const gradient = ctx.createLinearGradient(x, y, x, y + barHeight);
                gradient.addColorStop(0, 'rgba(102, 126, 234, 0.8)');
                gradient.addColorStop(1, 'rgba(118, 75, 162, 0.6)');
                
                ctx.fillStyle = gradient;
                ctx.fillRect(x, y, barWidth - 1, barHeight);
                
                // Mirror effect
                ctx.fillRect(x, height / 2, barWidth - 1, barHeight);
            }
            
            if (this.isRecording) {
                this.animationFrame = requestAnimationFrame(drawSpectrogram);
            }
        };
        
        // Store the draw function for this canvas
        canvas.drawSpectrogram = drawSpectrogram;
    }
    
    startRecording(type = 'voice') {
        if (this.isRecording) return;
        
        this.isRecording = true;
        this.currentRecordingType = type;
        
        const spectrogram = document.getElementById(type === 'voice' ? 'voiceSpectrogram' : 'enrollSpectrogram');
        const startBtn = document.getElementById(type === 'voice' ? 'voiceStartRecording' : 'enrollStartRecording');
        const stopBtn = document.getElementById(type === 'voice' ? 'voiceStopRecording' : 'enrollStopRecording');
        const statusDiv = document.getElementById(type === 'voice' ? 'voiceStatus' : 'enrollStatus');
        
        if (spectrogram) {
            spectrogram.classList.add('active');
            spectrogram.drawSpectrogram();
        }
        
        if (startBtn) startBtn.style.display = 'none';
        if (stopBtn) stopBtn.style.display = 'inline-block';
        if (statusDiv) statusDiv.innerHTML = '<div class="login-status">🎤 Recording... Speak clearly</div>';
        
        this.mediaRecorder.start();
    }
    
    stopRecording() {
        if (!this.isRecording) return;
        
        this.isRecording = false;
        const spectrogram = document.getElementById(this.currentRecordingType === 'voice' ? 'voiceSpectrogram' : 'enrollSpectrogram');
        const startBtn = document.getElementById(this.currentRecordingType === 'voice' ? 'voiceStartRecording' : 'enrollStartRecording');
        const stopBtn = document.getElementById(this.currentRecordingType === 'voice' ? 'voiceStopRecording' : 'enrollStopRecording');
        const statusDiv = document.getElementById(this.currentRecordingType === 'voice' ? 'voiceStatus' : 'enrollStatus');
        
        if (spectrogram) {
            spectrogram.classList.remove('active');
        }
        
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
        
        if (startBtn) startBtn.style.display = 'inline-block';
        if (stopBtn) stopBtn.style.display = 'none';
        if (statusDiv) statusDiv.innerHTML = '<div class="login-status">⏳ Processing...</div>';
        
        this.mediaRecorder.stop();
    }
    
    retakeRecording() {
        // Reset audio playback
        const audioElement = document.getElementById('enrollRecordedAudio');
        const playbackDiv = document.getElementById('enrollAudioPlayback');
        const retakeBtn = document.getElementById('enrollRetakeRecording');
        const submitBtn = document.getElementById('enrollSubmit');
        const statusDiv = document.getElementById('enrollStatus');
        
        if (audioElement) audioElement.src = '';
        if (playbackDiv) playbackDiv.style.display = 'none';
        if (retakeBtn) retakeBtn.style.display = 'none';
        if (submitBtn) submitBtn.disabled = true;
        if (statusDiv) statusDiv.innerHTML = '';
        
        // Reset recording state
        this.audioChunks = [];
        this.currentRecordingType = null;
        
        this.showNotification('Ready to record again. Click "Record Voice" to start.', 'info');
    }
    
    async handleAudioData(audioData) {
        if (this.currentRecordingType === 'voice') {
            await this.verifyVoice(audioData);
        } else if (this.currentRecordingType === 'enroll') {
            await this.enrollVoice(audioData);
        }
    }
    
    async verifyVoice(audioData) {
        let userIdInput = document.getElementById('loginUserId');
        const statusDiv = document.getElementById('loginStatus');
        console.log('DEBUG: userIdInput (loginUserId)', userIdInput);
        // Fallback: try voiceUserId if loginUserId is not found
        if (!userIdInput) {
            userIdInput = document.getElementById('voiceUserId');
            console.log('DEBUG: userIdInput (voiceUserId fallback)', userIdInput);
        }
        if (!userIdInput) {
            this.showNotification('User ID field not found!', 'error');
            if (statusDiv) statusDiv.innerHTML = '<div class="login-status error">❌ User ID field not found</div>';
            return;
        }
        const userId = userIdInput.value.trim();
        if (!userId) {
            this.showNotification('Please enter your user ID', 'error');
            if (statusDiv) statusDiv.innerHTML = '<div class="login-status error">❌ Please enter your user ID</div>';
            return;
        }
        if (statusDiv) statusDiv.innerHTML = '<div class="login-status">⏳ Processing...</div>';
        try {
            const response = await fetch('/voice/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin',
                body: JSON.stringify({
                    user_id: userId,
                    audio: audioData
                })
            });
            const data = await response.json();
            if (response.ok) {
                const transcription = data.transcription || 'Could not transcribe';
                const confidence = (data.confidence * 100).toFixed(1);
                if (data.authenticated) {
                    if (statusDiv) statusDiv.innerHTML = `
                        <div class="login-status success">✅ Voice verified successfully!</div>
                        <div style="margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #28a745;">
                            <strong>🎤 What you said:</strong> "${transcription}"<br>
                            <strong>📊 Confidence:</strong> ${confidence}%<br>
                            <small style="color: #666;">Redirecting to journal...</small>
                        </div>
                    `;
                    this.showNotification('Voice verification successful!', 'success');
                    setTimeout(() => {
                        window.location.href = '/journal_page';
                    }, 1500);
                } else {
                    if (statusDiv) statusDiv.innerHTML = `
                        <div class="login-status error">❌ Voice verification failed</div>
                        <div style="margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #dc3545;">
                            <strong>🎤 What you said:</strong> "${transcription}"<br>
                            <strong>📊 Confidence:</strong> ${confidence}%<br>
                            <small style="color: #666;">Please try again with the same passphrase.</small>
                        </div>
                    `;
                    this.showNotification('Voice verification failed. Please try again.', 'error');
                }
            } else {
                if (statusDiv) statusDiv.innerHTML = `<div class="login-status error">❌ ${data.error}</div>`;
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            console.error('Verification error:', error);
            if (statusDiv) statusDiv.innerHTML = '<div class="login-status error">❌ Verification failed</div>';
            this.showNotification('Verification failed. Please try again.', 'error');
        }
    }
    
    async enrollVoice(audioData) {
        const userId = document.getElementById('enrollUserId').value.trim();
        const password = document.getElementById('enrollPassword').value.trim();
        const passphrase = document.getElementById('enrollPassphrase').value.trim();
        const statusDiv = document.getElementById('enrollStatus');
        const submitBtn = document.getElementById('enrollSubmit');
        
        if (!userId || !password) {
            this.showNotification('Please fill in all required fields', 'error');
            return;
        }
        
        try {
            // Create voice profile
            const voiceResponse = await fetch('/voice/enroll', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    audio: audioData,
                    passphrase: passphrase || 'Hello Emora'
                })
            });
            
            if (!voiceResponse.ok) {
                const voiceData = await voiceResponse.json();
                statusDiv.innerHTML = `<div class="login-status error">❌ ${voiceData.error}</div>`;
                this.showNotification(voiceData.error, 'error');
                return;
            }
            
            const voiceData = await voiceResponse.json();
            
            // Show transcription and enable submit button
            const transcription = voiceData.transcription || 'Could not transcribe';
            const expectedPassphrase = voiceData.passphrase || passphrase;
            
            statusDiv.innerHTML = `
                <div class="login-status success">✅ Voice profile created successfully!</div>
                <div style="margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #007bff;">
                    <strong>🎤 What you said:</strong> "${transcription}"<br>
                    <strong>📝 Expected phrase:</strong> "${expectedPassphrase}"<br>
                    <small style="color: #666;">If the transcription doesn't match, please retake the recording.</small>
                </div>
            `;
            
            // Enable submit button for account creation
            submitBtn.disabled = false;
            submitBtn.textContent = 'Create Account';
            
            this.showNotification('Voice profile created! Review transcription and click "Create Account"', 'success');
            
        } catch (error) {
            console.error('Enrollment error:', error);
            statusDiv.innerHTML = '<div class="login-status error">❌ Enrollment failed</div>';
            this.showNotification('Enrollment failed. Please try again.', 'error');
        }
    }
    
    async createAccount() {
        const userId = document.getElementById('enrollUserId').value.trim();
        const password = document.getElementById('enrollPassword').value.trim();
        const name = document.getElementById('enrollName').value.trim();
        const statusDiv = document.getElementById('enrollStatus');
        const submitBtn = document.getElementById('enrollSubmit');
        
        if (!userId || !password || !name) {
            this.showNotification('Please fill in all required fields', 'error');
            return;
        }
        
        try {
            // Create password account
            const passwordResponse = await fetch('/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    password: password,
                    name: name
                })
            });
            
            const passwordData = await passwordResponse.json();
            
            if (passwordResponse.ok) {
                statusDiv.innerHTML = '<div class="login-status success">✅ Account created successfully! Redirecting to journal...</div>';
                submitBtn.disabled = true;
                this.showNotification('Account created successfully!', 'success');
                
                // Auto-login after successful registration
                setTimeout(() => {
                    this.loginUser(userId, 'voice');
                }, 1500);
            } else {
                statusDiv.innerHTML = `<div class="login-status error">❌ ${passwordData.error}</div>`;
                this.showNotification(passwordData.error, 'error');
            }
        } catch (error) {
            console.error('Account creation error:', error);
            statusDiv.innerHTML = '<div class="login-status error">❌ Account creation failed</div>';
            this.showNotification('Account creation failed. Please try again.', 'error');
        }
    }
    
    // Enable submit button after voice processing
    enableSubmitButton() {
        const submitBtn = document.getElementById('enrollSubmit');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Create Account';
        }
    }
    
    async loginWithPassword() {
        const userId = document.getElementById('passwordUserId').value.trim();
        const password = document.getElementById('userPassword').value.trim();
        const statusDiv = document.getElementById('passwordStatus');
        
        if (!userId || !password) {
            this.showNotification('Please enter both User ID and Password', 'error');
            return;
        }
        
        try {
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin',
                body: JSON.stringify({
                    user_id: userId,
                    password: password
                })
            });
            
            const data = await response.json();
            
            if (response.ok && data.authenticated) {
                statusDiv.innerHTML = '<div class="login-status success">✅ Password verified successfully!</div>';
                this.showNotification('Password verified successfully!', 'success');
                this.loginUser(userId, 'password');
            } else {
                statusDiv.innerHTML = '<div class="login-status error">❌ Invalid credentials</div>';
                this.showNotification('Invalid User ID or Password', 'error');
            }
        } catch (error) {
            console.error('Password login error:', error);
            statusDiv.innerHTML = '<div class="login-status error">❌ Login failed</div>';
            this.showNotification('Login failed. Please try again.', 'error');
        }
    }
    
    async loginUser(userId, method) {
        const statusDiv = document.getElementById('loginStatus');
        if (statusDiv) statusDiv.innerHTML = '<div class="login-status">⏳ Processing...</div>';
        try {
            let response;
            if (method === 'voice') {
                // Already authenticated by voice, just redirect
                window.location.href = '/journal_page';
                return;
            } else {
                response = await fetch('/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'same-origin',
                    body: JSON.stringify({
                        user_id: userId,
                        password: document.getElementById('userPassword').value.trim()
                    })
                });
            }
            const data = await response.json();
            if (response.ok && data.authenticated) {
                if (statusDiv) statusDiv.innerHTML = '<div class="login-status success">✅ Login successful! Redirecting...</div>';
                // Remove or delay notification to avoid showing it on login page
                setTimeout(() => {
                    window.location.href = '/journal_page';
                }, 500);
            } else {
                if (statusDiv) statusDiv.innerHTML = `<div class="login-status error">❌ ${data.error}</div>`;
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            console.error('Login error:', error);
            if (statusDiv) statusDiv.innerHTML = '<div class="login-status error">❌ Login failed</div>';
            this.showNotification('Login failed. Please try again.', 'error');
        }
    }
    
    checkLoginStatus() {
        const session = localStorage.getItem('emora_session');
        if (session) {
            try {
                const sessionData = JSON.parse(session);
                const expiresAt = new Date(sessionData.expires_at);
                
                if (expiresAt > new Date()) {
                    // Session is still valid, redirect to journal
                    window.location.href = '/journal_page';
                } else {
                    // Session expired, clear it
                    localStorage.removeItem('emora_session');
                }
            } catch (error) {
                localStorage.removeItem('emora_session');
            }
        }
    }
    
    initializeEventListeners() {
        // Voice login recording
        const voiceStartBtn = document.getElementById('voiceStartRecording');
        const voiceStopBtn = document.getElementById('voiceStopRecording');
        
        if (voiceStartBtn) {
            voiceStartBtn.addEventListener('click', () => this.startRecording('voice'));
        }
        if (voiceStopBtn) {
            voiceStopBtn.addEventListener('click', () => this.stopRecording());
        }
        
        // Enrollment recording
        const enrollStartBtn = document.getElementById('enrollStartRecording');
        const enrollStopBtn = document.getElementById('enrollStopRecording');
        const enrollRetakeBtn = document.getElementById('enrollRetakeRecording');
        
        if (enrollStartBtn) {
            enrollStartBtn.addEventListener('click', () => this.startRecording('enroll'));
        }
        if (enrollStopBtn) {
            enrollStopBtn.addEventListener('click', () => this.stopRecording());
        }
        if (enrollRetakeBtn) {
            enrollRetakeBtn.addEventListener('click', () => this.retakeRecording());
        }
        
        // Password login
        const passwordLoginBtn = document.getElementById('passwordLoginBtn');
        if (passwordLoginBtn) {
            passwordLoginBtn.addEventListener('click', () => this.loginWithPassword());
        }
        
        // Handle submit button click
        document.getElementById('enrollSubmit').addEventListener('click', async (e) => {
            e.preventDefault();
            
            const submitBtn = e.target;
            const isRecording = this.isRecording;
            const isEnrolled = submitBtn.textContent === 'Create Account';
            
            if (isRecording) {
                // Stop recording
                this.stopRecording();
            } else if (isEnrolled) {
                // Button shows "Create Account", so create the account
                await this.createAccount();
            } else {
                // Start recording
                this.startRecording();
            }
        });
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => notification.classList.add('show'), 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }
}

// Global functions for tab switching
window.switchToPassword = function() {
    const passwordTab = document.querySelector('[data-tab="password"]');
    if (passwordTab) {
        passwordTab.click();
    }
};

window.switchToVoice = function() {
    const voiceTab = document.querySelector('[data-tab="voice"]');
    if (voiceTab) {
        voiceTab.click();
    }
};

// Initialize when page loads
window.addEventListener('load', () => {
    initializeTheme();
    new LoginSystem();
}); 