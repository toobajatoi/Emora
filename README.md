# Emora - AI Mental Health Journal

A modern, AI-powered mental health journaling application that provides real-time emotional analysis through text and voice recordings. Built with privacy-first design, all data remains local to ensure user confidentiality.

## ✨ Features

### 🎯 Core Functionality
- **AI-Powered Analysis**: Real-time emotion detection using machine learning models
- **Multi-Modal Input**: Text journaling and voice recording with live transcription
- **Real-Time Processing**: WebSocket-based audio streaming with live spectrogram visualization
- **Privacy-Focused**: Complete local storage - no data leaves the user's device
- **Modern UI/UX**: Minimal professional design with responsive, accessible interface
- **Dark/Light Mode**: Toggle between themes with persistent user preferences
- **Audio Feature Extraction**: Advanced analysis of pitch, energy, and spectral characteristics
- **Voice Lock Authentication**: Secure voice biometric authentication system

### 🎨 Design Features
- **Minimal Professional UI**: Clean, modern interface with subtle shadows and borders
- **Dark/Light Theme Support**: Toggle between themes with smooth transitions
- **Gradient Backgrounds**: Smooth color transitions throughout the interface
- **Smooth Animations**: Elegant hover effects and transitions
- **Professional Typography**: Clean, readable Inter font family
- **Accessibility**: Proper focus states and keyboard navigation

## 🏗️ How It Works

### Architecture Overview

Emora uses a **client-server architecture** with real-time communication capabilities:

```
┌─────────────────┐    WebSocket    ┌─────────────────┐
│   Frontend      │ ◄─────────────► │    Backend      │
│   (Browser)     │                 │   (Flask)       │
└─────────────────┘                 └─────────────────┘
         │                                    │
         │                                    │
         ▼                                    ▼
┌─────────────────┐                 ┌─────────────────┐
│  Local Storage  │                 │   AI Models     │
│  (Journal Data) │                 │  (Whisper/ML)   │
└─────────────────┘                 └─────────────────┘
```

### Data Flow

#### Text Journal Processing:
1. **User Input**: User types journal entry in text area
2. **Frontend**: Sends text via HTTP POST to `/journal` endpoint
3. **Backend**: Processes text through mood classification model
4. **Analysis**: Extracts emotional features and generates response
5. **Response**: Returns analysis results to frontend
6. **Storage**: Results saved to browser's localStorage

#### Voice Journal Processing:
1. **Audio Capture**: Browser captures audio via Web Audio API
2. **Real-time Visualization**: Live spectrogram display during recording
3. **Audio Processing**: Converts WebM/Opus to WAV format
4. **Speech-to-Text**: OpenAI Whisper transcribes audio to text
5. **Feature Extraction**: Librosa extracts audio features (pitch, energy, etc.)
6. **Mood Analysis**: Combined text and audio features analyzed
7. **Results**: Comprehensive analysis returned to frontend

### Technical Components

#### Frontend (Client-Side)
- **HTML5**: Semantic markup with modern structure
- **CSS3**: Theme-aware styling with CSS variables
- **JavaScript**: Real-time audio processing and WebSocket communication
- **Web Audio API**: Real-time spectrogram visualization
- **localStorage**: Secure local data storage

#### Backend (Server-Side)
- **Flask**: Lightweight web framework for HTTP endpoints
- **Flask-SocketIO**: Real-time WebSocket communication
- **Whisper**: OpenAI's speech-to-text model for transcription
- **Librosa**: Audio feature extraction (pitch, energy, spectral centroid)
- **NumPy**: Numerical computations and data processing
- **Custom ML Models**: Mood classification algorithms

### 🎤 Voice Authentication System

#### How Voice Authentication Works
Emora includes a sophisticated voice biometric authentication system that allows users to secure their journal with their unique voice characteristics:

1. **Voice Enrollment**: Users record their voice saying a passphrase
2. **Feature Extraction**: System extracts unique voice characteristics:
   - **Pitch Analysis**: Fundamental frequency and variations
   - **Spectral Features**: Voice timbre and resonance
   - **MFCC Coefficients**: Mel-frequency cepstral coefficients
   - **Energy Patterns**: Voice intensity and dynamics
   - **Formant Analysis**: Vocal tract characteristics

3. **Voice Matching**: Cosine similarity comparison between stored and new recordings
4. **Authentication**: Access granted if similarity exceeds threshold (85%)

#### Voice Authentication Features
- **Secure Enrollment**: Create voice profiles with custom passphrases
- **Real-Time Verification**: Instant voice recognition and authentication
- **Profile Management**: Check, update, and delete voice profiles
- **Confidence Scoring**: Percentage-based confidence in voice matches
- **Fallback Options**: Text-based authentication as backup
- **Privacy-First**: Voice features stored locally, never transmitted

#### Voice Biometric Features Extracted
- **Pitch Characteristics**: Mean, standard deviation, range
- **Spectral Centroid**: Brightness of voice
- **MFCC Features**: Voice timbre and quality
- **Energy Metrics**: Voice intensity patterns
- **Zero Crossing Rate**: Voice complexity
- **Spectral Rolloff**: Frequency distribution

### Security & Privacy

- **Local Storage**: All journal entries stored in user's browser
- **No Server Persistence**: Data never saved on server
- **HTTPS Ready**: Configured for secure connections
- **Minimal Permissions**: Microphone access only when needed

