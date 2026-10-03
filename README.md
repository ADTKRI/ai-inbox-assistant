# AI Inbox Assistant (Executive Natural Language Triage Engine)

An autonomous executive email triage and productivity engine powered by the Google Gemini API, Pydantic v2, SQLite, and Streamlit. Engineered to solve inbox overload by transforming messy, high-volume natural language emails into deterministic priorities, explicit deadlines, categorized buckets, and actionable task checklists.

---

## 🎯 Problem Statement

Modern professionals and executives face high cognitive load triaging unstructured inboxes containing critical job updates, meeting invites, project deadlines, and marketing noise. Traditional email filters rely on fragile keyword rules that fail to understand context or extract commitments. 

**AI Inbox Assistant** provides an automated, deterministic triage pipeline:
1. Eliminates triage fatigue with instant priority classification (`HIGH`, `MEDIUM`, `LOW`).
2. Extracts concrete operational deadlines and calculates whether an explicit reply is required.
3. Automatically breaks emails down into an interactive action item checklist.
4. Renders an elevated, interactive single-card slideshow/paginator to maintain viewport balance without endless vertical scrolling.
5. Persists all decisions locally in SQLite and supports instant CSV/Markdown exports for executive briefings.

---

## 🏗️ Architecture Flow

```text
  +-----------------------------------------------------------------------------------+
  |                                   USER INTERFACE                                  |
  |                        Streamlit Humanized Dashboard (app.py)                     |
  |                                                                                   |
  |  +-----------------------------------------------------------------------------+  |
  |  |           Top Navigation Bar (Brand Title + Minimal Workspace Badge)        |  |
  |  +-----------------------------------------------------------------------------+  |
  |                                                                                   |
  |  +-------------------------------------+  +------------------------------------+  |
  |  |     Left Column: Analysis Panel     |  |    Right Column: Triage Carousel   |  |
  |  |  (38% Viewport Width)               |  |  (62% Viewport Width)              |  |
  |  | - 1-Click Chip Presets              |  | - Slideshow Bar: [Prev] [X of Y]   |  |
  |  | - Crisp White Inputs (#FFFFFF)      |  |   [Next] [CSV] [MD]                |  |
  |  | - Prominent Analyze Button (48px)   |  | - Elevated Active Card (16px, 28px)|  |
  |  | - Pipeline Flow Breadcrumb          |  | - Structured Action Checklist Box  |  |
  |  +------------------+------------------+  +-----------------+------------------+  |
  |                     |                                       |                     |
  +---------------------|---------------------------------------|---------------------+
                        |                                       |
                        v                                       |
  +------------------------------------+                        |
  |          ANALYSIS ENGINE           |                        |
  |       (services/analyzer.py)       |                        |
  |                                    |                        |
  |   Gemini 2.5 Flash / 3.1 Lite      |                        |
  |   Pydantic v2 Structured Output    |                        |
  |   (schemas.EmailTriageResult)      |                        |
  +---------------------+--------------+                        |
                        |                                       |
                        v                                       v
  +-----------------------------------------------------------------------------------+
  |                                PERSISTENCE & EXPORT                               |
  |   - Local SQLite Storage (services/storage.py -> data/inbox_history.db)           |
  |   - Structured CSV & Executive Markdown Exporter (services/exporter.py)           |
  +-----------------------------------------------------------------------------------+
```

---

## 🛠️ Tech Stack & Subsystems

| Subsystem | Technology | Purpose |
|---|---|---|
| **Language Runtime** | Python 3.10+ | Core backend logic & services |
| **LLM Inference** | Google GenAI SDK (`google-genai`) | Model inference with native structured JSON schema enforcement |
| **Model** | `gemini-2.5-flash` / `gemini-3.1-flash-lite` | Ultra-low latency, deterministic operational triage extraction |
| **Data Validation** | Pydantic v2 (`pydantic>=2.0.0`) | Strict runtime schema guarantees and JSON serialization |
| **Frontend UI** | Streamlit (`streamlit>=1.35.0`) | Modern 2-column layout with slideshow pagination & BaseWeb styling |
| **Persistence** | SQLite 3 (Standard Library) | Zero-dependency local persistence with context-managed connection safety |
| **Configuration** | `python-dotenv` | Clean, 12-factor environment variable loading |

