# F2C Analytics Panel - Retail Intelligence Dashboard

A production-ready Streamlit web application for real-time store analytics, combining computer vision telemetry from NVIDIA Jetson Orin Nano edge devices with POS transaction data via Supabase.

---

## 📋 Overview

The F2C Analytics Panel provides store managers and executives with a modern, dark-themed dashboard for monitoring:

- **Live Store Traffic**: Real-time footfall velocity and cumulative visitor count
- **Gross Revenue**: Aggregated transaction volumes from POS systems
- **Conversion KPI**: Calculated hourly conversion rates (transactions ÷ footfall)
- **Node Heartbeat**: Edge device connectivity status and telemetry streaming

### System Architecture

```
EDGE LAYER (Jetson Orin Nano)
    ↓ HTTPS streaming (DeepStream + occupancy metrics)
SUPABASE (PostgreSQL Data Lake)
    ├── f2c_footfall_raw (edge sensor data)
    ├── f2c_pos_sales (transaction logs)
    └── v_hourly_conversion_kpi (computed view)
    ↓ REST API
STREAMLIT FRONTEND (Port 8501)
    └── Real-time Analytics Dashboard
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+ installed
- `.env` file with Supabase credentials (included)
- Active Supabase project with configured tables

### Installation

1. **Navigate to project directory:**
   ```bash
   cd path/to/f2c_bridge
   ```

2. **Create a Python virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify `.env` file exists with credentials:**
   ```bash
   cat .env
   # Should output:
   # SUPABASE_URL=https://mfuqfpibknywivtculxk.supabase.co
   # SUPABASE_KEY=eyJhbGciOi...
   ```

5. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

   The dashboard will open automatically at: **http://localhost:8501**

---

## 📊 Dashboard Components

### Panel 1: Executive KPI Scorecard (Top Row)
Four key metrics in high-contrast cards:

| Metric | Source | Description |
|--------|--------|-------------|
| **Total Store Traffic** | `f2c_footfall_raw.cumulative_footfall` | Maximum cumulative visitor count |
| **Gross Revenue Volume** | `f2c_pos_sales.sale_amount` | Sum of all transactions |
| **Conversion Rate** | `v_hourly_conversion_kpi` | Avg hourly conversion % (transactions ÷ footfall) |
| **Node Heartbeat** | Latest `f2c_footfall_raw` timestamp | Device status (🟢 Online/🟡 Stale/🔴 Offline) |

### Panel 2: Real-Time Trend Grid (66% / 33% Split)

**Left: Conversion Performance Chart**
- Interactive line chart with area fill
- X-axis: Chronological hourly buckets
- Y-axis: Conversion rate percentage
- Built with Plotly for interactivity (hover, zoom, pan)

**Right: Live Edge Telemetry Table**
- Last 10 footfall sensor readings
- Columns: Timestamp, Device ID, Live Occupancy, Cumulative Total
- Real-time updates every 5 seconds

### Panel 3: Analytical Deep-Dive (Full Width)

- Complete `v_hourly_conversion_kpi` view data
- **Filtering**: Date range slider for temporal exploration
- **Sorting**: Multi-column sortable (descending)
- **Statistics**: Auto-generated summary (mean, std, min, max)

---

## 🔧 Configuration

### Environment Variables (`.env`)

```ini
# Supabase REST API Credentials
SUPABASE_URL=https://mfuqfpibknywivtculxk.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Data Refresh Settings

Edit `app.py` to customize cache TTL:

```python
CACHE_TTL = 5  # Refresh database queries every 5 seconds
```

Lower values = more frequent updates (higher API load)
Higher values = fewer API calls (slightly stale data)

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `streamlit` | 1.28.1 | Web framework & UI components |
| `supabase` | 2.0.3 | PostgreSQL REST client |
| `pandas` | 2.1.3 | Data manipulation & analysis |
| `plotly` | 5.18.0 | Interactive charting |
| `python-dotenv` | 1.0.0 | Environment variable loading |

---

## 🛡️ Error Handling & Fault Tolerance

The dashboard gracefully handles common failure scenarios:

### Network Errors
- ✅ Missing Supabase connection → Warning message displayed
- ✅ Missing columns in database → Fallback calculation logic
- ✅ Slow API responses → Data cached for 5 seconds

### Data Errors
- ✅ Empty result sets → Info messages ("No data available yet")
- ✅ Schema mutations → Dynamic column detection
- ✅ Type mismatches → Automatic type conversion

### UI Resilience
- ✅ Sidebar collapsed by default (reduces clutter)
- ✅ Manual refresh button for on-demand updates
- ✅ Timestamp display shows last cache update time
- ✅ Color-coded status indicators (🟢/🟡/🔴)

---

## 🎨 Customization

### Theming

The dashboard uses a dark theme optimized for executive display panels. To modify colors, edit the CSS in `app.py`:

```python
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        color: #00d9ff;  # Cyan accent color
    }
</style>
""", unsafe_allow_html=True)
```

### Metric Calculations

Modify KPI calculations in `calculate_kpi_metrics()`:

```python
def calculate_kpi_metrics() -> Tuple[int, float, float, str]:
    # Adjust thresholds, aggregation logic, or data sources here
```

---

## 📈 Performance Tips

