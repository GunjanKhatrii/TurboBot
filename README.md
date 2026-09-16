# TurboBot - Wind Turbine Performance Monitor ⚡🤖

A full-stack AI assistant for wind turbine maintenance and operations, powered by Retrieval-Augmented Generation (RAG) to provide accurate, **cited**, and actionable technical guidance — running entirely on a **local** language model.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)](https://reactjs.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-orange.svg)](https://ollama.ai/)

---

## 🎯 What is TurboBot?

TurboBot combines:
- **Real-time turbine data analysis** (power, temperature, vibration, wind speed)
- A curated **knowledge base** of wind-turbine maintenance manuals
- **RAG (Retrieval-Augmented Generation)** for accurate, grounded, source-cited responses
- A **local AI model** via Ollama — no per-query API cost, runs offline, data stays on-device
- A **three-layer guardrail system** (input, topic, and output validation) with graceful fallback

### The problem it solves

General-purpose LLMs hallucinate technical details — costs, thresholds, procedures — which is unacceptable for maintenance decisions. TurboBot retrieves the relevant passages from maintenance manuals **before** generating a response, so answers are:
- ✅ **Grounded** in the actual manuals rather than invented
- ✅ **Cited** — each answer references the source manual/section
- ✅ **Specific** — real thresholds, procedures, and cost ranges in euros
- ✅ **Honest** — when no manual matches, the bot explicitly says it's answering from general knowledge

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- [Ollama](https://ollama.ai/download) installed

### Installation

```bash
# 1. Clone repository
git clone https://github.com/GunjanKhatrii/TurboBot.git
cd TurboBot

# 2. Install Python dependencies
conda create -n turbobot python=3.9
conda activate turbobot
pip install -r requirements.txt

# 3. Install Ollama and download the model
ollama pull llama3.2:1b

# 4. Install frontend dependencies
npm install
```

> **Memory system (optional, off by default).** An experimental conversation-memory module lives in `memory/`. For single-query turbine analysis, RAG-only responses were clearer and the small model performed better without conversation history, so memory is disabled by default.

### Running the application

```bash
# Terminal 1: Start Ollama server
ollama serve

# Terminal 2: Start backend (Flask, port 5000)
python backend.py

# Terminal 3: Start frontend (Vite dev server)
npm run dev
```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   React + TypeScript Frontend                │
│               • Chat interface (ChatInterface.tsx)           │
│               • Real-time charts (Recharts)                  │
│               • Turbine dashboard & alerts                   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP / JSON (fetch → :5000)
┌────────────────────────▼────────────────────────────────────┐
│                 Flask Backend (Port 5000)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│  │   Turbine    │  │     RAG      │  │   Guardrails    │    │
│  │  Data API    │  │   Manager    │  │  (in/topic/out) │    │
│  └──────────────┘  └──────┬───────┘  └─────────────────┘    │
│                           │                                  │
│                    ┌──────▼───────┐    ┌────────────────┐   │
│                    │ TF-IDF       │    │  Local LLM     │   │
│                    │ Retriever    │    │  Ollama        │   │
│                    │ (scikit-learn)│    │  llama3.2:1b  │   │
│                    └──────────────┘    └────────────────┘   │
└──────────────────────────────────────────────────────────────┘
             │
    ┌────────▼─────┐   Knowledge base: 2 active manuals
    │ Knowledge    │   (gearbox maintenance + vibration analysis)
    │ Base (.txt)  │   → 30 chunks, TF-IDF indexed
    └──────────────┘
```

---

## 🧠 RAG System Explained

### How it works

1. **Knowledge base** — maintenance manuals as `.txt` files in `data/knowledge_base/`
2. **Document chunking** — documents are split section-aware into overlapping chunks (`chunk_size=2500`, `overlap=50`)
3. **TF-IDF indexing** — scikit-learn `TfidfVectorizer` (unigrams + bigrams) builds a sparse index
4. **Retrieval** — the query is vectorized and ranked against chunks by cosine similarity; the top matches above a minimum score are returned (`top_k=3`, `min_score=0.05`)
5. **Generation** — retrieved chunks are injected into the system prompt and the local LLM answers from them, citing sources

```python
# Example: user asks "What causes bearing failure?"

# Step 1: retrieve relevant knowledge
context = rag_manager.retrieve_context("bearing failure", top_k=3)
# → returns the most relevant chunks from the gearbox / vibration manuals

# Step 2: build a prompt that includes the retrieved context + live turbine data
# Step 3: the local model generates a grounded, cited response
```

---

## 📁 Project Structure

```
TurboBot/
├── backend.py                 # Flask API server + chat pipeline
├── requirements.txt           # Python dependencies
├── package.json               # Node.js dependencies
│
├── src/                       # React + TypeScript frontend
│   ├── pages/                 # Dashboard, Index, NotFound
│   ├── components/            # ChatInterface, PowerChart, MetricCard,
│   │   │                      #   WindPowerScatter, AlertSection …
│   │   └── ui/                # shadcn/ui components
│   └── lib/turbineData.ts     # frontend data helpers
│
├── rag/                       # RAG system (core)
│   ├── knowledge_loader.py    # loads .txt manuals from the knowledge base
│   ├── document_chunker.py    # section-aware chunking with overlap
│   ├── retriever.py           # TF-IDF + cosine-similarity retriever
│   └── rag_manager.py         # orchestrates load → chunk → index → retrieve
│
├── guardrails/                # Safety & quality layer
│   ├── input_validation.py    # security / length / spam + topic relevance
│   ├── output_validation.py   # quality, hallucination & citation checks
│   ├── topic_validator.py
│   └── content_filter.py      # coordinates input + output validation
│
├── memory/                    # Optional conversation memory (off by default)
│
└── data/
    └── knowledge_base/
        ├── 01_gearbox_maintenance.txt      # active
        ├── 02_vibration_analysis.txt       # active
        └── backup_optional/                # additional manuals (see below)
```

---

## 📚 Knowledge Base

The **active** knowledge base is intentionally scoped to the **two most critical and representative failure domains** in wind-turbine operations:

| Document | Focus | Words | Chars |
|----------|-------|------:|------:|
| **Gearbox Maintenance** | Bearing failures, oil analysis, thresholds, replacement costs | ~1,700 | ~11,700 |
| **Vibration Analysis** | Frequency analysis, diagnostic techniques, alarm thresholds | ~2,100 | ~14,300 |

**Active total: ~3,800 words / ~26,000 characters → 30 indexed chunks (561 TF-IDF features).**

### Why 2 manuals instead of the full set?

This was a deliberate scoping decision, not a shortcut:

- **Retrieval precision on a small local model.** With a compact 1B-parameter model and a limited context window, feeding a large, diverse corpus produced noisier retrieval and diluted prompts. A focused knowledge base keeps the retrieved chunks tightly relevant and the prompt within the size the small model handles reliably.
- **Highest-value coverage.** Gearbox and drivetrain issues (surfaced largely through **vibration**) are among the most frequent and most expensive wind-turbine failure modes, so these two manuals give the most representative coverage for a proof of concept.
- **Cleaner evaluation.** A small, well-understood corpus makes it easy to verify that the *right* passage is being retrieved for a given question.

The remaining maintenance manuals (power curve, temperature monitoring, common failures, maintenance schedule, safety protocols, troubleshooting, cost estimates, seasonal considerations) are **retained in `data/knowledge_base/backup_optional/`** and can be enabled at any time by moving them up into `data/knowledge_base/` — the loader will index them automatically on the next start. The system is designed to scale to the full set; the active set is scoped for demo quality on a local model.

---

## 🎯 Key Features

### 1. RAG-grounded, cited responses

**Without RAG:** generic answer, wrong currency, no source.
**With RAG:** *"According to the Gearbox Maintenance Manual, gearbox replacement costs €100,000–€250,000, including crane rental, the new gearbox, and installation …"* — specific, cited, actionable.

### 2. Real-time turbine monitoring
- Power output with a realistic cubic wind-speed relationship
- Temperature and vibration with multi-level thresholds (Normal / Monitor / Warning / Critical)
- Automatic status flags for out-of-range values

### 3. Interactive dashboard
- 48-hour performance charts (Recharts)
- Current readings against thresholds
- Anomaly / warning highlighting
- Context-aware chat that sees the live telemetry

### 4. Three-layer guardrails
- **Input:** length, spam, and security-pattern checks
- **Topic:** keeps the assistant scoped to turbine topics; off-topic questions get a helpful redirect (no LLM call)
- **Output:** quality scoring, hallucination detection against the retrieved context, citation verification, harmful-content checks — with a **rule-based fallback** if the model fails

### 5. Zero per-query cost, offline, private
- Runs 100% locally via Ollama — no API fees, no data leaving the machine

---

## 🔧 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/turbine-chat` | Ask a question (body: `question`, `turbineData`) |
| `GET`  | `/api/turbine-data` | 48 hours of (synthetic) turbine telemetry |
| `GET`  | `/api/knowledge-base/stats` | RAG statistics |
| `GET`  | `/api/guardrails/stats` | Guardrail configuration/stats |
| `GET`  | `/api/health` | Health check (model, RAG, guardrails) |
| `GET`  | `/api/test` | Basic status |

> **Note on data:** `/api/turbine-data` generates **synthetic** telemetry — 48 hours built on a cubic wind-to-power curve, with temperature/vibration correlated to load and a degradation trend injected in the final readings to create a realistic "warning" scenario. The engineering focus of the project is the RAG + guardrails pipeline, not real sensor ingestion (real SCADA integration is listed as future work).

---

## ⚙️ Configuration

### Environment variables (`.env`)

```bash
# AI provider — the committed backend runs Ollama locally.
# openai / claude were used during earlier iterations (see note below).
AI_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:1b

# Optional keys (only needed if switching provider back)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Flask
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### RAG / retrieval settings

```python
# rag/rag_manager.py
self.chunker = DocumentChunker(chunk_size=2500, overlap=50)
rag_manager.retrieve_context(query, top_k=3, min_score=0.05)

# rag/retriever.py
TfidfVectorizer(max_features=2000, stop_words='english',
                ngram_range=(1, 2), min_df=2, max_df=0.7)
```

---

## 🎓 Technical Deep Dive (design decisions)

### Why a local model (Ollama) instead of the OpenAI / Claude APIs?

The project was **first prototyped against the OpenAI and Anthropic Claude APIs**, but iterative development burns through tokens very quickly — many prompt/guardrail iterations exhausted the available token budget and rate limits fast, which made rapid experimentation slow and costly. Switching to a **local `llama3.2:1b` via Ollama** gave:
- **Unlimited, free local iteration** — no token budget to manage
- **Offline capability** and **data privacy** (operational data never leaves the machine)
- A single, reproducible dev setup

The trade-off is that a 1B local model is weaker than a frontier API model, so the design leans harder on **RAG grounding + guardrails** to keep answers accurate. The provider is env-driven, so switching back to a hosted model later is a configuration change, not a rewrite.

### Why TF-IDF for retrieval (instead of embeddings / a vector DB)?

- ⚡ **Fast** and **CPU-only** — no GPU, ~sub-second retrieval on this corpus
- 🧮 **Lightweight & interpretable** — you can see *why* a chunk matched
- 🔌 **Offline & free** — no external embedding API
- **Trade-off:** TF-IDF is lexical, so it can miss purely semantic matches. Embeddings (sentence-transformers) + a vector store are the documented next step.

### Chunk sizing — and why the values changed

Chunking was tuned iteratively. Earlier iterations used smaller chunks with heavier overlap; the committed configuration is **`chunk_size=2500`, `overlap=50`**. The shift to **larger chunks with minimal overlap** was deliberate:

- **Preserve complete units of meaning.** Maintenance content comes in whole procedures, threshold lists, and cost tables. Larger chunks keep these intact in a single retrieved passage, which improves answer completeness and makes citations reliable — small chunks tended to cut procedures in half.
- **Fewer, information-dense chunks suit a small model.** With a focused corpus and a 1B model, a modest number of rich chunks retrieves more cleanly and keeps the prompt compact than many fragmented ones.
- **Less overlap needed.** With fewer, larger chunks the redundancy from high overlap added little, so overlap was reduced to keep the index lean and prompts short.
- **Trade-off:** coarser retrieval granularity — accepted here because precision on this corpus stayed high (30 chunks, easy to verify).

### Why guardrails?

A small local model needs guarding. Three layers — input (security/spam), topic (stay a turbine assistant), and output (hallucination/citation/quality/harmful-content) — plus **graceful degradation**: if the model fails or output validation trips, a deterministic rule-based analysis still answers from the live telemetry.

---

## 🧪 Testing

```bash
# RAG components (initialization, retrieval quality, context format, stats)
python test_rag.py

# Guardrail behaviour
python test_guardrails.py

# Quick backend chat check
curl -X POST http://localhost:5000/api/turbine-chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What causes bearing failure?",
       "turbineData":[{"power_output":1200,"temperature":65,"vibration":3.2,"status":"operating"}]}'
```

`test_rag.py` is a **functional** test suite: it asserts that initialization succeeds, that known queries retrieve the expected keywords/source manual, and that the assembled context is well-formed and cites sources. It validates behaviour, not a headline accuracy percentage.

### On answer accuracy

RAG produces a clear qualitative improvement — grounded, source-cited, specific answers instead of generic or invented ones. A **rigorous accuracy figure is intentionally not claimed here** because it hasn't been formally benchmarked. Measuring it properly is planned future work: build a labelled set of question → expected-answer pairs, run the system with and without RAG, and score (a) answer correctness and (b) retrieval precision — whether the correct chunk appears in the top-k.

---

## 📦 A note on dependencies

`requirements.txt` includes some packages beyond what the committed backend runs at default settings — notably `openai`, `chromadb`, and `tiktoken`. These are **retained from the project's iterative development**: the OpenAI/Claude providers and a ChromaDB vector-store experiment were real steps along the way. They're kept so those paths remain reproducible and so the provider/retriever can be switched back without hunting down versions. The default runtime path uses **Ollama + scikit-learn TF-IDF**.

---

## 📈 Future Enhancements

- Semantic embeddings (sentence-transformers) + vector store (ChromaDB) as the KB grows
- Enable the full manual set from `backup_optional/`
- A quantitative RAG evaluation harness (see "On answer accuracy")
- Response caching, authentication, rate limiting
- Real SCADA / sensor integration in place of synthetic data
- Multi-turbine / farm-level view

---

## 🙏 Acknowledgments

- **RAG concept:** Lewis et al., *"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"* (2020)
- **Ollama** for accessible local LLMs · **scikit-learn** for TF-IDF · **React**, **Vite**, **shadcn/ui**, **Recharts** · **Flask**

---

## 📞 Contact

**Gunjan Khatri** — gunjan2002khatri@gmail.com
**Project:** https://github.com/GunjanKhatrii/TurboBot

---

<div align="center">

**⭐ Star this repo if you find it useful!** · Made for the wind energy industry 🌱

</div>
