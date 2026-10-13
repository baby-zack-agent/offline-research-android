#!/usr/bin/env python3
"""Steady-state benchmark: warmup, then 3 timed passes per query (median reported)."""
import os, statistics, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine-python"))
from engine import ResearchEngine  # noqa: E402
from run_demo import QUERIES  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
e = ResearchEngine(os.path.join(BASE, "pack-builder", "pack-v1.db"))
e.answer("warmup query about science and history")  # warm FTS5 + page cache

print(f"{'query':58s} {'median ms':>9s} {'type'}")
tot = 0
for label, q in QUERIES:
    samples = []
    for _ in range(3):
        a = e.answer(q)
        samples.append(a.ms)
    med = statistics.median(samples)
    tot += med
    print(f"{label[:58]:58s} {med:9.0f} {a.qtype}")
print(f"\nTOTAL {tot:.0f} ms over {len(QUERIES)} queries (avg {tot/len(QUERIES):.0f} ms/query, steady state)")
