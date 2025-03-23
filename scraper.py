import json
import feedparser
import logging
from newspaper import Article, Config, build
from transformers import pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Set up user agent to avoid 403 errors when scraping
user_agent = "Chrome/115.0.0.0"
config = Config()
config.browser_user_agent = user_agent

# Load topic classification model
model_name = "dstefa/roberta-base_topic_classification_nyt_news"
classifier = pipeline("text-classification", model=model_name, tokenizer=model_name)

def classify_article(text):
    result = classifier(text, truncation=True)
    pred_label = result[0]["label"]
    
    mapping = {
        "Sports": "sports",
        "Arts, Culture, and Entertainment": "music",
        "Business and Finance": "finance",
        "Health and Wellness": "lifestyle",
        "Lifestyle and Fashion": "lifestyle",
        "Science and Technology": "other news",
        "Politics": "other news",
        "Crime": "other news"
    }
    
    mapped = mapping.get(pred_label, "other news")
    allowed = {"sports", "lifestyle", "music", "finance"}
    return mapped if mapped in allowed else "other news"

allowed_labels = {"sports", "lifestyle", "music", "finance"}

base_urls = {
    "9News": "http://www.9news.com.au",
    "ABC": "https://www.abc.net.au",
    "SMH": "https://www.smh.com.au",
    "SBS": "https://www.sbs.com.au",
    "TheAge": "https://www.theage.com.au",
    "Yahoo": "https://au.news.yahoo.com",
}

RSS_FEEDS = {
    "9News": "http://www.9news.com.au/rss",
    "ABC": "https://www.abc.net.au/news/feed/51120/rss.xml",
    "SMH": "https://www.smh.com.au/rss/feed.xml",
    "SBS": "https://www.sbs.com.au/news/topic/latest/feed",
    "TheAge": "https://www.theage.com.au/rss/feed.xml",
    "Yahoo": "https://au.news.yahoo.com/rss",
}

def build_source_categories():
    source_categories = {}
    for source, base_url in base_urls.items():
        try:
            paper = build(base_url, memoize_articles=False)
            source_categories[source] = paper.category_urls()
        except Exception as e:
            logging.warning(f"Error building newspaper for {source}: {e}")
            source_categories[source] = []
    return source_categories

def infer_category_from_url(article_url, source, source_categories):
    cat_urls = source_categories.get(source, [])
    for cat_url in cat_urls:
        if cat_url.lower() in article_url.lower():
            if "sports" in cat_url.lower():
                return "sports"
            elif "lifestyle" in cat_url.lower():
                return "lifestyle"
            elif "business" in cat_url.lower() or "finance" in cat_url.lower():
                return "finance"
            elif "music" in cat_url.lower():
                return "music"
    return "other news"

def fetch_rss_articles(rss_url):
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries:
        category = None
        if 'tags' in entry and entry.tags:
            category = entry.tags[0].get("term", None)
        elif 'category' in entry:
            category = entry.get("category", None)
        articles.append({
            "url": entry.link,
            "title": entry.get("title", ""),
            "publish_date": entry.get("published", ""),
            "category": category
        })
    return articles

def extract_article_details(article_info):
    article = Article(article_info["url"], config=config)
    article.download()
    article.parse()
    article_info["authors"] = article.authors
    article_info["text"] = article.text
    return article_info

def main():
    source_categories = build_source_categories()
    all_articles = []

    for source, rss_url in RSS_FEEDS.items():
        logging.info(f"Fetching articles from {source}...")
        try:
            articles_info = fetch_rss_articles(rss_url)
        except Exception as e:
            logging.error(f"Error fetching RSS feed from {source}: {e}")
            continue

        for info in articles_info:
            try:
                logging.info(f"Processing: {info['url']}")
                article = extract_article_details(info)
                article["source"] = source

                category = article.get("category", "")
                assigned = False

                if category:
                    for label in allowed_labels:
                        if label in category.lower():
                            article["category"] = label
                            assigned = True
                            break

                if not assigned:
                    inferred = infer_category_from_url(article["url"], source, source_categories)
                    if inferred in allowed_labels:
                        article["category"] = inferred
                        assigned = True

                if not assigned and article.get("text"):
                    article["category"] = classify_article(article["text"])
                elif not article.get("category"):
                    article["category"] = "other news"

                if article["category"] in allowed_labels:
                    all_articles.append(article)

            except Exception as e:
                logging.warning(f"Error processing article: {e}")
    
    with open("data/articles.json", "w") as outfile:
        json.dump(all_articles, outfile, indent=4)

    logging.info(f"Extraction complete. {len(all_articles)} articles saved to data/articles.json.")

if __name__ == "__main__":
    main()
