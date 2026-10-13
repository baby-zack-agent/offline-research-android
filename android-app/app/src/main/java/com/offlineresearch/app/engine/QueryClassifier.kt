package com.offlineresearch.app.engine

/** Question-type classification. Mirrors ResearchEngine.classify in engine-python. */
object QueryClassifier {

    const val FACTUAL = "FACTUAL"
    const val EXPLANATION = "EXPLANATION"
    const val COMPARISON = "COMPARISON"
    const val SYNTHESIS = "SYNTHESIS"
    const val REASONING = "REASONING"

    private val COMPARE_RES = listOf(
        Regex("compar(?:e|ison of)\\s+(.+?)\\s+(?:and|with|to|vs\\.?|versus)\\s+(.+?)[\\?\\.!]*$", RegexOption.IGNORE_CASE),
        Regex("difference(?:s)?\\s+between\\s+(.+?)\\s+and\\s+(.+?)[\\?\\.!]*$", RegexOption.IGNORE_CASE),
        Regex("^(.+?)\\s+vs\\.?\\s+(.+?)[\\?\\.!]*$", RegexOption.IGNORE_CASE),
        Regex("(.+?)\\s+versus\\s+(.+?)[\\?\\.!]*$", RegexOption.IGNORE_CASE),
    )
    private val REASON_RE = Regex("\\b(why|what caused|what led to|what made|reason)\\b", RegexOption.IGNORE_CASE)
    private val EXPLAIN_RE = Regex("\\b(how does|how do|how did|how can|explain|describe the process|mechanism)\\b", RegexOption.IGNORE_CASE)
    private val SYNTH_RE = Regex("\\b(impl\\w*|synthesize|bring together|in light of|using .* and|both .* and)\\b", RegexOption.IGNORE_CASE)

    data class Classification(val qtype: String, val entities: Pair<String, String>?)

    fun classify(query: String): Classification {
        val ql = query.lowercase().trim()
        for (rx in COMPARE_RES) {
            val m = rx.find(ql) ?: continue
            val a = m.groupValues[1].trim()
            val b = m.groupValues[2].trim()
            if (a.split(" ").size <= 8 && b.split(" ").size <= 8 &&
                TextUtils.tokens(a).isNotEmpty() && TextUtils.tokens(b).isNotEmpty()
            ) return Classification(COMPARISON, a to b)
        }
        if (REASON_RE.containsMatchIn(ql)) return Classification(REASONING, null)
        if (SYNTH_RE.containsMatchIn(ql) && (" and " in ql || "," in ql)) return Classification(SYNTHESIS, null)
        if (EXPLAIN_RE.containsMatchIn(ql)) return Classification(EXPLANATION, null)
        return Classification(FACTUAL, null)
    }
}
