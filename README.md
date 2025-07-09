# Emora - AI Mental Health Journal

A modern, AI-powered mental health journaling application that provides real-time emotional analysis through text and voice recordings. Built with privacy-first design, all data remains local to ensure user confidentiality.

## ✨ Key Features

### 🎯 Core Functionality
- **AI-Powered Analysis**: Real-time emotion detection using machine learning models
- **Multi-Modal Input**: Text journaling and voice recording with live transcription
- **Real-Time Processing**: WebSocket-based audio streaming with live spectrogram visualization
- **Privacy-Focused**: Complete local storage - no data leaves the user's device
- **Modern UI/UX**: Minimal professional design with responsive, accessible interface
- **Dark/Light Mode**: Toggle between themes with persistent user preferences
- **Audio Feature Extraction**: Advanced analysis of pitch, energy, and spectral characteristics

### 🎯 Core Functionality
- **Text Journaling**: Write about your day and get emotional analysis
- **Voice Recording**: Record your voice and get real-time transcription and mood detection
- **Emotional Analysis**: AI-powered mood detection with supportive messages
- **Audio Visualization**: Real-time spectrogram display during recording
- **Journal History**: Secure local storage of all your entries
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile

### 🎨 Modern Design
- **Minimal Professional UI**: Clean, modern interface with subtle shadows and borders
- **Dark/Light Theme Support**: Toggle between themes with smooth transitions
- **Gradient Backgrounds**: Smooth color transitions throughout the interface
- **Smooth Animations**: Elegant hover effects and transitions
- **Professional Typography**: Clean, readable Inter font family
- **Accessibility**: Proper focus states and keyboard navigation

### 🔧 Technical Features
- **Real-time Processing**: WebSocket-based audio streaming
- **Audio Feature Extraction**: Pitch, energy, zero crossing rate, spectral centroid
- **Whisper Integration**: OpenAI's Whisper for accurate speech-to-text
- **Local Storage**: All data stays on your device for privacy
- **Cross-platform**: Works on all modern browsers

## 🛠️ Technical Stack

**Backend**: Python, Flask, Flask-SocketIO, Whisper (OpenAI), Librosa, NumPy  
**Frontend**: HTML5, CSS3 (Glassmorphism), JavaScript (ES6+), Web Audio API  
**AI/ML**: Custom mood classification models, audio feature extraction  
**Architecture**: Real-time WebSocket communication, RESTful APIs  

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

## 🏗️ Architecture

### Frontend
- **HTML5**: Semantic markup with modern structure
- **CSS3**: Custom glassmorphism design with responsive grid
- **JavaScript**: Real-time audio processing and WebSocket communication
- **Web Audio API**: Real-time spectrogram visualization

### Backend
- **Flask**: Lightweight web framework
- **Flask-SocketIO**: Real-time WebSocket communication
- **Whisper**: OpenAI's speech-to-text model
- **Librosa**: Audio feature extraction
- **NumPy**: Numerical computations

### Key Components
```
├── app.py                 # Main Flask application
├── feature_extractor.py   # Audio feature extraction
├── mood_classifier.py     # Mood detection logic
├── templates/
│   ├── index.html        # Main journal interface
│   └── dashboard.html    # Real-time dashboard
├── static/
│   ├── css/style.css     # Modern glassmorphism styles
│   └── js/
│       ├── app.js        # Main application logic
│       └── dashboard.js  # Dashboard functionality
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

### Project Structure
```
Emora/
├── app.py                 # Main application
├── audio_capture.py       # Audio capture utilities
├── feature_extractor.py   # Audio feature extraction
├── mood_classifier.py     # Mood classification
├── models/               # AI model storage
├── static/               # Static assets
│   ├── css/
│   └── js/
├── templates/            # HTML templates
├── tests/               # Test files
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

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
