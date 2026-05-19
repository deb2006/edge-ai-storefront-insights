import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: Missing credentials in .env file.")
    exit(1)

# Initialize Supabase REST client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"❌ Initialization Failed: {e}")
    exit(1)

def save_to_supabase(payload):
    """
    Parses edge telemetry metrics and inserts them into the data lake.
    """
    try:
        # Explicit mapping matching table schema constraints
        row_data = {
            "device_id": payload.get("device_id", "Orin_Nano_Kengeri"),
            "live_occupancy": payload["occupancy"],
            "cumulative_footfall": payload["total_footfall"]
        }
        
        # Execute the native HTTPS API network call
        response = supabase.table("f2c_footfall_raw").insert(row_data).execute()
        
        # Log success output
        print(f"🌲 HTTPS Synced to Data Lake -> Occupancy: {row_data['live_occupancy']} | Total: {row_data['cumulative_footfall']}")
        return response
        
    except KeyError as ke:
        print(f"❌ Payload Parsing Error: Missing expected key {ke}")
    except Exception as e:
        print(f"❌ Supabase HTTPS API insertion failed: {e}")

# --- Example Driver execution (Simulating your DeepStream/HiveMQ payload hook) ---
if __name__ == "__main__":
    print("🚀 Bridge engine running natively via HTTPS. Listening for edge metrics...")
    
    # Mock data layout representing your live sensor data payload
    mock_payload = {
        "device_id": "Orin_Nano_Kengeri",
        "occupancy": 7,
        "total_footfall": 63
    }
    
    # Execute single entry verification trace
    save_to_supabase(mock_payload)