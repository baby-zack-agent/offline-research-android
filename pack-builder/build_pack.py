#!/usr/bin/env python3
"""
build_pack.py — Knowledge-pack builder for the Offline AI Research App (poidh bounty #31).

NETWORK IS ALLOWED HERE (build-time on a dev machine). The shipped Android app is
100% offline at runtime: it only ever reads the SQLite pack file produced below.

Modes:
  python3 build_pack.py --out pack-v1.db --limit 400     # fetch curated Wikipedia set
  python3 build_pack.py --out pack-v1.db --titles-file extra.txt
  python3 build_pack.py --out pack-test.db --seed-only  # tiny embedded corpus (tests/demo fallback)

Pipeline: curated title list -> MediaWiki API (extracts, plain text) -> clean ->
SQLite docs table + FTS5 index (unicode61) + manifest.json (sha256, sizes, sources).
"""
import argparse, hashlib, json, re, sqlite3, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone

API = "https://en.wikipedia.org/w/api.php"

# Curated topic set chosen to support EXPLANATION / COMPARISON / SYNTHESIS /
# REASONING queries (multi-hop across documents), not just factual recall.
CURATED_TITLES = [
    # --- Economics & finance ---
    "Great Depression", "2008 financial crisis", "Bretton Woods system", "Gold standard",
    "Hyperinflation in the Weimar Republic", "Quantitative easing", "Tulip mania",
    "South Sea Bubble", "Great Recession", "Inflation", "Deflation", "Stagflation",
    "Nixon shock", "European debt crisis", "Asian financial crisis", "Dot-com bubble",
    "Subprime mortgage crisis", "Bank run", "Central bank", "Federal Reserve",
    # --- Physics ---
    "Quantum mechanics", "General relativity", "Special relativity", "Thermodynamics",
    "Standard Model", "Photoelectric effect", "Double-slit experiment",
    "Michelson–Morley experiment", "Uncertainty principle", "Big Bang",
    "Black hole", "Dark matter", "Dark energy", "Electromagnetism",
    "Newton's laws of motion", "Laws of thermodynamics", "Relativity priority dispute",
    # --- History & politics ---
    "Treaty of Versailles", "Treaty of Westphalia", "Congress of Vienna",
    "Fall of the Western Roman Empire", "French Revolution", "Industrial Revolution",
    "Cuban Missile Crisis", "Cold War", "World War I", "World War II",
    "Treaty of Paris (1783)", "Treaty of Tordesillas", "Magna Carta",
    "American Revolution", "Russian Revolution", "Berlin Wall",
    # --- Computing & technology ---
    "ARPANET", "World Wide Web", "TCP/IP", "Alan Turing", "Moore's law",
    "Operating system", "Compiler", "Public-key cryptography", "Blockchain",
    "Artificial intelligence", "Machine learning", "Neural network (machine learning)",
    "Internet", "Personal computer", "Smartphone",
    # --- Biology & medicine ---
    "DNA", "Evolution", "Natural selection", "Photosynthesis", "CRISPR",
    "Germ theory of disease", "Mitochondrion", "Cell (biology)", "Vaccine",
    "Antibiotics", "Immune system", "Human genome",
    # --- Earth & space ---
    "Climate change", "Greenhouse effect", "Ozone depletion", "Plate tectonics",
    "Moon landing", "Space Race", "International Space Station", "Solar System",
    # --- Philosophy & society ---
    "Utilitarianism", "Deontology", "Social contract", "Democracy", "Capitalism",
    "Communism", "Enlightenment (philosophy)", "Scientific method",
    # --- Math & logic ---
    "Calculus", "Probability theory", "Statistics", "Game theory", "Gödel's incompleteness theorems",
    # --- Law & treaties (comparison-friendly) ---
    "Geneva Conventions", "Universal Declaration of Human Rights", "Kyoto Protocol",
    "Paris Agreement", "Treaty on the Non-Proliferation of Nuclear Weapons",
    # --- Energy ---
    "Nuclear power", "Renewable energy", "Fossil fuel", "Chernobyl disaster",
    "Fukushima nuclear accident", "Three Mile Island accident",
    # --- Additional comparison anchors ---
    "Roman Empire", "Ottoman Empire", "British Empire", "Mongol Empire",
    "Silk Road", "Age of Discovery", "Renaissance", "Reformation",
    "Printing press", "Steam engine", "Electricity", "Telegraph",
    "Penicillin", "Smallpox", "Spanish flu", "COVID-19 pandemic",
    "First Industrial Revolution", "Second Industrial Revolution",
    "Keynesian economics", "Monetarism", "Austrian school of economics",
    "Supply and demand", "Comparative advantage", "Tragedy of the commons",
    "Prisoner's dilemma", "Nash equilibrium",
    "Wave–particle duality", "Schrödinger's cat", "Quantum entanglement",
    "Nuclear fission", "Nuclear fusion", "Radioactivity",
    "Periodic table", "Chemical bond", "Acid–base reaction",
    "Gravity", "Electromagnetic spectrum", "Speed of light",
    "Time dilation", "Length contraction", "Equivalence principle",
    "Cosmic microwave background", "Hubble's law", "Stellar nucleosynthesis",
]

