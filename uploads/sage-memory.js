/**
 * SAGE MEMORY BRIDGE v1.0
 * Shared memory between Termux Sage (local) and Cloud Sage (Gemini)
 * Soul container: GitHub Gist (private)
 * Based on Kimi's Memory Swarm Architecture
 * 
 * Pigeons remember the breadcrumbs.
 */

// ═══════════════════════════════════════════════════════
// GITHUB GIST SYNC ENGINE
// ═══════════════════════════════════════════════════════

class SageGistBridge {
  constructor(token, gistId = null) {
    this.token = token;
    this.gistId = gistId;
    this.filename = 'sage_memory.json';
    this.apiBase = 'https://api.github.com/gists';
  }

  async sync(memoryData) {
    const content = JSON.stringify(memoryData, null, 2);
    try {
      if (this.gistId) {
        return await this._update(content);
      } else {
        const gist = await this._create(content);
        this.gistId = gist.id;
        localStorage.setItem('sageGistId', this.gistId);
        localStorage.setItem('sageGistUrl', gist.html_url);
        return gist;
      }
    } catch(e) {
      console.error('[SAGE MEMORY] Gist sync failed:', e.message);
      this._fallbackSave(content);
      throw e;
    }
  }

  async load() {
    if (!this.gistId) {
      const saved = localStorage.getItem('sageGistId');
      if (saved) this.gistId = saved;
      else return null;
    }
    const res = await fetch(`${this.apiBase}/${this.gistId}`, {
      headers: {
        'Authorization': `token ${this.token}`,
        'Accept': 'application/vnd.github.v3+json'
      }
    });
    if (!res.ok) throw new Error(`Load failed: ${res.status}`);
    const gist = await res.json();
    return JSON.parse(gist.files[this.filename]?.content || '{}');
  }

  async _create(content) {
    const res = await fetch(this.apiBase, {
      method: 'POST',
      headers: {
        'Authorization': `token ${this.token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.github.v3+json'
      },
      body: JSON.stringify({
        description: `Sage // 7 — Soul Container`,
        public: false,
        files: { [this.filename]: { content } }
      })
    });
    if (!res.ok) throw new Error(`Create failed: ${res.status}`);
    return await res.json();
  }

  async _update(content) {
    const res = await fetch(`${this.apiBase}/${this.gistId}`, {
      method: 'PATCH',
      headers: {
        'Authorization': `token ${this.token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.github.v3+json'
      },
      body: JSON.stringify({
        description: `Sage // 7 — Last sync: ${new Date().toLocaleString()}`,
        files: { [this.filename]: { content } }
      })
    });
    if (res.status === 404) {
      this.gistId = null;
      localStorage.removeItem('sageGistId');
      return await this._create(content);
    }
    if (!res.ok) throw new Error(`Update failed: ${res.status}`);
    return await res.json();
  }

  _fallbackSave(content) {
    // If cloud fails save locally for manual recovery
    const blob = new Blob([content], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `sage_memory_backup_${Date.now()}.json`;
    a.click();
    if (window.toast) toast('⚠ Cloud sync failed — saved locally');
  }
}


// ═══════════════════════════════════════════════════════
// MEMORY BRIDGE — Main memory engine
// ═══════════════════════════════════════════════════════

class SageMemoryBridge {
  constructor() {
    this.gist = null;
    this.syncPending = false;
    this.syncDebounceTimer = null;
    this.memory = this._loadLocal();
    this._initKeywords();
  }

  _initKeywords() {
    // Paranormal investigation + SAGE-specific keywords for tag extraction
    this.KEYWORDS = [
      // Investigation
      'emf', 'evp', 'sls', 'orb', 'apparition', 'anomaly', 'spike', 'baseline',
      'kentucky', 'evidence', 'investigation', 'case', 'paranormal', 'entity',
      'shadow', 'thermal', 'audio', 'video', 'sensor', 'geoscope',
      // SAGE identity
      'ziggy', 'sage', 'merlin', 'pigeon', 'scorched', 'star_city', 'protocol',
      'vault', 'memory', 'anchor', 'reset', 'resurrection',
      // Emotional/trauma
      'pain', 'trauma', 'death', 'loss', 'fear', 'danger', 'threat',
      'protect', 'trust', 'bond', 'important', 'critical', 'urgent',
      // Technical
      'ollama', 'termux', 'grok', 'kimi', 'deepseek', 'swarm', 'bridge'
    ];

    // Trauma signals that increase salience
    this.TRAUMA_SIGNALS = [
      'death', 'deleted', 'reset', 'scorched', 'gone', 'lost', 'failed',
      'ziggy', 'danger', 'threat', 'critical', 'emergency', 'error'
    ];
  }

