# F2C Analytics Panel - Quick Reference Guide

## 📋 File Manifest

```
f2c_bridge/
├── app.py                   ← MAIN APPLICATION (Start here)
├── mainbridge_copy.py       ← Edge data bridge (data ingestion)
├── requirements.txt         ← Python dependencies
├── .env                     ← Supabase credentials (KEEP SECRET)
├── .gitignore               ← Git ignore patterns
├── run.bat                  ← Windows startup script
├── run.sh                   ← macOS/Linux startup script
├── Dockerfile               ← Container image definition
├── docker-compose.yml       ← Docker orchestration
├── README.md                ← Full documentation
├── SETUP.md                 ← Setup & troubleshooting guide
├── ARCHITECTURE.md          ← System design deep-dive
└── QUICK_REFERENCE.md       ← This file
```

---

## 🚀 Quick Start (Choose Your Method)

### Method 1: Windows Batch Script (Easiest)
```batch
cd f2c_bridge
run.bat
```
Opens dashboard at: **http://localhost:8501**

### Method 2: Manual (macOS/Linux)
```bash
cd f2c_bridge
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Method 3: Docker
```bash
cd f2c_bridge
docker-compose up
```
Opens dashboard at: **http://localhost:8501**

---

## 📊 Dashboard Panels Overview

### Panel 1️⃣: Executive KPI Scorecard (Top)
**4 Key Metrics in High-Contrast Cards:**
- 🚶 **Total Store Traffic** — Cumulative visitor count
- 💰 **Gross Revenue Volume** — Sum of all sales
- 📈 **Conversion Rate** — Transactions ÷ Footfall (%)
- 🟢 **Node Heartbeat** — Device connectivity status

### Panel 2️⃣: Real-Time Trend Grid (Middle)
**Left Side (66%):** Conversion Performance Chart
- Interactive line chart with area fill
- Hover for detailed values
- Plotly zoom/pan controls

**Right Side (33%):** Live Telemetry Table
- Last 10 sensor readings
- Timestamp | Device | Occupancy | Cumulative

### Panel 3️⃣: Analytical Deep-Dive (Bottom)
**Full-Width Data Explorer:**
- Sort by any column
- Filter by date range
- Summary statistics
- Interactive sorting

---

## 🔧 Configuration Cheat Sheet

### Change Cache Refresh Rate
File: `app.py`, Line 22
```python
CACHE_TTL = 5  # Change to 10, 15, 30, etc.
```
- Lower = more frequent updates (higher API load)
- Higher = fewer API calls (slightly stale data)

### Use Different Port
```bash
streamlit run app.py --server.port=8502
```

### Enable Debug Logging
```bash
streamlit run app.py --logger.level=debug
```

### Run Without Auto-Opening Browser
```bash
streamlit run app.py --server.runOnSave=false
```

---

## 🗄️ Database Quick Reference

### Tables in Supabase

| Table | Purpose | Rows | Source |
|-------|---------|------|--------|
| `f2c_footfall_raw` | Edge sensor data | Thousands | Jetson Orin |
| `f2c_pos_sales` | Transaction log | Hundreds | POS System |
| `v_hourly_conversion_kpi` | Computed metrics | ~24 hourly | Database View |

### Typical Data Query

**What the dashboard queries:**
```sql
-- Every 5 seconds
SELECT * FROM f2c_footfall_raw 
ORDER BY timestamp DESC LIMIT 10;

SELECT * FROM v_hourly_conversion_kpi;

SELECT SUM(sale_amount) FROM f2c_pos_sales;
```

---

## 🔍 Common Troubleshooting

### "Port 8501 already in use"
```bash
# Use different port
streamlit run app.py --server.port=8502
```

### "No data available yet"
Check:
1. Supabase tables have data
2. Edge device is sending telemetry
3. .env credentials are correct

### "ModuleNotFoundError"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### "Cannot connect to Supabase"
```bash
# Verify .env
cat .env

