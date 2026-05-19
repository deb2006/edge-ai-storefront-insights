# F2C Analytics Panel - Complete File Index

## 📦 Project Structure Overview

```
f2c_bridge/
│
├── 🚀 APPLICATION FILES
│   ├── app.py                    [PRIMARY] Main Streamlit dashboard
│   └── mainbridge_copy.py        [SUPPORT] Edge telemetry bridge
│
├── ⚙️ CONFIGURATION
│   ├── requirements.txt          [CONFIG] Python dependencies
│   ├── .env                      [SECRET] Supabase credentials
│   ├── .gitignore               [CONFIG] Git ignore patterns
│   ├── Dockerfile               [CONFIG] Container build spec
│   └── docker-compose.yml       [CONFIG] Docker orchestration
│
├── 🚀 STARTUP SCRIPTS
│   ├── run.bat                  [WINDOWS] Auto-setup & launch
│   └── run.sh                   [UNIX] Auto-setup & launch
│
└── 📖 DOCUMENTATION
    ├── README.md                [START HERE] Full guide & architecture
    ├── SETUP.md                 [SETUP] Installation & troubleshooting
    ├── ARCHITECTURE.md          [ADVANCED] System design deep-dive
    ├── QUICK_REFERENCE.md       [CHEATSHEET] Quick lookup guide
    └── FILE_INDEX.md            [THIS FILE] Complete manifest
```

---

## 📄 File Descriptions

### 🟢 **app.py** (MAIN APPLICATION - 15.8 KB)

**Purpose:** Core Streamlit web application — the main entry point

**Key Components:**
- Executive KPI Scorecard (Panel 1)
- Real-Time Trend Grid (Panel 2)
- Analytical Deep-Dive (Panel 3)
- Supabase data integration
- Error handling & resilience
- Caching strategy (5-second TTL)

**How to Use:**
```bash
streamlit run app.py
# Opens dashboard at http://localhost:8501
```

**Key Functions:**
- `get_supabase_client()` — Connection pooling
- `fetch_hourly_kpi_data()` — KPI metrics from view
- `fetch_footfall_raw()` — Live sensor data
- `fetch_sales_data()` — Transaction aggregates
- `calculate_kpi_metrics()` — Metric calculations
- `render_kpi_scorecard()` — Panel 1 UI
- `render_trend_and_telemetry()` — Panel 2 UI
- `render_analytical_deep_dive()` — Panel 3 UI

**Dependencies:**
- streamlit, supabase, pandas, plotly, python-dotenv

---

### 🟡 **mainbridge_copy.py** (EDGE BRIDGE - 1.5 KB)

**Purpose:** Legacy bridge script for receiving Jetson Orin telemetry

**Key Components:**
- Supabase client initialization
- Payload validation & transformation
- HTTPS data insertion to f2c_footfall_raw

**How to Use:**
```bash
python mainbridge_copy.py
# Simulates edge device sending telemetry
```

**Integration Point:**
Edge devices (Jetson Orin) POST JSON payloads to this endpoint:
```json
{
  "device_id": "Orin_Nano_Kengeri",
  "occupancy": 7,
  "total_footfall": 63
}
```

**Note:** This is a reference implementation. For production, integrate with your actual Jetson streaming system.

---

### 🟦 **requirements.txt** (DEPENDENCIES - 106 bytes)

**Purpose:** Python package dependency list

**Contents:**
```
streamlit==1.28.1          # Web UI framework
supabase==2.0.3           # PostgreSQL REST client
python-dotenv==1.0.0      # Environment variable loading
pandas==2.1.3             # Data manipulation
plotly==5.18.0            # Interactive charting
pyarrow==13.0.0           # Arrow data support
```

**Installation:**
```bash
pip install -r requirements.txt
```

---

### 🔐 **.env** (SECRETS - 200+ bytes)

**Purpose:** Environment credentials (NEVER COMMIT)