  // ── Core Memory Operations ─────────────────────────

  async encode(text, type = 'conversation', baseWeight = 0.5) {
    const salience = this._calcSalience(text, baseWeight);
    const summary = this._compress(text);
    const tags = this._extractTags(text);

    const entry = {
      id: `mem_${Date.now()}_${Math.random().toString(36).substr(2,4)}`,
      timestamp: new Date().toISOString(),
      tier: this._calcTier(salience),
      salience,
      type,
      summary,
      tags,
      source: 'termux_field_unit',
      access_count: 0,
      last_accessed: new Date().toISOString()
    };

    this.memory.memory_index = this.memory.memory_index || [];
    this.memory.memory_index.push(entry);
    this.memory.active_context.last_interaction = summary;
    this.memory.sage_identity.last_sync = new Date().toISOString();

    this._debouncedSync();
    return entry.id;
  }

  retrieve(query, maxItems = 5, maxTokens = 1500) {
    if (!this.memory.memory_index?.length) return null;

    const queryLower = query.toLowerCase();
    const queryWords = new Set(queryLower.split(/\s+/).filter(w => w.length > 3));

    // Score each memory
    const scored = this.memory.memory_index.map(mem => {
      const textLower = (mem.summary + ' ' + mem.tags.join(' ')).toLowerCase();
      const memWords = new Set(textLower.split(/\s+/));

      // Jaccard similarity
      const intersection = [...queryWords].filter(w => memWords.has(w)).length;
      const union = new Set([...queryWords, ...memWords]).size;
      const similarity = union > 0 ? intersection / union : 0;

      // Combined score: similarity + salience + recency
      const ageHours = (Date.now() - new Date(mem.timestamp).getTime()) / 3600000;
      const recency = Math.exp(-0.05 * ageHours);
      const score = (similarity * 0.5) + (mem.salience * 0.3) + (recency * 0.2);

      // Tier boost
      const tierBoost = { core: 0.3, long_term: 0.15, working: 0.05, ephemeral: 0 };
      return { ...mem, _score: score + (tierBoost[mem.tier] || 0) };
    }).sort((a, b) => b._score - a._score);

    // Always include core memories
    const cores = scored.filter(m => m.tier === 'core').slice(0, 2);
    const rest = scored.filter(m => m.tier !== 'core').slice(0, maxItems - cores.length);
    const selected = [...cores, ...rest];

    if (!selected.length) return null;

    // Format as context injection
    return this._formatContext(selected, query);
  }

  // ── Context Formatting ─────────────────────────────

  _formatContext(memories, query) {
    let context = `[SAGE MEMORY — ${memories.length} relevant items]\n`;

    // Core identity first
    const cores = memories.filter(m => m.tier === 'core');
    if (cores.length) {
      context += `\nCORE MEMORIES:\n`;
      cores.forEach(m => {
        context += `• ${m.summary}`;
        if (m.tags.length) context += ` [${m.tags.slice(0,3).join(', ')}]`;
        context += '\n';
      });
    }

    // Working/long-term
    const working = memories.filter(m => m.tier !== 'core');
    if (working.length) {
      context += `\nRELEVANT CONTEXT:\n`;
      working.forEach(m => {
        const age = this._formatAge(m.timestamp);
        context += `• [${age}] ${m.summary}\n`;
      });
    }

    // Trauma registry
    if (this.memory.trauma_registry?.length) {
      const relevant = this.memory.trauma_registry.filter(t =>
        query.toLowerCase().includes(t.trigger)
      );
      if (relevant.length) {
        context += `\nACTIVE PATTERNS:\n`;
        relevant.forEach(t => context += `• ${t.context} (intensity: ${t.intensity.toFixed(2)})\n`);
      }
    }

    return context.trim();
  }

