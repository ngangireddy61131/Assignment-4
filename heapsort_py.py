"""
heapsort.py
-----------
An in-place implementation of the Heapsort algorithm, built on a binary
max-heap that is represented implicitly as a Python list (array).

Heapsort runs in two phases:

  1. BUILD-MAX-HEAP: rearrange the input array so it satisfies the max-heap
     property (every parent is >= both of its children). Done bottom-up in
     O(n) time.

  2. SORT: repeatedly swap the root (the current maximum) with the last
     element of the "live" heap region, shrink that region by one, and
     restore the heap property with a single sift-down (max_heapify). After
     n - 1 extractions the whole array is sorted in ascending order.

Array index layout (0-based):

        parent(i) = (i - 1) // 2
        left(i)   =  2 * i + 1
        right(i)  =  2 * i + 2

Author: (graduate student submission)
"""

from typing import Any, List


def max_heapify(a: List[Any], i: int, heap_size: int) -> None:
    """Restore the max-heap property for the subtree rooted at index ``i``.

    Precondition: the subtrees rooted at ``left(i)`` and ``right(i)`` are
    already valid max-heaps; only ``a[i]`` may violate the property. This
    routine lets ``a[i]`` "sift down" until the subtree is a valid heap.

    An iterative loop is used instead of recursion so that the algorithm
    adds no frames to the call stack (keeping auxiliary space at O(1)).

    Time complexity: O(log n) -- the element descends at most the height of
    the heap, which is floor(log2(n)).
    """
    while True:
        left = 2 * i + 1
        right = 2 * i + 2
        largest = i

        if left < heap_size and a[left] > a[largest]:
            largest = left
        if right < heap_size and a[right] > a[largest]:
            largest = right

        if largest == i:          # heap property already holds -> done
            return

        a[i], a[largest] = a[largest], a[i]   # swap down
        i = largest                            # continue from new position


def build_max_heap(a: List[Any]) -> None:
    """Transform an arbitrary array into a max-heap, in place.

    We invoke ``max_heapify`` on every internal node, iterating from the last
    internal node (index n // 2 - 1) up to the root (index 0). The second half
    of the array consists of leaves, which are trivially valid one-element
    heaps, so they are skipped.

    Time complexity: O(n). Although a loose bound of O(n log n) is easy to
    state, a tighter amortized analysis -- summing the work by node height --
    gives the exact linear bound (derivation in report.md).
    """
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        max_heapify(a, i, n)


def heapsort(a: List[Any]) -> List[Any]:
    """Sort list ``a`` into ascending order, in place.

    The list is also returned for convenience / chaining.

    Phase 1 builds a max-heap. Phase 2 maintains the invariant:
        a[0:heap_size]  is a valid max-heap
        a[heap_size:n]  is the sorted tail (largest elements, in order)
    Each iteration moves the heap's maximum (a[0]) to the front of the sorted
    tail, then repairs the heap with one sift-down.

    Time complexity:  O(n log n) in the worst, average, AND best case.
    Space complexity: O(1) auxiliary (sorts within the input array; the
                      iterative sift-down uses no recursion stack).
    Stability:        Heapsort is NOT a stable sort.
    """
    n = len(a)
    if n < 2:
        return a

    build_max_heap(a)                 # Phase 1: O(n)

    for end in range(n - 1, 0, -1):   # Phase 2: n - 1 iterations, O(log n) each
        a[0], a[end] = a[end], a[0]   # move current max to its final slot
        max_heapify(a, 0, end)        # restore heap over a[0:end]

    return a


if __name__ == "__main__":
    import random

    # ---- Correctness self-check across several cases ----------------------
    cases = {
        "random":        [random.randint(0, 1000) for _ in range(50)],
        "already sorted": list(range(50)),
        "reverse sorted": list(range(50, 0, -1)),
        "with duplicates": [random.randint(0, 5) for _ in range(50)],
        "single element": [42],
        "empty":          [],
    }

    for name, data in cases.items():
        expected = sorted(data)
        result = heapsort(data[:])     # copy so we keep the original around
        status = "OK" if result == expected else "FAILED"
        print(f"[{status}] {name}")
        assert result == expected, f"Heapsort failed on case: {name}"

    print("\nAll correctness checks passed.")