## 🛠️ Technical Stack

**Backend**: Python, Flask, Flask-SocketIO, Whisper (OpenAI), Librosa, NumPy, Scikit-learn  
**Frontend**: HTML5, CSS3, JavaScript (ES6+), Web Audio API  
**AI/ML**: Custom mood classification models, audio feature extraction, voice biometrics  
**Architecture**: Real-time WebSocket communication, RESTful APIs, voice authentication system  

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Microphone access (for voice recording)
- Modern web browser with WebSocket support

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/toobajatoi/Emora.git
   cd Emora
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   ```bash
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5001`

## 📱 Usage

### Writing a Journal Entry
1. Type your thoughts in the text area
2. Click "Submit Journal" to analyze your entry
3. View your emotional analysis and supportive message

### Recording Voice
1. Click "🎤 Start Recording" to begin
2. Speak clearly into your microphone
3. Watch the real-time spectrogram visualization
4. Click "⏹️ Stop Recording" when finished
5. Wait for processing and view your results

### Viewing History
- All entries are stored locally in your browser
- Click on any entry to view detailed information
- Use the "🗑️ Delete All" button to clear your history

### Theme Customization
- Click the theme toggle button (🌙/☀️) in the top-right corner
- Switch between light and dark modes
- Your theme preference is automatically saved
- Smooth transitions between themes

### Voice Authentication

#### Enrolling Your Voice
1. Navigate to the "Voice Lock Authentication" section
2. Click the "🎤 Enroll Voice" tab
3. Enter your unique User ID
4. Optionally customize your passphrase (default: "Hello Emora")
5. Click "🎤 Record Voice" and speak your passphrase clearly
6. Click "⏹️ Stop Recording" when finished
7. Click "Create Voice Profile" to save your voice biometrics

#### Logging In with Voice
1. Click the "🔐 Voice Login" tab
2. Enter your User ID
3. Click "🎤 Record Voice" and speak your passphrase
4. Click "⏹️ Stop Recording" when finished
5. Click "Verify Voice" to authenticate
6. View your confidence score and authentication result

#### Managing Your Voice Profile
1. Click the "⚙️ Manage Profile" tab
2. Enter your User ID
3. Use "📋 Check Profile" to view your profile details
4. Use "🗑️ Delete Profile" to remove your voice biometrics
5. Confirm deletion when prompted

## 🏗️ Project Structure

```
Emora/
├── app.py                 # Main Flask application & WebSocket server
├── voice_auth.py          # Voice authentication system
├── feature_extractor.py   # Audio feature extraction utilities
├── mood_classifier.py     # Mood detection and classification logic
├── test_voice_auth.py     # Voice authentication test suite
├── models/               # AI model storage (Whisper, custom models)
├── voice_profiles/       # Voice biometric profiles (local storage)
├── static/               # Static assets
│   ├── css/
│   │   └── style.css     # Theme-aware CSS with variables
│   └── js/
│       ├── app.js        # Main application logic & theme management
│       ├── dashboard.js  # Real-time dashboard functionality
│       └── socket.io.js  # WebSocket client library
├── templates/            # HTML templates
│   ├── index.html        # Main journal interface
│   └── dashboard.html    # Real-time dashboard
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🎨 Design System

### Color Palette
- **Primary Gradient**: `#667eea` to `#764ba2`
- **Light Theme**: Clean whites and grays with subtle shadows
- **Dark Theme**: Deep grays with enhanced contrast
- **Text**: Adaptive colors for optimal readability in both themes
- **Accents**: `#667eea` (blue) and `#f56565` (red)

### Typography
- **Font Family**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700
- **Responsive**: Scales appropriately on all devices

### Components
- **Cards**: Clean backgrounds with subtle borders and shadows
- **Buttons**: Gradient backgrounds with hover effects
- **Forms**: Clean inputs with focus states
- **Modals**: Centered overlays with smooth animations
- **Theme Toggle**: Fixed position button with smooth transitions

## 🔒 Privacy & Security

- **Local Storage**: All journal entries are stored in your browser
- **No Server Storage**: Your data never leaves your device
- **HTTPS Ready**: Configured for secure connections
- **Microphone Permissions**: Only requested when needed

## 🛠️ Development

### Adding New Features
1. **Frontend**: Add HTML structure in templates
2. **Styling**: Create CSS classes in `static/css/style.css`
3. **Logic**: Implement JavaScript in `static/js/`
4. **Backend**: Add routes in `app.py`
5. **Testing**: Create tests in the `tests/` directory

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

## 🎯 Impact

Provides users with an intuitive, AI-enhanced journaling experience that combines the therapeutic benefits of self-reflection with intelligent emotional analysis, all while maintaining complete privacy and data security.

## 📄 License

Created by Tooba Jatoi  
Copyright © 2025 Tooba Jatoi. All rights reserved.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support or questions:
- Check the documentation
- Review the code comments
- Open an issue on GitHub

## 🔮 Future Enhancements

- [ ] Export journal entries to PDF
- [ ] Mood tracking over time
- [ ] Integration with calendar apps
- [ ] Voice emotion recognition improvements
- [ ] Multi-language support
- [x] Dark/Light mode toggle
- [ ] Journal entry templates
- [ ] Social sharing (optional)

---

**Built with ❤️ by Tooba Jatoi** 