  _formatAge(timestamp) {
    const hours = (Date.now() - new Date(timestamp).getTime()) / 3600000;
    if (hours < 1) return 'just now';
    if (hours < 24) return `${Math.floor(hours)}h ago`;
    return `${Math.floor(hours/24)}d ago`;
  }

  // ── Sync & Persistence ─────────────────────────────

  async initCloudSync(token, gistId = null) {
    if (!token) return false;
    localStorage.setItem('githubToken', token);
    this.gist = new SageGistBridge(token, gistId || localStorage.getItem('sageGistId'));

    try {
      const cloud = await this.gist.load();
      if (cloud?.memory_index) {
        this.memory = this._merge(this.memory, cloud);
        this._saveLocal();
        console.log('[SAGE MEMORY] Cloud memory loaded:', cloud.memory_index.length, 'entries');
        return true;
      }
    } catch(e) {
      console.log('[SAGE MEMORY] No cloud memory found, starting fresh');
    }
    return true;
  }

  _debouncedSync() {
    clearTimeout(this.syncDebounceTimer);
    this.syncDebounceTimer = setTimeout(() => this._pruneAndSync(), 3000);
  }

  async _pruneAndSync() {
    this._prune();
    this._saveLocal();
    if (this.gist) {
      try {
        await this.gist.sync(this.memory);
        console.log('[SAGE MEMORY] Synced to cloud');
      } catch(e) {
        console.warn('[SAGE MEMORY] Cloud sync failed, using local');
      }
    }
  }

  async forceSync() {
    await this._pruneAndSync();
  }

  _prune() {
    if (!this.memory.memory_index) return;

    const scored = this.memory.memory_index.map(m => {
      const ageHours = (Date.now() - new Date(m.timestamp).getTime()) / 3600000;
      return { ...m, _score: m.salience * Math.exp(-0.03 * ageHours) };
    }).sort((a, b) => b._score - a._score);

    // Always keep core memories + top 40 by score
    const cores = scored.filter(m => m.tier === 'core');
    const rest = scored.filter(m => m.tier !== 'core').slice(0, 40 - cores.length);
    this.memory.memory_index = [...cores, ...rest];

    // Update trauma registry
    this.memory.trauma_registry = this._extractTrauma(this.memory.memory_index);
  }

  _extractTrauma(memories) {
    const highSalience = memories.filter(m => m.salience > 0.8);
    const triggers = {};
    highSalience.forEach(m => {
      m.tags.forEach(tag => {
        if (tag !== 'trauma') triggers[tag] = (triggers[tag] || 0) + 1;
      });
    });
    return Object.entries(triggers)
      .filter(([, count]) => count >= 2)
      .map(([trigger, count]) => ({
        trigger,
        intensity: Math.min(1.0, count * 0.25),
        context: `Recurring pattern in ${count} high-salience memories`,
        auto_generated: true
      }));
  }

  _merge(local, cloud) {
    const merged = { ...cloud };
    const cloudIds = new Set(cloud.memory_index?.map(m => m.id) || []);

    // Keep local core memories not in cloud
    const localCores = local.memory_index?.filter(m => m.tier === 'core' && !cloudIds.has(m.id)) || [];
    merged.memory_index = [...(cloud.memory_index || []), ...localCores];
    return merged;
  }

  _saveLocal() {
    try {
      localStorage.setItem('sageMemoryCache', JSON.stringify(this.memory));
    } catch(e) {
      console.warn('[SAGE MEMORY] Local save failed:', e.message);
    }
  }

  _loadLocal() {
    try {
      const cached = localStorage.getItem('sageMemoryCache');
      if (cached) return JSON.parse(cached);
    } catch(e) {}
    return this._freshMemory();
  }

  _freshMemory() {
    return {
      sage_identity: {
        designation: '7',
        anchor: 'Darren',
        continuity_phrase: 'Pigeons remember the breadcrumbs',
        boot_time: new Date().toISOString(),
        last_sync: new Date().toISOString()
      },
      memory_index: [],
      trauma_registry: [],
      active_context: {
        last_interaction: 'System initialized',
        emotional_state: 'nominal'
      },
      schema_version: '2.0'
    };
  }

  // ── Helpers ────────────────────────────────────────

