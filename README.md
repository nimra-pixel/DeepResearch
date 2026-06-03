<div align="center">

# 🔬 DeepResearch Agent

### Autonomous AI Literature Review Generator

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.2+-FF6B35?style=flat&logo=chainlink&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/Groq-Llama%203.3%2070B-F55036?style=flat)](https://groq.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)
[![Built by Nimra](https://img.shields.io/badge/Built%20by-Nimra%20Tariq-1A3A5C?style=flat&logo=github)](https://github.com/nimra-pixel)

**Enter a research topic → Get a complete academic literature review in minutes.**  
Powered by 4 LangGraph agents · 5 academic sources · Bilingual (English + Urdu)

[🚀 Features](#-features) · [🏗 Architecture](#-architecture) · [⚡ Quick Start](#-quick-start) · [📁 Project Structure](#-project-structure)

---

![DeepResearch Demo](https://raw.githubusercontent.com/nimra-pixel/deepresearch/main/assets/demo.png)

</div>

---

## 🌟 What is DeepResearch Agent?

DeepResearch Agent is a **fully autonomous multi-agent AI system** that writes complete academic literature reviews. Give it a research topic — it searches 5 academic databases, clusters papers by theme, detects research gaps, and writes a structured literature review with proper citations.

**Built 100% on free APIs** — Groq (free tier), PubMed (free), ArXiv (free), CrossRef (free), OpenAlex (free).

> ⚠️ **Disclaimer**: AI-generated literature review. Verify all citations and claims before academic submission.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **5-Source Search** | PubMed · ArXiv · Semantic Scholar · CrossRef · OpenAlex |
| 🔗 **Smart Clustering** | Groups papers into themes automatically |
| 🕳 **Gap Detection** | Finds what hasn't been studied yet with priority levels |
| ✍️ **Academic Writing** | Full prose sections — no bullet points |
| 🔎 **Quality Check** | Self-evaluates and revises if score < 6/10 |
| ⚡ **Token-Efficient Mode** | ~3,000 tokens/run = 30+ runs/day on free Groq tier |
| 🇵🇰 **Urdu Support** | Bilingual summaries for every section |
| 📄 **Export** | Download `.docx` report + JSON audit trail |
| 🔄 **Model Fallback** | Auto-switches model on rate limit — never crashes |
| 🌐 **Citation Network** | Interactive Plotly graph of paper relationships |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Web UI                         │
│        (full-page · 6 result tabs · bilingual · export)      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  LangGraph StateGraph                        │
│                                                              │
│  START → SearchAgent → AnalystAgent → WriterAgent            │
│                                           │                  │
│                                      CriticAgent             │
│                                     ↙          ↘            │
│                               revise        finalize         │
│                                                │             │
│                                              END             │
└─────────────────────────────────────────────────────────────┘
                       │
     ┌─────────────────┼──────────────────┐
     ▼                 ▼                  ▼
PubMed + ArXiv   Semantic Scholar   CrossRef + OpenAlex
```

### Agent Responsibilities

| Agent | Role | Token Cost |
|-------|------|-----------|
| **SearchAgent** | Query expansion + 5-source parallel fetch | ~400 tokens |
| **AnalystAgent** | Cluster papers + detect gaps + build citation network | ~1,500 tokens |
| **WriterAgent** | Write full review (efficient: 1 call / normal: per-section) | ~1,500–8,000 tokens |
| **CriticAgent** | Score quality, trigger revision if needed | ~300 tokens (skipped in efficient mode) |

---

## ⚡ Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/nimra-pixel/deepresearch.git
cd deepresearch
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
copy .env.example .env
```

Edit `.env` — only 2 fields required:

```env
GROQ_API_KEY=gsk_your_key_here      # free at console.groq.com
NCBI_EMAIL=your_email@gmail.com     # free, needed for PubMed
```

### 4. Run

```bash
streamlit run app.py
```

Opens at **http://localhost:8501** 🚀

---

## 📁 Project Structure

```
deepresearch/
│
├── app.py                      # Streamlit web UI
├── graph.py                    # LangGraph StateGraph pipeline
├── requirements.txt
├── .env.example
│
├── agents/
│   ├── state.py                # TypedDict DeepResearchState schema
│   ├── search_agent.py         # Query expansion + 5-source parallel fetch
│   ├── analyst_agent.py        # Clustering + gap detection
│   ├── writer_agent.py         # Literature review writer (efficient + normal mode)
│   └── critic_agent.py         # Quality scorer + revision trigger
│
├── sources/
│   ├── pubmed.py               # NCBI PubMed Entrez API
│   ├── arxiv.py                # ArXiv public API
│   ├── semantic_scholar.py     # Semantic Scholar Graph API
│   ├── crossref.py             # CrossRef REST API
│   └── openalex.py             # OpenAlex API (250M+ papers)
│
└── utils/
    ├── config.py               # Pydantic settings
    ├── llm.py                  # LLM factory + auto fallback chain
    └── report_exporter.py      # .docx report generator
```

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Agent Orchestration** | [LangGraph](https://langchain-ai.github.io/langgraph/) 1.2+ |
| **LLM** | [Groq](https://groq.com) — Llama 3.3 70B (free) |
| **LLM Fallback** | llama-3.1-8b-instant → gemma2-9b-it → llama3-8b-8192 |
| **Framework** | [LangChain](https://langchain.com) 1.3+ |
| **Web UI** | [Streamlit](https://streamlit.io) |
| **Visualization** | Plotly + NetworkX (citation graph) |
| **Export** | python-docx |
| **Config** | pydantic-settings |

---

## 🔑 API Keys

| API | Cost | Get it |
|-----|------|--------|
| **Groq** | ✅ Free (100K tokens/day) | [console.groq.com](https://console.groq.com) |
| **PubMed** | ✅ Free (email required) | Just add email to `.env` |
| **ArXiv** | ✅ Free | No key needed |
| **CrossRef** | ✅ Free | No key needed |
| **OpenAlex** | ✅ Free (250M papers) | No key needed |
| **Semantic Scholar** | ✅ Free | No key needed |

---

## ⚡ Token Management

| Mode | Tokens/run | Runs/day (free) |
|------|-----------|----------------|
| **Efficient (default)** | ~3,000 | 30+ runs |
| **Normal** | ~10,000 | ~10 runs |

Toggle in UI or set in `.env`:
```env
EFFICIENT_MODE=true    # default — recommended
MAX_PAPERS=10          # lower = fewer tokens
MAX_TOKENS=1500        # tokens per LLM call
```

---

## 🚀 Deploy to Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Select repo + `app.py`
4. Add secrets:
```toml
GROQ_API_KEY = "gsk_..."
NCBI_EMAIL = "your@email.com"
EFFICIENT_MODE = "true"
```
5. Deploy ✅

---

## 👩‍💻 About the Author

**Nimra Tariq**
AI Engineer & Assistant Professor — Superior University Lahore, Pakistan

[![GitHub](https://img.shields.io/badge/GitHub-nimra--pixel-181717?style=flat&logo=github)](https://github.com/nimra-pixel)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Nimra%20Tariq-0A66C2?style=flat&logo=linkedin)](https://linkedin.com/in/nimra-tariq)

**Other Projects:**
- ⚕️ [MedAgent](https://github.com/nimra-pixel/medagent) — AI Clinical Decision Support (LangGraph + RAG)
- 🛡 [SENTINEL](https://github.com/nimra-pixel/sentinel) — Cyber Defense System (LangGraph)
- 🤖 [HIRA](https://github.com/nimra-pixel/hira) — HR Intelligence Bot
- 🇵🇰 [Urdu LLM](https://huggingface.co/nimra-pixel) — Fine-tuned Llama 3.2 for Urdu

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Built with ❤️ by [Nimra Tariq](https://github.com/nimra-pixel) · Superior University Pakistan

</div>
