package com.offlineresearch.app.engine

import com.offlineresearch.app.engine.QueryClassifier.Classification
import com.offlineresearch.app.engine.QueryClassifier.COMPARISON
import com.offlineresearch.app.engine.QueryClassifier.EXPLANATION
import com.offlineresearch.app.engine.QueryClassifier.FACTUAL
import com.offlineresearch.app.engine.QueryClassifier.REASONING
import com.offlineresearch.app.engine.QueryClassifier.SYNTHESIS
import com.offlineresearch.app.engine.TextUtils.CAUSAL
import com.offlineresearch.app.engine.TextUtils.NUM_RE
import com.offlineresearch.app.engine.TextUtils.OUTCOME
import com.offlineresearch.app.engine.TextUtils.YEAR_RE
import com.offlineresearch.app.engine.TextUtils.splitSentences
import com.offlineresearch.app.engine.TextUtils.tokens

/**
 * Offline research engine — Kotlin port of engine-python/engine.py.
 * Same algorithm, same scoring constants, same answer templates.
 * The Python copy is the verified reference; this is the shipped implementation.
 */
class ResearchEngine(private val pack: PackDatabase) {

    fun answer(query: String): EngineAnswer {
        val t0 = System.currentTimeMillis()
        val c = QueryClassifier.classify(query)
        val ans = when (c.qtype) {
            COMPARISON -> answerCompare(query, c.entities!!)
            SYNTHESIS -> answerSynth(query)
            else -> answerSingle(query, c.qtype)
        }
        return ans.copy(elapsedMs = System.currentTimeMillis() - t0)
    }

    // ---------------- sentence scoring ----------------

    private fun scoreSentence(s: String, qtok: Set<String>, qtype: String, pos: Int): Pair<Double, Int> {
        val stok = tokens(s).toSet()
        val ov = qtok.intersect(stok).size
        var score = ov * 3.0
        score += maxOf(0.0, 2.0 - pos * 0.15)
        val sl = s.lowercase()
        if ((qtype == EXPLANATION || qtype == REASONING) && CAUSAL.any { it in sl }) score += 4.0
        if (YEAR_RE.containsMatchIn(s)) score += 1.5
        if (NUM_RE.containsMatchIn(s)) score += 1.0
        if (s.length > 600) score -= 3.0
        return score to ov
    }

    private fun bestSentences(doc: DocRow, qtok: Set<String>, qtype: String, n: Int): List<String> {
        val scored = splitSentences(doc.text).mapIndexed { i, s ->
            val (score, ov) = scoreSentence(s, qtok, qtype, i)
            Triple(score, i, s) to ov
        }.filter { (t, ov) -> ov > 0 || t.first >= 3.0 }
            .map { it.first }
            .sortedWith(compareByDescending<Triple<Double, Int, String>> { it.first }.thenBy { it.second })
        return dedupe(scored.map { it.third }, n)
    }

    private fun dedupe(cands: List<String>, n: Int): List<String> {
        val picked = mutableListOf<String>()
        for (s in cands) {
            val st = tokens(s).toSet()
            if (picked.all { p -> st.intersect(tokens(p).toSet()).size < 4 }) picked += s
            if (picked.size == n) break
        }
        return picked
    }

    /** Score every sentence of a doc once; aspect filters reuse the list. */
    private fun scoredSents(doc: DocRow, qtok: Set<String>): List<Triple<Double, Int, String>> =
        splitSentences(doc.text).mapIndexed { i, s ->
            val (score, _) = scoreSentence(s, qtok, EXPLANATION, i)
            Triple(score, i, s)
        }

    private fun pick(
        scored: List<Triple<Double, Int, String>>,
        markers: List<String>?, n: Int, wantYear: Boolean = false,
        exclude: MutableSet<String>? = null
    ): List<String> {
        val cands = scored.filter { (_, _, s) ->
            val sl = s.lowercase()
            (markers == null || markers.any { it in sl }) &&
            (!wantYear || YEAR_RE.containsMatchIn(s)) &&
            (exclude == null || s !in exclude)
        }.sortedWith(compareByDescending<Triple<Double, Int, String>> { it.first }.thenBy { it.second })
        val out = dedupe(cands.map { it.third }, n)
        exclude?.addAll(out)
        return out
    }

    private fun definition(doc: DocRow): String =
        splitSentences(doc.text).firstOrNull() ?: ""

    private fun citeBlock(titles: List<String>): String =
        titles.mapIndexed { i, t -> "[${i + 1}] $t" }.joinToString("\n")

    // ---------------- answer builders ----------------

