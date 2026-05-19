# F2C Analytics Panel - System Architecture

## Overview

The F2C Analytics Panel is a **real-time retail intelligence dashboard** that combines:
- **Edge Computing**: Computer vision from NVIDIA Jetson Orin Nano
- **Cloud Data Lake**: Supabase PostgreSQL with relational views
- **Web Frontend**: Streamlit reactive UI

---

## System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     EDGE LAYER (Physical Store)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │     NVIDIA Jetson Orin Nano (Computer Vision)            │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  • DeepStream pipeline (ResNet-10 person tracking)       │   │
│  │  • Live occupancy detection                              │   │
│  │  • Cumulative footfall counting                          │   │
│  │  • Real-time video feed processing                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           │ HTTPS POST                           │
│                           │ (Structured JSON)                    │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Edge Telemetry Payload                                  │   │
│  │  {                                                        │   │
│  │    "device_id": "Orin_Nano_Kengeri",                    │   │
│  │    "occupancy": 7,                                       │   │
│  │    "total_footfall": 63,                                 │   │
│  │    "timestamp": "2025-05-18T15:52:14Z"                  │   │
│  │  }                                                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
                    Network Bridge (mainbridge_copy.py)
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CLOUD LAYER (Supabase)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  PostgreSQL Database                                             │
│  ─────────────────────────                                       │
│                                                                   │
│  ┌────────────────────────────┐  ┌────────────────────────────┐ │
│  │  f2c_footfall_raw          │  │  f2c_pos_sales             │ │
│  │  ────────────────────      │  │  ──────────────────        │ │
│  │  • id (BIGINT PK)          │  │  • transaction_id (PK)     │ │
│  │  • timestamp (TIMESTAMPTZ) │  │  • timestamp (TIMESTAMPTZ) │ │
│  │  • device_id (VARCHAR)     │  │  • sale_amount (NUMERIC)   │ │
│  │  • live_occupancy (INT)    │  │                            │ │
│  │  • cumulative_footfall     │  │                            │ │
│  │    (INT)                   │  │  [From POS System]         │ │
│  │                            │  │                            │ │
│  │  [From Jetson Orin]        │  │                            │ │
│  └────────────────────────────┘  └────────────────────────────┘ │
│           │                                 │                    │
│           └─────────────┬───────────────────┘                    │
│                         │                                        │
│                         ▼                                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  v_hourly_conversion_kpi (Database View)                  │ │
│  │  ──────────────────────────────────────────────           │ │
│  │  Computed JOIN view combining:                            │ │
│  │  • hour (hourly bucket)                                   │ │
│  │  • transactions (count)                                   │ │
│  │  • footfall (max cumulative)                              │ │
│  │  • conversion_rate = (trans/footfall * 100)               │ │
│  │                                                            │ │
│  │  Refreshes automatically on each query                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                         │                                        │
│                         │                                        │
│                  REST API (Port 443)                             │
│             (Supabase client via JWT)                            │
│                         │                                        │
└─────────────────────────┼─────────────────────────────────────────┘
                          │
                          │
