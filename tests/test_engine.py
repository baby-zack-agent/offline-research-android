#!/usr/bin/env python3
"""
test_engine.py — unit tests for the offline research engine (Python reference mirror).

Runs against a tiny hand-built in-memory knowledge pack (no network, deterministic).
Covers: classification (all 5 types), retrieval relevance + anti-hallucination guard,
comparison entity resolution, citation integrity, and out-of-pack honesty.
"""
import os, sqlite3, sys, tempfile, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine-python"))
from engine import ResearchEngine, tokens  # noqa: E402

DOCS = [
    ("Treaty of Versailles",
     "The Treaty of Versailles was the peace treaty of 28 June 1919 that ended World War I. "
     "Germany accepted full responsibility under Article 231. "
     "Reparations were set at 132 billion gold marks in 1921. "
     "Historians argue its harshness contributed to the rise of Adolf Hitler."),
    ("Treaty of Westphalia",
     "The Peace of Westphalia of 1648 ended the Thirty Years' War. "
     "It established state sovereignty, the foundation of the modern nation-state system. "
     "Each ruler could determine the religion of their own state."),
    ("Great Depression",
     "The Great Depression (1929-1939) began after the October 1929 stock market crash. "
     "Causes included bank failures, a one-third contraction of the money supply, "
     "and the Smoot-Hawley Tariff of 1930. Unemployment reached 25% in 1933."),
    ("Quantum mechanics",
     "Quantum mechanics describes nature at atomic scales. "
     "Einstein's 1905 explanation of the photoelectric effect helped found quantum theory. "
     "The Heisenberg uncertainty principle limits simultaneous knowledge of position and momentum."),
]


def make_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.execute("CREATE TABLE docs(id INTEGER PRIMARY KEY, title TEXT, text TEXT, words INT, source TEXT, fetched_at TEXT)")
    cur.execute("CREATE VIRTUAL TABLE docs_fts USING fts5(title, text, tokenize='unicode61')")
    for i, (t, x) in enumerate(DOCS):
        cur.execute("INSERT INTO docs(title,text,words,source,fetched_at) VALUES(?,?,?,?,?)",
                    (t, x, len(x.split()), "test", "now"))
        cur.execute("INSERT INTO docs_fts(rowid,title,text) VALUES(?,?,?)", (i + 1, t, x))
    con.commit(); con.close()
    return path


class TestEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = make_db()
        cls.e = ResearchEngine(cls.db)

    # ---- classification ----
    def test_classify_compare(self):
        q, e = self.e.classify("Compare the Treaty of Versailles and the Treaty of Westphalia")
        self.assertEqual(q, "COMPARISON")
        self.assertIn("versailles", e[0].lower()); self.assertIn("westphalia", e[1].lower())

    def test_classify_compare_vs(self):
        q, e = self.e.classify("Great Depression vs Quantum mechanics")
        self.assertEqual(q, "COMPARISON")

    def test_classify_compare_differences(self):
        q, _ = self.e.classify("What are the differences between the Treaty of Versailles and the Treaty of Westphalia?")
        self.assertEqual(q, "COMPARISON")

    def test_classify_reasoning(self):
        q, _ = self.e.classify("Why did the Great Depression happen?")
        self.assertEqual(q, "REASONING")

    def test_classify_explanation(self):
        q, _ = self.e.classify("How does quantum mechanics describe atoms?")
        self.assertEqual(q, "EXPLANATION")

    def test_classify_factual(self):
        q, _ = self.e.classify("When was the Treaty of Versailles signed?")
        self.assertEqual(q, "FACTUAL")

    # ---- retrieval ----
    def test_retrieval_relevant(self):
        docs = self.e.retrieve("stock market crash unemployment 1929", k=2)
        self.assertTrue(docs)
        self.assertEqual(docs[0]["title"], "Great Depression")

    def test_retrieval_offtopic_guard(self):
        # gibberish must not return docs (anti-hallucination guard)
        docs = self.e.retrieve("xqz florp wobble zzzqq", k=3)
        self.assertEqual(docs, [])

    # ---- answers ----
    def test_factual_answer_cited(self):
        a = self.e.answer("When was the Treaty of Versailles signed?")
        self.assertIn("1919", a.markdown)
        self.assertIn("[1]", a.markdown)
        self.assertIn("Treaty of Versailles", a.markdown)

    def test_compare_answer_table(self):
        a = self.e.answer("Compare the Treaty of Versailles and the Treaty of Westphalia")
        self.assertEqual(a.qtype, "COMPARISON")
        self.assertIn("|", a.markdown)  # markdown table present
        self.assertIn("[1]", a.markdown); self.assertIn("[2]", a.markdown)
        self.assertIn("1648", a.markdown); self.assertIn("1919", a.markdown)

    def test_compare_missing_side_honest(self):
        a = self.e.answer("Compare the Treaty of Versailles and the Moon Cheese Treaty")
        self.assertIn("won't guess", a.markdown)

    def test_out_of_pack_honest(self):
        a = self.e.answer("xqz florp wobble zzzqq")
        self.assertIn("couldn't find", a.markdown)

    def test_reasoning_mentions_causes(self):
        a = self.e.answer("Why did the Great Depression happen?")
        self.assertEqual(a.qtype, "REASONING")
        self.assertIn("bank failures", a.markdown)

    def test_citations_resolve(self):
        a = self.e.answer("What is quantum mechanics?")
        nums = set(int(m) for m in __import__("re").findall(r"\[(\d+)\]", a.markdown))
        self.assertTrue(nums)
        self.assertTrue(all(1 <= n <= len(a.doc_titles) for n in nums))

    def test_tokens_stopwords(self):
        self.assertNotIn("the", tokens("the quick brown fox"))
        self.assertIn("quick", tokens("the quick brown fox"))

    def test_answer_speed(self):
        a = self.e.answer("Compare the Treaty of Versailles and the Treaty of Westphalia")
        self.assertLess(a.ms, 2000, f"too slow: {a.ms}ms")


if __name__ == "__main__":
    unittest.main(verbosity=2)
