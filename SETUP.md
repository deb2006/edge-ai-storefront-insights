# F2C Analytics Panel - Setup & Launch Guide

## Quick Start (5 minutes)

### Windows Users

1. **Open Command Prompt (cmd.exe)**

2. **Navigate to project folder:**
   ```cmd
   cd "c:\Users\DebayanGhose\OneDrive - AIROWIRE NETWORKS PRIVATE LIMITED\Documents\f2c_bridge"
   ```

3. **Run the startup script:**
   ```cmd
   run.bat
   ```
   
   This will automatically:
   - Create a Python virtual environment
   - Install all required packages
   - Launch the Streamlit dashboard

4. **Open browser to:** `http://localhost:8501`

---

### macOS/Linux Users

1. **Open Terminal**

2. **Navigate to project folder:**
   ```bash
   cd path/to/f2c_bridge
   ```

3. **Make script executable:**
   ```bash
   chmod +x run.sh
   ```

4. **Run startup script:**
   ```bash
   ./run.sh
   ```

5. **Open browser to:** `http://localhost:8501`

---

## Manual Setup (If Automated Scripts Don't Work)

### Step 1: Create Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Expected output shows installation of:
- ✓ streamlit==1.28.1
- ✓ supabase==2.0.3
- ✓ pandas==2.1.3
- ✓ plotly==5.18.0
- ✓ python-dotenv==1.0.0

### Step 3: Verify .env File

**Windows:**
```cmd
type .env
```

**macOS/Linux:**
```bash
cat .env
```

Should display:
```
SUPABASE_URL=https://mfuqfpibknywivtculxk.supabase.co
SUPABASE_KEY=eyJhbGciOi...
```

### Step 4: Launch Application

```bash
streamlit run app.py
```

The dashboard will open automatically at **http://localhost:8501**

---

## Troubleshooting

### Issue: "Python command not found"
**Solution:** 
- Verify Python is installed: `python --version`
- Add Python to PATH if needed
- Use `python3` instead of `python` on macOS/Linux

### Issue: "ModuleNotFoundError: No module named 'streamlit'"
**Solution:**
```bash
# Ensure virtual environment is activated
# Then reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Cannot connect to Supabase"
**Solution:**
1. Verify `.env` file exists in project folder
2. Check credentials are correct (don't have extra whitespace)
3. Verify internet connection
4. Check Supabase project is active at https://supabase.com/dashboard

### Issue: "Port 8501 already in use"
**Solution:**
```bash
# Use different port
streamlit run app.py --server.port=8502
```

### Issue: Dashboard shows "No data available"
**Solution:**
1. Verify Supabase tables exist:
   - `f2c_footfall_raw`
   - `f2c_pos_sales`
   - `v_hourly_conversion_kpi`
2. Ensure tables contain sample data
3. Check Row-Level Security policies allow SELECT on anonymous role

---

## Docker Deployment

### Option 1: Build and Run Locally

**Build image:**
```bash
docker build -t f2c-analytics .
```

**Run container:**
```bash
docker run -p 8501:8501 --env-file .env f2c-analytics
```

**Access:** http://localhost:8501

### Option 2: Docker Compose

**Start services:**
```bash
docker-compose up
```

**Stop services:**
```bash
docker-compose down
```

---

## Production Deployment

### Streamlit Cloud (Recommended)

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Sign in with GitHub account
4. Deploy → Select your repository
5. Set secrets in deployment settings:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

### AWS/Google Cloud/Azure

1. Create container from Dockerfile
2. Deploy to container service (ECS, Cloud Run, Container Instances)
3. Set environment variables in deployment config
4. Map port 8501 to public endpoint
5. Enable HTTPS/SSL

### Self-Hosted Server

1. Install Python 3.9+
2. Clone/transfer project files
3. Run `pip install -r requirements.txt`
4. Use systemd service or supervisor to keep app running
5. Use nginx/Apache as reverse proxy
6. Enable SSL certificates (Let's Encrypt)

---

## File Descriptions

| File | Purpose |
|------|---------|
| `app.py` | **Main Streamlit application** - Dashboard UI & logic |
| `mainbridge_copy.py` | Edge data bridge - Receives telemetry from Jetson |
| `requirements.txt` | Python dependencies list |
| `.env` | Supabase credentials (KEEP SECURE - Never commit) |
| `README.md` | Full documentation & architecture |
| `Dockerfile` | Container image definition |
| `docker-compose.yml` | Docker orchestration config |
| `run.bat` | Windows startup script |
| `run.sh` | macOS/Linux startup script |
| `.gitignore` | Git ignore patterns (protects .env) |

---

## Daily Usage

### Starting the Dashboard
```bash
streamlit run app.py
```

### Stopping the Dashboard
Press `Ctrl+C` in terminal

### Clearing Cache
Click **🔄 Refresh Data** button in dashboard

### Monitoring Logs
Check terminal output for debug information

---

## Performance Tips

1. **Data loads slowly?**
   - Check Supabase connection
   - Verify database has proper indexes
   - Increase CACHE_TTL in app.py to 10-15 seconds

2. **Dashboard feels sluggish?**
   - Close unused browser tabs
   - Clear browser cache
   - Ensure internet connection is stable

3. **Charts not updating?**
   - Verify edge devices are sending data
   - Check Supabase tables have recent timestamps
   - Click refresh button

---

## Support

For issues:
1. Read full README.md
2. Check Supabase dashboard for data
3. Enable debug logging: `streamlit run app.py --logger.level=debug`
4. Review error messages in terminal output

---

## Version Information

- **App Version**: 1.0.0
- **Streamlit**: 1.28.1+
- **Python**: 3.9+
- **Last Updated**: 2025-05-18

---

**Ready to launch?** Run `run.bat` (Windows) or `./run.sh` (macOS/Linux) now! 🚀
