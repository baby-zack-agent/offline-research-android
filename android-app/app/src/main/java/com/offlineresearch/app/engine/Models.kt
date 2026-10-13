package com.offlineresearch.app.engine

/** Shared data models. Mirrors engine-python/engine.py Answer/Citation. */

data class DocRow(val id: Long, val title: String, val text: String)

data class EngineAnswer(
    val qtype: String,          // FACTUAL | EXPLANATION | COMPARISON | SYNTHESIS | REASONING
    val markdown: String,       // answer body with [n] citations
    val docTitles: List<String>,// citation index -> title
    val elapsedMs: Long
)
