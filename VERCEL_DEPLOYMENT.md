# 🚀 Deploy Emora to Vercel

## ⚠️ Important Considerations

**Vercel is primarily designed for frontend applications and serverless functions.** Your Flask app with audio processing may face some limitations:

### Potential Challenges:
- **Audio Processing**: Large ML models (Whisper, transformers) may exceed function size limits
- **WebSocket Support**: Limited real-time audio streaming capabilities
- **Function Timeout**: 30-second limit for serverless functions
- **Memory Limits**: Large models may not fit in serverless environment

## Prerequisites
- GitHub account with your Emora repository
- Vercel account (free)

## Step-by-Step Deployment

### 1. Sign up for Vercel
- Go to [vercel.com](https://vercel.com)
- Sign up with your GitHub account

### 2. Import Your Repository
- Click "New Project"
- Import your `toobajatoi/Emora` repository
- Vercel will auto-detect it's a Python project

### 3. Configure the Project
- **Framework Preset**: Python
- **Root Directory**: `./` (leave as default)
- **Build Command**: Leave empty (Vercel will auto-detect)
- **Output Directory**: Leave empty
- **Install Command**: `pip install -r requirements-vercel.txt`

### 4. Environment Variables (Optional)
Add these if needed:
- `FLASK_ENV`: `production`
- `FLASK_DEBUG`: `false`

### 5. Deploy
- Click "Deploy"
- Vercel will build and deploy your app
- Wait for the build to complete

### 6. Access Your App
- Your app will be available at: `https://your-app-name.vercel.app`
- The URL will be shown in your Vercel dashboard

## Alternative: Hybrid Approach (Recommended)

If you encounter issues with the full app on Vercel, consider:

### Frontend on Vercel + Backend on Railway
1. **Deploy frontend** (HTML/CSS/JS) on Vercel
2. **Deploy backend** (Flask API) on Railway
3. **Connect them** via API calls

### Steps for Hybrid:
1. **Split your app** into frontend and backend
2. **Deploy frontend** to Vercel for fast static hosting
3. **Deploy backend** to Railway for full Flask support
4. **Update frontend** to call Railway API

## Troubleshooting

### Common Issues:
- **Function timeout**: Audio processing takes too long
- **Size limits**: ML models too large for serverless
- **WebSocket issues**: Real-time features may not work

### Solutions:
- **Use hybrid approach** (frontend on Vercel, backend elsewhere)
- **Optimize models** for smaller size
- **Use external API** for heavy processing

## Support
If you encounter issues:
1. Check Vercel build logs
2. Consider the hybrid approach
3. Try Railway for full backend deployment

## Recommended Next Steps
1. **Try Vercel deployment** first
2. **If issues arise**, consider Railway for backend
3. **Use Vercel for frontend** if splitting the app 