# 🚀 Deploy Emora to Render

## Prerequisites
- GitHub account with your Emora repository
- Render account (free)

## Step-by-Step Deployment

### 1. Sign up for Render
- Go to [render.com](https://render.com)
- Sign up with your GitHub account

### 2. Create New Web Service
- Click "New +" → "Web Service"
- Connect your GitHub repository
- Select the `sarcasm-detect` repository

### 3. Configure the Service
- **Name**: `emora-ai-journal` (or your preferred name)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

### 4. Environment Variables (Optional)
Add these if needed:
- `FLASK_ENV`: `production`
- `FLASK_DEBUG`: `false`

### 5. Deploy
- Click "Create Web Service"
- Render will automatically build and deploy your app
- Wait for the build to complete (usually 5-10 minutes)

### 6. Access Your App
- Your app will be available at: `https://your-app-name.onrender.com`
- The URL will be shown in your Render dashboard

## Important Notes

### ⚠️ Free Tier Limitations
- **Sleep after 15 minutes** of inactivity
- **750 hours/month** (usually sufficient)
- **First request** after sleep may take 30-60 seconds

### 🔧 Troubleshooting
- Check build logs in Render dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify Python version compatibility

### 📝 Custom Domain (Optional)
- In Render dashboard, go to your service
- Click "Settings" → "Custom Domains"
- Add your domain and configure DNS

## Support
If you encounter issues:
1. Check Render build logs
2. Verify all files are committed to GitHub
3. Ensure `render.yaml` is in your repository root 