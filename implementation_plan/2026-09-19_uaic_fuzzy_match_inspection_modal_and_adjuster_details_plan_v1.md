# Implementation Plan — Fuzzy Match Inspection & Adjuster Resolution Modal

**Implementation ID:** `IMP-2026-0919-001`  
**System Target:** UAIC Claim & RPA Orchestrator — Fuzzy Match Exception Review Subsystem  
**Primary Routes:** `/exceptions` (`frontend/src/app/exceptions/page.tsx`)  
**Backend Endpoints:** `/api/v1/matches/pending`, `/api/v1/matches/{id}/review`, `/api/v1/matches/{id}`  
**Authoritative Documentation:** `README.md`, `PowerAutomateSolutions/BotCreation_1_0_0_7/`  
**Governing Skill:** `.agents/skills/diagnose-plan-confirm-execute/SKILL.md`

---

## 1. Problem Statement & User Insight

On the **Fuzzy Match Exception Review** page (`/exceptions`), the user rightly pointed out:
> *"you have given approve and reject option but don't you think without seeing the required details why we approve or reject anything?"*

Currently:
1. Adjusters only see basic truncated rows (County, Party Name, Party Type, Case Number, Case Style snippet, and Confidence Score).
2. The `Approve` and `Reject` buttons trigger an immediate backend resolution without displaying:
   - The underlying **Claim Master Record** (Claim #, Exposure #, DOL, Policy State, Loss Location State, Insured, Claimant, Driver).
   - The full **Scraped Court Case Details** (Full Docket #, Full Legal Case Style, Cleaned Style, Filing Date, Case Type, Case Status, official County Website link).
   - The **Matching Engine Evidence & Token Overlap Breakdown** (Evaluated Party Name vs Docket Case Style, RapidFuzz partial_ratio calculation, matching tokens highlighted, threshold comparison).
   - An **Adjuster Resolution Justification / Audit Notes** input to document *why* a borderline match was legally approved or rejected for Guidewire Insurance Cloud provenance.

---

## 2. User Review Required

> [!IMPORTANT]
> **Adjuster Decision Workflow Integrity:**
> Approving a fuzzy match directly creates a Guidewire Activity with court case payload. Therefore, human adjusters must have full side-by-side evidence before approving or rejecting.
> 
> The proposed solution introduces an interactive **Match Inspection & Adjuster Resolution Modal**:
> 1. Accessible via a new **`Inspect`** button with an `Eye` icon on every table row and card, plus direct row clicking.
> 2. Side-by-side dual-pane comparison between **Claim Master Record** and **Discovered Court Docket**.
> 3. Visual token overlap highlighting showing exactly which words matched in the Case Style.
> 4. Mandatory/recommended **Review Notes** input field for the adjuster to record decision rationale before approving or rejecting.
> 5. Direct `Approve Match` and `Reject Match` actions within the modal, as well as preserving quick-actions on the table for high-volume users.

---

## 3. Architecture & Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor Adjuster as Claims Adjuster
    participant UI as Exceptions Page (/exceptions)
    participant Modal as Match Inspection Modal
    participant API as FastAPI Backend (/api/v1/matches)
    participant DB as SQLite DB (MatchPair + Claim + CourtCase)
    participant Celery as Celery Workers (notify_guidewire_task)

    UI->>API: GET /api/v1/matches/pending
    API->>DB: select(MatchPair).options(selectinload(court_case), selectinload(claim))
    DB-->>API: MatchPair with full Claim & CourtCase models
    API-->>UI: MatchPairResponse[] (enriched with claim & court case metadata)
    
    Adjuster->>UI: Clicks "Inspect" or Table Row
    UI->>Modal: Opens Inspection Modal with full side-by-side comparison
    Modal-->>Adjuster: Displays Claim Master, Court Docket, Token Matches, Confidence Analytics
    
    Adjuster->>Modal: Enters Reviewer Name & Justification Notes ("Verified DOB & VIN...")
    Adjuster->>Modal: Clicks "Approve Match" or "Reject Match"
    Modal->>API: POST /api/v1/matches/{id}/review (decision, reviewed_by, review_notes)
    API->>DB: Update MatchPair & ClaimRecord; insert AuditLog
    opt If APPROVED
        API->>Celery: celery_app.send_task("notify_guidewire_task", args=[claim_id])
    end
    API-->>Modal: 200 OK
    Modal->>UI: Refreshes list and displays success toast
```

---

## 4. Proposed Changes

### Component 1: Backend Schemas & Endpoints

#### [MODIFY] `backend/app/schemas/match.py`
- Enrich `MatchPairResponse` to include comprehensive claim and court case metadata:
  ```python
  # Claim Master Metadata
  claim_number: str | None = None
  exposure_number: str | None = None
  dol: str | None = None
  policy_state: str | None = None
  loss_location_state: str | None = None
  insured_name: str | None = None
  claimant_name: str | None = None
  driver_name: str | None = None
  claim_status: str | None = None

  # Court Case Metadata
  case_status: str | None = None
  case_type: str | None = None
  cleaned_case_style: str | None = None
  raw_payload: dict | None = None
  ```

#### [MODIFY] `backend/app/api/v1/endpoints/matches.py`
- In `list_pending_match_reviews`:
  - Update SQLAlchemy query to eager-load both `MatchPair.court_case` and `MatchPair.claim`:
    `.options(selectinload(MatchPair.court_case), selectinload(MatchPair.claim))`.
  - Populate all claim fields:
    - `claim_number=mp.claim.claim_number if mp.claim else None`
    - `exposure_number=mp.claim.exposure_number if mp.claim else None`
    - `dol=mp.claim.dol if mp.claim else None`
    - `policy_state=mp.claim.policy_state if mp.claim else None`
    - `loss_location_state=mp.claim.loss_location_state if mp.claim else None`
    - `insured_name=f"{mp.claim.insured_first_name or ''} {mp.claim.insured_last_name or ''}".strip() if mp.claim else None`
    - `claimant_name=f"{mp.claim.claimant_first_name or ''} {mp.claim.claimant_last_name or ''}".strip() if mp.claim else None`
    - `driver_name=f"{mp.claim.driver_first_name or ''} {mp.claim.driver_last_name or ''}".strip() if mp.claim else None`
    - `claim_status=mp.claim.record_status.value if mp.claim else None`
  - Populate court case fields:
    - `case_status=mp.court_case.case_status if mp.court_case else None`
    - `case_type=mp.court_case.case_type if mp.court_case else None`
    - `cleaned_case_style=mp.court_case.cleaned_case_style if mp.court_case else None`
    - `raw_payload=mp.court_case.raw_payload if mp.court_case else None`
- Add `GET /api/v1/matches/{match_pair_id}` endpoint to retrieve a single match pair with full claim and court case details.

---

### Component 2: Frontend Types & API Client

#### [MODIFY] `frontend/src/types/index.ts`
- Update `MatchPair` interface:
  ```typescript
  export interface MatchPair {
    id: string;
    claim_id: string;
    court_case_id: string;
    party_type: 'CLAIMANT' | 'INSURED' | 'DRIVER';
    party_name: string;
    case_style: string;
    county_name?: string;
    case_number?: string;
    filing_date?: string;
    county_website?: string;
    similarity_score: number;
    threshold_applied: number;
    is_match: boolean;
    review_status: 'AUTO_MATCHED' | 'PENDING_REVIEW' | 'APPROVED' | 'REJECTED';
    reviewed_by?: string;
    reviewed_at?: string;
    review_notes?: string;
    created_at: string;
    
    // Enriched Claim Master metadata
    claim_number?: string;
    exposure_number?: string;
    dol?: string;
    policy_state?: string;
    loss_location_state?: string;
    insured_name?: string;
    claimant_name?: string;
    driver_name?: string;
    claim_status?: string;

    // Enriched Court Case metadata
    case_status?: string;
    case_type?: string;
    cleaned_case_style?: string;
    raw_payload?: Record<string, any>;
  }
  ```

#### [MODIFY] `frontend/src/lib/api.ts`
- Ensure `reviewMatchPair` passes `review_notes` and `reviewed_by` properly.
- Add `getMatchPair: async (id: string): Promise<MatchPair>` method.

---

### Component 3: Frontend Exceptions UI & Modal

#### [MODIFY] `frontend/src/app/exceptions/page.tsx`
- Add state:
  ```typescript
  const [selectedMatch, setSelectedMatch] = useState<MatchPair | null>(null);
  const [reviewNotes, setReviewNotes] = useState("");
  const [reviewerName, setReviewerName] = useState("Claims Adjuster");
  ```
- In Table View:
  - Add `Inspect` action button with `Eye` icon to each row.
  - Add `onClick` on table rows (excluding action buttons) to open `selectedMatch`.
- In Cards View:
  - Add `Inspect & Resolve` action button with `Eye` icon.
- Create **Match Inspection & Adjuster Resolution Modal**:
  1. **Header:**
     - Modal title: "Fuzzy Match Candidate Inspection & Resolution"
     - Subtitle: Match Evaluation ID and County Court Portal
     - Confidence Score Pill (Emerald for ≥60%, Amber for 40–59%, Rose for <40%)
     - Close `(X)` button
  2. **Side-by-Side Dual Pane Comparison Grid:**
     - **Pane 1: Insurance Claim Master (Internal Source of Truth)**
       - Claim # (linked to `/claims/[id]`), Exposure #
       - Date of Loss (DOL)
       - Policy State & Loss Location State
       - Party Hierarchy:
         - Insured: `insured_name`
         - Claimant: `claimant_name`
         - Driver: `driver_name`
       - Status badge
     - **Pane 2: Discovered Court Case Docket (Public Record)**
       - Docket / Case Number
       - County Name & Portal Link (`county_website` with `ExternalLink` icon)
       - Filing Date (with check indicator: >= 2010 compliance)
       - Case Status (Open, Closed, Pending, etc.)
       - Case Type (Auto Negligence, Civil, etc.)
       - Full Case Style (styled prominently)
  3. **Matching Engine Analytics & Token Overlap Box:**
     - Evaluated Party Name vs Docket Case Style
     - Visual Token Match Highlight: renders the Case Style with matching name tokens highlighted in yellow/emerald chips
     - Algorithmic Breakdown: `RapidFuzz partial_ratio` score, Threshold applied (Default 60%, Borderline 40%)
     - Decision Recommendation Badge (e.g. "Borderline Match — Requires Adjuster Verification", "Strong Match — Guidewire Candidate")
  4. **Adjuster Resolution & Audit Box:**
     - Reviewer Name input (default: "Claims Adjuster")
     - Justification / Review Notes textarea (e.g., "Verified DOB and incident address; approved for Guidewire sync")
     - Action buttons:
       - `Cancel / Close`
       - `Reject Match` (Rose button with `XCircle` icon)
       - `Approve Match` (Emerald button with `CheckCircle2` icon)
       - Loading spinner state during async execution

---

## 5. Verification Plan

### Automated Tests
1. **Backend Tests:**
   ```bash
   cd backend
   .venv\Scripts\pytest tests/test_fuzzymatch_api_parity.py -q
   .venv\Scripts\pytest tests/ -k match -q
   ```
2. **Backend Linting:**
   ```bash
   .venv\Scripts\ruff check app tests
   ```
3. **Frontend TypeScript & Linting:**
   ```bash
   cd frontend
   npx tsc --noEmit
   npm run lint
   ```
4. **PowerShell Launcher Integrity:**
   ```bash
   powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
   ```

### Visual & Browser Verification
1. Run Playwright script against `http://localhost:3000/exceptions`:
   - Capture Table View with new `Inspect` action buttons.
   - Click `Inspect` button on a pending match row.
   - Capture the **Match Inspection & Adjuster Resolution Modal** showing:
     - Side-by-side Claim Master Record vs. Discovered Court Case Docket.
     - Token overlap highlighting in Case Style.
     - Reviewer name and filled-in justification notes.
   - Click `Approve Match` or `Reject Match` and capture the resulting success notification and updated state.
2. Save screenshots to `implementation_plan/Images/`:
   - `implementation_plan/Images/exceptions_inspect_button_table.png`
   - `implementation_plan/Images/exceptions_match_inspection_modal_open.png`
   - `implementation_plan/Images/exceptions_match_inspection_modal_notes.png`
   - `implementation_plan/Images/exceptions_match_resolution_toast.png`

---

## 6. Definition of Done Checklist
- [ ] Backend `MatchPairResponse` schema enriched with claim and court case metadata
- [ ] Backend `list_pending_match_reviews` eager-loads `MatchPair.claim` and populates all metadata
- [ ] Backend `GET /api/v1/matches/{id}` endpoint added
- [ ] Frontend `MatchPair` interface enriched with metadata
- [ ] Frontend `api.getMatchPair` and `api.reviewMatchPair` fully wired
- [ ] Frontend Exceptions page equipped with `Inspect` buttons and interactive table rows
- [ ] Match Inspection & Adjuster Resolution Modal renders side-by-side comparison, token overlap highlighting, reviewer name, and notes textarea
- [ ] Approve and Reject actions in modal persist review notes to backend and update claim status
- [ ] All 4 automated checks pass (pytest, ruff, tsc, ps1) with zero errors
- [ ] Screenshots captured and archived in `implementation_plan/Images/`
- [ ] Implementation record saved to `implementation_plan/`