1. **Optimize Database View**: Ensure `v_hourly_conversion_kpi` has proper indexes
2. **Connection Pooling**: Supabase client is cached via `@st.cache_resource`
3. **Data Caching**: All queries cached for 5 seconds (configurable)
4. **Lazy Loading**: Tables rendered only when visible
5. **Monitor Port 8501**: Streamlit runs on port 8501 by default

---

## 🚢 Deployment Options

### Option 1: Local Development
```bash
streamlit run app.py
```

### Option 2: Streamlit Cloud
1. Push code to GitHub repository
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Deploy from repo with environment secrets configured

### Option 3: Docker Containerization
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t f2c-analytics .
docker run -p 8501:8501 --env-file .env f2c-analytics
```

### Option 4: Production Hosting (Heroku/AWS/GCP)
1. Ensure port binding: `streamlit run app.py --server.port=$PORT`
2. Mount `.env` as secrets in deployment platform
3. Set `STREAMLIT_SERVER_HEADLESS=true` for servers

---

## 📊 Database Schema Reference

### `f2c_footfall_raw` Table
```sql
CREATE TABLE f2c_footfall_raw (
    id BIGINT PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT now(),
    device_id VARCHAR,
    live_occupancy INT,
    cumulative_footfall INT
);
```

### `f2c_pos_sales` Table
```sql
CREATE TABLE f2c_pos_sales (
    transaction_id VARCHAR PRIMARY KEY,
    timestamp TIMESTAMPTZ,
    sale_amount NUMERIC
);
```

### `v_hourly_conversion_kpi` View (Example)
```sql
CREATE VIEW v_hourly_conversion_kpi AS
SELECT
    DATE_TRUNC('hour', f.timestamp) as hour,
    COUNT(DISTINCT p.transaction_id) as transactions,
    MAX(f.cumulative_footfall) as footfall,
    (COUNT(DISTINCT p.transaction_id)::FLOAT / NULLIF(MAX(f.cumulative_footfall), 0) * 100) as conversion_rate
FROM f2c_footfall_raw f
LEFT JOIN f2c_pos_sales p ON DATE_TRUNC('hour', f.timestamp) = DATE_TRUNC('hour', p.timestamp)
GROUP BY DATE_TRUNC('hour', f.timestamp)
ORDER BY hour DESC;
```

---

## 🔐 Security Best Practices

✅ **DO:**
- Keep `.env` file in `.gitignore` (never commit)
- Use Row-Level Security (RLS) policies on Supabase tables
- Restrict API key scopes to minimal permissions
- Rotate Supabase keys quarterly
- Use environment variable secrets in production

❌ **DON'T:**
- Hardcode credentials in source code
- Commit `.env` to public repositories
- Share API keys in emails or Slack
- Use production keys in development
- Expose dashboard on public networks without authentication

---

## 🆘 Troubleshooting

### Dashboard won't load
```
Solution: Check Supabase URL and key in .env
$ streamlit run app.py --logger.level=debug
```

### "No data available" message
```
Solution: Verify tables exist and contain data
$ supabase inspection list-tables  # Check Supabase project
```

### Slow performance / high latency
```
Solution: 
1. Increase CACHE_TTL to 10-15 seconds
2. Verify Supabase indexes on timestamp columns
3. Check network connectivity
```

### Port 8501 already in use
```
Solution: Use custom port
$ streamlit run app.py --server.port=8502
```

---

## 📝 File Structure

```
f2c_bridge/
├── app.py                    # Main Streamlit application (MAIN ENTRY POINT)
├── mainbridge_copy.py        # Legacy bridge script (data ingestion)
├── requirements.txt          # Python dependencies
├── .env                      # Environment credentials (secure)
├── .gitignore               # Git ignore configuration
└── README.md                # This documentation
```

---

## 🤝 Integration with Edge Layer

### Receiving Jetson Orin Data

The `mainbridge_copy.py` script receives edge telemetry via HTTP POST:

```python
# Example edge device payload
payload = {
    "device_id": "Orin_Nano_Kengeri",
    "occupancy": 7,           # Current live occupancy
    "total_footfall": 63      # Cumulative count
}

# Sent to Supabase via HTTPS
supabase.table("f2c_footfall_raw").insert({
    "device_id": payload["device_id"],
    "live_occupancy": payload["occupancy"],
    "cumulative_footfall": payload["total_footfall"]
}).execute()
```

Ensure edge devices are configured to POST to this endpoint continuously.

---

## 📞 Support & Troubleshooting

For issues or questions:
1. Check Supabase project dashboard for table structure
2. Verify API key permissions (RLS policies)
3. Enable debug logging: `streamlit run app.py --logger.level=debug`
4. Review Streamlit documentation: https://docs.streamlit.io
5. Supabase docs: https://supabase.com/docs

---

## 📄 License & Attribution

**F2C Analytics Panel** © 2025 AIROWIRE NETWORKS PRIVATE LIMITED

Built with:
- 🎨 Streamlit - Web UI framework
- 🗄️ Supabase - PostgreSQL backend
- 📊 Plotly - Interactive visualizations
- 🐼 Pandas - Data processing

---

## 🎯 Version Info

- **Application Version**: 1.0.0
- **Last Updated**: 2025-05-18
- **Streamlit Version**: 1.28.1+
- **Python Version**: 3.9+

---

**Ready to monitor your retail operations in real-time!** 🚀📊
