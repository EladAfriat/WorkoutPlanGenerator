# ⚡ Quick Deploy Checklist

## Before You Start
- [ ] GitHub account created
- [ ] Git installed on your computer
- [ ] All files saved and working locally

## Deployment Steps

### 1. Initialize Git (if not done)
```bash
git init
git add .
git commit -m "Initial commit"
```

### 2. Create GitHub Repo
- Go to: https://github.com/new
- Name: `workout-plan-generator`
- Make it **Public**
- Click "Create repository"

### 3. Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/workout-plan-generator.git
git branch -M main
git push -u origin main
```

### 4. Deploy to Streamlit Cloud
- Go to: https://share.streamlit.io
- Sign in with GitHub
- Click "New app"
- Repository: `your-username/workout-plan-generator`
- Main file: `src/streamlit_app.py`
- Click "Deploy"

### 5. Done! 🎉
Your app will be live at: `https://your-app-name.streamlit.app`

---

**Full guide:** See `DEPLOYMENT_GUIDE.md` for detailed instructions.

