import json
import os
import streamlit as st
from collections import defaultdict
from chatbot.rag_chat import generate_answer

# Load clustered articles
with open("data/articles_clustered.json", "r") as f:
    articles = json.load(f)

# Group articles by cluster ID
clusters = defaultdict(list)
for article in articles:
    cluster_id = article.get("cluster_id", -1)
    clusters[cluster_id].append(article)

# Merge metadata for each cluster
cluster_data = []
for cluster_id, items in clusters.items():
    sample = items[0]
    merged = {
        "cluster_id": cluster_id,
        "title": sample["title"],
        "category": sample.get("category", "other news"),
        "sources": set(),
        "urls_sources": set(),
        "publish_dates": set(),
        "frequency": len(items),
    }
    for item in items:
        merged["sources"].add(item.get("source", "Unknown"))
        merged["urls_sources"].add((item.get("source", "Unknown"), item["url"]))
        merged["publish_dates"].add(item.get("publish_date", ""))
    cluster_data.append(merged)

# Organize clusters by category
grouped_by_category = defaultdict(list)
for item in cluster_data:
    grouped_by_category[item["category"]].append(item)

# Sort each category by frequency
for category in grouped_by_category:
    grouped_by_category[category] = sorted(
        grouped_by_category[category], key=lambda x: x["frequency"], reverse=True
    )

# ========== Streamlit UI ==========
st.set_page_config(page_title="News Highlights Dashboard", layout="wide")
st.title("🗞️ News Highlights Dashboard")

# Sidebar: Category Selector
categories = sorted(grouped_by_category.keys())
selected_category = st.sidebar.selectbox("Select a category", categories)

# Main: Article Highlights
st.header(f"Top News in **{selected_category.capitalize()}**")

for article in grouped_by_category[selected_category]:
    st.markdown(f"### {article['title']}")
    st.write(f"**Sources:** {', '.join(sorted(article['sources']))}")
    st.write(f"**Frequency:** {article['frequency']}")

    st.markdown("**Read from:**")
    for source, url in sorted(article["urls_sources"]):
        matching = [
            a for a in clusters[article["cluster_id"]]
            if a.get("source") == source and a.get("url") == url
        ]
        if matching:
            a = matching[0]
            authors = ", ".join(a.get("authors", [])) or "Unknown"
            date = a.get("publish_date", "Unknown")
            st.markdown(f"- [{source}]({url}) — _{authors} • {date}_")
        else:
            st.markdown(f"- [{source}]({url}) — _Unknown author • Unknown date_")

    st.markdown("---")

# === Sidebar Chatbot ===
st.sidebar.markdown("---")
st.sidebar.subheader("Ask the NewsBot")

user_query = st.sidebar.text_input("What do you want to know?", key="chatbox")

if user_query:
    with st.spinner("Thinking..."):
        response = generate_answer(user_query)
        st.sidebar.markdown("**Response:**")
        st.sidebar.write(response)