    private fun answerSingle(query: String, qtype: String): EngineAnswer {
        val docs = pack.retrieve(query, 4)
        if (docs.isEmpty()) return EngineAnswer(qtype,
            "I couldn't find relevant material in the offline knowledge pack for this question. " +
            "The pack covers the curated topic set; this query falls outside it.",
            emptyList(), 0)
        val qtok = tokens(query).toSet()
        val n = if (qtype == FACTUAL) 5 else 6
        val titles = mutableListOf<String>()
        val body = mutableListOf<String>()
        for (d in docs) {
            titles += d.row.title
            val idx = titles.size
            for (s in bestSentences(d.row, qtok, qtype, 3)) body += "$s [$idx]"
            if (body.size >= n) break
        }
        val head = mapOf(FACTUAL to "Answer", EXPLANATION to "Explanation",
            REASONING to "Analysis", SYNTHESIS to "Synthesis")[qtype] ?: "Answer"
        val md = "## $head\n\n" + body.take(n).joinToString("\n\n") +
            "\n\n**Sources**\n" + citeBlock(titles)
        return EngineAnswer(qtype, md, titles, 0)
    }

    private fun docForEntity(entity: String): PackDatabase.ScoredDoc? {
        val docs = pack.retrieve(entity, 4)
        if (docs.isEmpty()) return null
        val et = tokens(entity).toSet()
        return docs.firstOrNull { et.intersect(tokens(it.row.title).toSet()).isNotEmpty() } ?: docs[0]
    }

    private fun answerCompare(query: String, ents: Pair<String, String>): EngineAnswer {
        val da = docForEntity(ents.first)
        val db = docForEntity(ents.second)
        val have = listOfNotNull(da, db).map { it.row.title }
        if (da == null || db == null) {
            val missing = if (da == null) ents.first else ents.second
            return EngineAnswer(COMPARISON,
                "I found material on one side of this comparison but nothing reliable on **$missing** " +
                "in the offline pack, so I won't guess at the other half.",
                have, 0)
        }
        val qtok = tokens(query).toSet()
        val titles = listOf(da.row.title, db.row.title)
        val scoredA = scoredSents(da.row, qtok)
        val scoredB = scoredSents(db.row, qtok)
        val usedA = mutableSetOf(definition(da.row))  // cross-aspect dedupe
        val usedB = mutableSetOf(definition(db.row))
        val rows = listOf(
            "| **Overview** | ${definition(da.row)} [1] | ${definition(db.row)} [2] |",
            "| **Causes / origins** | ${pick(scoredA, CAUSAL, 2, exclude = usedA).joinToString("; ").ifEmpty { "—" }} [1] | " +
                "${pick(scoredB, CAUSAL, 2, exclude = usedB).joinToString("; ").ifEmpty { "—" }} [2] |",
            "| **Key dates & figures** | ${pick(scoredA, null, 2, wantYear = true, exclude = usedA).joinToString("; ").ifEmpty { "—" }} [1] | " +
                "${pick(scoredB, null, 2, wantYear = true, exclude = usedB).joinToString("; ").ifEmpty { "—" }} [2] |",
            "| **Outcomes / legacy** | ${pick(scoredA, OUTCOME, 2, exclude = usedA).joinToString("; ").ifEmpty { "—" }} [1] | " +
                "${pick(scoredB, OUTCOME, 2, exclude = usedB).joinToString("; ").ifEmpty { "—" }} [2] |",
        )
        var md = "## Comparison: ${da.row.title} vs ${db.row.title}\n\n" +
            "| Aspect | ${da.row.title} | ${db.row.title} |\n|---|---|---|\n" + rows.joinToString("\n")
        val sa = pick(scoredA, CAUSAL, 1).firstOrNull()
        val sb = pick(scoredB, CAUSAL, 1).firstOrNull()
        if (sa != null || sb != null) {
            md += "\n\n**In short:** "
            if (sa != null) md += "$sa [1] "
            if (sb != null) md += "By contrast, $sb [2]"
        }
        md += "\n\n**Sources**\n" + citeBlock(titles)
        return EngineAnswer(COMPARISON, md, titles, 0)
    }

    private fun answerSynth(query: String): EngineAnswer {
        val docs = pack.retrieve(query, 4)
        if (docs.size < 2) return answerSingle(query, FACTUAL)
        val qtok = tokens(query).toSet()
        val titles = docs.map { it.row.title }
        var md = "## Synthesis\n\n"
        for ((i, d) in docs.withIndex()) {
            val sents = bestSentences(d.row, qtok, SYNTHESIS, 2)
            if (sents.isNotEmpty())
                md += "**Evidence — ${d.row.title}:** " +
                    sents.joinToString(" ") { "$it [${i + 1}]" } + "\n\n"
        }
        val pool = docs.flatMapIndexed { i, d ->
            bestSentences(d.row, qtok, SYNTHESIS, 3).map { s ->
                Triple(scoreSentence(s, qtok, SYNTHESIS, 0).first, i, s)
            }
        }.sortedWith(compareByDescending<Triple<Double, Int, String>> { it.first })
        val synth = mutableListOf<Pair<String, Int>>()
        for ((_, i, s) in pool.take(6)) {
            val st = tokens(s).toSet()
            if (synth.all { (p, _) -> st.intersect(tokens(p).toSet()).size < 4 }) synth += s to i
            if (synth.size == 3) break
        }
        if (synth.isNotEmpty())
            md += "**Putting it together:** " + synth.joinToString(" ") { (s, i) -> "$s [${i + 1}]" }
        md += "\n\n**Sources**\n" + citeBlock(titles)
        return EngineAnswer(SYNTHESIS, md, titles, 0)
    }
}
