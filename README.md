# 🚀 ContentBoost AI

**Product Description Optimization Engine** for e-commerce teams.

Automatically improve product descriptions using competitor scraping, memory-based learning, and LLM generation.

## ✨ Features

- **Competitor Scraping** — Scrape 3–5 competitor product pages via Firecrawl to extract titles, descriptions, bullet points, and key features
- **Memory-Based Learning** — mem0 stores past descriptions and feedback; retrieves top relevant improvements for each new request
- **3-Stage LLM Chain** — Claude-powered pipeline: competitor analysis → memory context → variant generation
- **3 Optimized Variants** — SEO-focused, Conversion-focused, and Brand-differentiated descriptions
- **SEO Scorer** — Scores each variant 0–100 on keyword match, length, readability, and power words
- **Optimization History** — SQLite-backed history with "Save Best Variant" functionality
- **Demo Mode** — Fully functional without API keys using rich sample data

## 🏗️ Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Firecrawl   │    │   Anthropic  │    │    mem0      │
│  (Scraping)  │    │   (Claude)   │    │  (Memory)    │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────┬───────┴───────────────────┘
                   │
          ┌────────▼────────┐
          │   optimizer.py  │  ← 3-stage chain
          │  (Orchestrator) │
          └────────┬────────┘
                   │
     ┌─────────────┼──────────────┐
     │             │              │
┌────▼────┐  ┌────▼────┐  ┌──────▼──────┐
│ utils.py│  │  db.py  │  │ prompts.py  │
│(Scoring)│  │(SQLite) │  │ (Templates) │
└─────────┘  └─────────┘  └─────────────┘
                   │
          ┌────────▼────────┐
          │     app.py      │
          │  (Streamlit UI) │
          └─────────────────┘
```

## 🚀 Quick Start

### 1. Clone & Setup
```bash
cd contentboostai
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### 2. Configure API Keys (Optional)
```bash
copy .env.example .env
# Edit .env with your API keys
```

| Key | Service | Required? |
|-----|---------|-----------|
| `ANTHROPIC_API_KEY` | Claude LLM | Optional (demo mode available) |
| `FIRECRAWL_API_KEY` | Competitor scraping | Optional (demo mode available) |
| `MEM0_API_KEY` | Memory learning | Optional (demo mode available) |

### 3. Run
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`. Without API keys, it runs in **Demo Mode** with sample data.

## 📁 File Structure

| File | Purpose |
|------|---------|
| `app.py` | Streamlit dashboard UI |
| `optimizer.py` | 3-stage LLM optimization chain |
| `firecrawl_scraper.py` | Competitor page scraping |
| `memory_manager.py` | mem0 memory integration |
| `db.py` | SQLite history storage |
| `prompts.py` | LLM prompt templates |
| `utils.py` | SEO scoring engine |
| `fixtures/` | Sample data for demo mode |

## 📊 SEO Scoring

Each variant is scored 0–100:
- **Keyword Match (40%)** — Target keywords found in content
- **Optimal Length (20%)** — Long description in 150–300 word sweet spot
- **Readability (20%)** — Average sentence length 15–20 words
- **Power Words (20%)** — Presence of conversion-boosting words

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit** — Dashboard UI
- **Anthropic Claude** — LLM generation
- **Firecrawl** — Web scraping
- **mem0** — Memory management
- **SQLite** — Local persistence
