# Heterogeneous Edge-Vision & Cloud-Intelligence Retail Framework

An asymmetric, end-to-end analytical pipeline that merges high-throughput edge computer vision tracking with conversational cloud business intelligence. This system isolates processing planes, running low-latency edge inference on-premise while leveraging serverless cloud LLM compilation to drive conversational database querying with zero hosting overhead.

---

## 🏗️ Architectural Topology & Core Data Flow

The framework operates via an asymmetric allocation of AI labor, ensuring zero cloud bandwidth bloat for video processing coupled with zero local compute requirements for semantic reasoning:

1. **Edge Perception Layer (NVIDIA Compute):** An NVIDIA Jetson Orin Nano processes live storefront video matrices locally (utilizing OpenCV / DeepStream vector layers). It strips out network bandwidth bloat by crunching complex pixel imagery right at the source, compressing raw video frames down into lightweight numerical integers (e.g., `live_occupancy: 14`).
2. **Telemetry Ingestion Bridge:** An unbuffered background Python data daemon captures local edge metrics from the storefront node and dispatches structured event payloads upstream via secure HTTPS requests.
3. **Analytical Matrix & View Engine:** A cloud-hosted Supabase (PostgreSQL) data lake aggregates incoming streaming telemetry (`f2c_footfall_raw`) and bridges spatial traffic logs directly against Point-of-Sale transaction records (`f2c_pos_sales`) through specialized database relations (`v_hourly_conversion_kpi`).
4. **Conversational Orchestration Console:** A centralized Streamlit web console provides executive analytics screens alongside a secure, natural language text interface powered by the `google-genai` SDK running `gemini-2.5-flash-lite`.

---

## 💬 Operational Mechanics: The Conversational Chat Loop

When an executive inputs an abstract query (e.g., *"How was our footfall yesterday afternoon?"*), the system avoids sending massive historical data sets or arbitrary code blocks. Instead, it coordinates state transitions across a strict three-step lifecycle:

### Step 1: Translating the Question to SQL (Semantic Compilation)
When a user submits a question via the Streamlit interface (`st.chat_input`), the app packages the phrase and routes it to the `gemini-2.5-flash-lite` model. This request includes the core database structure and structural schema hints, but containing **zero actual row records**:
> *"Here are the columns in my f2c_footfall_raw and f2c_pos_sales tables. Translate this question into a read-only PostgreSQL query."*

Gemini utilizes its language comprehension capabilities to behave as a deterministic compiler, translating the user's abstract temporal intent into a optimized, valid SQL query targeting our cloud database schemas.

### Step 2: Pulling the Live Data from Supabase (Data Extraction)
The Streamlit application intercepts the generated SQL payload from the model, executes an internal string-matching safety routine, and dispatches the query directly against the Supabase PostgreSQL data lake using secure project environment credentials. 

Supabase scans its indexed tables, evaluates the live telemetry vectors, compiles the relational dataset, and returns a raw, condensed JSON array back to the active Streamlit runtime.

### Step 3: Summarizing the Results (Natural Language Synthesis)
The Streamlit app captures the raw rows returned by the database engine and pipes them back to Gemini for final contextual synthesis:
> *"The database returned these raw rows. Summarize these specific numbers into a single, friendly, executive-level sentence for our retail console."*

Gemini reads the concise dataset matrix and responds with an operational, human-readable summary (e.g., *"Yesterday, the 'Orin_Nano_Kengeri' device recorded a total of 63 cumulative footfalls with an optimized conversion delta."*), which is rendered natively inside the Streamlit chat layout.

---

## 🛡️ Sandbox Security & SQL Injection Guardrails

To enforce absolute database isolation and guarantee that user prompts cannot mutate or corrupt structural schemas, the pipeline deploys a multi-layered gateway architecture:

* **Semantic Decoupling:** The AI model has zero direct write paths, execution access, or open socket channels to the database instance; it functions purely as an external code compiler generating text strings.
* **In-Flight Ingestion Filter:** The Streamlit controller intercepts the model's generated text payload before it reaches the cloud data lake, verifying the query against an explicit local keyword blocklist targeting structural mutations (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`).
* **Database RPC Isolation:** Validated SQL read strings are piped exclusively through a highly isolated Supabase database remote procedure call (`execute_read_only_sql`), running under restricted read-only role permissions to completely eliminate unauthorized execution vectors.

---

## 🛠️ Stack Composition Matrix

* **Edge Core Hardware:** NVIDIA Jetson Orin Nano
* **Cloud Infrastructure & Data Lake:** Supabase / PostgreSQL Engine
* **UI Orchestration Frame:** Streamlit Framework
* **Cloud Intelligence Client:** Google GenAI SDK (`gemini-2.5-flash-lite`) utilizing strict Pydantic JSON schema generation modes.
* **Core Language Runtime:** Python 3.10+

---

## ⚙️ Configuration & Local Deployment

To run this project locally, establish your private environment configurations within a root `.env` file. 

```ini
# Core AI Endpoint Configuration
GEMINI_API_KEY=your_google_ai_studio_api_key

# Supabase Cloud Database Credentials
SUPABASE_URL=your_supabase_project_reference_url
SUPABASE_KEY=your_supabase_anon_or_service_role_token
```
