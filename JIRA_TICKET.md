# JIRA Ticket: SPICE Assistant RAG Integration

## Ticket ID: SPICE-042

| Field            | Value                                             |
|------------------|---------------------------------------------------|
| **Project**      | SPICE Energy Dashboard                            |
| **Type**         | Story                                             |
| **Priority**     | Medium                                            |
| **Status**       | Done                                              |
| **Sprint**       | Sprint 4 — MVP Enhancements                       |
| **Assignee**     | Alma Soria (Team 11)                              |
| **Labels**       | `rag`, `feature`, `nlp`, `dashboard`              |
| **Epic**         | Dashboard Feature Development                     |

---

## Summary

**Add retrieval-based RAG assistant page ("SPICE Assistant") to the Streamlit dashboard**

## Description

Integrated a semantic-retrieval chatbot into the SPICE Energy Dashboard that allows users to ask natural-language questions about SPICE projects, solar production data, environmental impact, and financials. The assistant retrieves the most relevant information from a dynamically built knowledge base grounded in actual SPICE data.

## Acceptance Criteria

- [x] New "SPICE Assistant" page accessible from the sidebar navigation
- [x] Knowledge base auto-populated from existing dashboard data (Bissell production, project portfolio, environmental stats, financials)
- [x] Semantic search powered by `sentence-transformers` (`all-MiniLM-L6-v2`)
- [x] Chat interface with persistent message history using `st.chat_input` / `st.chat_message`
- [x] Relevance scores displayed with each result; low-relevance results filtered out
- [x] Expandable "View Knowledge Base Contents" section for transparency
- [x] Requirements file updated with new dependency
- [x] No API keys required — fully local and free

## Changes Made

### Files Modified

| File | Change |
|------|--------|
| `app.py` | Added `sentence_transformers` import (line 16) |
| `app.py` | Added "SPICE Assistant" to sidebar navigation selectbox (line 267) |
| `app.py` | Added PAGE 8: SPICE Assistant — full RAG retrieval page (lines 1808–2040) |
| `requirements.txt` | Added `sentence-transformers>=3.4.0`; removed unused `transformers` and `torch` |

### Knowledge Base Documents (9 total)

1. **SPICE Overview** — Organization background, mission, membership
2. **Project Portfolio** — All 4 solar projects with capacity, location, status
3. **Bissell Production** — Total kWh, peak day, producing days, averages (dynamic from data)
4. **Bissell Monthly** — Per-month breakdown of production stats
5. **Inverter Performance** — Per-inverter kWh totals for the 3 Fronius Primo units
6. **Environmental Impact** — CO2 avoided, trees equivalent, cars equivalent
7. **Financial Info** — Electricity rates, savings estimates, portfolio projections
8. **Edmonton Solar** — Regional solar resource data, seasonal irradiance patterns
9. **ML Forecasting** — Model types, key features, XAI techniques used

### Architecture Decision

Chose **retrieval-only** (no generative model) over full RAG with LLM for these reasons:
- **Free & local** — no API keys, no cloud costs
- **Lightweight** — `all-MiniLM-L6-v2` is ~80 MB vs 3+ GB for FLAN-T5
- **Fast** — near-instant retrieval vs 5–15s generation time
- **Accurate** — returns actual SPICE data, no hallucination risk

## Testing Notes

```bash
pip install sentence-transformers
streamlit run app.py
# Navigate to "SPICE Assistant" in sidebar
# Test queries: "How much energy has Bissell produced?", "What is SPICE?", "financial savings"
```

## Story Points: 3
