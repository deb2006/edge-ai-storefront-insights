"""
F2C Analytics Panel - Real-time Retail Intelligence Dashboard
A Streamlit-based web UI for store managers and executives to monitor
live traffic velocity, gross revenues, and conversion KPIs.
"""

import os
import sys
import time
import json
import re
import ssl
import urllib3
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
from supabase import create_client, Client
from google import genai  # type: ignore
from google.genai import types  # type: ignore

# SSL verification bypass (for testing only - NOT for production)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

# ─────────────────────────────────────────────────────────────
# ENVIRONMENT & CONFIG
# ─────────────────────────────────────────────────────────────

import os as _os_module
import ssl
import urllib3
from urllib3.util.ssl_ import create_urllib3_context
import certifi
from pathlib import Path

# ⚠️ Aggressive SSL bypass for certificate issues
# (Temporary workaround - not for production)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Option 1: Disable SSL verification completely
ssl._create_default_https_context = ssl._create_unverified_context

# Option 2: Create custom context
try:
    ctx = create_urllib3_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
except:
    pass

# Force certifi to use system certificates
import os
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['CURL_CA_BUNDLE'] = certifi.where()

# Load .env from current directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = _os_module.getenv("SUPABASE_URL")
SUPABASE_KEY = _os_module.getenv("SUPABASE_KEY")
OPENAI_API_KEY = _os_module.getenv("OPENAI_API_KEY")
OPENAI_MODEL = _os_module.getenv("OPENAI_MODEL", "gpt-4o-mini")
GEMINI_API_KEY = _os_module.getenv("GEMINI_API_KEY")
SUPABASE_SQL_RPC = _os_module.getenv("SUPABASE_SQL_RPC", "execute_read_only_sql")
SUPABASE_SQL_RPC_PARAM = _os_module.getenv("SUPABASE_SQL_RPC_PARAM", "query_text")

# Initialize unified Google GenAI client
client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"CRITICAL GEMINI INIT ERROR: {e}")
        pass

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ Error: Missing SUPABASE_URL or SUPABASE_KEY in .env file")
    st.info(f"Looking for .env at: {env_path}")
    st.info(f"SUPABASE_URL found: {bool(SUPABASE_URL)}")
    st.info(f"SUPABASE_KEY found: {bool(SUPABASE_KEY)}")
    sys.exit(1)

# Cache TTL in seconds (database refresh interval)
CACHE_TTL = 60

# Some Windows environments set proxy variables to a closed local port. The
# dashboard talks directly to Supabase/OpenAI, so disable proxy inheritance here.
for proxy_var in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
    os.environ.pop(proxy_var, None)