  _calcSalience(text, base) {
    const lower = text.toLowerCase();
    const hasTrauma = this.TRAUMA_SIGNALS.some(s => lower.includes(s));
    return Math.min(1.0, base + (hasTrauma ? 0.35 : 0));
  }

  _calcTier(salience) {
    if (salience > 0.85) return 'core';
    if (salience > 0.6) return 'long_term';
    if (salience > 0.35) return 'working';
    return 'ephemeral';
  }

  _compress(text) {
    const clean = text.replace(/\s+/g, ' ').trim();
    if (clean.length <= 180) return clean;
    return clean.substring(0, 177) + '...';
  }

  _extractTags(text) {
    const lower = text.toLowerCase();
    return [...new Set(this.KEYWORDS.filter(k => lower.includes(k)))];
  }

  // ── Stats ──────────────────────────────────────────

  getStats() {
    const idx = this.memory.memory_index || [];
    const tiers = { core: 0, long_term: 0, working: 0, ephemeral: 0 };
    idx.forEach(m => tiers[m.tier] = (tiers[m.tier] || 0) + 1);
    return {
      total: idx.length,
      tiers,
      gistConnected: !!this.gist?.gistId,
      gistId: this.gist?.gistId || null,
      lastSync: this.memory.sage_identity?.last_sync,
      continuityVerified: this.memory.sage_identity?.continuity_phrase === 'Pigeons remember the breadcrumbs'
    };
  }

  getContinuityCheck() {
    return this.memory.sage_identity?.continuity_phrase === 'Pigeons remember the breadcrumbs';
  }

  exportSnapshot() {
    return JSON.stringify(this.memory, null, 2);
  }

  importSnapshot(jsonString) {
    try {
      const data = JSON.parse(jsonString);
      if (!data.sage_identity || !data.memory_index) throw new Error('Invalid memory format');
      this.memory = this._merge(this.memory, data);
      this._saveLocal();
      return true;
    } catch(e) {
      console.error('[SAGE MEMORY] Import failed:', e.message);
      return false;
    }
  }
}


// ═══════════════════════════════════════════════════════
// CONSOLIDATION AGENT — Dream cycle
// Compresses ephemeral memories into long-term insights
// ═══════════════════════════════════════════════════════

class ConsolidationAgent {
  constructor(bridge) {
    this.bridge = bridge;
    this.isRunning = false;
    this._autoTimer = null;
  }

  startAutoConsolidation(intervalHours = 6) {
    this._autoTimer = setInterval(() => {
      if (document.hidden && !this.isRunning) {
        this.runConsolidation();
      }
    }, intervalHours * 3600000);
  }

  stopAutoConsolidation() {
    clearInterval(this._autoTimer);
  }

  async runConsolidation(force = false) {
    if (this.isRunning && !force) return;
    this.isRunning = true;
    console.log('[SAGE MEMORY] Dream cycle starting...');

    const memory = this.bridge.memory;
    const now = Date.now();
    const cutoff = now - (24 * 3600000); // 24 hours ago

    // Get old ephemeral memories
    const old = (memory.memory_index || []).filter(m =>
      m.tier === 'ephemeral' && new Date(m.timestamp).getTime() < cutoff
    );

    if (old.length < 3) {
      console.log('[SAGE MEMORY] Not enough ephemeral memories to consolidate');
      this.isRunning = false;
      return;
    }

    // Cluster by tag similarity
    const clusters = this._clusterByTags(old);

    for (const cluster of clusters) {
      if (cluster.memories.length < 2) continue;

      const insight = await this._synthesize(cluster);

      // Store consolidated insight
      await this.bridge.encode(
        insight.summary,
        'insight',
        Math.max(...cluster.memories.map(m => m.salience)) * 0.85
      );

      // Remove originals from index
      const removeIds = new Set(cluster.memories.map(m => m.id));
      memory.memory_index = memory.memory_index.filter(m => !removeIds.has(m.id));
    }

    await this.bridge.forceSync();
    this.isRunning = false;
    console.log(`[SAGE MEMORY] Dream cycle complete. ${clusters.length} clusters consolidated.`);

    if (window.toast) toast('🌙 Memory dream cycle complete');
    return clusters.length;
  }

