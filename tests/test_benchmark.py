from src.benchmark import (
    benchmark_function,
    compare_results,
)


def simple_search():
    total = 0

    for number in range(1000):
        total += number

    return total


def test_benchmark_measures_time():
    result, elapsed = benchmark_function(simple_search)

    assert result == 499500
    assert elapsed >= 0


def test_compare_results():
    result = compare_results(
        original_time=1.0,
        optimized_time=0.5,
        original_size=100,
        optimized_size=80,
        original_quality=0.70,
        optimized_quality=0.80,
    )

    assert result["original"]["response_time_seconds"] == 1.0
    assert result["optimized"]["response_time_seconds"] == 0.5
    assert result["improvement"]["response_time_change_percent"] == 50.0