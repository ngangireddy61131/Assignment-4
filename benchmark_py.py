"""
benchmark.py
------------
Empirical running-time comparison of Heapsort against Quicksort and Merge
Sort, across several input SIZES and several input DISTRIBUTIONS
(random, already-sorted, reverse-sorted, few-unique).

Run:
    python benchmark.py

It prints a table of average wall-clock times (milliseconds) and, if
matplotlib is installed, saves a plot to ``benchmark_results.png``.

Copy the printed table into report.md where indicated.

NOTE on Quicksort: we use a RANDOMIZED pivot. A deterministic last-element
pivot would hit its O(n^2) worst case on sorted / reverse-sorted input and
also blow Python's recursion limit; randomization makes the expected time
O(n log n) regardless of the input order, which is the fair comparison.
"""

import random
import sys
import time
from typing import Callable, List

from heapsort import heapsort   # reuse the implementation under test

sys.setrecursionlimit(1_000_000)


# --------------------------------------------------------------------------
# Sorting algorithms to compare
# --------------------------------------------------------------------------
def quicksort(a: List[int]) -> List[int]:
    """In-place randomized quicksort (iterative stack to avoid deep recursion)."""
    a = a[:]  # work on a copy so callers' data is untouched
    stack = [(0, len(a) - 1)]
    while stack:
        lo, hi = stack.pop()
        if lo >= hi:
            continue
        # randomized pivot -> expected O(n log n) on any input order
        p = random.randint(lo, hi)
        a[p], a[hi] = a[hi], a[p]
        pivot = a[hi]
        i = lo
        for j in range(lo, hi):
            if a[j] < pivot:
                a[i], a[j] = a[j], a[i]
                i += 1
        a[i], a[hi] = a[hi], a[i]
        # push larger side last so the smaller side is processed first
        stack.append((lo, i - 1))
        stack.append((i + 1, hi))
    return a


def merge_sort(a: List[int]) -> List[int]:
    """Classic top-down merge sort. O(n log n) time, O(n) auxiliary space."""
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left = merge_sort(a[:mid])
    right = merge_sort(a[mid:])

    merged: List[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def heapsort_copy(a: List[int]) -> List[int]:
    """Wrapper so the harness never mutates the shared input array."""
    return heapsort(a[:])


# --------------------------------------------------------------------------
# Input generators
# --------------------------------------------------------------------------
def gen_random(n: int) -> List[int]:
    return [random.randint(0, n) for _ in range(n)]


def gen_sorted(n: int) -> List[int]:
    return list(range(n))


def gen_reversed(n: int) -> List[int]:
    return list(range(n, 0, -1))


def gen_few_unique(n: int) -> List[int]:
    return [random.randint(0, 9) for _ in range(n)]


DISTRIBUTIONS = {
    "random":        gen_random,
    "sorted":        gen_sorted,
    "reverse":       gen_reversed,
    "few-unique":    gen_few_unique,
}

ALGORITHMS = {
    "Heapsort":   heapsort_copy,
    "Quicksort":  quicksort,
    "MergeSort":  merge_sort,
}


# --------------------------------------------------------------------------
# Timing
# --------------------------------------------------------------------------
def time_algorithm(fn: Callable[[List[int]], List[int]],
                   data: List[int], repeats: int = 3) -> float:
    """Return the best wall-clock time (ms) over ``repeats`` runs.

    Best-of-k reduces noise from GC pauses and OS scheduling; it reflects the
    algorithm's intrinsic cost better than an average that includes outliers.
    """
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        fn(data)
        elapsed = (time.perf_counter() - start) * 1000.0
        best = min(best, elapsed)
    return best


def run_benchmarks() -> dict:
    sizes = [1_000, 5_000, 10_000, 50_000, 100_000]
    results: dict = {}

    for dist_name, gen in DISTRIBUTIONS.items():
        print(f"\n### Distribution: {dist_name}")
        header = f"{'n':>8} | " + " | ".join(f"{name:>10}" for name in ALGORITHMS)
        print(header)
        print("-" * len(header))
        for n in sizes:
            data = gen(n)
            row = {}
            cells = []
            for alg_name, fn in ALGORITHMS.items():
                # correctness guard on the first, smallest case
                if n == sizes[0]:
                    assert fn(data) == sorted(data), f"{alg_name} wrong on {dist_name}"
                t = time_algorithm(fn, data)
                row[alg_name] = t
                cells.append(f"{t:>10.2f}")
            results[(dist_name, n)] = row
            print(f"{n:>8} | " + " | ".join(cells))

    return results


def maybe_plot(results: dict) -> None:
    """Save a log-log runtime plot per distribution, if matplotlib exists."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n(matplotlib not installed -- skipping plot. "
              "`pip install matplotlib` to enable.)")
        return

    sizes = sorted({n for (_, n) in results})
    dists = list(DISTRIBUTIONS)
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    for ax, dist in zip(axes.ravel(), dists):
        for alg in ALGORITHMS:
            ys = [results[(dist, n)][alg] for n in sizes]
            ax.plot(sizes, ys, marker="o", label=alg)
        ax.set_title(f"{dist} input")
        ax.set_xlabel("n (elements)")
        ax.set_ylabel("time (ms)")
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.grid(True, which="both", ls=":", alpha=0.5)
        ax.legend()
    fig.suptitle("Sorting algorithm runtime vs input size (log-log)")
    fig.tight_layout()
    fig.savefig("benchmark_results.png", dpi=120)
    print("\nSaved plot -> benchmark_results.png")


if __name__ == "__main__":
    random.seed(42)   # reproducible inputs
    print("Benchmarking Heapsort vs Quicksort vs Merge Sort")
    print("(times are best-of-3, in milliseconds)")
    results = run_benchmarks()
    maybe_plot(results)
    print("\nDone. Paste the tables above into report.md (Section 3).")