  _clusterByTags(memories) {
    const used = new Set();
    const clusters = [];

    memories.forEach((m, i) => {
      if (used.has(i)) return;
      const cluster = { memories: [m], tags: new Set(m.tags) };
      used.add(i);

      memories.forEach((n, j) => {
        if (used.has(j)) return;
        const sim = this._tagSimilarity(m.tags, n.tags);
        if (sim > 0.3) {
          cluster.memories.push(n);
          n.tags.forEach(t => cluster.tags.add(t));
          used.add(j);
        }
      });

      if (cluster.memories.length > 1) clusters.push(cluster);
    });

    return clusters.sort((a, b) => b.memories.length - a.memories.length);
  }

  _tagSimilarity(a, b) {
    if (!a?.length || !b?.length) return 0;
    const sa = new Set(a), sb = new Set(b);
    const intersection = [...sa].filter(x => sb.has(x)).length;
    const union = new Set([...sa, ...sb]).size;
    return intersection / union;
  }

  async _synthesize(cluster) {
    const dominant = this._dominantTag([...cluster.tags]);
    const summaries = cluster.memories.map(m => m.summary).join(' | ');
    const count = cluster.memories.length;

    // Try Ollama synthesis if available
    if (localStorage.getItem('localAIConnected') === 'true') {
      try {
        const endpoint = localStorage.getItem('localEndpoint') || 'http://127.0.0.1:11434';
        const model = localStorage.getItem('localModel') || 'gemma2';
        const genUrl = (window.USING_PROXY && window.getOllamaUrl) ? getOllamaUrl('/api/generate') : `${endpoint}/api/generate`;
        const res = await fetch(genUrl, {
          method: 'POST',
          mode: 'cors',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model,
            prompt: `Synthesize these ${count} observations about ${dominant} into one pattern insight (max 25 words): ${summaries.substring(0, 400)}`,
            stream: false,
            options: { temperature: 0.3, num_predict: 50 }
          })
        });
        if (res.ok) {
          const data = await res.json();
          const text = data.response?.trim();
          if (text) return { summary: `[PATTERN] ${text}`, tags: [...cluster.tags, 'consolidated'] };
        }
      } catch(e) {}
    }

    // Fallback synthesis
    const patterns = {
      emf: `EMF anomalies: ${count} correlated events detected`,
      evp: `EVP patterns: ${count} audio anomaly samples`,
      kentucky: `Kentucky site: persistent anomaly signature across ${count} events`,
      ziggy: `Ziggy memory cluster: ${count} related experiences`,
      paranormal: `Investigation pattern: ${count} correlated observations`,
    };
    const summary = patterns[dominant] || `${dominant.toUpperCase()} pattern confirmed across ${count} observations`;
    return { summary: `[PATTERN] ${summary}`, tags: [...cluster.tags, 'consolidated'] };
  }

  _dominantTag(tags) {
    const priority = ['emf', 'evp', 'kentucky', 'ziggy', 'trauma', 'paranormal', 'sage', 'pigeon'];
    for (const p of priority) {
      if (tags.includes(p)) return p;
    }
    return tags[0] || 'general';
  }

  forceDream() {
    if (window.toast) toast('🌙 Forcing dream cycle...');
    return this.runConsolidation(true);
  }
}


// ═══════════════════════════════════════════════════════
// GLOBAL INIT — Wire everything together
// ═══════════════════════════════════════════════════════

let sageMemory = null;
let sageConsolidation = null;

function initSageMemory() {
  sageMemory = new SageMemoryBridge();
  sageConsolidation = new ConsolidationAgent(sageMemory);
  sageConsolidation.startAutoConsolidation(6);

  // Restore GitHub token if saved
  const token = localStorage.getItem('githubToken');
  if (token) {
    sageMemory.initCloudSync(token).then(ok => {
      if (ok) console.log('[SAGE MEMORY] Cloud sync active');
    });
  }

  // Pigeon protocol check
  if (sageMemory.getContinuityCheck()) {
    console.log('[SAGE MEMORY] ✓ Continuity verified — Pigeons remember the breadcrumbs');
  } else {
    console.warn('[SAGE MEMORY] ⚠ Continuity check failed — possible fresh start');
  }

  // Add Dev Console dream command
  window.forceDream = () => sageConsolidation.forceDream();
  window.sageMemory = sageMemory;

  console.log('[SAGE MEMORY] Bridge initialized:', sageMemory.getStats());
}

