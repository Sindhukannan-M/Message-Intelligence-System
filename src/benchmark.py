import time
import json
from pathlib import Path


def benchmark_function(function, *args, **kwargs):
    """Measure execution time for a function."""

    start = time.perf_counter()

    result = function(*args, **kwargs)

    elapsed = time.perf_counter() - start

    return result, elapsed


def get_file_size(path):
    """Return file size in KB."""

    file_path = Path(path)

    if not file_path.exists():
        return None

    return round(file_path.stat().st_size / 1024, 2)


def compare_results(
    original_time,
    optimized_time,
    original_size=None,
    optimized_size=None,
    original_quality=None,
    optimized_quality=None,
):
    """Create a simple benchmark comparison."""

    if original_time > 0:
        speed_change = (
            (original_time - optimized_time)
            / original_time
        ) * 100
    else:
        speed_change = 0

    result = {
        "original": {
            "response_time_seconds": round(
                original_time,
                4,
            ),
            "size_kb": original_size,
            "quality": original_quality,
        },
        "optimized": {
            "response_time_seconds": round(
                optimized_time,
                4,
            ),
            "size_kb": optimized_size,
            "quality": optimized_quality,
        },
        "improvement": {
            "response_time_change_percent": round(
                speed_change,
                2,
            )
        },
    }

    return result


def save_benchmark(result, output_path):
    """Save benchmark results as JSON."""

    output_file = Path(output_path)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            indent=2,
        )