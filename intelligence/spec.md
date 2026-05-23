
### 3.2 Data Ingestion Sources

**A. Initial Import from Confluence**
- Export strategic pages only.
- Convert to Markdown + synthesize using Claude.
- Import via PRs into GitHub.

**B. Ongoing Capture from MS Teams (Key Requirement)**
- Automatically capture decisions and discussions from designated channels.
- Use Microsoft Graph API to fetch messages (scheduled + webhook where possible).
- **Synthesis Pipeline**:
- Raw messages → Claude Code → Synthesized Markdown (ADR-style or decision record).
- Optional human review gate.
- Output committed to GitHub repo.

**C. Manual Contributions**
- Engineers/Leads create or update Markdown files directly in GitHub via PRs.

### 3.3 Synthesis & AI Layer

- **Primary AI Tool**: **Claude (via Claude Code / Anthropic API)**
- **Development Environment**: **Cursor** (heavily used with Cursor SDK where applicable)
- All synthesis, summarization, and code generation must leverage Claude for high-quality reasoning.
- Use Cursor + Claude Code for building all pipelines, prompts, and the web application.

### 3.4 Intelligence Layer (RAG)

- GitHub Markdown files are automatically indexed.
- RAG system built with LangChain / LlamaIndex + vector database (Chroma or Qdrant recommended for lean setup).
- Embeddings generated via Claude or compatible model.
- Strong citation support back to GitHub source files.

### 3.5 Consumption Interface

- **Primary Interface**: **Lean Web Application** (Domain Intelligence Hub)
- Features:
- Natural language chat interface
- Browse knowledge (repo structure view)
- "Create New Decision" workflow
- Ask for summaries, trade-offs, recommendations
- Export options
- Built as a simple, fast web app (Next.js recommended).

---

## 4. Technology Stack (Explicit)

- **Code Editor / IDE**: Cursor (primary development tool)
- **AI Coding Assistant**: Claude Code (heavily utilized)
- **AI Model for Synthesis & RAG**: Claude (Anthropic)
- **Source Control**: GitHub
- **Frontend**: Next.js 15+ + Tailwind + shadcn/ui
- **Backend**: Next.js API routes or FastAPI
- **Auth**: Microsoft Entra ID (SSO)
- **Microsoft Integration**: Microsoft Graph API (for Teams message capture)
- **Vector DB**: Chroma (initial) or Qdrant
- **Deployment**: Vercel (preferred) or Azure
- **Automation**: GitHub Actions

---

## 5. High-Level Workflows

1. **Decision in Teams** → Auto-capture → Claude synthesis → GitHub PR/Merge → Auto-index → Available in Web App.
2. **User Query** → Lean Web App → RAG over GitHub → Response with citations.
3. **Knowledge Update** → Engineer creates PR in GitHub → Reviewed → Merged → Re-indexed.

---

## 6. Non-Goals (Out of Scope)

- Dumping all existing Confluence content.
- Replacing Confluence entirely (only using it for optional visibility).
- Building a heavy enterprise platform.
- Supporting real-time chat ingestion (batch/daily is acceptable initially).

---

## 7. Success Criteria

- POD team members prefer the Intelligence Hub over raw Confluence/Teams for domain questions.
- Knowledge remains high-signal and up-to-date.
- System is maintainable by the Accredo Experience + Platform teams.
- Built primarily using **Cursor + Claude Code**.

---

**Created**: May 23, 2026  
**Owner**: Accredo Experience Team + Platform Team  
**Status**: Draft