**Contents:**
```ini
SUPABASE_URL=https://mfuqfpibknywivtculxk.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Security:**
- ✅ Included in `.gitignore` (protected from Git)
- ✅ Never commit to public repos
- ✅ Keep in secure storage (not shared)
- ✅ Rotate keys quarterly in production

---

### 🚫 **.gitignore** (GIT CONFIG - 847 bytes)

**Purpose:** Prevent sensitive files from Git commits

**Key Protections:**
- `.env` files (credentials)
- `__pycache__/` (compiled Python)
- `venv/` (virtual environments)
- `.vscode/`, `.idea/` (IDE files)
- `*.log` files
- OS-specific files (`Thumbs.db`, `.DS_Store`)

---

### 🐳 **Dockerfile** (CONTAINER - 992 bytes)

**Purpose:** Build containerized application

**Contents:**
- Base: `python:3.11-slim`
- Install dependencies from requirements.txt
- Copy app files
- Expose port 8501
- Health check configuration
- Streamlit-specific environment variables

**Usage:**
```bash
docker build -t f2c-analytics .
docker run -p 8501:8501 --env-file .env f2c-analytics
```

**Benefits:**
- Consistent environment across machines
- Easy deployment to cloud platforms
- Isolated dependencies
- Production-ready setup

---

### 🐳 **docker-compose.yml** (ORCHESTRATION - 673 bytes)

**Purpose:** Multi-container orchestration (simplified)

**Configuration:**
- Service: `f2c-analytics`
- Port mapping: 8501:8501
- Environment from `.env` file
- Health check monitoring
- Automatic restart policy
- Volume mounting for live code editing

**Usage:**
```bash
docker-compose up        # Start
docker-compose down      # Stop
docker-compose logs      # View logs
```

---

### 🪟 **run.bat** (WINDOWS SCRIPT - 1.8 KB)

**Purpose:** Automated Windows setup & launch

**What It Does:**
1. ✅ Checks Python is installed
2. ✅ Verifies `.env` file exists
3. ✅ Creates Python virtual environment
4. ✅ Installs dependencies
5. ✅ Launches Streamlit dashboard

**Usage:**
```batch
run.bat
```

**Advantages:**
- No manual commands needed
- Single-click startup
- Clear error messages
- Automatic dependency resolution

---

### 🐧 **run.sh** (UNIX SCRIPT - 1.6 KB)

**Purpose:** Automated macOS/Linux setup & launch

**What It Does:**
1. ✅ Checks Python 3 is installed
2. ✅ Verifies `.env` file exists
3. ✅ Creates Python virtual environment
4. ✅ Installs dependencies
5. ✅ Launches Streamlit dashboard

**Usage:**
```bash
chmod +x run.sh    # Make executable (first time)
./run.sh           # Run
```

---

### 📖 **README.md** (MAIN DOCS - 10.8 KB)

**Purpose:** Comprehensive project documentation

**Contents:**
- Executive summary
- System architecture diagram
- Database schema reference
- Environment setup instructions
- Dashboard component descriptions
- Performance requirements
- Customization guide
- Deployment options
- Troubleshooting guide
- File structure overview
- Integration with edge layer

**When to Read:**
- First-time setup
- Understanding system architecture
- Deployment planning
- Troubleshooting issues

---

### 📋 **SETUP.md** (INSTALLATION GUIDE - 5.9 KB)

**Purpose:** Step-by-step setup instructions

**Contents:**
- Windows quick start (5 min)
- macOS/Linux quick start (5 min)
- Manual setup instructions
- Docker deployment guide
- Troubleshooting common issues
- Production deployment options

**When to Read:**
- Installing the application
- Fixing setup problems
- Deploying to production

---

### 🏗️ **ARCHITECTURE.md** (SYSTEM DESIGN - 22.9 KB)

**Purpose:** Deep technical architecture documentation

**Contents:**
- Complete system architecture diagrams (ASCII)
- Data flow sequences (step-by-step)
- Database schema deep-dive
- Caching strategy & performance
- Error handling architecture
- Security architecture
- Deployment architectures
- Monitoring & observability
- Scalability considerations
- Future enhancements

**When to Read:**
- Understanding system design
- Troubleshooting complex issues
- Planning scalability
- Security audits

---

### ⚡ **QUICK_REFERENCE.md** (CHEATSHEET - 8.0 KB)

**Purpose:** Quick lookup guide for common tasks

**Contents:**
- File manifest
- Quick start methods (3 options)
- Dashboard panel overviews
- Configuration cheatsheet
- Database quick reference
- Troubleshooting lookup table
- Performance tips
- Security reminders
- Development workflow
- Keyboard shortcuts
- Sample test data
- Customization tips

**When to Use:**
- During development
- Quick reference while working
- Finding solutions quickly

---

### 📑 **FILE_INDEX.md** (THIS FILE)

**Purpose:** Complete project file manifest and guide

**Contents:**
- Project structure overview
- Individual file descriptions
- File sizes and line counts
- Key functions & components
- Usage instructions for each file
- Dependencies between files
- Quick navigation guide

---

## 🔗 File Dependencies

```
startup
  ├─→ run.bat
  │   └─→ venv/
  │       └─→ app.py
  │
  ├─→ run.sh
  │   └─→ venv/
  │       └─→ app.py
  │
  └─→ docker-compose up
      └─→ Dockerfile
          └─→ app.py