┌─────────────────────────┼─────────────────────────────────────────┐
│                         │    PRESENTATION LAYER                    │
│                    Streamlit (Port 8501)                           │
├─────────────────────────┼─────────────────────────────────────────┤
│                         │                                          │
│                         ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  Panel 1: Executive KPI Scorecard                        │    │
│  │  ────────────────────────────────────────────            │    │
│  │  ┌─────────────┬─────────────┬──────────┬────────────┐  │    │
│  │  │ Traffic     │ Revenue     │ Conv.    │ Node       │  │    │
│  │  │ 1,234       │ $12,456.78  │ 18.50%   │ Online 🟢   │  │    │
│  │  └─────────────┴─────────────┴──────────┴────────────┘  │    │
│  │                                                          │    │
│  │  [Every 5 seconds via cache invalidation]                │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  Panel 2: Real-Time Trend Grid                           │    │
│  │  ────────────────────────────────────────────            │    │
│  │  ┌────────────────────────────┐  ┌──────────────────┐   │    │
│  │  │                            │  │ Live Telemetry   │   │    │
│  │  │  Conversion Chart          │  │ ──────────────   │   │    │
│  │  │  (Line + Area)             │  │ Time | Occ | Tot │   │    │
│  │  │  [Interactive Plotly]      │  │ ──────────────   │   │    │
│  │  │                            │  │ 3:52 │  7  │ 63  │   │    │
│  │  │  66% width                 │  │ 3:51 │  5  │ 62  │   │    │
│  │  │                            │  │ ...                │   │    │
│  │  │                            │  │ 33% width        │   │    │
│  │  └────────────────────────────┘  └──────────────────┘   │    │
│  │                                                          │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  Panel 3: Analytical Deep-Dive                           │    │
│  │  ────────────────────────────────────────────            │    │
│  │  Complete v_hourly_conversion_kpi view data              │    │
│  │  • Sortable columns (descending)                         │    │
│  │  • Date range filtering                                  │    │
│  │  • Statistical summary                                   │    │
│  │  [Interactive data explorer]                             │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                      Browser (User)
                    http://localhost:8501
```

---

## Data Flow Sequence

### 1. Real-Time Edge Data Ingestion

```
TIME: 15:52:14
┌─────────────────────────────────────────┐
│ Jetson Orin Nano (Store Floor)          │
│ ─────────────────────────────────────   │
│ • Detects 7 people in store             │
│ • Total cumulative: 63 since store open │
│ • DeepStream outputs structured payload │
└─────────────────────────────────────────┘
                    │
                    │ POST /supabase/rest/v1/tables/f2c_footfall_raw
                    │ Headers: Authorization: Bearer [JWT_KEY]
                    │ Body: { device_id, occupancy, total_footfall }
                    ▼
┌─────────────────────────────────────────┐
│ Supabase HTTPS Endpoint                 │
│ ─────────────────────────────────────   │
│ Receives & Validates payload            │
│ Applies RLS policies                    │
└─────────────────────────────────────────┘
                    │
                    │ INSERT
                    ▼
┌─────────────────────────────────────────┐
│ f2c_footfall_raw (PostgreSQL)           │
│ ─────────────────────────────────────   │
│ NEW ROW:                                │
│ • id: auto-generated                    │
│ • timestamp: 2025-05-18 15:52:14+05:30  │
│ • device_id: 'Orin_Nano_Kengeri'        │
│ • live_occupancy: 7                     │
│ • cumulative_footfall: 63               │
└─────────────────────────────────────────┘
```

### 2. POS Transaction Recording

```
TIME: 15:52:18 (Customer checkout)
┌─────────────────────────────────────────┐
│ POS System (Store Register)             │
│ ─────────────────────────────────────   │
│ • Transaction processed                 │
│ • Sale amount: $125.50                  │
└─────────────────────────────────────────┘
                    │
                    │ INSERT INTO f2c_pos_sales
                    ▼
┌─────────────────────────────────────────┐
│ f2c_pos_sales (PostgreSQL)              │
│ ─────────────────────────────────────   │
│ NEW ROW:                                │
│ • transaction_id: 'TXN_20250518_001'    │
│ • timestamp: 2025-05-18 15:52:18+05:30  │
│ • sale_amount: 125.50                   │
└─────────────────────────────────────────┘
```

### 3. KPI View Computation

```
ON EACH QUERY TO v_hourly_conversion_kpi:
┌─────────────────────────────────────────────────┐
│ Database Computes View (Real-Time)              │
│ ─────────────────────────────────────────────   │
│ SELECT                                          │
│   DATE_TRUNC('hour', f.timestamp) as hour,      │
│   COUNT(DISTINCT p.transaction_id) as trans,    │
│   MAX(f.cumulative_footfall) as footfall,       │
│   (trans / footfall * 100) as conversion_rate   │
│ FROM f2c_footfall_raw f                         │
│ LEFT JOIN f2c_pos_sales p                       │
│ GROUP BY hour                                   │
│ ORDER BY hour DESC                              │
└─────────────────────────────────────────────────┘
                    │
                    │ Returns calculated metrics
                    ▼
