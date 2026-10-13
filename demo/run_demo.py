#!/usr/bin/env python3
"""
run_demo.py — runs the hard demo query set against the REAL pack (pack-v1.db),
verifies citation integrity + timing, and writes demo-transcripts/DEMO_TRANSCRIPT.md.

Every output below is produced by an actual engine run — nothing hand-written.
"""
import os, re, sys, time
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine-python"))
from engine import ResearchEngine  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(BASE, "pack-builder", "pack-v1.db")
OUT = os.path.join(BASE, "demo-transcripts", "DEMO_TRANSCRIPT.md")

QUERIES = [
    ("FACTUAL (baseline)", "What is the photoelectric effect and who explained it?"),
    ("EXPLANATION", "Explain how quantitative easing works and how it differs from the money printing that caused hyperinflation in the Weimar Republic."),
    ("COMPARISON (hard: 1B models conflate these)", "Compare the causes of the Great Depression and the 2008 financial crisis."),
    ("COMPARISON (hard: 271 years apart, often confused)", "What were the key differences between the Treaty of Versailles and the Treaty of Westphalia?"),
    ("SYNTHESIS (multi-hop: two experiments -> one conclusion)", "Using the Michelson-Morley experiment and the photoelectric effect, explain how both challenged classical physics."),
    ("REASONING", "Why did the Bretton Woods system collapse?"),
    ("COMPARISON", "Compare nuclear fission and nuclear fusion as energy sources."),
    ("EXPLANATION", "Explain how natural selection produces new species over time."),
    ("SYNTHESIS (cross-century pattern)", "What do the South Sea Bubble and the dot-com bubble imply about the recurring causes of financial bubbles?"),
    ("FACTUAL (baseline)", "When did the Berlin Wall fall and what did it symbolize?"),
]


def check_citations(a):
    nums = set(int(m) for m in re.findall(r"\[(\d+)\]", a.markdown))
    bad = [n for n in nums if not (1 <= n <= len(a.doc_titles))]
    return nums, bad


def main():
    e = ResearchEngine(PACK)
    print(f"pack docs: {e.n_docs}")
    lines = [
        "# Demo transcript — Offline AI Research App (poidh bounty #31)",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Knowledge pack: pack-v1.db — {e.n_docs} documents, "
        f"{os.path.getsize(PACK)/1e6:.1f} MB, FTS5-indexed",
        "Engine: extractive RAG (FTS5 BM25 retrieval + sentence ranking + cited templates).",
        "Runtime: 100% offline, zero network calls, zero inference weights.",
        "",
    ]
    total_ms, failures = 0, []
    for i, (label, q) in enumerate(QUERIES, 1):
        t0 = time.time()
        a = e.answer(q)
        wall = int((time.time() - t0) * 1000)
        total_ms += a.ms
        nums, bad = check_citations(a)
        status = "OK" if not bad and a.doc_titles else "CHECK"
        if bad:
            failures.append((q, bad))
        print(f"[{i:02d}] {label:45s} type={a.qtype:11s} docs={len(a.doc_titles)} "
              f"cites={sorted(nums)} ms={a.ms} wall={wall}ms {status}")
        lines += [f"## Q{i} — {label}", "", f"**Query:** {q}", "",
                  f"**Type detected:** {a.qtype} · **engine time:** {a.ms} ms · "
                  f"**sources used:** {len(a.doc_titles)}", "", a.markdown, "",
                  "---", ""]
    lines += [f"**Total engine time for 10 queries: {total_ms} ms "
              f"(avg {total_ms/len(QUERIES):.0f} ms/query).**", ""]
    if failures:
        lines += ["**CITATION FAILURES:** " + str(failures), ""]
        print("FAILURES:", failures)
    else:
        print("All citations resolve. No failures.")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write("\n".join(lines))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
