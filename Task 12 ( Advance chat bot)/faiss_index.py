import faiss
import numpy as np
from data import qna_data
from embedder import get_embedding

dimension = 384
index = faiss.IndexFlatL2(dimension)

questions = []
answers = []

# Build index
for item in qna_data:
    questions.append(item["question"])
    answers.append(item["answer"])

    emb = get_embedding(item["question"])
    index.add(np.array([emb]))

def search(query):
    query_vec = get_embedding(query)
    D, I = index.search(np.array([query_vec]), 1)

    idx = I[0][0]
    return answers[idx]