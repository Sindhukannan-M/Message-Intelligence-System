from src.semantic_search import SemanticSearch


def test_search_returns_relevant_message():
    documents = [
        {
            "message_id": "MSG_0901",
            "message": "Please submit the project report by Friday.",
        },
        {
            "message_id": "MSG_0902",
            "message": "The team lunch is scheduled for tomorrow.",
        },
        {
            "message_id": "MSG_0903",
            "message": "The project report has been submitted.",
        },
    ]

    search = SemanticSearch()
    search.fit(documents)

    results = search.search(
        "When is the project report due?",
        top_k=2,
    )

    assert len(results) == 2
    assert results[0]["message_id"] in {
        "MSG_0901",
        "MSG_0903",
    }
    assert "relevance_score" in results[0]

def test_answer_query_uses_evidence():
    from src.semantic_search import answer_query

    documents = [
        {
            "message_id": "MSG_0901",
            "message": "Please submit the project report by Friday.",
        },
        {
            "message_id": "MSG_0902",
            "message": "The team lunch is scheduled for tomorrow.",
        },
    ]

    search = SemanticSearch()
    search.fit(documents)

    result = answer_query(
        search,
        "When is the project report due?",
    )

    assert "query" in result
    assert "answer" in result
    assert "supporting_message_ids" in result
    assert "relevance_scores" in result
    assert "reason" in result