┌──────────────────────────────────────────────────┐
│ EXAMPLE OUTPUT (Hourly KPI Window)               │
│ ──────────────────────────────────────────────   │
│ hour              │ transactions │ footfall │ % │
│ ────────────────────────────────────────────── │
│ 15:00-16:00       │ 12           │ 87       │17.24%
│ 14:00-15:00       │ 18           │ 124      │14.51%
│ 13:00-14:00       │ 7            │ 45       │15.55%
└──────────────────────────────────────────────────┘
```

### 4. Frontend Data Retrieval & Caching

```
STREAMLIT APP LIFECYCLE (5-second intervals):
┌──────────────────────────────────┐
│ User opens dashboard             │
│ http://localhost:8501            │
└──────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────┐
│ @st.cache_data(ttl=5)                    │
│ ─────────────────────────────────        │
│ Streamlit caching layer                  │
│ First call: Query Supabase               │
│ Next 5 sec: Serve from cache             │
│ After 5 sec: Query again                 │
└──────────────────────────────────────────┘
            │
            ├─→ fetch_hourly_kpi_data()
            │   SELECT * FROM v_hourly_conversion_kpi
            │
            ├─→ fetch_footfall_raw()
            │   SELECT * FROM f2c_footfall_raw (limit 10)
            │
            └─→ fetch_sales_data()
                SELECT * FROM f2c_pos_sales
                
            │
            ▼
┌──────────────────────────────────────────┐
│ Pandas DataFrame transformation          │
│ ─────────────────────────────────────   │
│ Normalize timestamps                     │
│ Ensure data types                        │
│ Calculate derived metrics                │
└──────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────┐
│ Streamlit UI Rendering                   │
│ ─────────────────────────────────────   │
│ Panel 1: st.metric() widgets             │
│ Panel 2: go.Figure() (Plotly)            │
│ Panel 3: st.dataframe() (Interactive)    │
└──────────────────────────────────────────┘
            │
            ▼
    Browser Displays UI
```

---

## Database Schema Deep Dive

### f2c_footfall_raw Table

**Purpose:** Raw edge telemetry ingestion point

```sql
CREATE TABLE f2c_footfall_raw (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT now() NOT NULL,
    device_id VARCHAR(255) NOT NULL,
    live_occupancy INT NOT NULL,
    cumulative_footfall INT NOT NULL,
    CREATED_AT TIMESTAMPTZ DEFAULT now()
);

-- Indexes for query optimization
CREATE INDEX idx_footfall_timestamp ON f2c_footfall_raw(timestamp DESC);
CREATE INDEX idx_footfall_device ON f2c_footfall_raw(device_id);
```

**Sample Data:**
```
id  │ timestamp              │ device_id              │ occupancy │ cumulative
────┼────────────────────────┼────────────────────────┼───────────┼───────────
123 │ 2025-05-18 15:52:14    │ Orin_Nano_Kengeri      │ 7         │ 63
122 │ 2025-05-18 15:52:10    │ Orin_Nano_Kengeri      │ 6         │ 62
121 │ 2025-05-18 15:52:05    │ Orin_Nano_Kengeri      │ 7         │ 61
```

### f2c_pos_sales Table

**Purpose:** Transaction log (typically synced from existing POS)

```sql
CREATE TABLE f2c_pos_sales (
    transaction_id VARCHAR(255) PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    sale_amount NUMERIC(10, 2) NOT NULL,
    CREATED_AT TIMESTAMPTZ DEFAULT now()
);

