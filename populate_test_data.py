"""
F2C Analytics Panel - Test Data Generator
Populates Supabase tables with sample data for testing
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
import ssl
import urllib3

# SSL bypass for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"Connecting to: {SUPABASE_URL}")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("✅ Connected to Supabase\n")

# ─────────────────────────────────────────────────────────────
# 1. Insert Test Footfall Data
# ─────────────────────────────────────────────────────────────

print("📊 Inserting footfall data...")

footfall_data = []
base_time = datetime.utcnow() - timedelta(hours=3)

for i in range(30):
    timestamp = base_time + timedelta(minutes=i*5)
    footfall_data.append({
        "timestamp": timestamp.isoformat(),
        "device_id": "Orin_Nano_Kengeri",
        "live_occupancy": 5 + (i % 10),
        "cumulative_footfall": 50 + (i * 3)
    })

try:
    response = supabase.table("f2c_footfall_raw").insert(footfall_data).execute()
    print(f"✅ Inserted {len(footfall_data)} footfall records\n")
except Exception as e:
    print(f"⚠️ Error inserting footfall data: {e}\n")

# ─────────────────────────────────────────────────────────────
# 2. Insert Test Sales Data
# ─────────────────────────────────────────────────────────────

print("💳 Inserting sales data...")

sales_data = []

for i in range(15):
    timestamp = base_time + timedelta(minutes=i*10)
    sales_data.append({
        "transaction_id": f"TXN_{datetime.utcnow().strftime('%Y%m%d')}_{i:04d}",
        "timestamp": timestamp.isoformat(),
        "sale_amount": 50 + (i * 15.5)
    })

try:
    response = supabase.table("f2c_pos_sales").insert(sales_data).execute()
    print(f"✅ Inserted {len(sales_data)} sales records\n")
except Exception as e:
    print(f"⚠️ Error inserting sales data: {e}\n")

# ─────────────────────────────────────────────────────────────
# 3. Verify Data
# ─────────────────────────────────────────────────────────────

print("🔍 Verifying data...\n")

try:
    footfall_count = supabase.table("f2c_footfall_raw").select("count").execute()
    print(f"✅ f2c_footfall_raw rows: {len(footfall_count.data)}")
except Exception as e:
    print(f"❌ Error: {e}")

try:
    sales_count = supabase.table("f2c_pos_sales").select("count").execute()
    print(f"✅ f2c_pos_sales rows: {len(sales_count.data)}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*50)
print("✅ TEST DATA POPULATED SUCCESSFULLY")
print("="*50)
print("\nNow refresh your Streamlit dashboard at:")
print("   http://localhost:8501")
print("\nYou should see:")
print("  • KPI metrics with values")
print("  • Conversion chart with data")
print("  • Telemetry table populated")
print("="*50)
