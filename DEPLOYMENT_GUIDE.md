# 🚀 Streamlit Cloud Deployment Guide

## Step-by-Step Instructions

### Step 1: Create GitHub Account (if you don't have one)
1. Go to https://github.com
2. Sign up for a free account

### Step 2: Initialize Git Repository

Open terminal in your project folder and run:

```bash
# Initialize git repository
git init

# Add all files
git add .

# Make first commit
git commit -m "Initial commit: Workout Plan Generator"
```

### Step 3: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `workout-plan-generator` (or any name you like)
3. Description: "Smart workout plan generator using BFS algorithm"
4. Choose **Public** (required for free Streamlit Cloud)
5. **Don't** initialize with README (you already have one)
6. Click "Create repository"

### Step 4: Push Code to GitHub

GitHub will show you commands. Run these in your terminal:

```bash
# Add remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/workout-plan-generator.git

# Rename branch to main (if needed)
git branch -M main

# Push code
git push -u origin main
```

**Note:** You may need to authenticate. GitHub will guide you through this.

### Step 5: Deploy to Streamlit Cloud

1. Go to **https://share.streamlit.io**
2. Click **"Sign in"** and sign in with your GitHub account
3. Click **"New app"** button
4. Fill in the form:
   - **Repository**: Select `your-username/workout-plan-generator`
   - **Branch**: `main` (or `master`)
   - **Main file path**: `src/streamlit_app.py`
   - **App URL**: Choose a unique name (e.g., `workout-plan-generator`)
5. Click **"Deploy"**

### Step 6: Wait for Deployment

- Streamlit Cloud will install dependencies from `requirements.txt`
- First deployment takes 2-5 minutes
- You'll see build logs in real-time
- When done, you'll get a URL like: `https://workout-plan-generator.streamlit.app`

### Step 7: Share Your App! 🎉

Your app is now live and accessible from anywhere!

---

## Troubleshooting

### Build Fails

**Error: Module not found**
- Check `requirements.txt` has all dependencies
- Make sure all imports are correct

**Error: File not found**
- Verify `src/streamlit_app.py` path is correct
- Check that `data/exercises.json` exists

**Error: Port already in use**
- This shouldn't happen on Streamlit Cloud, but if it does, check the config

### App Doesn't Load

- Check build logs in Streamlit Cloud dashboard
- Verify all files were pushed to GitHub
- Make sure `requirements.txt` is in the root directory

### Updates Not Showing

- After pushing changes to GitHub, Streamlit Cloud auto-deploys
- If not, click "Reboot app" in the Streamlit Cloud dashboard
- Or wait a few minutes for auto-deployment

---

## File Structure for Deployment

Your repository should have this structure:
```
workout-plan-generator/
├── .gitignore
├── .streamlit/
│   └── config.toml
├── data/
│   └── exercises.json
├── src/
│   ├── __init__.py
│   ├── bfs_algorithm.py
│   ├── data_handler.py
│   └── streamlit_app.py
├── requirements.txt
└── README.md
```

---

## Quick Commands Reference

```bash
# Check git status
git status

# Add all files
git add .

# Commit changes
git commit -m "Your commit message"

# Push to GitHub
git push

# Check remote
git remote -v
```

---

## Next Steps After Deployment

1. **Customize your app URL** in Streamlit Cloud settings
2. **Add app description** in Streamlit Cloud dashboard
3. **Share the link** with others!
4. **Monitor usage** in Streamlit Cloud dashboard

---

## Security Notes

⚠️ **Important:**
- Your app is public (free tier)
- Don't store sensitive data in code
- Exercise data is public (which is fine for this app)
- For private apps, you need Streamlit Cloud Team plan

---

## Need Help?

- Streamlit Cloud Docs: https://docs.streamlit.io/streamlit-community-cloud
- GitHub Docs: https://docs.github.com
- Streamlit Community: https://discuss.streamlit.io

