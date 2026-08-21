import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticSearch:
    """
    Local text retrieval using TF-IDF and cosine similarity.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
        )

        self.documents = []
        self.vectors = None

    def fit(self, documents):
        """
        Build the local search index.
        """

        self.documents = documents

        texts = [
            document.get("message", "")
            for document in documents
        ]

        self.vectors = self.vectorizer.fit_transform(texts)

    def search(self, query, top_k=5):
        """
        Retrieve the most relevant messages for a query.
        """

        if self.vectors is None:
            raise ValueError("Search index has not been built.")

        query_vector = self.vectorizer.transform([query])

        scores = cosine_similarity(
            query_vector,
            self.vectors,
        )[0]

        ranked_indices = np.argsort(scores)[::-1][:top_k]

        results = []

        for index in ranked_indices:
            results.append({
                "message_id": self.documents[index]["message_id"],
                "message": self.documents[index]["message"],
                "relevance_score": round(
                    float(scores[index]),
                    4,
                ),
            })

        return results


def answer_query(search_engine, query, top_k=5):
    """
    Answer a query using retrieved messages as evidence.

    This baseline does not generate unsupported facts.
    It returns the strongest retrieved evidence for the query.
    """

    results = search_engine.search(
        query,
        top_k=top_k,
    )

    if not results:
        return {
            "query": query,
            "answer": "Insufficient evidence to answer this question.",
            "supporting_message_ids": [],
            "relevance_scores": [],
            "reason": "No relevant messages were retrieved.",
        }

    # Require a minimum relevance level before presenting evidence.
    relevant_results = [
        result
        for result in results
        if result["relevance_score"] >= 0.10
    ]

    if not relevant_results:
        return {
            "query": query,
            "answer": "Insufficient evidence to answer this question.",
            "supporting_message_ids": [],
            "relevance_scores": [],
            "reason": "Retrieved messages did not provide sufficient evidence.",
        }

    supporting_ids = [
        result["message_id"]
        for result in relevant_results
    ]

    scores = [
        result["relevance_score"]
        for result in relevant_results
    ]

    # Conservative baseline answer: expose the retrieved evidence
    # instead of generating unsupported information.
    answer = (
        "Relevant information was found in: "
        + ", ".join(supporting_ids)
        + "."
    )

    return {
        "query": query,
        "answer": answer,
        "supporting_message_ids": supporting_ids,
        "relevance_scores": scores,
        "reason": (
            "The answer is based only on messages retrieved "
            "above the relevance threshold."
        ),
    }