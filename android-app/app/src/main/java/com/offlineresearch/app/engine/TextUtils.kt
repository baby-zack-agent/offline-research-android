package com.offlineresearch.app.engine

/** Tokenization / sentence utilities. Identical behavior to engine-python. */
object TextUtils {

    private val STOP: Set<String> = setOf(
        "a","an","the","and","or","but","of","to","in","on","for","with","as","at","by","from",
        "is","are","was","were","be","been","being","it","its","this","that","these","those",
        "i","you","he","she","we","they","them","his","her","our","their","my","your",
        "what","which","who","whom","whose","when","where","why","how","does","do","did",
        "can","could","should","would","will","there","here","than","then","so","such",
        "no","not","only","also","very","more","most","much","many","any","some","all",
        "into","out","over","under","between","through","during","about","against","per",
        "each","other","own","same"
    )

    private val TOKEN_RE = Regex("[a-z0-9']+")
    private val SENT_SPLIT = Regex("(?<=[.!?])\\s+(?=[A-Z0-9\\(\\\"'])")

    fun tokens(s: String): List<String> =
        TOKEN_RE.findAll(s.lowercase()).map { it.value }
            .filter { it !in STOP && it.length > 1 }.toList()

    fun splitSentences(text: String): List<String> =
        text.split(SENT_SPLIT).map { it.trim() }
            .filter { it.length > 30 }
            .filter { s ->
                // fragment guard: a real sentence starts with uppercase / digit / quote
                val first = s.trimStart('"', '\'', '(').firstOrNull()
                first == null || first.isUpperCase() || first.isDigit()
            }

    val CAUSAL = listOf("caus","due to","led to","resulted in","triggered","because",
        "gave rise","brought about","stemmed from","attributed to")
    val OUTCOME = listOf("led to","resulted in","outcome","aftermath","consequence",
        "ended","legacy","ultimately","in response","replaced by")

    val YEAR_RE = Regex("\\b(1[0-9]{3}|20[0-2][0-9])\\b")
    val NUM_RE = Regex("\\b\\d[\\d,]*(?:\\.\\d+)?\\s*(?:%|percent|million|billion|trillion|thousand)?\\b",
        RegexOption.IGNORE_CASE)
}