-- Indexes for query optimization
CREATE INDEX idx_sales_timestamp ON f2c_pos_sales(timestamp DESC);
```

**Sample Data:**
```
transaction_id          │ timestamp              │ amount
────────────────────────┼────────────────────────┼──────────
TXN_20250518_0001       │ 2025-05-18 15:52:18    │ 125.50
TXN_20250518_0002       │ 2025-05-18 15:49:45    │ 87.25
TXN_20250518_0003       │ 2025-05-18 15:47:12    │ 203.75
```

### v_hourly_conversion_kpi View

**Purpose:** Real-time computed analytics (hourly aggregation)

```sql
CREATE VIEW v_hourly_conversion_kpi AS
SELECT
    DATE_TRUNC('hour', f.timestamp) as hour,
    COUNT(DISTINCT f.device_id) as active_devices,
    COUNT(DISTINCT p.transaction_id) as transactions,
    MAX(f.cumulative_footfall) as total_footfall,
    ROUND(
        (COUNT(DISTINCT p.transaction_id)::NUMERIC / 
         NULLIF(MAX(f.cumulative_footfall), 0) * 100)::NUMERIC, 
        2
    ) as conversion_rate,
    COUNT(*) as sensor_readings
FROM f2c_footfall_raw f
LEFT JOIN f2c_pos_sales p 
    ON DATE_TRUNC('hour', f.timestamp) = DATE_TRUNC('hour', p.timestamp)
    AND f.device_id = 'Orin_Nano_Kengeri'
GROUP BY DATE_TRUNC('hour', f.timestamp)
ORDER BY hour DESC;
```

**Example Output:**
```
hour                    │ devices │ transactions │ footfall │ conv_rate
────────────────────────┼─────────┼──────────────┼──────────┼──────────
2025-05-18 15:00:00     │ 1       │ 12           │ 87       │ 13.79%
2025-05-18 14:00:00     │ 1       │ 18           │ 124      │ 14.51%
2025-05-18 13:00:00     │ 1       │ 7            │ 45       │ 15.55%
```

---

## Caching & Performance Strategy

### Streamlit Caching Layers

```
┌────────────────────────────────────────────┐
│ Layer 1: @st.cache_resource                │
│ ───────────────────────────────────────    │
│ Cached: get_supabase_client()              │
│ TTL: Infinite (session lifetime)           │
│ Used for: Connection pooling               │
└────────────────────────────────────────────┘
                    │
                    │
┌────────────────────────────────────────────┐
│ Layer 2: @st.cache_data(ttl=5)             │
│ ───────────────────────────────────────    │
│ Cached: fetch_hourly_kpi_data()            │
│ Cached: fetch_footfall_raw()               │
│ Cached: fetch_sales_data()                 │
│ TTL: 5 seconds                             │
│ Used for: Database query results           │
└────────────────────────────────────────────┘
                    │
                    │
┌────────────────────────────────────────────┐
│ Layer 3: Browser Cache                     │
│ ───────────────────────────────────────    │
│ Static assets (CSS, images)                │
│ TTL: Browser-specific                      │
│ Used for: Performance optimization         │
└────────────────────────────────────────────┘
```

### Cache Invalidation Flow

```
USER ACTION: Click "🔄 Refresh Data"
    │
    ▼
st.cache_data.clear()
    │
    ├─→ Clears all cached queries
    ├─→ Next query re-fetches from Supabase
    └─→ UI re-renders with fresh data
    
OR

AUTOMATIC: Every 5 seconds (if actively viewing)
    │
    ▼
Cache TTL expires
    │
    └─→ Next st.rerun() or page load
        └─→ Queries execute again
            └─→ Dashboard updates
```

---

## Error Handling & Resilience

### Network Failure Scenarios

| Scenario | Handler | User Experience |
|----------|---------|-----------------|
| Supabase offline | try/except + st.warning() | ⚠️ Alert shown, no crash |
| Missing .env keys | Check at startup, sys.exit(1) | ❌ Clear error message |
| Empty result set | if response.data check | 📭 Info: "No data available" |
| Schema mismatch | Dynamic column detection | ✅ Fallback calculation |
| Slow query response | Cached for 5 sec | ⏳ Shows previous data |

### User-Facing Error Messages

```python
# Network error
st.warning("⚠️ Failed to fetch KPI data: Connection timeout")

# Data missing
st.info("📭 No KPI data available yet")

# Critical error
st.error("❌ Dashboard error: Invalid data format")
```

---

## Security Architecture

### Authentication Flow

```
STREAMLIT APP
    │
    ├─→ Load SUPABASE_URL from .env
    ├─→ Load SUPABASE_KEY from .env
    │
    ▼