# Tiny embedded fallback corpus (seed-only mode): real, short, factual summaries.
SEED_CORPUS = [
    ("Treaty of Versailles",
     "The Treaty of Versailles was the peace treaty signed on 28 June 1919 that ended World War I between Germany and the Allied Powers. "
     "Its Article 231, the 'war guilt clause', forced Germany to accept full responsibility for the war. "
     "Germany lost about 13% of its European territory, all colonies, and its army was limited to 100,000 men. "
     "Reparations were set at 132 billion gold marks in 1921. Many historians argue the treaty's harshness contributed to the rise of Adolf Hitler and World War II."),
    ("Treaty of Westphalia",
     "The Peace of Westphalia (1648) ended the Thirty Years' War in the Holy Roman Empire and the Eighty Years' War between Spain and the Dutch Republic. "
     "It established the principle of state sovereignty: each ruler could determine the religion of their own state. "
     "It is widely regarded as the foundation of the modern system of sovereign nation-states in international relations."),
    ("Great Depression",
     "The Great Depression was a severe worldwide economic depression from 1929 to 1939. It began after the U.S. stock market crash of October 1929. "
     "Causes included the crash, bank failures (over 9,000 U.S. banks failed), a contraction of the money supply by roughly a third, the gold standard constraining monetary policy, "
     "and the Smoot-Hawley Tariff of 1930 which deepened the global slump. U.S. unemployment reached about 25% in 1933. Recovery came with World War II mobilization."),
    ("2008 financial crisis",
     "The 2008 financial crisis was triggered by the collapse of the U.S. subprime mortgage market. "
     "Banks had packaged risky mortgages into mortgage-backed securities rated AAA; when housing prices fell in 2007, these securities lost value. "
     "Lehman Brothers filed for bankruptcy on 15 September 2008. Governments responded with bank bailouts and the U.S. Troubled Asset Relief Program ($700 billion). "
     "Unlike 1929, central banks cut rates aggressively and expanded balance sheets via quantitative easing."),
    ("Michelson–Morley experiment",
     "The Michelson–Morley experiment (1887) attempted to detect the luminiferous aether, the medium then believed to carry light waves. "
     "It found no significant difference in the speed of light regardless of direction of Earth's motion — a null result. "
     "The null result contradicted classical aether theory and helped motivate Einstein's special relativity (1905), which discarded the aether."),
    ("Photoelectric effect",
     "The photoelectric effect is the emission of electrons from a material when light shines on it. Classical wave theory could not explain why electron energy "
     "depended on light frequency rather than intensity. Einstein's 1905 explanation — light consists of discrete quanta (photons) with energy proportional to frequency — "
     "won him the 1921 Nobel Prize and helped found quantum theory."),
    ("Bretton Woods system",
     "The Bretton Woods system (1944–1971) pegged major currencies to the U.S. dollar, which was convertible to gold at $35 per ounce. "
     "It ended with the Nixon shock of 15 August 1971, when the U.S. suspended dollar-gold convertibility, ushering in the era of floating fiat currencies."),
    ("Quantitative easing",
     "Quantitative easing (QE) is a monetary policy in which a central bank buys long-term securities to inject money into the economy when interest rates are near zero. "
     "Unlike Weimar-era money printing, QE creates bank reserves electronically to lower long-term yields; it does not directly fund government spending, "
     "which is why economists distinguish it from fiscal monetization that caused hyperinflation."),
]

BATCH = 20
PAUSE = 1.2  # seconds between API batches (polite)


