%% =========================================================
%% AI JOB-SEARCH AGENT — V1
%% Script-First, AI-Assisted Job Surfacing Architecture
%% =========================================================


%% =========================================================
%% 1. USER INPUT & GOVERNANCE
%% =========================================================
subgraph A["1. USER INPUT & AGENT GOVERNANCE"]
direction LR

A1["User Input\<br/>Target Roles • Locations • Preferences\<br/>CV / Skills • Constraints"]

A2["Target Job Websites\<br/>Job Boards • Company Career Pages\<br/>Specified Sources"]

A3["AGENTS.md / SOPs\<br/>Expectations • Preferences • Boundaries\<br/>Fallback Rules • Output Standards"]

A4["Restatement Check\<br/>Agent confirms understanding\<br/>before execution"]

A1 --> A4
A2 --> A4
A3 --> A4
end


%% =========================================================
%% 2. ORCHESTRATION
%% =========================================================
subgraph B["2. ORCHESTRATION LAYER"]
direction LR

B1["Job-Search Orchestrator\<br/>Plan execution • Manage state\<br/>Delegate tasks"]

B2["Task Decomposition\<br/>Collection → Processing → Evaluation"]

B3["Run Context\<br/>Search criteria • Previous results\<br/>User feedback"]

B1 --> B2
B1 --> B3
end

A4 --> B1


%% =========================================================
%% 3. JOB COLLECTION
%% =========================================================
subgraph C["3. SCRIPT-BASED JOB COLLECTION"]
direction TB

subgraph C0["Target Sources"]
direction LR

C1["LinkedIn / Job Boards"]
C2["Company Career Pages"]
C3["Other Target Websites"]

end

subgraph C00["Collection Methods"]
direction LR

C4["Official API\<br/>when available"]
C5["Scraper / Browser Script"]
C6["Search / X-Ray\<br/>Fallback"]

end

C1 --> C4
C1 --> C5

C2 --> C4
C2 --> C5

C3 --> C5
C3 --> C6

C7{"Collection\<br/>Successful?"}

C4 --> C7
C5 --> C7
C6 --> C7

C8["Retry / Alternate Method"]
C9["Flag Source\<br/>for Manual Review"]

C7 -->|No| C8
C8 --> C7
C8 -->|Still Failing| C9

C10["Raw Job Pool\<br/>Target: \~1,000 Listings"]

C7 -->|Yes| C10

end

B2 --> C1
B2 --> C2
B2 --> C3


%% =========================================================
%% 4. DETERMINISTIC PROCESSING
%% =========================================================
subgraph D["4. SCRIPT PROCESSING & PRE-FILTERING"]
direction LR

D1["Parse Listings\<br/>Title • Company • Location\<br/>Requirements • URL"]

D2["Normalize Data\<br/>Standardize fields"]

D3["Deduplicate\<br/>Remove repeated listings"]

D4["Validate Jobs\<br/>Remove expired / broken posts"]

D5["Hard Filters\<br/>Role • Location • Experience\<br/>Visa / Work Auth • Exclusions"]

D6["Deterministic Pre-Score\<br/>Keywords • Skills • Requirements"]

D7["Candidate Pool\<br/>\~200–300 Jobs"]

D1 --> D2 --> D3 --> D4 --> D5 --> D6 --> D7

end

C10 --> D1


%% =========================================================
%% 5. AI — FINAL REASONING LAYER
%% =========================================================
subgraph E["5. AI FIT EVALUATION — FINAL LINE OF DEFENSE"]
direction TB

E1["AI Fit Evaluator\<br/>Contextual / semantic reasoning"]

E2["Evaluate\<br/>Role Fit • Skill Transferability\<br/>Requirement Meaning • Red Flags"]

E3{"Suitable\<br/>Enough?"}

E4["Reject / Archive\<br/>with reason"]

E5["Final Fit Score\<br/>Rank suitable jobs"]

E1 --> E2 --> E3
E3 -->|No| E4
E3 -->|Yes| E5

end

D7 --> E1
B3 --> E1


%% =========================================================
%% 6. OUTPUT
%% =========================================================
subgraph F["6. SURFACED JOB OUTPUT"]
direction LR

F1["Ranked Shortlist\<br/>Target: \~100 Suitable Jobs"]

F2["Structured Result\<br/>Company • Role • Location\<br/>Fit Score • Reason • Link"]

F3["User-Facing Summary\<br/>Best Matches • Key Reasons\<br/>Potential Concerns"]

F1 --> F2 --> F3

end

E5 --> F1


%% =========================================================
%% 7. HUMAN REVIEW & FEEDBACK
%% =========================================================
subgraph G["7. HUMAN REVIEW & LEARNING"]
direction LR

G1["User Review\<br/>Relevant • Not Relevant\<br/>Preference Changes"]

G2["Feedback Capture\<br/>Accepted / Rejected Recommendations"]

G3["Refine Next Run\<br/>Rules • Preferences • Prompts\<br/>AGENTS.md Updates"]

G1 --> G2 --> G3

end

F3 --> G1


%% =========================================================
%% 8. FUTURE SCOPE
%% =========================================================
subgraph H["8. FUTURE ITERATIONS — OUTSIDE V1"]
direction LR

H1["V2\<br/>Resume Tailoring"]

H2["V2\<br/>Cover Letter Generation"]

H3["V3\<br/>Application Automation"]

H4["V3\<br/>Tracking & Follow-Up"]

H1 --> H2 --> H3 --> H4

end

G3 -. "Future Expansion" .-> H1


%% =========================================================
%% CORE ARCHITECTURE PRINCIPLE
%% =========================================================
N1["CORE PRINCIPLE\<br/>Scripts handle bulk deterministic work.\<br/>AI handles ambiguity and final reasoning."]

D7 -.-> N1
N1 -.-> E1


%% =========================================================
%% STYLING
%% =========================================================
classDef input fill:#312e81,stroke:#818cf8,color:#ffffff,stroke-width:2px
classDef governance fill:#4c1d95,stroke:#c4b5fd,color:#ffffff,stroke-width:2px
classDef orchestration fill:#164e63,stroke:#22d3ee,color:#ffffff,stroke-width:2px
classDef collection fill:#1e3a8a,stroke:#60a5fa,color:#ffffff,stroke-width:2px
classDef processing fill:#0f766e,stroke:#2dd4bf,color:#ffffff,stroke-width:2px
classDef intelligence fill:#713f12,stroke:#facc15,color:#ffffff,stroke-width:2px
classDef output fill:#14532d,stroke:#4ade80,color:#ffffff,stroke-width:2px
classDef human fill:#7c2d12,stroke:#fb923c,color:#ffffff,stroke-width:2px
classDef future fill:#374151,stroke:#9ca3af,color:#ffffff,stroke-width:2px
classDef decision fill:#111827,stroke:#fbbf24,color:#ffffff,stroke-width:2px
classDef principle fill:#18181b,stroke:#eab308,color:#ffffff,stroke-width:2px

class A1,A2 input
class A3,A4 governance

class B1,B2,B3 orchestration

class C1,C2,C3,C4,C5,C6,C8,C9,C10 collection
class C7 decision

class D1,D2,D3,D4,D5,D6,D7 processing

class E1,E2,E4,E5 intelligence
class E3 decision

class F1,F2,F3 output

class G1,G2,G3 human

class H1,H2,H3,H4 future

class N1 principle

if this is the mermaid diagram, could you list out the steps for the ai job agent