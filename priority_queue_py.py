"""
priority_queue.py
-----------------
A priority queue for task scheduling, implemented on an array-backed binary
*min*-heap, together with a ``Task`` data class and a small scheduler
simulation.

DESIGN CHOICES (see report.md for full justification)
-----------------------------------------------------
* Backing store: a Python ``list`` used as an implicit binary heap. A list
  gives O(1) amortized append, O(1) random access by index (needed to repair
  the heap after a key change), and perfect cache locality -- all without the
  pointer overhead of an explicit tree.

* Min-heap, keyed by ``priority`` where a SMALLER number means a HIGHER
  priority (priority 1 is more urgent than priority 5). This matches the
  real-world "P1 / P2 / P3" convention used by incident and job schedulers,
  so ``extract_min`` naturally returns the most urgent task.

* To make ``increase_key`` / ``decrease_key`` efficient we keep a ``position``
  dictionary mapping each task's id to its current index in the heap array.
  Without it we would need an O(n) scan to locate a task; with it, a key
  change is O(log n).

Index layout (0-based):
    parent(i) = (i - 1) // 2
    left(i)   =  2 * i + 1
    right(i)  =  2 * i + 2
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(order=False)
class Task:
    """A unit of work to be scheduled.

    Attributes
    ----------
    task_id      : unique identifier (used as the key in the position map)
    priority     : smaller value == higher priority (min-heap key)
    arrival_time : when the task entered the system (tie-breaker / logging)
    deadline     : optional deadline, for reporting
    description  : human-readable label
    """
    task_id: int
    priority: int
    arrival_time: float = 0.0
    deadline: Optional[float] = None
    description: str = ""

    def __repr__(self) -> str:  # concise, readable logs
        return (f"Task(id={self.task_id}, prio={self.priority}, "
                f"arr={self.arrival_time}, dl={self.deadline})")


class MinHeapPriorityQueue:
    """A min-heap priority queue of ``Task`` objects (lowest priority first).

    All ordering is by ``Task.priority``; ties are broken by ``arrival_time``
    so that, among equally-urgent tasks, the one that arrived first wins
    (FIFO within a priority level).
    """

    def __init__(self) -> None:
        self._heap: List[Task] = []
        self._position: Dict[int, int] = {}   # task_id -> index in self._heap

    # ----------------------------------------------------------------- utils
    def is_empty(self) -> bool:
        """Return True iff the queue holds no tasks. Time: O(1)."""
        return len(self._heap) == 0

    def __len__(self) -> int:
        return len(self._heap)

    def _less(self, i: int, j: int) -> bool:
        """Does task at index i rank ahead of task at index j?

        Primary key: priority (smaller first). Tie-break: earlier arrival.
        """
        a, b = self._heap[i], self._heap[j]
        if a.priority != b.priority:
            return a.priority < b.priority
        return a.arrival_time < b.arrival_time

    def _swap(self, i: int, j: int) -> None:
        """Swap two heap entries and keep the position map in sync. O(1)."""
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]
        self._position[self._heap[i].task_id] = i
        self._position[self._heap[j].task_id] = j

    def _sift_up(self, i: int) -> None:
        """Move entry at ``i`` up until the heap property holds. O(log n)."""
        while i > 0:
            parent = (i - 1) // 2
            if self._less(i, parent):
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i: int) -> None:
        """Move entry at ``i`` down until the heap property holds. O(log n)."""
        n = len(self._heap)
        while True:
            left = 2 * i + 1
            right = 2 * i + 2
            smallest = i
            if left < n and self._less(left, smallest):
                smallest = left
            if right < n and self._less(right, smallest):
                smallest = right
            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest

    # ------------------------------------------------------------ operations
    def insert(self, task: Task) -> None:
        """Insert a new task, preserving the heap property.

        Append to the end (O(1) amortized), then sift it up to its correct
        level. Time complexity: O(log n).
        """
        if task.task_id in self._position:
            raise KeyError(f"Task id {task.task_id} is already in the queue.")
        self._heap.append(task)
        i = len(self._heap) - 1
        self._position[task.task_id] = i
        self._sift_up(i)

    def peek(self) -> Task:
        """Return (without removing) the highest-priority task. O(1)."""
        if self.is_empty():
            raise IndexError("peek from an empty priority queue")
        return self._heap[0]

    def extract_min(self) -> Task:
        """Remove and return the highest-priority (smallest-key) task.

        Swap the root with the last element, pop the last element, then sift
        the new root down. Time complexity: O(log n).
        """
        if self.is_empty():
            raise IndexError("extract_min from an empty priority queue")

        root = self._heap[0]
        last = self._heap.pop()                 # O(1)
        del self._position[root.task_id]

        if self._heap:                          # if anything remains, re-root
            self._heap[0] = last
            self._position[last.task_id] = 0
            self._sift_down(0)
        return root

    # Alias so the API matches the assignment's "extract_max/min" wording.
    # Because smaller priority == more urgent, the min IS the max-priority task.
    extract_max = extract_min

    def _change_key(self, task_id: int, new_priority: int) -> None:
        """Internal: set a task's priority and restore the heap. O(log n)."""
        if task_id not in self._position:
            raise KeyError(f"Task id {task_id} is not in the queue.")
        i = self._position[task_id]
        old_priority = self._heap[i].priority
        self._heap[i].priority = new_priority
        if new_priority < old_priority:
            self._sift_up(i)        # became more urgent -> may rise
        elif new_priority > old_priority:
            self._sift_down(i)      # became less urgent -> may sink
        # equal: nothing to do

    def decrease_key(self, task_id: int, new_priority: int) -> None:
        """Make a task MORE urgent (smaller priority value). O(log n).

        Named from the heap-key's perspective: we are decreasing the numeric
        key, which raises the task's scheduling urgency.
        """
        i = self._position.get(task_id)
        if i is None:
            raise KeyError(f"Task id {task_id} is not in the queue.")
        if new_priority > self._heap[i].priority:
            raise ValueError("decrease_key cannot raise the key value; "
                             "use increase_key instead.")
        self._change_key(task_id, new_priority)

    def increase_key(self, task_id: int, new_priority: int) -> None:
        """Make a task LESS urgent (larger priority value). O(log n)."""
        i = self._position.get(task_id)
        if i is None:
            raise KeyError(f"Task id {task_id} is not in the queue.")
        if new_priority < self._heap[i].priority:
            raise ValueError("increase_key cannot lower the key value; "
                             "use decrease_key instead.")
        self._change_key(task_id, new_priority)


