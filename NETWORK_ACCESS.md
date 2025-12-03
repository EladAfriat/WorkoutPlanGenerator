# 🌐 Accessing Streamlit App from Other Computers

## Same Network (Local Network)

### On This Computer:
1. Run the app using `run_app.bat` or:
   ```bash
   python -m streamlit run src\streamlit_app.py --server.port 8501 --server.address 0.0.0.0
   ```

2. Your local IP address: **10.8.33.228**

### On Other Computers (Same Network):
- Open browser and go to: **http://10.8.33.228:8501**
- Make sure both computers are on the same Wi-Fi/network

### Troubleshooting:
- **Firewall blocking?** 
  - Windows: Allow Python/Streamlit through Windows Firewall
  - Or temporarily disable firewall for testing

- **Can't connect?**
  - Check both devices are on same network
  - Verify IP address hasn't changed (run `ipconfig` to check)
  - Make sure Streamlit is running with `--server.address 0.0.0.0`

---

## Internet Access (From Anywhere)

To access from anywhere on the internet, you have several options:

### Option 1: ngrok (Easiest - Free)
1. Download ngrok from https://ngrok.com
2. Run Streamlit normally
3. In another terminal, run:
   ```bash
   ngrok http 8501
   ```
4. ngrok will give you a public URL like: `https://abc123.ngrok.io`
5. Share this URL with anyone

### Option 2: Streamlit Cloud (Free Hosting)
1. Push your code to GitHub
2. Go to https://share.streamlit.io
3. Connect your GitHub repo
4. Deploy - get a permanent URL like: `https://your-app.streamlit.app`

### Option 3: Other Cloud Services
- Heroku
- AWS
- Google Cloud
- Azure

---

## Security Notes

⚠️ **Important:**
- When using `--server.address 0.0.0.0`, your app is accessible to anyone on your network
- For production, add authentication/security
- Don't expose sensitive data without proper security

---

## Quick Commands

**Start with network access:**
```bash
python -m streamlit run src\streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

**Check your IP address:**
```bash
ipconfig | findstr IPv4
```

**Stop Streamlit:**
Press `Ctrl+C` in the terminal