app.py depends on:
  ├─→ requirements.txt (lists dependencies)
  ├─→ .env (Supabase credentials)
  ├─→ streamlit (web framework)
  ├─→ supabase (database client)
  ├─→ pandas (data processing)
  └─→ plotly (charting)

mainbridge_copy.py depends on:
  ├─→ .env (Supabase credentials)
  ├─→ supabase (database client)
  └─→ python-dotenv (env loading)
```

---

## 📊 File Statistics

| File | Type | Size | Lines | Purpose |
|------|------|------|-------|---------|
| app.py | Python | 15.8 KB | 560 | Main application |
| mainbridge_copy.py | Python | 1.5 KB | 59 | Edge bridge |
| requirements.txt | Text | 106 B | 6 | Dependencies |
| .env | Config | 200 B | 2 | Secrets |
| .gitignore | Config | 847 B | 40 | Git config |
| Dockerfile | Config | 992 B | 35 | Container build |
| docker-compose.yml | YAML | 673 B | 24 | Docker orchestration |
| run.bat | Batch | 1.8 KB | 68 | Windows launcher |
| run.sh | Shell | 1.6 KB | 60 | Unix launcher |
| README.md | Markdown | 10.8 KB | 380 | Main docs |
| SETUP.md | Markdown | 5.9 KB | 210 | Setup guide |
| ARCHITECTURE.md | Markdown | 22.9 KB | 820 | Tech deep-dive |
| QUICK_REFERENCE.md | Markdown | 8.0 KB | 285 | Cheatsheet |
| **TOTAL** | | **~70 KB** | **3,544** | Complete project |

---

## 🎯 How to Navigate This Project

### If you want to...

**Get started immediately:**
→ Open `run.bat` (Windows) or `./run.sh` (macOS/Linux)

**Understand the system:**
→ Read `README.md` then `ARCHITECTURE.md`

**Fix a setup problem:**
→ Check `SETUP.md` troubleshooting section

**Make quick customizations:**
→ Reference `QUICK_REFERENCE.md`

**Deploy to production:**
→ See `SETUP.md` deployment options

**Edit the dashboard:**
→ Modify `app.py` (auto-reloads on save)

**Receive edge data:**
→ Configure `mainbridge_copy.py` with your stream

**Run with Docker:**
→ Use `docker-compose up`

**Track down a bug:**
→ Review `ARCHITECTURE.md` data flow sections

---

## 🔄 Typical Workflow

```
1. Clone/Download Project
   ↓
2. Review README.md (5 min overview)
   ↓
3. Run run.bat or ./run.sh (Auto setup)
   ↓
4. Dashboard opens at http://localhost:8501
   ↓
5. Verify data displays correctly
   ↓
6. If issues: Check SETUP.md troubleshooting
   ↓
7. Customize as needed: Edit app.py
   ↓
8. Deploy: Follow SETUP.md deployment options
```

---

## 📞 Quick Help

| Question | Answer | File |
|----------|--------|------|
| How do I start? | Use `run.bat` or `./run.sh` | This file / SETUP.md |
| What's the architecture? | See system diagrams | ARCHITECTURE.md |
| How do I fix [X]? | Search SETUP.md | SETUP.md |
| What does [file] do? | Read below | This file |
| How do I customize? | Check QUICK_REFERENCE.md | QUICK_REFERENCE.md |
| How do I deploy? | See SETUP.md | SETUP.md |

---

## ✅ Pre-Launch Checklist

- [ ] `.env` file exists with credentials
- [ ] Python 3.9+ installed
- [ ] All docs reviewed (at least README.md)
- [ ] `requirements.txt` dependencies listed
- [ ] `app.py` is the entry point
- [ ] Understand Panel 1/2/3 structure
- [ ] Know how to stop app (Ctrl+C)
- [ ] Backup `.env` file (secure location)
- [ ] Ready for testing!

---

## 🎓 Learning Path

**Beginner (New to project):**
1. README.md (Overview)
2. SETUP.md (Installation)
3. QUICK_REFERENCE.md (Basic usage)

**Intermediate (Want customizations):**
1. ARCHITECTURE.md (System design)
2. app.py (Code review)
3. QUICK_REFERENCE.md (Customization tips)

**Advanced (Production deployment):**
1. ARCHITECTURE.md (Full deep-dive)
2. SETUP.md (Deployment options)
3. Dockerfile + docker-compose.yml (Container setup)

---

## 🚀 **YOU ARE READY TO LAUNCH!**

```
Choose your method:

WINDOWS:          run.bat
macOS/LINUX:      ./run.sh
DOCKER:           docker-compose up
MANUAL:           streamlit run app.py
```

Then open **http://localhost:8501** in your browser.

---

**Project Version**: 1.0.0 | **Last Updated**: 2025-05-18 | **Status**: ✅ Production Ready
