#!/usr/bin/env python3
"""
engine.py — Offline research engine (Python reference mirror of the Android app's
Kotlin engine: engine-python <-> android-app/.../engine/*.kt implement the SAME
algorithm; this file is the verified, runnable copy).

Architecture (100% offline at runtime, zero network, zero inference weights):
  1. classify()    — question type: FACTUAL / EXPLANATION / COMPARISON / SYNTHESIS / REASONING
  2. retrieve()    — SQLite FTS5 (unicode61) + BM25 ranking, k docs
  3. extract()     — sentence-level extractive ranking w/ type-specific signals
  4. compose()     — template answers with [n] citations -> cited sources

No generative model: answers are composed from retrieved sentences. This is
deliberate — extractive RAG gives grounded, cited answers at usable speed with
no GPU, no weights, and a tiny RAM/storage footprint, satisfying every bounty
constraint (12GB RAM, 50GB assets, offline, no Play Services).
"""
import re, sqlite3, time
from dataclasses import dataclass, field

STOP = set("""a an the and or but of to in on for with as at by from is are was were be been
being it its this that these those i you he she we they them his her our their my your
what which who whom whose when where why how does do did can could should would will
there here than then so such no not only also very more most much many any some all
into out over under between through during about against per each other own same""".split())

CAUSAL = ["caus", "due to", "led to", "resulted in", "triggered", "because", "gave rise",
          "brought about", "stemmed from", "attributed to"]
OUTCOME = ["led to", "resulted in", "outcome", "aftermath", "consequence", "ended",
           "legacy", "ultimately", "in response", "replaced by"]
YEAR_RE = re.compile(r"\b(1[0-9]{3}|20[0-2][0-9])\b")
NUM_RE = re.compile(r"\b\d[\d,]*(?:\.\d+)?\s*(?:%|percent|million|billion|trillion|thousand)?\b", re.I)

QTYPE_FACTUAL, QTYPE_EXPLAIN, QTYPE_COMPARE, QTYPE_SYNTH, QTYPE_REASON = \
    "FACTUAL", "EXPLANATION", "COMPARISON", "SYNTHESIS", "REASONING"


@dataclass
class Citation:
    n: int
    title: str


@dataclass
class Answer:
    qtype: str
    markdown: str
    citations: list = field(default_factory=list)
    doc_titles: list = field(default_factory=list)
    ms: int = 0


def tokens(s):
    return [t for t in re.findall(r"[a-z0-9']+", s.lower()) if t not in STOP and len(t) > 1]


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\(\"'])", text)
    out = []
    for p in parts:
        p = p.strip()
        if len(p) <= 30:
            continue
        # fragment guard: a real sentence starts with uppercase / digit / quote
        first = p.lstrip("\"'(")[:1]
        if first and not (first.isupper() or first.isdigit()):
            continue
        out.append(p)
    return out


COMPARE_RES = [
    re.compile(r"compar(?:e|ison of)\s+(.+?)\s+(?:and|with|to|vs\.?|versus)\s+(.+?)[\?\.\!]*$", re.I),
    re.compile(r"difference(?:s)?\s+between\s+(.+?)\s+and\s+(.+?)[\?\.\!]*$", re.I),
    re.compile(r"^(.+?)\s+vs\.?\s+(.+?)[\?\.\!]*$", re.I),
    re.compile(r"(.+?)\s+versus\s+(.+?)[\?\.\!]*$", re.I),
]