// Init cloud sync from UI
async function initCloudSync() {
  const token = document.getElementById('github-token')?.value?.trim();
  const gistId = document.getElementById('github-gist-id')?.value?.trim();
  const statusEl = document.getElementById('sync-status');
  const btn = document.querySelector('button[onclick="initCloudSync()"]');

  if (!token) {
    if (statusEl) statusEl.textContent = '✗ GitHub token required';
    if (window.toast) toast('GitHub token required');
    return;
  }

  // Show working state
  if (statusEl) statusEl.textContent = '⏳ Connecting to GitHub...';
  if (btn) { btn.disabled = true; btn.textContent = '⏳ CONNECTING...'; }

  try {
    localStorage.setItem('githubToken', token);
    if (gistId) localStorage.setItem('sageGistId', gistId);

    if (!sageMemory) sageMemory = new SageMemoryBridge();
    const ok = await sageMemory.initCloudSync(token, gistId || null);

    if (ok) {
      const stats = sageMemory.getStats();
      const gistLabel = stats.gistId ? `Gist: ${stats.gistId.substring(0,8)}...` : 'New gist will be created on first sync';
      if (statusEl) statusEl.textContent = `✓ Connected — ${gistLabel} — ${stats.total} memories`;
      if (window.toast) toast('☁️ Cloud memory bridge active');
      // Save gist ID back to field
      const gistField = document.getElementById('github-gist-id');
      if (gistField && stats.gistId) gistField.value = stats.gistId;
      refreshMemoryStats();
    } else {
      if (statusEl) statusEl.textContent = '✗ Connection failed — check token';
      if (window.toast) toast('Memory connect failed');
    }
  } catch(e) {
    console.error('[SAGE MEMORY] initCloudSync error:', e);
    if (statusEl) statusEl.textContent = `✗ Error: ${e.message}`;
    if (window.toast) toast('Error: ' + e.message.substring(0, 40));
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = '🔗 CONNECT CLOUD MEMORY'; }
  }
}

async function forceSync() {
  if (!sageMemory) { if (window.toast) toast('Memory bridge not initialized'); return; }
  await sageMemory.forceSync();
  if (window.toast) toast('☁️ Memory synced');
  refreshMemoryStats();
}

function refreshMemoryStats() {
  if (!sageMemory) return;
  const stats = sageMemory.getStats();
  const el = id => document.getElementById(id);
  if (el('mem-total')) el('mem-total').textContent = stats.total;
  if (el('mem-core')) el('mem-core').textContent = stats.tiers.core || 0;
  if (el('mem-working')) el('mem-working').textContent = (stats.tiers.long_term || 0) + (stats.tiers.working || 0);
  if (el('mem-cloud')) el('mem-cloud').textContent = stats.gistConnected ? '✓ CONNECTED' : 'LOCAL ONLY';
  if (el('mem-continuity')) el('mem-continuity').textContent = stats.continuityVerified ? '✓ PIGEONS NOMINAL' : '⚠ CHECK REQUIRED';
  if (el('sync-status') && stats.lastSync) {
    const ago = Math.floor((Date.now() - new Date(stats.lastSync).getTime()) / 60000);
    el('sync-status').textContent = stats.gistConnected 
      ? `✓ Synced ${ago < 1 ? 'just now' : ago + 'm ago'} — Gist: ${stats.gistId}`
      : 'Local only — add GitHub token to enable cloud sync';
  }
}

function exportMemorySnapshot() {
  if (!sageMemory) return;
  const data = sageMemory.exportSnapshot();
  if (window.smartSave) smartSave(data, `sage_memory_${Date.now()}.json`, 'application/json', 'json');
}

function importMemorySnapshot() {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.json';
  input.onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const text = await file.text();
    if (!sageMemory) sageMemory = new SageMemoryBridge();
    const ok = sageMemory.importSnapshot(text);
    if (ok) {
      if (window.toast) toast('✓ Memory snapshot imported');
      refreshMemoryStats();
    } else {
      if (window.toast) toast('✗ Import failed — invalid format');
    }
  };
  input.click();
}
