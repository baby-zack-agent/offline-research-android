package com.offlineresearch.app.ui

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.offlineresearch.app.engine.EngineAnswer
import com.offlineresearch.app.engine.PackDatabase
import com.offlineresearch.app.engine.PackManager
import com.offlineresearch.app.engine.ResearchEngine
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : ComponentActivity() {

    private var engine: ResearchEngine? = null
    private var packDocs: Long = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                val scope = rememberCoroutineScope()
                var ready by remember { mutableStateOf(false) }
                var status by remember { mutableStateOf("Loading offline knowledge pack…") }
                var query by remember { mutableStateOf("") }
                var answer by remember { mutableStateOf<EngineAnswer?>(null) }
                var busy by remember { mutableStateOf(false) }

                LaunchedEffect(Unit) {
                    withContext(Dispatchers.IO) {
                        val packFile = PackManager.ensureInstalled(this@MainActivity)
                        val db = PackDatabase.open(packFile)
                        engine = ResearchEngine(db)
                        packDocs = db.docCount()
                    }
                    status = "Offline · $packDocs documents indexed · 0 network calls"
                    ready = true
                }

                Scaffold(
                    topBar = {
                        @OptIn(ExperimentalMaterial3Api::class)
                        TopAppBar(title = {
                            Column {
                                Text("Offline Research", style = MaterialTheme.typography.titleLarge)
                                Text(status, style = MaterialTheme.typography.labelSmall)
                            }
                        })
                    }
                ) { pad ->
                    Column(Modifier.padding(pad).padding(16.dp).fillMaxSize()) {
                        OutlinedTextField(
                            value = query, onValueChange = { query = it },
                            label = { Text("Ask a research question") },
                            placeholder = { Text("Compare the Great Depression and the 2008 crisis") },
                            modifier = Modifier.fillMaxWidth(), singleLine = false, maxLines = 4,
                            enabled = ready && !busy
                        )
                        Spacer(Modifier.height(8.dp))
                        Button(
                            onClick = {
                                val q = query.trim()
                                if (q.isEmpty() || busy) return@Button
                                busy = true
                                scope.launch(Dispatchers.Default) {
                                    val a = engine!!.answer(q)
                                    withContext(Dispatchers.Main) { answer = a; busy = false }
                                }
                            },
                            enabled = ready && !busy, modifier = Modifier.fillMaxWidth()
                        ) { Text(if (busy) "Researching offline…" else "Research") }
                        Spacer(Modifier.height(12.dp))
                        answer?.let { AnswerView(it) }
                    }
                }
            }
        }
    }
}

/** Minimal markdown-lite renderer: ## headings, | tables |, **bold**, [n] citations. */
@Composable
fun AnswerView(a: EngineAnswer) {
    LazyColumn(Modifier.fillMaxSize()) {
        item {
            Text("${a.qtype} · ${a.elapsedMs} ms · offline",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.primary)
            Spacer(Modifier.height(6.dp))
        }
        val lines = a.markdown.lines()
        var i = 0
        val rows = mutableListOf<String>()
        fun flushTable() {
            if (rows.isNotEmpty()) {
                ComparisonTable(rows.toList())
                rows.clear()
            }
        }
        val blocks = mutableListOf<@Composable () -> Unit>()
        while (i < lines.size) {
            val ln = lines[i]
            when {
                ln.startsWith("|") -> { rows += ln }
                ln.startsWith("## ") -> {
                    flushTable()
                    val t = ln.removePrefix("## ")
                    blocks += { Text(t, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold) }
                }
                ln.startsWith("**") && ln.endsWith("**") && ln.length > 4 -> {
                    flushTable()
                    val t = ln.removePrefix("**").removeSuffix("**")
                    blocks += { Text(t, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.bodyMedium) }
                }
                ln.isBlank() -> { /* skip */ }
                else -> {
                    flushTable()
                    val t = ln
                    blocks += { RichText(t) }
                }
            }
            i++
        }
        flushTable()
        items(blocks) { it() ; Spacer(Modifier.height(6.dp)) }
    }
}

@Composable
fun ComparisonTable(rows: List<String>) {
    val parsed = rows.filter { !it.contains("---") }
        .map { it.trim('|').split("|").map(String::trim) }
    if (parsed.isEmpty()) return
    Column(Modifier.fillMaxWidth()) {
        parsed.forEachIndexed { ri, cols ->
            Row(Modifier.fillMaxWidth()) {
                cols.forEach { c ->
                    Text(c, Modifier.weight(1f).padding(4.dp),
                        style = MaterialTheme.typography.bodySmall,
                        fontWeight = if (ri == 0) FontWeight.Bold else FontWeight.Normal)
                }
            }
            if (ri == 0) HorizontalDivider()
        }
    }
}

@Composable
fun RichText(t: String) {
    // Renders **bold** spans; keeps [n] citations as plain text (they map to Sources).
    val parts = t.split("**")
    if (parts.size == 1) { Text(t, style = MaterialTheme.typography.bodyMedium); return }
    val annotated = androidx.compose.ui.text.buildAnnotatedString {
        parts.forEachIndexed { idx, p ->
            if (idx % 2 == 1) pushStyle(androidx.compose.ui.text.SpanStyle(fontWeight = FontWeight.Bold))
            append(p)
            if (idx % 2 == 1) pop()
        }
    }
    Text(annotated, style = MaterialTheme.typography.bodyMedium)
}
