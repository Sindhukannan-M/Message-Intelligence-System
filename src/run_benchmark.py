import json
import time
from pathlib import Path

from src.l2_pipeline import run_l2_pipeline
from src.benchmark import (
    benchmark_function,
    compare_results,
    get_file_size,
    save_benchmark,
)


OUTPUT_FILE = Path(
    "l2_outputs/benchmark_comparison.json"
)


def baseline_search(messages, query):
    """Simple linear scan used as the baseline."""

    query = query.lower()

    results = []

    for _, row in messages.iterrows():

        message = str(row["message"]).lower()

        if query in message:
            results.append(
                row["message_id"]
            )

    return results


def optimized_search(search_engine, query):
    """TF-IDF based retrieval used by the L2 system."""

    return search_engine.search(
        query,
        top_k=5,
    )


def main():

    pipeline = run_l2_pipeline()

    messages = pipeline["messages"]

    search_engine = pipeline[
        "search_engine"
    ]

    query = "project report"


    # --------------------------------------------------------
    # Baseline
    # --------------------------------------------------------

    baseline_results, baseline_time = (
        benchmark_function(
            baseline_search,
            messages,
            query,
        )
    )


    # --------------------------------------------------------
    # Optimized
    # --------------------------------------------------------

    optimized_results, optimized_time = (
        benchmark_function(
            optimized_search,
            search_engine,
            query,
        )
    )


    # --------------------------------------------------------
    # Result quality comparison
    # --------------------------------------------------------

    optimized_ids = {
        item["message_id"]
        for item in optimized_results
    }

    baseline_ids = set(
        baseline_results
    )

    if optimized_ids:

        overlap = (
            len(
                optimized_ids
                & baseline_ids
            )
            / len(optimized_ids)
        )

    else:

        overlap = 0.0


    # --------------------------------------------------------
    # Compare
    # --------------------------------------------------------

    result = compare_results(
        original_time=baseline_time,
        optimized_time=optimized_time,
        original_size=None,
        optimized_size=None,
        original_quality=1.0,
        optimized_quality=round(
            overlap,
            4,
        ),
    )


    result["query"] = query

    result["baseline_method"] = (
        "linear message scan"
    )

    result["optimized_method"] = (
        "TF-IDF cosine similarity"
    )

    result["baseline_result_count"] = (
        len(baseline_results)
    )

    result["optimized_result_count"] = (
        len(optimized_results)
    )

    result["notes"] = [
        "Baseline uses a direct message scan.",
        "Optimized retrieval uses TF-IDF and cosine similarity.",
        "Response time is measured locally.",
        "Quality is represented by overlap with baseline results.",
    ]


    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_benchmark(
        result,
        OUTPUT_FILE,
    )


    print("Benchmark completed.")

    print(
        f"Baseline time: "
        f"{baseline_time:.6f}s"
    )

    print(
        f"Optimized time: "
        f"{optimized_time:.6f}s"
    )

    print(
        f"Result overlap: "
        f"{overlap:.2%}"
    )

    print(
        f"Saved: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()