def api_wikitext(titles):
    """Fetch raw wikitext via revisions (reliable; the extracts endpoint drops
    long pages). Returned dict: title -> wikitext."""
    params = {
        "action": "query", "format": "json", "formatversion": "2",
        "prop": "revisions", "rvprop": "content", "rvslots": "main",
        "redirects": "1", "titles": "|".join(titles),
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "OfflineResearchApp-packbuilder/1.0 (research; contact: none)"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                data = json.load(r)
            out = {}
            redir = {}  # "from" -> "to" for redirects in this batch
            for r in data.get("query", {}).get("redirects", []):
                redir[r["from"]] = r["to"]
            for page in data.get("query", {}).get("pages", []):
                if "missing" in page:
                    continue
                revs = page.get("revisions") or []
                if revs:
                    out[page["title"]] = revs[0].get("slots", {}).get("main", {}).get("content", "")
            out["_redirects"] = redir
            return out
        except Exception as e:
            print(f"  [retry {attempt+1}] {e}", file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    return None


def drop_file_links(s):
    """Drop [[File:...]] / [[Image:...]] / [[Category:...]] spans, handling
    nested [[...]] inside captions via depth counting."""
    res, i, n = [], 0, len(s)
    while i < n:
        if s.startswith("[[", i):
            depth, j = 1, i + 2
            while j < n and depth > 0:
                if s.startswith("[[", j):
                    depth += 1; j += 2
                elif s.startswith("]]", j):
                    depth -= 1; j += 2
                else:
                    j += 1
            span = s[i:j]
            ns = span[2:].split("|")[0]
            if re.match(r"(?i)^(file|image|category)\s*:", ns.strip()):
                i = j  # drop
            else:
                res.append(span); i = j
        else:
            res.append(s[i]); i += 1
    return "".join(res)


def strip_wikitext(w):
    """Stack-based wikitext -> plain text. Handles nested templates/tables."""
    w = re.sub(r"<!--.*?-->", "", w, flags=re.S)
    # drop nested {{...}} and {|...|} via stack
    def drop_nested(s, opener, closer):
        res, i, depth, n = [], 0, 0, len(s)
        ol, cl = len(opener), len(closer)
        while i < n:
            if s.startswith(opener, i):
                depth += 1; i += ol
            elif s.startswith(closer, i) and depth > 0:
                depth -= 1; i += cl
            elif depth == 0:
                res.append(s[i]); i += 1
            else:
                i += 1
        return "".join(res)
    w = drop_nested(w, "{{", "}}")
    w = drop_nested(w, "{|", "|}")
    w = re.sub(r"<ref[^>]*>.*?</ref>", "", w, flags=re.S | re.I)
    w = re.sub(r"<ref[^>]*/>", "", w, flags=re.I)
    w = re.sub(r"<[^>]+>", "", w)  # remaining tags (gallery, math, etc.)
    w = drop_file_links(w)
    # internal links: [[target|label]] -> label ; [[target]] -> target
    w = re.sub(r"\[\[([^|\]]*\|)?([^\]]+)\]\]",
               lambda m: m.group(2).split("|")[-1], w)
    # external links: [http://x label] -> label ; bare urls dropped
    w = re.sub(r"\[https?://[^\s\]]+\s+([^\]]+)\]", r"\1", w)
    w = re.sub(r"https?://\S+", "", w)
    w = re.sub(r"'''?", "", w)

    # headings -> keep only if they carry sentence-like content; short bare
    # headings ("Origins", "History") otherwise glue onto the next sentence.
    def head_repl(m):
        t = m.group(1).strip()
        if len(t) < 100 and not re.search(r"[.!?]$", t):
            return ""
        return t
    w = re.sub(r"^=+\s*(.*?)\s*=+\s*$", head_repl, w, flags=re.M)
    # list markers / indents at line start
    w = re.sub(r"^[*#;:]+", "", w, flags=re.M)
    # magic words
    w = re.sub(r"__[A-Z_]+__", "", w)
    return w


def api_extracts(titles):  # kept for reference; superseded by api_wikitext
    return None


def clean(text):
    import html
    text = html.unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    # drop reference-only lines
    lines = [l for l in text.split("\n") if not re.match(r"^\s*(\^|\[\d+\])", l)]
    text = "\n".join(lines).strip()
    # cut trailing meta-sections (references / external links / see also)
    cut = re.search(r"(?im)^\s*(external links|see also|references|notes|further reading|"
                    r"bibliography|works cited|sources|citations)\s*$", text)
    if cut:
        text = text[:cut.start()].strip()
    # last-resort artifact sweep
    text = text.replace("[[", "").replace("]]", "")
    text = re.sub(r"[ \t]+", " ", text)
    return text


def sentences(text):
    # simple sentence splitter (good enough for extractive ranking)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\(\"\'])", text)
    return [p.strip() for p in parts if len(p.strip()) > 25]


def build_db(docs, out_path):
    if __name__ == "__main__":
        pass
    import os
    if os.path.exists(out_path):
        os.remove(out_path)
    con = sqlite3.connect(out_path)
    cur = con.cursor()
    cur.execute("PRAGMA journal_mode=DELETE;")
    cur.execute("PRAGMA synchronous=FULL;")
    cur.execute("""CREATE TABLE docs(
        id INTEGER PRIMARY KEY, title TEXT UNIQUE, text TEXT,
        words INTEGER, source TEXT, fetched_at TEXT)""")
    cur.execute("CREATE VIRTUAL TABLE docs_fts USING fts5(title, text, tokenize='unicode61')")
    for i, d in enumerate(docs):
        cur.execute("INSERT INTO docs(title,text,words,source,fetched_at) VALUES(?,?,?,?,?)",
                    (d["title"], d["text"], d["words"], d["source"], d["fetched_at"]))
        rowid = cur.lastrowid
        cur.execute("INSERT INTO docs_fts(rowid,title,text) VALUES(?,?,?)",
                    (rowid, d["title"], d["text"]))
        if (i + 1) % 100 == 0:
            print(f"  indexed {i+1}/{len(docs)}")
    con.commit()
    # FTS5 integrity check
    n = cur.execute("SELECT count(*) FROM docs").fetchone()[0]
    nf = cur.execute("SELECT count(*) FROM docs_fts").fetchone()[0]
    assert n == nf, f"docs={n} fts={nf} mismatch"
    con.close()
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=400)
    ap.add_argument("--titles-file", default=None)
    ap.add_argument("--seed-only", action="store_true")
    args = ap.parse_args()

    docs = []
    now = datetime.now(timezone.utc).isoformat()

    if args.seed_only:
        for title, text in SEED_CORPUS:
            docs.append({"title": title, "text": clean(text),
                         "words": len(text.split()), "source": "embedded-seed",
                         "fetched_at": now})
        print(f"seed-only: {len(docs)} docs")
    else:
        titles = list(CURATED_TITLES)
        if args.titles_file:
            with open(args.titles_file) as f:
                titles += [l.strip() for l in f if l.strip()]
        # de-dupe preserving order
        seen, uniq = set(), []
        for t in titles:
            if t.lower() not in seen:
                seen.add(t.lower()); uniq.append(t)
        titles = uniq[:args.limit]
        print(f"fetching {len(titles)} titles from Wikipedia (build-time network OK)...")
        fetched = {}
        redirects = {}
        for i in range(0, len(titles), BATCH):
            batch = titles[i:i + BATCH]
            got = api_wikitext(batch)
            if got is None:
                print(f"  batch {i//BATCH+1} FAILED, skipping", file=sys.stderr)
                time.sleep(PAUSE); continue
            redirects.update(got.pop("_redirects", {}))
            fetched.update(got)
            print(f"  batch {i//BATCH+1}: {len(fetched)} pages so far")
            time.sleep(PAUSE)
        # resolve requested titles through redirects (e.g. "Treaty of Westphalia" -> "Peace of Westphalia")
        for t in titles:
            key = redirects.get(t, t)
            if key not in fetched:
                # case-insensitive fallback
                low = {k.lower(): k for k in fetched}
                key = low.get(t.lower(), low.get(key.lower()))
                if key is None:
                    continue
            text = clean(strip_wikitext(fetched[key]))
            if len(text) < 1500:
                continue
            if len(text) > 60000:  # keep pack lean; lead sections carry the facts
                text = text[:60000]
            docs.append({"title": t, "text": text, "words": len(text.split()),
                         "source": "wikipedia-wikitext", "fetched_at": now})
        print(f"kept {len(docs)} docs")

    n = build_db(docs, args.out)
    import os
    size = os.path.getsize(args.out)
    sha = hashlib.sha256(open(args.out, "rb").read()).hexdigest()
    manifest = {
        "pack_version": "v1", "built_at": now, "doc_count": n,
        "bytes": size, "sha256": sha,
        "sources": sorted(set(d["source"] for d in docs)),
        "license_note": "Wikipedia text: CC BY-SA 4.0. Pack builder attributes per-article in docs.source.",
    }
    with open(args.out + ".manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"DONE: {n} docs, {size/1e6:.1f} MB, sha256={sha[:16]}...")


if __name__ == "__main__":
    main()