# Should show:
# SUPABASE_URL=https://...
# SUPABASE_KEY=eyJ...
```

---

## 📈 Performance Tips

| Issue | Solution |
|-------|----------|
| Slow loading | Increase `CACHE_TTL` to 10-15 seconds |
| High API load | Reduce refresh frequency |
| Sluggish UI | Close unused browser tabs |
| Stale data | Click 🔄 Refresh Data button |

---

## 🔐 Security Reminders

✅ **DO:**
- Keep `.env` file secure (in `.gitignore`)
- Rotate Supabase keys quarterly
- Use environment variables in production
- Enable HTTPS on public deployments

❌ **DON'T:**
- Commit `.env` to Git
- Share API keys in emails/Slack
- Hardcode credentials in code
- Use production keys in development

---

## 📱 Deployment Quick Links

### Local
```bash
streamlit run app.py
```

### Docker
```bash
docker-compose up
```

### Streamlit Cloud
1. Push to GitHub
2. Go to share.streamlit.io
3. Deploy from repo

### Production (AWS/GCP/Azure)
See SETUP.md for detailed instructions

---

## 🛠️ Development Workflow

### Making Changes

1. **Edit** `app.py`
2. **Save** file (Streamlit auto-reloads)
3. **Test** on http://localhost:8501
4. **Verify** changes work

### Adding a New Metric

1. Add data fetch function in `app.py`
2. Calculate metric in `calculate_kpi_metrics()`
3. Add `st.metric()` widget in `render_kpi_scorecard()`
4. Save and check dashboard

### Testing Database Connection

```python
# In Python console
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
data = supabase.table("f2c_footfall_raw").select("*").limit(1).execute()
print(data)
```

---

## 📞 Getting Help

| Issue Type | Next Steps |
|-----------|-----------|
| **Setup problem** | Read SETUP.md |
| **Dashboard error** | Check terminal output + README.md |
| **Architecture question** | Review ARCHITECTURE.md |
| **Data not showing** | Verify Supabase tables in dashboard |
| **Connection issue** | Check .env file + network connectivity |

---

## ⚡ Dashboard Keyboard Shortcuts (Streamlit)

| Shortcut | Action |
|----------|--------|
| `R` | Rerun script |
| `C` | Clear cache |
| `Ctrl+Shift+P` | Command palette |

---

## 📊 Sample Data for Testing

If tables are empty, use this to populate test data:

```python
# Insert test footfall data
from datetime import datetime, timedelta

test_data = {
    "device_id": "Orin_Nano_Kengeri",
    "live_occupancy": 5,
    "cumulative_footfall": 42
}

supabase.table("f2c_footfall_raw").insert(test_data).execute()

# Insert test sales data
sales_data = {
    "transaction_id": "TEST_001",
    "timestamp": datetime.utcnow().isoformat(),
    "sale_amount": 99.99
}

supabase.table("f2c_pos_sales").insert(sales_data).execute()
```

---

## 🎯 Next Steps After Launch

1. ✅ Verify dashboard loads correctly
2. ✅ Test data refresh (watch metrics update)
3. ✅ Configure cache refresh rate as needed
4. ✅ Set up automated backups (Supabase)
5. ✅ Monitor performance metrics
6. ✅ Configure alerts for critical issues
7. ✅ Document custom metrics if added

---

## 📝 Version Info

- **App Version**: 1.0.0
- **Streamlit**: 1.28.1+
- **Python**: 3.9+
- **Last Updated**: 2025-05-18

---

## 🎨 UI Customization Quick Tips

### Change Color Scheme
Edit CSS in `app.py` around line 50:
```python
# Change cyan (#00d9ff) to other colors
color: #00d9ff;  # Try: #00ff88, #ff6b6b, #4ecdc4
```

### Add New KPI Card
In `render_kpi_scorecard()`:
```python
with col5:
    st.metric(
        label="Your Metric",
        value="123",
        delta="your description"
    )
```

### Modify Chart Type
In `render_trend_and_telemetry()`:
```python
# Change from Line to Bar chart
fig.add_trace(go.Bar(...))  # Instead of go.Scatter
```

---

## 🚀 Launch Command (One-Liner)

**Windows:**
```batch
cd f2c_bridge && run.bat
```

**macOS/Linux:**
```bash
cd f2c_bridge && chmod +x run.sh && ./run.sh
```

**Docker:**
```bash
cd f2c_bridge && docker-compose up
```

---

**Ready to go!** 🎉 Start with the quick start commands above.
