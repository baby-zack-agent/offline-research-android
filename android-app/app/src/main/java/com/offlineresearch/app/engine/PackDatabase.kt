package com.offlineresearch.app.engine

import android.content.Context
import android.database.sqlite.SQLiteDatabase
import java.io.File

/**
 * Read-only access to the knowledge-pack SQLite database.
 *
 * Uses raw android.database.sqlite queries against the FTS5 virtual table
 * (docs_fts) produced by pack-builder/build_pack.py. Room is deliberately NOT
 * used: raw SQL keeps the dependency surface minimal and FTS5 rank/bm25
 * behavior identical to the verified Python reference.
 *
 * No network I/O anywhere in this class — the pack is a local file.
 */
class PackDatabase private constructor(private val db: SQLiteDatabase) {

    data class ScoredDoc(val row: DocRow, val rank: Double, val overlap: Int)

    /** FTS5 BM25 retrieval with lexical-overlap guard (anti-hallucination). */
    fun retrieve(query: String, k: Int): List<ScoredDoc> {
        val toks = TextUtils.tokens(query).take(24)
        if (toks.isEmpty()) return emptyList()
        val match = toks.joinToString(" OR ")
        val cur = db.rawQuery(
            "SELECT rowid AS id, title, text, bm25(docs_fts) AS r " +
            "FROM docs_fts WHERE docs_fts MATCH ? ORDER BY r LIMIT ?",
            arrayOf(match, (k * 3).toString())
        )
        val qtok = TextUtils.tokens(query).toSet()
        val out = mutableListOf<ScoredDoc>()
        cur.use {
            val ciId = it.getColumnIndexOrThrow("id")
            val ciTitle = it.getColumnIndexOrThrow("title")
            val ciText = it.getColumnIndexOrThrow("text")
            val ciR = it.getColumnIndexOrThrow("r")
            while (it.moveToNext()) {
                val title = it.getString(ciTitle)
                val text = it.getString(ciText)
                val head = (title + " " + text.take(2000))
                val overlap = TextUtils.tokens(head).toSet().intersect(qtok).size
                out += ScoredDoc(
                    DocRow(it.getLong(ciId), title, text),
                    it.getDouble(ciR), overlap
                )
            }
        }
        return out.filter { it.overlap >= 2 }
            .sortedWith(compareByDescending<ScoredDoc> { it.overlap }.thenBy { it.rank })
            .take(k)
    }

    fun docCount(): Long {
        db.rawQuery("SELECT count(*) FROM docs", null).use {
            it.moveToFirst(); return it.getLong(0)
        }
    }

    fun close() = db.close()

    companion object {
        fun open(packFile: File): PackDatabase {
            val db = SQLiteDatabase.openDatabase(
                packFile.absolutePath, null,
                SQLiteDatabase.OPEN_READONLY or SQLiteDatabase.NO_LOCALIZED_COLLATORS
            )
            return PackDatabase(db)
        }
    }
}

/**
 * Installs/verifies the knowledge pack from the APK assets into internal storage.
 * Runs once; thereafter the engine reads the local file. No downloads, no network.
 */
object PackManager {
    const val PACK_ASSET = "pack-v1.db"
    const val PACK_SHA256_ASSET = "pack-v1.db.sha256"

    fun installedPackFile(context: Context): File =
        File(context.filesDir, "packs/$PACK_ASSET")

    /** Copies the asset pack on first launch; verifies SHA-256. Returns the pack file. */
    fun ensureInstalled(context: Context): File {
        val dest = installedPackFile(context)
        val want = context.assets.open(PACK_SHA256_ASSET).bufferedReader().readText().trim()
        if (dest.exists() && sha256(dest) == want) return dest
        dest.parentFile?.mkdirs()
        context.assets.open(PACK_ASSET).use { inp ->
            dest.outputStream().use { out -> inp.copyTo(out) }
        }
        check(sha256(dest) == want) { "Knowledge-pack checksum mismatch — refusing to load." }
        return dest
    }

    private fun sha256(f: File): String {
        val md = java.security.MessageDigest.getInstance("SHA-256")
        f.inputStream().use { inp ->
            val buf = ByteArray(8192)
            var n: Int
            while (inp.read(buf).also { n = it } > 0) md.update(buf, 0, n)
        }
        return md.digest().joinToString("") { "%02x".format(it) }
    }
}