class ResearchEngine:
    def __init__(self, db_path):
        self.db_path = db_path
        self.con = sqlite3.connect(db_path)
        self.con.row_factory = sqlite3.Row
        self.n_docs = self.con.execute("SELECT count(*) FROM docs").fetchone()[0]

    # ---------------- 1. classify ----------------
    def classify(self, q):
        ql = q.lower().strip()
        for rx in COMPARE_RES:
            m = rx.search(ql)
            if m:
                a, b = m.group(1).strip(), m.group(2).strip()
                # reject degenerate splits ("what is x versus ...")
                if len(a.split()) <= 8 and len(b.split()) <= 8 and len(tokens(a)) and len(tokens(b)):
                    return QTYPE_COMPARE, (a, b)
        if re.search(r"\b(why|what caused|what led to|what made|reason)\b", ql):
            return QTYPE_REASON, None
        if re.search(r"\b(implicat|impl\w*|synthesize|bring together|in light of|using .* and|both .* and)\b", ql) \
                and (" and " in ql or "," in ql):
            return QTYPE_SYNTH, None
        if re.search(r"\b(how does|how do|how did|how can|explain|describe the process|mechanism)\b", ql):
            return QTYPE_EXPLAIN, None
        return QTYPE_FACTUAL, None

    # ---------------- 2. retrieve ----------------
    def _fts_query(self, q):
        toks = tokens(q)
        if not toks:
            return None
        # OR of terms; FTS5 handles ranking via bm25
        return " OR ".join(f'"{t}"' if re.search(r"\W", t) else t for t in toks[:24])

    def retrieve(self, q, k=5):
        fq = self._fts_query(q)
        if not fq:
            return []
        rows = self.con.execute(
            """SELECT rowid AS id, title, text, bm25(docs_fts) AS r
               FROM docs_fts WHERE docs_fts MATCH ? ORDER BY r LIMIT ?""",
            (fq, k * 3)).fetchall()
        out = []
        qtok = set(tokens(q))
        for r in rows:
            dtok = set(tokens(r["title"] + " " + r["text"][:2000]))
            overlap = len(qtok & dtok)
            out.append({"id": r["id"], "title": r["title"], "text": r["text"],
                        "bm25": r["r"], "overlap": overlap})
        out.sort(key=lambda d: (d["overlap"], -d["bm25"]), reverse=True)
        # drop docs with no lexical connection to the query (anti-hallucination guard)
        out = [d for d in out if d["overlap"] >= 2][:k]
        return out

    def _doc_for_entity(self, entity):
        docs = self.retrieve(entity, k=4)
        if not docs:
            return None
        et = set(tokens(entity))
        # prefer title match
        for d in docs:
            if et & set(tokens(d["title"])):
                return d
        return docs[0]

    # ---------------- 3. extract ----------------
    def _score_sent(self, s, qtok, qtype, pos):
        stok = set(tokens(s))
        ov = len(qtok & stok)
        score = ov * 3.0
        score += max(0, 2.0 - pos * 0.15)          # earlier sentences slightly favored
        sl = s.lower()
        if qtype in (QTYPE_EXPLAIN, QTYPE_REASON) and any(c in sl for c in CAUSAL):
            score += 4.0
        if YEAR_RE.search(s):
            score += 1.5
        if NUM_RE.search(s):
            score += 1.0
        if len(s) > 600:
            score -= 3.0
        return score, ov

    def _best_sentences(self, doc, qtok, qtype, n=4, must_overlap=True):
        sents = split_sentences(doc["text"])
        scored = []
        for i, s in enumerate(sents):
            score, ov = self._score_sent(s, qtok, qtype, i)
            if must_overlap and ov == 0 and score < 3:
                continue
            scored.append((score, i, s))
        scored.sort(key=lambda x: (-x[0], x[1]))
        # de-dupe near-identical
        picked = []
        for _, _, s in scored:
            if all(len(set(tokens(s)) & set(tokens(p))) < 4 for p in picked):
                picked.append(s)
            if len(picked) == n:
                break
        return picked

    def _definition(self, doc):
        sents = split_sentences(doc["text"])
        return sents[0] if sents else ""

    # ---------------- 4. compose ----------------
    def answer(self, query):
        t0 = time.time()
        qtype, ents = self.classify(query)
        if qtype == QTYPE_COMPARE:
            ans = self._answer_compare(query, ents)
        elif qtype == QTYPE_SYNTH:
            ans = self._answer_synth(query)
        else:
            ans = self._answer_single(query, qtype)
        ans.ms = int((time.time() - t0) * 1000)
        return ans

    def _cite_block(self, titles):
        return "\n".join(f"[{i+1}] {t}" for i, t in enumerate(titles))

    def _answer_single(self, query, qtype):
        docs = self.retrieve(query, k=4)
        if not docs:
            return Answer(qtype, "I couldn't find relevant material in the offline knowledge pack for this question. "
                                 "The pack covers the curated topic set; this query falls outside it.",
                          [], [], 0)
        qtok = set(tokens(query))
        n = 5 if qtype == QTYPE_FACTUAL else 6
        body, titles = [], []
        for d in docs:
            titles.append(d["title"])
            idx = len(titles)
            for s in self._best_sentences(d, qtok, qtype, n=3):
                body.append(f"{s} [{idx}]")
            if len(body) >= n:
                break
        head = {"FACTUAL": "Answer", "EXPLANATION": "Explanation",
                "REASONING": "Analysis"}[qtype]
        md = f"## {head}\n\n" + "\n\n".join(body[:n])
        md += "\n\n**Sources**\n" + self._cite_block(titles)
        return Answer(qtype, md, [], titles, 0)

    def _answer_compare(self, query, ents):
        a_ent, b_ent = ents
        da = self._doc_for_entity(a_ent)
        db = self._doc_for_entity(b_ent)
        if not da or not db:
            missing = a_ent if not da else b_ent
            return Answer(QTYPE_COMPARE,
                          f"I found material on one side of this comparison but nothing reliable on **{missing}** "
                          f"in the offline pack, so I won't guess at the other half.",
                          [], [d["title"] for d in (da, db) if d], 0)
        qtok = set(tokens(query))
        titles = [da["title"], db["title"]]
        scored_a = self._scored_sents(da, qtok)
        scored_b = self._scored_sents(db, qtok)
        used_a, used_b = {self._definition(da)}, {self._definition(db)}  # cross-aspect dedupe
        rows = [
            f"| **Overview** | {self._definition(da)} [1] | {self._definition(db)} [2] |",
            f"| **Causes / origins** | {'; '.join(self._pick(scored_a, CAUSAL, 2, exclude=used_a)) or '—'} [1] | "
            f"{'; '.join(self._pick(scored_b, CAUSAL, 2, exclude=used_b)) or '—'} [2] |",
            f"| **Key dates & figures** | {'; '.join(self._pick(scored_a, None, 2, want_year=True, exclude=used_a)) or '—'} [1] | "
            f"{'; '.join(self._pick(scored_b, None, 2, want_year=True, exclude=used_b)) or '—'} [2] |",
            f"| **Outcomes / legacy** | {'; '.join(self._pick(scored_a, OUTCOME, 2, exclude=used_a)) or '—'} [1] | "
            f"{'; '.join(self._pick(scored_b, OUTCOME, 2, exclude=used_b)) or '—'} [2] |",
        ]
        md = (f"## Comparison: {da['title']} vs {db['title']}\n\n"
              f"| Aspect | {da['title']} | {db['title']} |\n|---|---|---|\n" + "\n".join(rows))
        # contrast paragraph: highest-contrast causal sentences from each side
        # (fresh picks — may reuse a sentence already in the table for emphasis)
        sa = self._pick(scored_a, CAUSAL, 1)
        sb = self._pick(scored_b, CAUSAL, 1)
        if sa or sb:
            md += "\n\n**In short:** "
            if sa:
                md += sa[0] + " [1] "
            if sb:
                md += "By contrast, " + sb[0] + " [2]"
        md += "\n\n**Sources**\n" + self._cite_block(titles)
        return Answer(QTYPE_COMPARE, md, [], titles, 0)

    def _scored_sents(self, doc, qtok):
        """Score every sentence once; aspect filters reuse this list."""
        sents = split_sentences(doc["text"])
        return [(self._score_sent(s, qtok, QTYPE_EXPLAIN, i)[0], i, s)
                for i, s in enumerate(sents)]

    def _pick(self, scored, markers, n, want_year=False, exclude=None):
        cands = []
        for score, i, s in scored:
            sl = s.lower()
            if markers and not any(m in sl for m in markers):
                continue
            if want_year and not YEAR_RE.search(s):
                continue
            if exclude is not None and s in exclude:
                continue
            cands.append((score, i, s))
        cands.sort(key=lambda x: (-x[0], x[1]))
        out = []
        for _, _, s in cands:
            if all(len(set(tokens(s)) & set(tokens(p))) < 4 for p in out):
                out.append(s)
            if len(out) == n:
                break
        if exclude is not None:
            exclude.update(out)
        return out

    def _answer_synth(self, query):
        docs = self.retrieve(query, k=4)
        if len(docs) < 2:
            return self._answer_single(query, QTYPE_FACTUAL)
        qtok = set(tokens(query))
        titles = [d["title"] for d in docs]
        md = "## Synthesis\n\n"
        for i, d in enumerate(docs):
            sents = self._best_sentences(d, qtok, QTYPE_SYNTH, n=2)
            if sents:
                md += f"**Evidence — {d['title']}:** " + " ".join(f"{s} [{i+1}]" for s in sents) + "\n\n"
        # synthesis paragraph: top cross-doc sentences stitched with attribution
        pool = []
        for i, d in enumerate(docs):
            for s in self._best_sentences(d, qtok, QTYPE_SYNTH, n=3):
                sc, _ = self._score_sent(s, qtok, QTYPE_SYNTH, 0)
                pool.append((sc, i, s))
        pool.sort(reverse=True)
        synth = []
        for _, i, s in pool[:3]:
            if all(len(set(tokens(s)) & set(tokens(p))) < 4 for p, _ in synth):
                synth.append((s, i))
        if synth:
            md += "**Putting it together:** " + " ".join(f"{s} [{i+1}]" for s, i in synth)
        md += "\n\n**Sources**\n" + self._cite_block(titles)
        return Answer(QTYPE_SYNTH, md, [], titles, 0)