# ---------------------------------------------------------------------------
# Scheduler simulation
# ---------------------------------------------------------------------------
def run_scheduler_simulation() -> None:
    """A tiny demonstration of using the priority queue as a task scheduler.

    Tasks arrive, the scheduler always runs the most urgent available task
    next, and we show a dynamic priority change (a task being promoted).
    """
    print("=" * 60)
    print("TASK SCHEDULER SIMULATION (min-heap priority queue)")
    print("=" * 60)

    pq = MinHeapPriorityQueue()

    initial = [
        Task(task_id=1, priority=5, arrival_time=0.0, deadline=20, description="backup"),
        Task(task_id=2, priority=2, arrival_time=1.0, deadline=8,  description="user request"),
        Task(task_id=3, priority=8, arrival_time=2.0, deadline=40, description="log rotation"),
        Task(task_id=4, priority=2, arrival_time=0.5, deadline=8,  description="payment"),
        Task(task_id=5, priority=1, arrival_time=3.0, deadline=5,  description="P1 incident"),
    ]

    print("\nInserting tasks:")
    for t in initial:
        pq.insert(t)
        print(f"  + {t}")

    # Dynamically promote task 3 (log rotation) to top urgency.
    print("\nPromoting task 3 to priority 0 (decrease_key)...")
    pq.decrease_key(task_id=3, new_priority=0)

    # Demote task 5 a little (increase_key) to show the reverse operation.
    print("Demoting task 5 to priority 4 (increase_key)...")
    pq.increase_key(task_id=5, new_priority=4)

    print("\nExecution order (always run most urgent first):")
    order = 1
    while not pq.is_empty():
        t = pq.extract_min()
        print(f"  {order:>2}. run {t}")
        order += 1

    print("\nSimulation complete.")


if __name__ == "__main__":
    # ---- Correctness self-checks -----------------------------------------
    pq = MinHeapPriorityQueue()
    assert pq.is_empty()

    import random
    ids = list(range(1, 101))
    random.shuffle(ids)
    for tid in ids:
        pq.insert(Task(task_id=tid, priority=random.randint(0, 50),
                       arrival_time=tid))

    # Extraction must come out in non-decreasing priority order.
    prev = -1
    while not pq.is_empty():
        t = pq.extract_min()
        assert t.priority >= prev, "Heap property violated on extraction!"
        prev = t.priority
    print("[OK] extraction order is non-decreasing by priority")

    # key-change checks
    pq = MinHeapPriorityQueue()
    pq.insert(Task(1, priority=10, arrival_time=0))
    pq.insert(Task(2, priority=20, arrival_time=1))
    pq.decrease_key(2, 5)                      # task 2 now most urgent
    assert pq.peek().task_id == 2
    pq.increase_key(2, 99)                     # task 2 now least urgent
    assert pq.peek().task_id == 1
    print("[OK] increase_key / decrease_key reposition correctly")

    print("\nAll priority-queue checks passed.\n")

    run_scheduler_simulation()