# ─────────────────────────────────────────────────────────────
# STREAMLIT PAGE CONFIG
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="F2C Analytics Panel",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for a dark glass dashboard theme
st.markdown("""
<style>
    :root {
        --bg: #07111f;
        --bg-soft: #0d1a2d;
        --panel: rgba(14, 26, 44, 0.58);
        --panel-strong: rgba(18, 32, 54, 0.84);
        --panel-soft: rgba(118, 155, 210, 0.10);
        --ink: #eef4ff;
        --muted: #9cb0cb;
        --line: rgba(173, 201, 255, 0.16);
        --brand: #69a7ff;
        --brand-dark: #0d2343;
        --accent: #4de2b1;
        --warning: #ffb454;
        --shadow: 0 18px 48px rgba(0, 0, 0, 0.34);
    }
    * {
        font-family: 'IBM Plex Sans', 'Segoe UI', '-apple-system', 'BlinkMacSystemFont', sans-serif;
    }
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMainContainer"], [data-testid="stSidebar"] {
        background:
            radial-gradient(circle at top left, rgba(105, 167, 255, 0.18), transparent 28%),
            radial-gradient(circle at top right, rgba(77, 226, 177, 0.12), transparent 22%),
            linear-gradient(180deg, #0a1628 0%, #07111f 52%, #050c16 100%),
            var(--bg) !important;
        color: var(--ink) !important;
    }
    .block-container, .main, .css-1lcbmhc, .css-1d391kg, .css-18e3th9 {
        background-color: transparent !important;
        color: var(--ink) !important;
    }
    .block-container {
        max-width: 1480px;
        padding-top: 1.75rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3, [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 {
        color: var(--ink);
        letter-spacing: 0;
    }
    [data-testid="stMarkdownContainer"] h2 {
        font-size: 1.08rem;
        font-weight: 750;
        margin: 1.45rem 0 0.9rem;
    }
    [data-testid="stMarkdownContainer"] h3 {
        font-size: 0.98rem;
        font-weight: 700;
    }
    .hero-panel {
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(181, 211, 255, 0.18);
        border-radius: 8px;
        background:
            linear-gradient(135deg, rgba(11, 32, 61, 0.92), rgba(23, 53, 96, 0.72)),
            rgba(255,255,255,0.02);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        box-shadow: var(--shadow);
        padding: 26px 30px;
        margin-bottom: 1rem;
        color: #ffffff;
    }
    .hero-panel:after {
        content: "";
        position: absolute;
        inset: auto -8% -70% 54%;
        width: 420px;
        height: 420px;
        border-radius: 50%;
        border: 52px solid rgba(255,255,255,0.08);
    }
    .hero-kicker {
        color: #b8d7ff;
        font-size: 0.72rem;
        font-weight: 750;
        letter-spacing: 0.13em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }
    .hero-title {
        font-size: clamp(1.7rem, 2.6vw, 2.55rem);
        font-weight: 800;
        line-height: 1.08;
        margin: 0;
        color: #ffffff;
    }
    .hero-subtitle {
        max-width: 720px;
        margin: 0.65rem 0 0;
        color: #dceaff;
        font-size: 0.98rem;
    }
    .hero-meta {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 1.15rem;
    }
    .hero-chip {
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.20);
        border-radius: 999px;
        padding: 7px 12px;
        color: #f4f8ff;
        font-size: 0.78rem;
        font-weight: 650;
    }
    .metric-card {
        min-height: 142px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background:
            linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)),
            var(--panel);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        box-shadow: var(--shadow);
        padding: 18px 20px;
        position: relative;
        overflow: hidden;
    }
    .metric-card:before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, var(--brand), var(--accent));
    }
    .metric-label {
        color: var(--muted);
        font-size: 0.78rem;
        font-weight: 750;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    .metric-value {
        margin-top: 10px;
        color: var(--ink);
        font-size: clamp(1.55rem, 2vw, 2.15rem);
        line-height: 1.1;
        font-weight: 800;
    }
    .metric-note {
        margin-top: 10px;
        color: var(--muted);
        font-size: 0.82rem;
    }
    .metric-icon {
        position: absolute;
        right: 18px;
        top: 18px;
        display: grid;
        place-items: center;
        width: 36px;
        height: 36px;
        border-radius: 8px;
        background: rgba(105, 167, 255, 0.14);
        color: #d9e8ff;
        font-weight: 800;
        font-size: 1rem;
    }
    .info-banner {
        border: 1px solid var(--line);
        border-radius: 8px;
        background:
            linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.025)),
            var(--panel);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 0.95rem 1rem;
        color: var(--ink);
        margin-bottom: 1rem;
    }
    .info-banner strong {
        color: #ffffff;
    }
    div[data-testid="stVerticalBlock"] > div:has(.stPlotlyChart),
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stDataFrameContainer"]) {
        border: 1px solid var(--line);
        border-radius: 8px;
        background:
            linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02)),
            var(--panel);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        box-shadow: var(--shadow);
        padding: 1.05rem 1.15rem 1.2rem;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 1.1rem;
    }
    hr {
        border-color: rgba(95, 111, 134, 0.18) !important;
        margin: 1.4rem 0 !important;
    }
    .stAlert, .stInfo, .stWarning, .stError {
        background-color: var(--panel-strong) !important;
        border-color: var(--line) !important;
        color: var(--ink) !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: var(--brand);
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .stButton > button {
        border-radius: 8px;
        border: 1px solid rgba(136, 183, 255, 0.28);
        background: linear-gradient(135deg, rgba(92, 151, 255, 0.95), rgba(62, 120, 228, 0.92));
        color: #ffffff;
        font-weight: 700;
        box-shadow: 0 12px 24px rgba(17, 55, 115, 0.28);
    }
    .stButton > button:hover {
        border-color: rgba(178, 210, 255, 0.40);
        background: linear-gradient(135deg, rgba(112, 168, 255, 1), rgba(71, 130, 240, 0.96));
        color: #ffffff;
    }
    .stSlider, .stSelectbox, .stDateInput, .stTextInput {
        color: var(--ink) !important;
    }
    .stSelectbox > div > div,
    .stSlider [data-baseweb="slider"],
    .stDateInput > div,
    .stTextInput > div > div {
        background: var(--panel-strong) !important;
        border-color: var(--line) !important;
    }
    [data-testid="stChatInput"] {
        margin: 0.25rem 0 1rem !important;
        border: 1px solid rgba(173, 201, 255, 0.20) !important;
        border-radius: 8px !important;
        background:
            linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.025)),
            rgba(6, 14, 27, 0.82) !important;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.28) !important;
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
    }
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] textarea,
    [data-testid="stChatInput"] textarea:focus {
        color: #d1dce8 !important;
        background: rgba(6, 14, 27, 0.88) !important;
        border-radius: 8px !important;
        caret-color: var(--accent) !important;
        -webkit-text-fill-color: var(--ink) !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: rgba(221, 234, 255, 0.72) !important;
        -webkit-text-fill-color: rgba(221, 234, 255, 0.72) !important;
    }
    [data-testid="stChatInput"] button {
        background: rgba(105, 167, 255, 0.16) !important;
        color: var(--ink) !important;
    }
    [data-testid="stBottomBlockContainer"] {
        background: transparent !important;
        pointer-events: none;
    }
    [data-testid="stBottomBlockContainer"] [data-testid="stChatInput"] {
        pointer-events: auto;
    }
    [data-testid="stChatMessage"] {
        border: 1px solid rgba(173, 201, 255, 0.12);
        border-radius: 8px;
        background: rgba(10, 22, 40, 0.45);
        padding: 0.35rem 0.75rem;
        margin-bottom: 0.65rem;
    }
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] h1,
    [data-testid="stChatMessage"] h2,
    [data-testid="stChatMessage"] h3,
    [data-testid="stChatMessage"] strong,
    [data-testid="stChatMessage"] em {
        color: #eef4ff !important;
    }
    [data-testid="stChatMessage"] pre {
        background-color: #050c16 !important;
        border: 1px solid rgba(173, 201, 255, 0.16) !important;
        border-radius: 6px !important;
        padding: 10px !important;
    }
    [data-testid="stChatMessage"] code {
        background-color: #050c16 !important;
        color: #eef4ff !important;
    }
    div[data-testid="stDataFrameContainer"], .stDataFrame, .stTable {
        background-color: transparent !important;
        color: var(--ink) !important;
    }
    div[data-testid="stDataFrameContainer"] table,
    .stDataFrame table,
    .stTable table {
        background-color: rgba(8, 18, 33, 0.72) !important;
        color: var(--ink) !important;
        border-color: var(--line) !important;
    }
    div[data-testid="stDataFrameContainer"] th,
    .stDataFrame th,
    .stTable th,
    div[data-testid="stDataFrameContainer"] td,
    .stDataFrame td,
    .stTable td {
        color: var(--ink) !important;
        border-color: var(--line) !important;
    }
    div[data-testid="stDataFrameContainer"] th,
    .stDataFrame th,
    .stTable th {
        background-color: rgba(105, 167, 255, 0.12) !important;
    }
    div[data-testid="stDataFrameContainer"] tbody tr:nth-child(even),
    .stDataFrame tbody tr:nth-child(even),
    .stTable tbody tr:nth-child(even) {
        background-color: rgba(255,255,255,0.02) !important;
    }
    div[data-testid="stDataFrameContainer"] tbody tr:hover,
    .stDataFrame tbody tr:hover,
    .stTable tbody tr:hover {
        background-color: rgba(105, 167, 255, 0.10) !important;
    }
    .footer {
        text-align: center;
        color: var(--muted);
        font-size: 0.78rem;
        padding: 1rem 0 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SUPABASE CLIENT INITIALIZATION
# ─────────────────────────────────────────────────────────────

@st.cache_resource
def get_supabase_client() -> Client:
    """Initialize and cache Supabase client connection."""
    try:
        import httpx
        
        # Create custom httpx client with SSL disabled
        client = httpx.Client(verify=False, trust_env=False)
        
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Override the default session
        import postgrest
        supabase_client.postgrest.session = client
        
        return supabase_client
    except Exception as e:
        st.error(f"Failed to initialize Supabase client: {e}")
        sys.exit(1)


supabase = get_supabase_client()


def friendly_exception_message(error: Exception) -> str:
    """Convert noisy network/database exceptions into a user-facing status."""
    message = str(error)
    if "WinError 10061" in message or "actively refused" in message:
        return "Connection refused. Check your network, proxy, firewall, and Supabase/API availability."
    if "ConnectError" in message or "ConnectTimeout" in message:
        return "Could not reach the remote service. Check your internet connection and service URL."
    if "401" in message or "Unauthorized" in message:
        return "Authentication failed. Check the relevant API key in .env."
    if "429" in message or "Too Many Requests" in message:
        return "OpenAI rate limit or quota was reached. Check project billing, usage limits, or try again later."
    if "404" in message:
        return "Requested endpoint was not found. Check the Supabase URL, RPC name, or API route."
    return message


def show_notice_once(level: str, key: str, message: str) -> None:
    """Avoid flooding the dashboard with repeated copies of the same failure."""
    notice_key = f"notice_{key}"
    if st.session_state.get(notice_key):
        return

    st.session_state[notice_key] = True
    if level == "error":
        st.error(message)
    elif level == "warning":
        st.warning(message)
    else:
        st.info(message)

# ─────────────────────────────────────────────────────────────
# DATA FETCHING FUNCTIONS
# ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=CACHE_TTL)
def fetch_hourly_kpi_data() -> Optional[pd.DataFrame]:
    """
    Fetch processed KPI data from the v_hourly_conversion_kpi view.
    Returns aggregated hourly metrics with conversion rates.
    """
    try:
        response = supabase.table("v_hourly_conversion_kpi").select("*").execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            return df
        else:
            st.warning("⚠️ v_hourly_conversion_kpi view has no rows")
            
            # Fallback: compute from raw tables
            footfall_df = fetch_footfall_raw()
            sales_df = fetch_sales_data()
            
            if footfall_df is not None and sales_df is not None:
                st.warning("⚠️ Using computed KPI from raw tables (view doesn't have data)")
            
            return None
    except Exception as e:
        show_notice_once(
            "error",
            "kpi_fetch",
            f"KPI data is temporarily unavailable. {friendly_exception_message(e)}",
        )
        return None


@st.cache_data(ttl=CACHE_TTL)
def fetch_footfall_raw() -> Optional[pd.DataFrame]:
    """
    Fetch raw footfall metrics from f2c_footfall_raw table.
    Returns edge sensor telemetry with occupancy and cumulative metrics.
    """
    try:
        response = supabase.table("f2c_footfall_raw") \
            .select("*") \
            .order("timestamp", desc=True) \
            .limit(10) \
            .execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            return df
        else:
            st.warning("⚠️ No footfall data returned from Supabase")
            return None
    except Exception as e:
        show_notice_once(
            "error",
            "footfall_fetch",
            f"Footfall data is temporarily unavailable. {friendly_exception_message(e)}",
        )
        return None


@st.cache_data(ttl=CACHE_TTL)
def fetch_sales_data() -> Optional[pd.DataFrame]:
    """
    Fetch transaction data from f2c_pos_sales table.
    Returns aggregated sales metrics.
    """
    try:
        response = supabase.table("f2c_pos_sales").select("*").execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            return df
        return None
    except Exception as e:
        show_notice_once(
            "warning",
            "sales_fetch",
            f"Sales data is temporarily unavailable. {friendly_exception_message(e)}",
        )
        return None


@st.cache_data(ttl=CACHE_TTL)
def get_node_heartbeat_status() -> Dict[str, str]:
    """
    Check node connectivity status by fetching the most recent footfall entry.
    Returns device_id and status indicator.
    """
    try:
        response = supabase.table("f2c_footfall_raw") \
            .select("device_id, timestamp") \
            .order("timestamp", desc=True) \
            .limit(1) \
            .execute()
        
        if response.data:
            device_id = response.data[0].get("device_id", "Unknown")
            timestamp = response.data[0].get("timestamp")
            
            # Check if data is recent (within last 2 minutes)
            if timestamp:
                last_update = pd.to_datetime(timestamp)
                time_diff = datetime.utcnow() - last_update.replace(tzinfo=None)
                
                if time_diff < timedelta(minutes=2):
                    return {"device_id": device_id, "status": "🟢 Online"}
                else:
                    return {"device_id": device_id, "status": "🟡 Stale"}
            
        return {"device_id": "No Device", "status": "🔴 Offline"}
    except Exception as e:
        show_notice_once(
            "warning",
            "heartbeat_fetch",
            f"Heartbeat status is temporarily unavailable. {friendly_exception_message(e)}",
        )
        return {"device_id": "Error", "status": "🔴 Offline"}


# ─────────────────────────────────────────────────────────────
# METRIC CALCULATION FUNCTIONS
# ─────────────────────────────────────────────────────────────

def calculate_kpi_metrics() -> Tuple[int, float, float, str]:
    """
    Calculate executive-level KPI metrics.
    Returns: (total_traffic, gross_revenue, conversion_rate, node_status)
    """
    
    # Total Store Traffic (sum total_footfall from view)
    kpi_df = fetch_hourly_kpi_data()
    total_traffic = 0
    gross_revenue = 0.0
    conversion_rate = 0.0
    
    if kpi_df is not None and len(kpi_df) > 0:
        # Use view columns: total_footfall, revenue, conversion_rate_percent
        if "total_footfall" in kpi_df.columns:
            total_traffic = int(kpi_df["total_footfall"].sum())
        
        if "revenue" in kpi_df.columns:
            gross_revenue = float(kpi_df["revenue"].sum())
        
        conversion_columns = ["conversion_rate_percent", "conversion_rate_percentage", "conversion_rate"]
        for col in conversion_columns:
            if col in kpi_df.columns:
                conversion_rate = float(kpi_df[col].mean())
                break
    else:
        # Fallback to raw tables if view doesn't have data
        footfall_df = fetch_footfall_raw()
        if footfall_df is not None and len(footfall_df) > 0:
            total_traffic = int(footfall_df["cumulative_footfall"].max())
        
        sales_df = fetch_sales_data()
        if sales_df is not None and len(sales_df) > 0:
            gross_revenue = float(sales_df["sale_amount"].sum())
    
    # Node Heartbeat Monitor
    heartbeat = get_node_heartbeat_status()
    node_status = f"{heartbeat['device_id']} • {heartbeat['status']}"
    
    return total_traffic, gross_revenue, conversion_rate, node_status


# ─────────────────────────────────────────────────────────────
# UI COMPONENTS
# ─────────────────────────────────────────────────────────────

def render_metric_card(label: str, value: str, note: str, icon: str) -> None:
    """Render a branded KPI card with stable corporate styling."""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">{icon}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_scorecard():
    """Panel 1: Executive KPI Scorecard Grid"""
    st.markdown("## Executive KPI Scorecard")
    
    total_traffic, gross_revenue, conversion_rate, node_status = calculate_kpi_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card("Total Store Traffic", f"{total_traffic:,}", "Cumulative footfall", "TF")
    
    with col2:
        render_metric_card("Gross Revenue", f"${gross_revenue:,.2f}", "Aggregate sales volume", "RV")
    
    with col3:
        render_metric_card("Conversion Rate", f"{conversion_rate:.2f}%", "Average hourly KPI", "CR")
    
    with col4:
        render_metric_card("Node Heartbeat", node_status, "Backend connectivity", "HB")


def render_trend_and_telemetry():
    """Panel 2: Interactive Real-Time Trend Grid with Live Telemetry"""
    st.markdown("## Real-Time Analytics")
    
    col_chart, col_table = st.columns([0.66, 0.34])
    
    with col_chart:
        st.subheader("Conversion Performance Chart")
        kpi_df = fetch_hourly_kpi_data()
        
        if kpi_df is not None and len(kpi_df) > 0:
            try:
                # Ensure proper sorting
                if "hour" in kpi_df.columns:
                    kpi_df = kpi_df.sort_values("hour")
                
                conversion_columns = ["conversion_rate_percent", "conversion_rate_percentage", "conversion_rate"]
                conversion_col = next((col for col in conversion_columns if col in kpi_df.columns), None)
                x_axis = kpi_df.get("hour", kpi_df.get("report_hour", kpi_df.index))
                
                if conversion_col is not None:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=x_axis,
                        y=kpi_df[conversion_col],
                        mode="lines+markers",
                        name="Conversion Rate (%)",
                        line=dict(color="#0b4ea2", width=3),
                        marker=dict(size=7, color="#18b57e", line=dict(color="#ffffff", width=1)),
                        fill="tozeroy",
                        fillcolor="rgba(11, 78, 162, 0.10)"
                    ))
                    
                    fig.update_layout(
                        title="Hourly Conversion Performance",
                        xaxis_title="Time",
                        yaxis_title="Conversion Rate (%)",
                        hovermode="x unified",
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        legend_bgcolor="rgba(0,0,0,0)",
                        font=dict(size=11, color="#eef4ff"),
                        title_font=dict(size=15, color="#eef4ff"),
                        xaxis=dict(
                            showgrid=True,
                            gridcolor="rgba(173, 201, 255, 0.12)",
                            zeroline=False,
                            color="#9cb0cb"
                        ),
                        yaxis=dict(
                            showgrid=True,
                            gridcolor="rgba(173, 201, 255, 0.12)",
                            zeroline=False,
                            color="#9cb0cb"
                        ),
                        margin=dict(l=40, r=20, t=56, b=40)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No conversion rate data available")
            except Exception as e:
                st.warning(f"⚠️ Error rendering chart: {e}")
        else:
            st.info("📭 No KPI data available yet")
    
    with col_table:
        st.subheader("Live Edge Telemetry (Last 10)")
        footfall_df = fetch_footfall_raw()
        
        if footfall_df is not None and len(footfall_df) > 0:
            try:
                # Format display dataframe
                display_df = footfall_df[["timestamp", "device_id", "live_occupancy", "cumulative_footfall"]].copy()
                display_df["timestamp"] = display_df["timestamp"].dt.strftime("%H:%M:%S")
                display_df = display_df.rename(columns={
                    "timestamp": "Time",
                    "device_id": "Device",
                    "live_occupancy": "Occupancy",
                    "cumulative_footfall": "Total"
                })
                
                st.dataframe(display_df, use_container_width=True, height=400)
            except Exception as e:
                st.warning(f"⚠️ Error rendering telemetry table: {e}")
        else:
            st.info("📭 No telemetry data available yet")


def render_analytical_deep_dive():
    """Panel 3: Analytical Deep-Dive Log View"""
    st.markdown("## Analytical Deep-Dive")
    
    kpi_df = fetch_hourly_kpi_data()
    
    if kpi_df is not None and len(kpi_df) > 0:
        st.subheader("Hourly Conversion KPI View (v_hourly_conversion_kpi)")
        
        # Add filtering and sorting capabilities
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            if "hour" in kpi_df.columns:
                date_range = st.slider(
                    "Select time range:",
                    value=(kpi_df["hour"].min(), kpi_df["hour"].max()),
                    min_value=kpi_df["hour"].min(),
                    max_value=kpi_df["hour"].max(),
                    format="YYYY-MM-DD HH:mm"
                )
                filtered_df = kpi_df[
                    (kpi_df["hour"] >= date_range[0]) & 
                    (kpi_df["hour"] <= date_range[1])
                ]
            else:
                filtered_df = kpi_df
        
        with col_filter2:
            sort_column = st.selectbox(
                "Sort by:",
                options=filtered_df.columns,
                index=0
            )
        
        # Sort and display
        try:
            filtered_df = filtered_df.sort_values(sort_column, ascending=False)
            filtered_count = len(filtered_df)
            total_count = len(kpi_df)

            st.markdown(
                f"""
                <div class="info-banner">
                    <strong>Filtered dataset:</strong> showing {filtered_count} row(s) out of {total_count}.
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.dataframe(filtered_df, use_container_width=True, height=500)

            st.markdown("### Summary")

            if filtered_count == 0:
                st.info("No rows match the current filter.")
            elif filtered_count == 1:
                st.markdown(
                    """
                    <div class="info-banner">
                        <strong>Single record selected.</strong> Distribution statistics are not meaningful for one row,
                        so this view shows the record values directly instead of repeated summary numbers.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.dataframe(filtered_df.transpose(), use_container_width=True)
            else:
                numeric_summary = filtered_df.describe(include="number")
                if not numeric_summary.empty:
                    st.dataframe(numeric_summary, use_container_width=True)
                else:
                    st.info("No numeric columns are available for summary statistics.")
        except Exception as e:
            st.warning(f"⚠️ Error processing data: {e}")
    else:
        st.info("📭 No analytical data available yet")


# ─────────────────────────────────────────────────────────────
# MAIN APPLICATION
# ─────────────────────────────────────────────────────────────

# ---------------------------------------------------------------------------
# AI DATA ASSISTANT - API EXECUTION WRAPPER (GEMINI & OPENAI INTEGRATIONS)
# ---------------------------------------------------------------------------

def generate_sql_with_gemini(user_question: str) -> str:
    """Translates user queries to PostgreSQL using gemini-2.5-flash-lite with a 429/503 retry safety mechanism."""
    if not client:
        return ""
    schema_context = """
    You are an elite data assistant for a retail tracking pipeline. Translate human questions into valid, optimized PostgreSQL queries.
    Available database assets:
    1. Table: f2c_footfall_raw (timestamp, device_id, live_occupancy, cumulative_footfall)
    2. Table: f2c_pos_sales (transaction_id, timestamp, sale_amount)
    3. View: v_hourly_conversion_kpi (report_hour, total_footfall, completed_sales, revenue, conversion_rate_percentage)
    CRITICAL: You must return ONLY a raw JSON object matching the requested schema. Do not include markdown code block syntax formatting wrappers.
    """
    
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=f"User question: {user_question}\n\nReturn a JSON object with a single key 'sql' containing the PostgreSQL query.",
                config=types.GenerateContentConfig(
                    system_instruction=schema_context,
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            data_response = json.loads(response.text)
            return data_response.get("sql", "")
        except Exception as e:
            # Catch rate limiting or service drops, wait, and retry
            if "429" in str(e) or "503" in str(e):
                time.sleep(2)
                continue
            st.error(f"Gemini Translation Failure: {e}")
            return ""
    return ""

def synthesize_natural_response(user_question: str, raw_db_data: list) -> str:
    """Converts raw table JSON returned by Supabase back into an operational sentence using gemini-2.5-flash-lite."""
    if not client:
        return str(raw_db_data)
    prompt = f'User asked: "{user_question}". DB returned raw payload: {json.dumps(raw_db_data)}. Summarize these data insights into a short, executive-friendly overview sentence for our retail console.'
    
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=prompt
            )
            return response.text
        except Exception as e:
            if "429" in str(e) or "503" in str(e):
                time.sleep(2)
                continue
            return f"Data compiled successfully: {raw_db_data}"
    return str(raw_db_data)

SQL_GENERATION_SYSTEM_PROMPT = """
You are a PostgreSQL analyst for a retail telemetry dashboard.
Return ONLY one raw PostgreSQL SELECT query. Do not include markdown, prose,
comments, code fences, explanations, or trailing semicolons.

Allowed targets:
1. f2c_footfall_raw
   - timestamp timestamptz
   - device_id varchar
   - live_occupancy int8
   - cumulative_footfall int8
2. f2c_pos_sales
   - transaction_id varchar primary key
   - timestamp timestamptz
   - sale_amount numeric
3. v_hourly_conversion_kpi
   - report_hour timestamptz
   - total_footfall int4
   - completed_sales int8
   - revenue numeric
   - conversion_rate_percentage numeric

Rules:
- Generate read-only PostgreSQL only.
- Use SELECT or WITH ... SELECT only.
- Prefer v_hourly_conversion_kpi for conversion, hourly, or joined sales and
  footfall questions.
- Add a LIMIT of 100 unless the query is a scalar aggregate.
- If the question cannot be answered from the schema, return:
  SELECT 'This question cannot be answered from the available dashboard schema.' AS answer
"""

ANSWER_SYNTHESIS_SYSTEM_PROMPT = """
You are a concise retail analytics assistant. Explain the query result in a
friendly business sentence. Do not mention internal implementation details
unless the user asks. If there are no rows, say that no matching data was found.
"""

DESTRUCTIVE_SQL_KEYWORDS = ("DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE")


def call_llm(messages: List[Dict[str, str]], temperature: float = 0.0) -> str:
    """Call the configured LLM using httpx so no extra SDK dependency is required."""
    if not OPENAI_API_KEY:
        raise RuntimeError("Missing OPENAI_API_KEY in .env.")

    import httpx

    payload = {
        "model": OPENAI_MODEL,
        "messages": messages,
        "temperature": temperature,
    }
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=45.0, verify=False, trust_env=False) as client:
            response = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            if response.status_code >= 400:
                raise RuntimeError(f"{response.status_code} {response.text[:500]}")
            data = response.json()
    except Exception as e:
        raise RuntimeError(f"OpenAI API request failed. {friendly_exception_message(e)}") from e

    return data["choices"][0]["message"]["content"].strip()


def clean_generated_sql(raw_sql: str) -> str:
    """Remove common LLM formatting wrappers before validation."""
    sql = raw_sql.strip()
    sql = re.sub(r"^```(?:sql|postgresql)?\s*", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s*```$", "", sql)
    return sql.strip()


def validate_read_only_sql(sql: str) -> str:
    """Block destructive SQL and allow only a single SELECT-style statement."""
    cleaned_sql = clean_generated_sql(sql).rstrip(";").strip()
    upper_sql = cleaned_sql.upper()

    for keyword in DESTRUCTIVE_SQL_KEYWORDS:
        if re.search(rf"\b{keyword}\b", upper_sql):
            raise ValueError(f"Blocked unsafe SQL keyword: {keyword}")

    if ";" in cleaned_sql:
        raise ValueError("Blocked multi-statement SQL. Only one SELECT query is allowed.")

    if not re.match(r"^\s*(SELECT|WITH)\b", cleaned_sql, flags=re.IGNORECASE):
        raise ValueError("Only SELECT or WITH ... SELECT queries are allowed.")

    return cleaned_sql


def fallback_sql_from_question(question: str) -> Optional[str]:
    """Use deterministic read-only SQL for common dashboard questions if the LLM is unavailable."""
    q = question.lower()
    
    # Determine the date range filter based on whether the user asks for yesterday
    is_yesterday = "yesterday" in q
    if is_yesterday:
        date_filter = "WHERE report_hour >= date_trunc('day', now() - interval '1 day') AND report_hour < date_trunc('day', now())"
    else:
        date_filter = "WHERE report_hour >= date_trunc('day', now())"

    if "heartbeat" in q or "node" in q or "device" in q:
        return """
        SELECT timestamp, device_id, live_occupancy
        FROM f2c_footfall_raw
        ORDER BY timestamp DESC
        LIMIT 1
        """

    if "conversion" in q or "convert" in q:
        return f"""
        SELECT
            ROUND((SUM(completed_sales)::numeric / NULLIF(SUM(total_footfall), 0)) * 100, 2)
                AS conversion_rate_percentage,
            SUM(total_footfall) AS total_footfall,
            SUM(completed_sales) AS completed_sales,
            SUM(revenue) AS revenue
        FROM v_hourly_conversion_kpi
        {date_filter}
        """

    if "revenue" in q or "sales" in q:
        return f"""
        SELECT
            SUM(revenue) AS revenue,
            SUM(completed_sales) AS completed_sales
        FROM v_hourly_conversion_kpi
        {date_filter}
        """

    if "footfall" in q or "traffic" in q:
        return f"""
        SELECT
            SUM(total_footfall) AS total_footfall
        FROM v_hourly_conversion_kpi
        {date_filter}
        """

    if "occupancy" in q and any(term in q for term in ("average", "avg", "mean")):
        # Occupancy raw telemetry queries can restrict to yesterday's date bounds
        occupancy_date_filter = "WHERE timestamp >= date_trunc('day', now() - interval '1 day') AND timestamp < date_trunc('day', now())" if is_yesterday else "WHERE timestamp >= date_trunc('day', now())"
        return f"""
        SELECT
            ROUND(AVG(live_occupancy)::numeric, 2) AS average_occupancy,
            MIN(live_occupancy) AS min_occupancy,
            MAX(live_occupancy) AS max_occupancy,
            COUNT(*) AS sample_count
        FROM (
            SELECT live_occupancy
            FROM f2c_footfall_raw
            {occupancy_date_filter}
            ORDER BY timestamp DESC
            LIMIT 100
        ) recent_occupancy
        """

    if "occupancy" in q:
        occupancy_date_filter = "WHERE timestamp >= date_trunc('day', now() - interval '1 day') AND timestamp < date_trunc('day', now())" if is_yesterday else "WHERE timestamp >= date_trunc('day', now())"
        return f"""
        SELECT timestamp, device_id, live_occupancy
        FROM f2c_footfall_raw
        {occupancy_date_filter}
        ORDER BY timestamp DESC
        LIMIT 10
        """

    return None


def generate_sql_from_question(question: str) -> Tuple[str, bool]:
    """Step A: Convert a natural language question into read-only SQL."""
    try:
        raw_sql = call_llm(
            [
                {"role": "system", "content": SQL_GENERATION_SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            temperature=0.0,
        )
        used_openai = True
    except RuntimeError as e:
        fallback_sql = fallback_sql_from_question(question)
        if fallback_sql:
            return validate_read_only_sql(fallback_sql), False
        raise e

    return validate_read_only_sql(raw_sql), used_openai


def execute_read_only_sql(sql: str) -> List[Dict]:
    """Step B: Execute SQL through a safe Supabase RPC/read-only endpoint."""
    safe_sql = validate_read_only_sql(sql)

    try:
        response = supabase.rpc(SUPABASE_SQL_RPC, {SUPABASE_SQL_RPC_PARAM: safe_sql}).execute()
        return response.data or []
    except Exception as e:
        raise RuntimeError(
            f"Database query failed. Check the SQL, schema, Supabase network access, "
            f"or RPC '{SUPABASE_SQL_RPC}'. {friendly_exception_message(e)}"
        ) from e


def synthesize_answer(question: str, sql: str, rows: List[Dict]) -> Tuple[str, bool]:
    """Step C: Turn raw query rows into a user-friendly answer."""
    result_payload = json.dumps(rows[:50], default=str)
    try:
        answer = call_llm(
            [
                {"role": "system", "content": ANSWER_SYNTHESIS_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Question: {question}\n"
                        f"SQL: {sql}\n"
                        f"Rows returned: {len(rows)}\n"
                        f"JSON result sample: {result_payload}"
                    ),
                },
            ],
            temperature=0.2,
        )
        return answer, True
    except RuntimeError:
        return synthesize_answer_locally(question, rows), False


def synthesize_answer_locally(question: str, rows: List[Dict]) -> str:
    """Fallback answer writer for common aggregate result shapes."""
    if not rows:
        return "No matching dashboard data was found for that question."

    q = question.lower()
    time_prefix = "Yesterday's" if "yesterday" in q else "Today's"

    row = rows[0]
    if "device_id" in row and ("heartbeat" in q or "node" in q or "device" in q):
        return (
            f"The edge device '{row.get('device_id')}' is reporting live. "
            f"The latest heartbeat timestamp was {row.get('timestamp')} with a "
            f"live occupancy reading of {int(row.get('live_occupancy') or 0)}."
        )

    conversion = row.get("conversion_rate_percentage") or row.get("conversion_rate_percent") or row.get("conversion_rate")
    if conversion is not None:
        return (
            f"{time_prefix} conversion rate is {float(conversion):.2f}% "
            f"from {int(row.get('completed_sales') or 0)} completed sales and "
            f"{int(row.get('total_footfall') or 0)} total footfall."
        )

    if "revenue" in row:
        revenue = float(row.get("revenue") or 0)
        sales = int(row.get("completed_sales") or 0)
        return f"{time_prefix} revenue is ${revenue:,.2f} across {sales} completed sales."

    if "total_footfall" in row:
        return f"{time_prefix} total footfall is {int(row.get('total_footfall') or 0)}."

    if "average_occupancy" in row:
        average_occupancy = float(row.get("average_occupancy") or 0)
        min_occupancy = int(row.get("min_occupancy") or 0)
        max_occupancy = int(row.get("max_occupancy") or 0)
        sample_count = int(row.get("sample_count") or 0)
        label = "yesterday" if "yesterday" in q else "latest"
        return (
            f"The average live occupancy across the {label} {sample_count} readings is "
            f"{average_occupancy:.2f}, with a range from {min_occupancy} to {max_occupancy}."
        )

    return f"I found {len(rows)} matching row(s). The first result is: {json.dumps(row, default=str)}"


# ---------------------------------------------------------------------------
# AI DATA ASSISTANT - UI RENDERING CODE
# ---------------------------------------------------------------------------

def render_ai_data_assistant():
    """Render a natural language chat assistant near the top of the dashboard."""
    col_title, col_clear = st.columns([0.8, 0.2])
    with col_title:
        st.markdown("## AI Data Assistant")
    with col_clear:
        def clear_chat_history():
            st.session_state.messages = []
        
        st.button("🗑️ Clear Chat", key="clear_chat_history_btn", use_container_width=True, on_click=clear_chat_history)
    st.caption("Ask about footfall, occupancy, sales, revenue, or conversion performance.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    input_area = st.container()
    with input_area:
        prompt = st.chat_input(
            "Ask a data question, e.g. What was today's conversion rate?",
            key="ai_data_assistant_prompt",
        )
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            sql = ""
            used_gemini = False
            used_openai_for_sql = False

            with st.spinner("Building a safe read-only query..."):
                # 1. Try Gemini first
                gemini_sql = generate_sql_with_gemini(prompt)
                if gemini_sql:
                    # 2. Clean, validate, and screen the returned SQL query
                    sql = validate_read_only_sql(gemini_sql)
                    used_gemini = True
                else:
                    try:
                        sql, used_openai_for_sql = generate_sql_from_question(prompt)
                    except Exception as e:
                        raise RuntimeError(
                            "Both Gemini and OpenAI services are currently out of quota or unavailable. "
                            "Please check your API key settings or ask a standard dashboard question "
                            "(e.g., 'conversion rate', 'gross revenue', 'footfall', or 'node status') "
                            "to trigger the offline local backup."
                        ) from e

            with st.spinner("Querying Supabase..."):
                if used_gemini:
                    # Direct Supabase RPC execution as requested
                    response = supabase.rpc("execute_read_only_sql", {"query_text": sql}).execute()
                    rows = response.data or []
                else:
                    rows = execute_read_only_sql(sql)

            with st.spinner("Summarizing the result..."):
                if used_gemini:
                    answer = synthesize_natural_response(prompt, rows)
                    used_gemini_for_answer = True
                    used_openai_for_answer = False
                else:
                    answer, used_openai_for_answer = synthesize_answer(prompt, sql, rows)
                    used_gemini_for_answer = False

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sql": sql,
                    "rows": rows[:25],
                    "used_gemini": used_gemini or used_gemini_for_answer,
                    "used_openai": (not used_gemini) and (used_openai_for_sql or used_openai_for_answer),
                }
            )
        except ValueError as e:
            error_message = f"Security boundary blocked the generated query: {e}"
            st.session_state.messages.append({"role": "assistant", "content": error_message})
        except Exception as e:
            error_message = f"I could not complete that data request: {e}"
            st.session_state.messages.append({"role": "assistant", "content": error_message})

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("used_gemini"):
                st.caption("⚡ Powered by Gemini 2.5 Flash-lite")
            elif message.get("used_openai"):
                st.caption("Powered by OpenAI")
            if message.get("sql"):
                with st.expander("SQL used"):
                    st.code(message["sql"], language="sql")
            if message.get("rows"):
                st.dataframe(pd.DataFrame(message["rows"]), use_container_width=True)


def main():
    """Main application entry point."""
    
    # Header
    st.markdown("""
    <div class="hero-panel">
        <div class="hero-kicker">Enterprise Operations Console</div>
        <h1 class="hero-title">F2C Analytics Panel</h1>
        <p class="hero-subtitle">
            From Frame to Commerce - real-time retail intelligence for traffic, revenue,
            conversion performance, and edge-device health.
        </p>
        <div class="hero-meta">
            <span class="hero-chip">Live Supabase feed</span>
            <span class="hero-chip">Executive KPI view</span>
            <span class="hero-chip">Refresh interval: 5s</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add refresh button
    col_refresh, col_status = st.columns([1, 5])
    with col_refresh:
        if st.button("Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    with col_status:
        st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')} | Cache TTL: {CACHE_TTL}s")

    render_ai_data_assistant()
    st.divider()
    
    # Render dashboard panels
    try:
        render_kpi_scorecard()
        st.divider()
        
        render_trend_and_telemetry()
        st.divider()
        
        render_analytical_deep_dive()
        
    except Exception as e:
        st.error(f"❌ Dashboard error: {e}")
        st.caption("Please refresh the page or check your Supabase connection.")
    
    # Footer
    st.markdown("""
    <hr>
    <div class="footer">
        <p>F2C Analytics Engine - Powered by Streamlit + Supabase | Port: 8501</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
