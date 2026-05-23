# Accredo Domain Intelligence System - Architecture

## 1. Overview

The **Accredo Domain Intelligence System** is a lean, AI-augmented knowledge platform designed to capture, synthesize, and deliver high-quality domain intelligence to POD teams and Engineering Leadership.

**Core Philosophy**: 
- GitHub as the **single source of truth**.
- Human + AI co-curation for noise-free, strategic knowledge only.
- Chat-first consumption via a lean web application.

---

## 2. High-Level Architecture Diagram

(Refer to the Component Diagram generated earlier)

**Key Layers**:

1. **Ingestion Layer** — MS Teams + Confluence
2. **Synthesis & Curation Layer** — Claude-powered pipeline
3. **Storage Layer** — GitHub (Markdown)
4. **Intelligence Layer** — RAG Engine
5. **Presentation Layer** — Lean Web Application

---

## 3. Detailed Component Architecture

### 3.1 Ingestion Layer

**Components**:
- **MS Teams Integration**
  - Microsoft Graph API (`/chats`, `/teams/channels/messages`)
  - Scheduled jobs (Azure Function / GitHub Actions) + Webhooks (change notifications)
  - Targeted channels only (architecture, design-review, decision-log)

- **Confluence Import**
  - One-time + periodic strategic export
  - Converted to Markdown using Claude

- **Manual Input**
  - Direct GitHub contributions via PRs

### 3.2 Synthesis Pipeline

**Technology**: Built using **Cursor + Claude Code**

**Flow**:
1. Raw data (Teams messages or Confluence export) is fetched.
2. Claude processes the content with structured prompts:
   - Extract decisions, rationale, trade-offs, context.
   - Output standardized Markdown (Decision Record / ADR Lite).
3. Optional human review via GitHub PR.
4. Merged into `foundations` repository.

**Key Tools**:
- Cursor (primary IDE for development)
- Claude (Anthropic API / Claude Code) for all synthesis and code generation
- Node.js/Python scripts (GitHub Actions + Azure Functions)

### 3.3 Source of Truth (GitHub)

**Repository**: `foundations` (central repo)

**Structure**:
```markdown
foundations/
├── README.md
├── architecture/
│   ├── accredo-experience/
│   │   ├── blueprint.md
│   │   ├── key-decisions/
│   │   └── patterns/
├── decision-records/
│   ├── ADR-001-xxx.md
├── how-we-do/
├── glossaries/
├── templates/
└── .github/
    └── workflows/
        ├── index-rag.yml
        ├── synthesize-teams.yml
