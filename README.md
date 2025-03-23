# AussieNewsAI

**AussieNewsAI** is an intelligent news aggregation and analysis platform tailored for Australian media. It scrapes news from major Australian outlets, classifies them using NLP, clusters similar articles, and presents them in a clean Streamlit dashboard. Users can interact with a chatbot to ask questions about the day’s top stories using Retrieval-Augmented Generation (RAG).

## 🌐 Live App

**[👉 Try the app on Streamlit](https://aussienewsai-6wvvp7yylgaabbyxyguef8.streamlit.app/)**

---

## Features

- **Automated News Scraping** from major Australian news sites
- **Topic Classification** using fine-tuned RoBERTa
- **Semantic Clustering** using Sentence-BERT and cosine similarity
- **Interactive News Dashboard** with category filtering and frequency-based highlights
- **Chatbot (RAG)** powered by OpenAI’s GPT-4
- **Automated Pipeline** with GitHub Actions to refresh news daily

---

## Setup

### 1. Clone the Repo

```
git clone https://github.com/yourusername/AussieNewsAI.git
cd AussieNewsAI
```

### 2. Install Dependencies

```
pip install -r requirements.txt
```

### 3. Add Your OpenAI API Key

Create a `.streamlit/secrets.toml` file:

```toml
OPENAI_API_KEY = "your-openai-api-key"
```

---

## Running the Project

### Run Full Pipeline (Scraper + Clustering)

```bash
python pipeline.py
```

### Launch the Dashboard

```bash
streamlit run news_dashboard.py
```

---

## Ask the NewsBot

Type questions in the sidebar like:

- “What happened in sports today?”
- “Tell me about the Chinese Grand Prix”
- “Any major finance news?”

The chatbot uses semantic search + GPT-4 to find the most relevant highlights and generate answers.

---

## Automated Refresh

The GitHub Actions workflow (`.github/workflows/daily-pipeline.yml`) runs daily at midnight UTC to:

- Scrape fresh news
- Re-cluster articles
- Push updated data to the repo

You can also trigger it manually via the **Actions** tab in your GitHub repository.

---

## Roadmap

- [ ] Add article summarization in dashboard using LLMs
- [ ] Improve categorization of articles
- [ ] Deploy on cloud with CI/CD (e.g., GCP Cloud Run, AWS Lambda)
- [ ] Support chatbot interaction in main UI (not just sidebar)
- [ ] Replace file-based storage with a scalable database (e.g., PostgreSQL)