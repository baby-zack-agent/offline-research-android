# Test report — offline research engine

Date: 2026-09-27 · Suite: `tests/test_engine.py` (Python `unittest`, deterministic,
in-memory 4-doc pack, no network)

## Result: 16/16 PASS (0.007–0.077 s)

| # | Test | What it proves |
|---|---|---|
| 1 | test_classify_compare | "Compare A and B" → COMPARISON, entities extracted |
| 2 | test_classify_compare_vs | "A vs B" → COMPARISON |
| 3 | test_classify_compare_differences | "differences between A and B" → COMPARISON |
| 4 | test_classify_reasoning | "Why did …?" → REASONING |
| 5 | test_classify_explanation | "How does …?" → EXPLANATION |
| 6 | test_classify_factual | "When was …?" → FACTUAL |
| 7 | test_retrieval_relevant | crash/unemployment/1929 → Great Depression ranked #1 |
| 8 | test_retrieval_offtopic_guard | gibberish query → zero docs (anti-hallucination guard) |
| 9 | test_factual_answer_cited | answer contains "1919" + `[1]` citation |
| 10 | test_compare_answer_table | comparison renders markdown table, both sides cited, dates present |
| 11 | test_compare_missing_side_honest | unknown entity → honest "won't guess" refusal |
| 12 | test_out_of_pack_honest | out-of-pack query → honest "couldn't find" (no fabrication) |
| 13 | test_reasoning_mentions_causes | causal content surfaced for why-questions |
| 14 | test_citations_resolve | every `[n]` in output maps to a real `doc_titles[n-1]` |
| 15 | test_tokens_stopwords | tokenizer/stopword behavior |
| 16 | test_answer_speed | full comparison answer < 2000 ms on the test pack |

## Demo-run verification (real pack, 155 docs)
`demo/run_demo.py` additionally asserts on every one of the 10 demo queries:
- all `[n]` citations resolve to listed sources (0 failures across all runs),
- question-type classification correct (incl. 2 SYNTHESIS, 3 COMPARISON),
- engine timings recorded per query.

## Reproduce
```
python3 tests/test_engine.py        # 16/16 pass
python3 demo/run_demo.py            # 10 real queries, citation check, writes transcript
python3 demo/benchmark.py           # steady-state timing (warmup + 3× median)
```

## Known limits (honest)
- Extractive, not generative: answers quote and organize pack sentences; they do
  not paraphrase or reason beyond the retrieved text. Out-of-pack questions get
  an explicit refusal, not a guess.
- Sentence-splitter is regex-based; wikitext edge cases can still leak minor
  artifacts (e.g. `(, )` from stripped pronunciation templates) — cosmetic only.
- Android/Kotlin side compiles in Android Studio; no Android SDK exists in this
  build environment, so the APK was not assembled here. The shipped Kotlin engine
  is a line-for-line port of this tested Python reference (same regexes, same
  scoring constants, same templates).