---

## 📂 Project File Tree

```text
ai-inbox-assistant/
├── app.py                      # Streamlit application entrypoint & design-system CSS
├── config.py                   # Environment configuration & lazy API key validation
├── schemas.py                  # Pydantic v2 data models (EmailTriageResult)
├── requirements.txt            # Pinned production dependencies
├── run_checks.py               # Unified diagnostic health check script
├── DEMO_GUIDE.md               # Curated test scenarios & presenter script
├── README.md                   # System documentation & architectural reference
├── .env                        # Local secret configuration (git-ignored)
├── .env.example                # Sample environment template
├── .gitignore                  # Git exclusions for environments, caches & databases
├── components/                 # Modular frontend UI components
│   ├── __init__.py             # Component exports
│   ├── navbar.py               # Top Forest Green header with brand logo & Workspace badge
│   ├── input_panel.py          # Email inputs, 1-click chip presets, and analysis flow
│   ├── triage_card.py          # Slideshow paginator toolbar, elevated card & action box
│   └── analytics_sidebar.py    # Analytics metrics & capability indicators
├── data/                       # Local data directory (auto-created)
│   └── inbox_history.db        # SQLite database storing persistent triage history
├── services/                   # Modular backend service layer
│   ├── __init__.py             # Package initializer
│   ├── analyzer.py             # Gemini API client, system prompting & extraction engine
│   ├── exporter.py             # Spreadsheet CSV and executive Markdown export generators
│   └── storage.py              # SQLite schema initialization and CRUD transaction logic
└── tests/                      # Automated verification test suite
    ├── __init__.py             # Test package initializer
    ├── test_analyzer.py        # Live Gemini benchmark evaluation test
    ├── test_schemas.py         # Pydantic schema validation & constraint tests
    └── test_storage.py         # SQLite persistence lifecycle tests
```

---

## 🚀 Setup & Local Run Instructions

### 1. Prerequisites
- Python 3.10 or higher.
- A Google Gemini API key from [Google AI Studio](https://aistudio.google.com/).

### 2. Environment Setup
```bash
# Navigate to the project root
cd ai-inbox-assistant

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Secrets
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```
Edit `.env` with your Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-2.5-flash
```

### 4. Run Diagnostic Health Checks
Verify that all subsystems (environment, SQLite, Pydantic schemas, and Gemini API) are functional:
```bash
python run_checks.py
```
Expected output:
```text
============================================================================
  AI INBOX ASSISTANT -- PRODUCTION DIAGNOSTIC SUITE
============================================================================
...
SUBSYSTEM                    | STATUS   | DETAILS
Environment & Credentials    | [PASS]   | .env found, GEMINI_API_KEY=AIzaSy..., MODEL=...
SQLite Persistence           | [PASS]   | data/inbox_history.db writable (Schema: triage_history OK)
Schema Validation            | [PASS]   | Pydantic v2 EmailTriageResult validated
Gemini API Connectivity      | [PASS]   | Model responded in 850ms ('PONG')
----------------------------------------------------------------------------
  ALL SUBSYSTEMS VERIFIED -- [READY FOR PRODUCTION]
============================================================================
```

### 5. Launch the Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Running Automated Tests

Run unit tests directly with the Python test runner:
```bash
# Validate SQLite persistence CRUD lifecycle
python tests/test_storage.py

# Validate Pydantic v2 schema constraints & JSON schema export
python tests/test_schemas.py

# Run live benchmark evaluation against Gemini
python tests/test_analyzer.py
```

---

## 📊 Exporting Triage Data
From the active card slideshow toolbar:
- **`📄 CSV`**: Downloads an spreadsheet-ready CSV (`inbox_triage_export.csv`) with IDs, timestamps, categories, and serialized action lists.
- **`📝 MD`**: Generates an executive Markdown briefing (`inbox_triage_briefing.md`) formatted for team standups and leadership syncs.
