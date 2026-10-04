# Assignment-4
Heapsort implementation and analysis and an array-based binary-heap priority queue (with a task-scheduler simulation), and Heapsort versus Quicksort and Merge Sort.


Repository contents

heapsort.py =>	In-place Heapsort on an array-backed max-heap. Self-tests when run directly.
priority_queue.py =>	Task class + min-heap priority queue (insert, extract_min/max, increase_key, decrease_key, is_empty) and a scheduler simulation.
benchmark.py =>	Times Heapsort vs Quicksort vs Merge Sort across sizes and distributions.
report.md =>	Full written report: complexity proofs, space analysis, empirical discussion, design justifications.
README.md =>	This file.


Requirements
•	Python 3.8+ (uses dataclasses and from __future__ import annotations).
•	No third-party packages are required to run the code or the benchmark.
•	Optional: matplotlib if installed, benchmark.py also saves a benchmark_results.png plot. Install with pip install matplotlib.


How to run
Each module is runnable on its own.
1. Heapsort correctness self-checks (random, sorted, reverse, duplicates, edge cases)
python heapsort.py
2. Priority-queue self-checks + the task-scheduler simulation
python priority_queue.py
3. Empirical comparison (prints timing tables; optionally saves a plot)
python benchmark.py
benchmark.py uses a fixed random seed, so the inputs are reproducible across runs on the same machine.


Summary of findings
Heapsort has the best and worst case of O(n log n) Heapsort is an O(n) algorithm to build the heap; The extraction loop is O(log n) and the total of the two is 0 (n log n) without some shortcut that would depend on the input. Their best and the worst cases are similar.
Space: It is a heap sort of space with value (iterative sift-down, no recursion stack) - the primary favorable aspect of the space sort in comparison with Merge Sort is O(n).
The three sorts are all empirical increasing functions of n log n and randomized Quicksort is the fastest of wall-clock time and Heapsort is the slowest, and the index jumps of Heapsort are not cache-friendly. Heapsort and merge sort are all-time wise, in that they are not sensitive to the input order and the theory All cases O(n log n) is not sensitive to the input order.
Priority queue: Binary heap, implemented in a Python list, has O(log n) insertion and extraction and key-change, O(1) is_empty/peek. An example table keeps track of mapping of task_id and index location hence increase_key/decrease_key is achieved at O(log n) instead of O(n).