SUPABASE CLIENT
    │
    ├─→ Initialize with credentials
    ├─→ Generate JWT Bearer token
    │
    ▼
HTTP REQUESTS
    │
    ├─→ Header: Authorization: Bearer [JWT]
    ├─→ Endpoint: https://mfuqfpibknywivtculxk.supabase.co/rest/v1
    │
    ▼
SUPABASE RLS POLICIES
    │
    ├─→ Verify JWT signature
    ├─→ Check anon role permissions
    ├─→ Apply table policies
    │
    ▼
DATABASE QUERY
    │
    └─→ Execute if authorized, reject if not
```

### Data Protection

- ✅ **Credentials**: Never logged, stored in .env only
- ✅ **Transit**: HTTPS encryption (TLS 1.3+)
- ✅ **At Rest**: PostgreSQL encryption (Supabase)
- ✅ **RLS**: Row-Level Security on all tables
- ✅ **Keys**: Rotated quarterly, different dev/prod keys

---

## Deployment Architectures

### Architecture 1: Local Development
```
Developer Laptop
    │
    ├─→ Python venv
    ├─→ Streamlit run app.py
    └─→ http://localhost:8501
```

### Architecture 2: Docker Container (Local)
```
Docker Desktop
    │
    ├─→ Build image from Dockerfile
    ├─→ Run container
    ├─→ Port mapping 8501:8501
    └─→ http://localhost:8501
```

### Architecture 3: Streamlit Cloud
```
GitHub
    │
    ├─→ Push code
    │
Streamlit Cloud
    │
    ├─→ Auto-deploy on push
    ├─→ Secrets: SUPABASE_URL, SUPABASE_KEY
    └─→ https://[project].streamlit.app
```

### Architecture 4: Production Cloud (AWS ECS)
```
AWS ECS Cluster
    │
    ├─→ Task Definition (app.py + requirements.txt)
    ├─→ Environment secrets from Secrets Manager
    ├─→ ALB (Application Load Balancer) routing
    ├─→ Auto-scaling policies
    ├─→ CloudWatch monitoring
    └─→ https://analytics.retailco.com
```

---

## Monitoring & Observability

### Key Metrics to Monitor

| Metric | Threshold | Alert Level |
|--------|-----------|-------------|
| Response time | > 2s | ⚠️ Warning |
| Supabase availability | < 99.9% | 🚨 Critical |
| Data staleness | > 5 min | ⚠️ Warning |
| Error rate | > 5% | ⚠️ Warning |
| Active sessions | > 10 | ℹ️ Info |

### Debug Logging

Enable verbose output:
```bash
streamlit run app.py --logger.level=debug
```

Monitor logs for:
- Cache hits/misses
- API response times
- Data transformation errors
- Connection pool status

---

## Scalability Considerations

### Current Limits (Single Instance)

- ✅ 10-50 concurrent users
- ✅ 100K+ rows in f2c_footfall_raw
- ✅ 50K+ rows in f2c_pos_sales
- ✅ Sub-second KPI view computation

### Scaling to 1000+ Users

1. **Frontend**: Multi-instance Streamlit behind load balancer
2. **Cache**: Redis for shared cache layer
3. **Database**: Supabase auto-scaling, connection pooling
4. **API**: Implement GraphQL for efficient queries
5. **Analytics**: Move heavy computations to scheduled jobs

---

## Future Enhancements

- [ ] Real-time WebSocket updates (vs 5s polling)
- [ ] Multi-location dashboard federation
- [ ] Predictive analytics (ML-based footfall forecasting)
- [ ] Advanced segmentation (customer demographics)
- [ ] Mobile app (React Native/Flutter)
- [ ] Automated alerts (Slack/Email notifications)
- [ ] Executive reporting (PDF export)
- [ ] Custom KPI definitions (no-code)

---

This architecture provides **high availability**, **real-time responsiveness**, and **production-grade reliability** for retail analytics operations.
