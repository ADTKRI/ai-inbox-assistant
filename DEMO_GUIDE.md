# AI Inbox Assistant -- Demo & Presentation Guide

This guide provides a structured 5-minute presentation script and 3 real-world email scenarios to demonstrate the AI Inbox Assistant to an engineering lead, mentor, or executive stakeholder.

---

## 🎭 3-Step Presenter Script

### Step 1: The Problem & Architectural Hook (1 Minute)
> *"Most email productivity tools fail because they are either rigid keyword filters or open-ended chatbots that hallucinate. We engineered the **AI Inbox Assistant** as a deterministic operational pipeline. Instead of freeform text, we enforce strict Pydantic v2 schemas directly inside the Gemini API. Every email is parsed into typed metadata: urgency level, ISO/textual deadline, explicit reply requirements, and a discrete action checklist."*

**Key Points to Highlight:**
- Show the **Pipeline Flow** breadcrumb on the left panel (`1. Input ➔ 2. Gemini ➔ 3. JSON ➔ 4. SQLite`).
- Emphasize zero-hallucination data validation with Pydantic v2.

---

### Step 2: Live Triage & Interactive Slideshow (2.5 Minutes)
> *"Let's test this with live scenarios. The UI uses a balanced 2-column layout. Instead of an endless vertical feed that forces endless scrolling, we built an interactive card carousel that keeps the viewport balanced and responsive."*

#### Demo Scenario 1: Urgent Internship Document Deadline
1. Click the **`Internship`** preset chip (or paste the text below):
   - **Subject**: `Internship Onboarding - Document Submission`
   - **Body**: `Please submit your updated resume and offer letter by September 28. Also confirm once the documents have been uploaded.`
2. Click **`Analyze Email`** (48px primary action).
3. **Observe**:
   - Priority Badge: Crimson **`HIGH PRIORITY`** with justification.
   - Executive Summary in soft green callout box (`#F0FDF4`).
   - Actions Box: 3 interactive tasks (`Upload updated resume`, `Upload offer letter`, `Reply to confirm document upload`).
   - Details: Warm amber deadline badge (`⏰ September 28`) and category pill (`📁 INTERNSHIP`).
   - Reply Banner: Amber alert (`⚠️ Reply Required: The sender explicitly requested confirmation...`).
   - Check off a task: Notice the instant visual strike-through (`~~Task~~`).

#### Demo Scenario 2: Team Collaboration & Next-Day Demo
1. Click the **`Standup Sync`** preset chip:
   - **Subject**: `Sprint 4 Standup & Demo Sync`
   - **Body**: `Hi team, please prepare your 3-minute demo slides for the cross-functional sync tomorrow at 11 AM. Review the ticket backlog if you have pending PRs.`
2. Click **`Analyze Email`**.
3. **Observe**:
   - Priority Badge: Royal Blue **`MEDIUM PRIORITY`**.
   - Deadline: `⏰ Tomorrow at 11 AM`.
   - Reply Banner: Emerald pill (`✅ No Reply Needed: Informational meeting preparation`).
   - Slideshow Bar: Shows `● Email 1 of 5`. Click `Next ▶` to navigate between triaged emails.

#### Demo Scenario 3: Zero-Action Broadcast Newsletter
1. Click the **`Newsletter`** preset chip:
   - **Subject**: `Tech Digest #142: Future of Generative Agents`
   - **Body**: `Welcome to this week's issue covering new reasoning models, local LLM architectures, and our favorite open-source tools. No action needed, enjoy the weekend read!`
2. Click **`Analyze Email`**.
3. **Observe**:
   - Priority Badge: Slate **`LOW PRIORITY`**.
   - Actions Box: Clean italicized empty state: `No action items required.`
   - Category: `📁 NEWSLETTER`.

---

### Step 3: Persistence, Export & Subsystem Verification (1.5 Minutes)
> *"All triage results are automatically persisted to a local SQLite database (`data/inbox_history.db`) with transactional safety. Nothing is lost on browser refresh. Furthermore, executives can export their active triage queue with one click."*

**Actions to Perform:**
1. Click **`📄 CSV`** in the navigation bar to download `inbox_triage_export.csv` formatted for Excel or Google Sheets.
2. Click **`📝 MD`** to generate `inbox_triage_briefing.md`, a formatted Markdown summary ready for team standups.
3. Switch to the terminal and run the automated health check:
   ```bash
   .\.venv\Scripts\python run_checks.py
   ```
4. Point out that all 4 subsystems (`Environment`, `SQLite Persistence`, `Schema Validation`, `Gemini API Connectivity`) pass diagnostics with verified latency.

---

## 📋 Quick Test Scenarios Reference Table

| Preset | Subject | Expected Priority | Expected Deadline | Reply Required? |
|---|---|---|---|---|
| **Internship** | Internship Onboarding - Document Submission | `HIGH` (Crimson) | `September 28` | Yes (`⚠️`) |
| **Standup Sync** | Sprint 4 Standup & Demo Sync | `MEDIUM` (Royal Blue) | `Tomorrow at 11 AM` | No (`✅`) |
| **Newsletter** | Tech Digest #142: Future of Generative Agents | `LOW` (Slate) | `None specified` | No (`✅`) |

---

## 💡 Key Technical Talking Points for Leads / Mentors

1. **Why Gemini 2.5 Flash / 3.1 Lite?**
   Sub-second latency with high reasoning density, ideal for user-facing stream/triage operations.
2. **Why Pydantic v2 Schema Enforcement?**
   Guarantees that LLM outputs conform to typed constraints (`Literal['HIGH', 'MEDIUM', 'LOW']`, lists of strings, boolean flags) before reaching the UI or SQLite layer.
3. **Why SQLite Context Management?**
   Uses Python's `contextlib.contextmanager` to ensure connections are strictly closed after transactions, preventing Windows `WinError 32` file locking bugs.
4. **Why Single-Card Slideshow Layout?**
   Eliminates infinite vertical scrolling and awkward whitespace, maintaining visual parity between the input panel and triage board on any standard monitor.
