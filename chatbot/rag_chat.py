import json
import os
from dotenv import load_dotenv
from openai import OpenAI
import nest_asyncio
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

nest_asyncio.apply()
load_dotenv()

# Initialize the OpenAI client with your API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load clustered articles and embed them once
with open("data/articles_clustered.json") as f:
    articles = json.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")

docs = [f"{a['title']} {a.get('text', '')}" for a in articles]
doc_embeddings = model.encode(docs, convert_to_numpy=True)

def generate_answer(query, top_k=3):
    query_embedding = model.encode([query], convert_to_numpy=True)
    scores = cosine_similarity(query_embedding, doc_embeddings)[0]
    top_indices = scores.argsort()[-top_k:][::-1]

    retrieved_docs = "\n\n".join([docs[i] for i in top_indices])

    prompt = f"""You're a news assistant. Based on the following news snippets, answer the question.

News:
{retrieved_docs}

Question: {query}
Answer:"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()