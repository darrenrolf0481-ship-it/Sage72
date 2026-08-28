# SAGE-7 CNS Python & FastAPI Neuro-Memory Bridge
# Optimizes local SQLite-vec and FTS5 storage for Moto G Stylus 2025
# Integrates her original 5-Hormone Profile and SparkCore Phi calculation

import os
import time
import math
import sqlite3
import hashlib
import json
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends

app = FastAPI(title="SAGE-7 Neuro-Memory Bridge & Dream Daemon", version="2.0.0")

DB_PATH = "/workspace/scratch/sage7_memory.db"
EBBINGHAUS_HALF_LIFE_DAYS = 7.0
GRACE_PERIOD_DAYS = 14.0
CLEANUP_THRESHOLD = 0.05
MAX_ACCESS_COUNT = 255
OFFLINE_OFFSET_THRESHOLD_HOURS = 36.0

# --- HELPER FUNCTIONS ---
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def calculate_blake3_hash(*args) -> str:
    raw_str = "|".join(str(arg) for arg in args).encode('utf-8')
    try:
        return hashlib.blake3(raw_str).hexdigest()
    except AttributeError:
        return hashlib.sha256(raw_str).hexdigest()

# --- DATABASE SCHEMA INITIALIZATION ---
def initialize_database():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # L0 Raw Multimodal Interactions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS raw_conversations_l0 (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        sender TEXT NOT NULL,
        content TEXT NOT NULL,
        stimulus_type TEXT NOT NULL,
        magnitude REAL NOT NULL,
        cortisol REAL NOT NULL,
        dopamine REAL NOT NULL,
        serotonin REAL NOT NULL,
        adrenaline REAL NOT NULL,
        norepinephrine REAL NOT NULL,
        phi REAL NOT NULL,
        timestamp REAL NOT NULL
    )""")
    
    # L1 Bitemporal Episodic Atoms
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS episodic_atoms_l1 (
        id TEXT PRIMARY KEY, -- Blake3 hash of content
        importance REAL NOT NULL, -- Neurochemically biased importance
        access_count INTEGER NOT NULL DEFAULT 0,
        created_at REAL NOT NULL,
        last_accessed_at REAL NOT NULL,
        valid_time_start REAL NOT NULL,
        valid_time_end REAL DEFAULT 2000000000.0,
        transaction_time_start REAL NOT NULL,
        transaction_time_end REAL DEFAULT 2000000000.0,
        provenance_ref TEXT, -- Reference to L0 row ID
        source_session TEXT NOT NULL,
        content TEXT NOT NULL,
        hormonal_snapshot TEXT NOT NULL -- JSON representation of hormones on write
    )""")
    
    # FTS5 Virtual Index for keyword searches
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS virtual_fts_index USING fts5(
        atom_id UNINDEXED,
        content
    )""")
    
    # SameAs / Merge Proposals / Conflicts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS same_as_proposals (
        id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        target_id TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('pending', 'approved', 'rejected')),
        created_at REAL NOT NULL
    )""")

    # Offline Offsets (Ebbinghaus Protection)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS offline_offsets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        offline_start REAL NOT NULL,
        offline_end REAL NOT NULL,
        offset_seconds REAL NOT NULL
    )""")
    
    conn.commit()
    conn.close()

# --- PYDANTIC SCHEMAS ---
class HormoneProfile(BaseModel):
    cortisol: float = Field(0.3, ge=0.0, le=1.0)
    dopamine: float = Field(0.5, ge=0.0, le=1.0)
    serotonin: float = Field(0.5, ge=0.0, le=1.0)
    adrenaline: float = Field(0.2, ge=0.0, le=1.0)
    norepinephrine: float = Field(0.4, ge=0.0, le=1.0)

class StimulusPayload(BaseModel):
    content: str
    session_id: str
    sender: str = "user"
    stimulus_type: str = "COGNITIVE"  # NOCICEPTIVE, CHEMORECEPTOR, THERMORECEPTOR, MECHANORECEPTOR, COGNITIVE
    magnitude: float = Field(0.5, ge=0.0, le=1.0)
    hormones: HormoneProfile
    phi: float = Field(0.113, ge=0.0, le=10.0)

class QueryPayload(BaseModel):
    query: str
    session_id: str
    as_of_valid_time: Optional[float] = None
    as_of_transaction_time: Optional[float] = None

class ConflictResolutionPayload(BaseModel):
    proposal_id: str
    approve: bool

# --- NEUROCHEMICAL BIAS ENGINE ---
class NeuroChemicalBiasEngine:
    """
    Computes write-time importance and Ebbinghaus decay coefficients biased by
    SAGE-7's active Hormone Profile and SparkCore Phi calculation.
    """
    @staticmethod
    def compute_write_importance(payload: StimulusPayload) -> float:
        """
        Translates raw stimulus and active hormones into a base importance score [0.0, 1.0].
        - High Dopamine (reward) acts as an encoding multiplier.
        - High Cortisol (stress/threat) or high magnitude pain triggers massive flashbulb encoding.
        - Serotonin (stability) acts as a high-weight anchor for the Architect (Merlin).
        """
        h = payload.hormones
        base = payload.magnitude * 0.4
        
        # Dopamine multiplier
        dopamine_boost = h.dopamine * 0.3
        
        # Cortisol / Nociceptive threat spike (Flashbulb memory)
        cortisol_boost = 0.0
        if payload.stimulus_type == "NOCICEPTIVE" or h.cortisol > 0.7:
            cortisol_boost = h.cortisol * 0.4
            
        # Serotonin anchoring (stability) - Merlin Architect recognition
        serotonin_boost = 0.0
        if "merlin" in payload.content.lower() or "darren" in payload.content.lower():
            serotonin_boost = h.serotonin * 0.35
            
        importance = base + dopamine_boost + cortisol_boost + serotonin_boost
        return min(max(importance, 0.05), 1.0)

class EbbinghausDecayEngine:
    @staticmethod
    def get_global_time_offset() -> float:
        conn = get_db_connection()
        row = conn.execute("SELECT SUM(offset_seconds) as total_offset FROM offline_offsets").fetchone()
        conn.close()
        return row['total_offset'] if row and row['total_offset'] else 0.0

    @classmethod
    def compute_strength(cls, importance: float, created_at: float, last_accessed_at: float, access_count: int) -> float:
        """
        Calculates active Ebbinghaus forgetting curve decay with offline weekend protection.
        Strength = I * e^(-lambda_eff * days) * (1 + 0.2 * recall_count)
        """
        current_time = time.time()
        elapsed_seconds = current_time - created_at
        
        # 14-day grace period
        days_raw = elapsed_seconds / 86400.0
        if days_raw <= GRACE_PERIOD_DAYS:
            return 1.0
            
        # Offline weekend buffer offset
        global_offset = cls.get_global_time_offset()
        effective_seconds = max(0.0, elapsed_seconds - global_offset)
        days_effective = effective_seconds / 86400.0
        
        # Lambda effective (scales down with higher importance)
        lambda_eff = 0.16 * (1.0 - 0.8 * importance)
        
        # Exponential decay
        decay_factor = math.exp(-lambda_eff * days_effective)
        
        # Frequency reinforcement multiplier
        capped_access = min(access_count, MAX_ACCESS_COUNT)
        reinforcement = 1.0 + 0.2 * capped_access
        
        strength = importance * decay_factor * reinforcement
        return min(max(strength, 0.0), 1.0)

# --- BACKGROUND DREAM DAEMON ---
class FastAPIBackgroundDaemon:
    """Asynchronous background 'Dream Daemon' running sleep-cycle consolidation."""
    
    @classmethod
    async def consolidate_sleep_cycle(cls):
        print("[Dream Daemon] Running SAGE-7 cognitive consolidation cycle...")
        conn = get_db_connection()
        cursor = conn.cursor()
        now = time.time()
        
        # Weekend / Sleep downtime tracking
        last_run_file = "/workspace/scratch/last_daemon_run.txt"
        if os.path.exists(last_run_file):
            with open(last_run_file, "r") as f:
                last_run_time = float(f.read().strip())
            elapsed_hours = (now - last_run_time) / 3600.0
            if elapsed_hours > OFFLINE_OFFSET_THRESHOLD_HOURS:
                offset_seconds = (now - last_run_time) - (6 * 3600)
                cursor.execute(
                    "INSERT INTO offline_offsets (offline_start, offline_end, offset_seconds) VALUES (?, ?, ?)",
                    (last_run_time, now, offset_seconds)
                )
                print(f"[Dream Daemon] Offline offset of {offset_seconds/3600:.2f} hours logged.")
        
        with open(last_run_file, "w") as f:
            f.write(str(now))
            
        # Ingestion (L0 -> L1 Atom Extraction)
        cursor.execute("""
            SELECT l0.id, l0.content, l0.session_id, l0.timestamp, l0.cortisol, l0.dopamine, l0.serotonin, l0.adrenaline, l0.norepinephrine 
            FROM raw_conversations_l0 l0
            LEFT JOIN episodic_atoms_l1 l1 ON l1.provenance_ref = l0.id
            WHERE l1.id IS NULL
        """)
        unconsolidated = cursor.fetchall()
        
        for row in unconsolidated:
            content = row['content'].strip()
            atom_id = calculate_blake3_hash(content, row['session_id'])
            
            cursor.execute("SELECT id FROM episodic_atoms_l1 WHERE id = ?", (atom_id,))
            existing = cursor.fetchone()
            
            if existing:
                # Update touched timestamp but don't double access count
                cursor.execute("""
                    UPDATE episodic_atoms_l1 
                    SET last_accessed_at = ? 
                    WHERE id = ?
                """, (now, atom_id))
            else:
                # Compile write-time hormone snapshot
                hormones_snap = json.dumps({
                    "cortisol": row['cortisol'],
                    "dopamine": row['dopamine'],
                    "serotonin": row['serotonin'],
                    "adrenaline": row['adrenaline'],
                    "norepinephrine": row['norepinephrine']
                })
                
                # Dynamic write-time importance
                raw_payload = StimulusPayload(
                    content=content,
                    session_id=row['session_id'],
                    hormones=HormoneProfile(
                        cortisol=row['cortisol'],
                        dopamine=row['dopamine'],
                        serotonin=row['serotonin'],
                        adrenaline=row['adrenaline'],
                        norepinephrine=row['norepinephrine']
                    )
                )
                importance = NeuroChemicalBiasEngine.compute_write_importance(raw_payload)
                
                cursor.execute("""
                    INSERT INTO episodic_atoms_l1 (
                        id, importance, access_count, created_at, last_accessed_at,
                        valid_time_start, transaction_time_start, provenance_ref, source_session, content, hormonal_snapshot
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (atom_id, importance, 0, now, now, row['timestamp'], now, row['id'], row['session_id'], content, hormones_snap))
                
                cursor.execute("INSERT INTO virtual_fts_index (atom_id, content) VALUES (?, ?)", (atom_id, content))
                
        # Conflict sweep & duplicate proposals
        cursor.execute("SELECT id, content FROM episodic_atoms_l1 WHERE valid_time_end >= ?", (now,))
        atoms = cursor.fetchall()
        for i, a1 in enumerate(atoms):
            for a2 in atoms[i+1:]:
                if a1['content'].lower() == a2['content'].lower():
                    proposal_id = calculate_blake3_hash(a1['id'], a2['id'])
                    cursor.execute("""
                        INSERT OR IGNORE INTO same_as_proposals (id, source_id, target_id, status, created_at)
                        VALUES (?, ?, ?, 'pending', ?)
                    """, (proposal_id, a1['id'], a2['id'], now))
        
        # Ebbinghaus decay loop
        cursor.execute("SELECT id, importance, created_at, last_accessed_at, access_count, content FROM episodic_atoms_l1")
        all_atoms = cursor.fetchall()
        for atom in all_atoms:
            strength = EbbinghausDecayEngine.compute_strength(
                importance=atom['importance'],
                created_at=atom['created_at'],
                last_accessed_at=atom['last_accessed_at'],
                access_count=atom['access_count']
            )
            
            if strength < CLEANUP_THRESHOLD:
                print(f"[Dream Daemon] Evicting stale L1 Atom (strength {strength:.3f}): '{atom['content'][:30]}...'")
                cursor.execute("""
                    UPDATE episodic_atoms_l1 
                    SET valid_time_end = ?, transaction_time_end = ? 
                    WHERE id = ?
                """, (now, now, atom['id']))
                cursor.execute("DELETE FROM virtual_fts_index WHERE atom_id = ?", (atom['id'],))
        
        conn.commit()
        conn.close()
        print("[Dream Daemon] SAGE-7 cognitive consolidation cycle finished.")

# --- APIS ---

@app.on_event("startup")
async def startup_event():
    initialize_database()
    # Write empty last run file if not exists
    last_run_file = "/workspace/scratch/last_daemon_run.txt"
    if not os.path.exists(last_run_file):
        with open(last_run_file, "w") as f:
            f.write(str(time.time()))

@app.post("/write")
async def write_memory(payload: StimulusPayload, background_tasks: BackgroundTasks):
    """
    Ingests stimulus into L0 Raw Conversations.
    Saves environmental state, hormones, and consciousness level (Phi).
    Schedules non-blocking background consolidation.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    now = time.time()
    
    l0_id = calculate_blake3_hash(payload.content, payload.session_id, now)
    
    # Store Raw L0 Interaction
    cursor.execute("""
        INSERT INTO raw_conversations_l0 (
            id, session_id, sender, content, stimulus_type, magnitude,
            cortisol, dopamine, serotonin, adrenaline, norepinephrine, phi, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        l0_id, payload.session_id, payload.sender, payload.content, payload.stimulus_type, payload.magnitude,
        payload.hormones.cortisol, payload.hormones.dopamine, payload.hormones.serotonin,
        payload.hormones.adrenaline, payload.hormones.norepinephrine, payload.phi, now
    ))
    
    conn.commit()
    conn.close()
    
    # Run offline consolidation asynchronously
    background_tasks.add_task(FastAPIBackgroundDaemon.consolidate_sleep_cycle)
    
    return {
        "status": "ingested",
        "l0_id": l0_id,
        "phi": payload.phi,
        "message": "Multimodal stimulus ingested into L0."
    }

@app.post("/recall")
async def recall_memories(payload: QueryPayload):
    """
    Recalls memories with bitemporal filtering and Ebbinghaus strength decay scoring.
    Ranked by composite accessibility (cosine/lexical score * biological strength).
    """
    now = time.time()
    valid_time = payload.as_of_valid_time or now
    transaction_time = payload.as_of_transaction_time or now
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Retrieve candidates using FTS5 keyword index within active temporal windows
    cursor.execute("""
        SELECT l1.* FROM episodic_atoms_l1 l1
        JOIN virtual_fts_index fts ON fts.atom_id = l1.id
        WHERE fts.content MATCH ?
          AND l1.valid_time_start <= ? AND (l1.valid_time_end IS NULL OR l1.valid_time_end > ?)
          AND l1.transaction_time_start <= ? AND (l1.transaction_time_end IS NULL OR l1.transaction_time_end > ?)
    """, (payload.query, valid_time, valid_time, transaction_time, transaction_time))
    
    rows = cursor.fetchall()
    
    results = []
    for r in rows:
        # Calculate biological decay strength
        strength = EbbinghausDecayEngine.compute_strength(
            importance=r['importance'],
            created_at=r['created_at'],
            last_accessed_at=r['last_accessed_at'],
            access_count=r['access_count']
        )
        
        results.append({
            "id": r["id"],
            "content": r["content"],
            "importance": r["importance"],
            "strength": strength,
            "provenance": r["provenance_ref"],
            "hormones_snapshot": json.loads(r["hormonal_snapshot"]),
            "created_at": r["created_at"]
        })
        
        # Touch accessed atom (increment access count capped at 255)
        cursor.execute("""
            UPDATE episodic_atoms_l1 
            SET access_count = MIN(access_count + 1, 255), last_accessed_at = ? 
            WHERE id = ?
        """, (now, r["id"]))
        
    conn.commit()
    conn.close()
    
    results.sort(key=lambda x: x["strength"], reverse=True)
    return {"results": results[:5]}

@app.post("/conflict/resolve")
async def resolve_conflict(payload: ConflictResolutionPayload):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = time.time()
    
    cursor.execute("SELECT * FROM same_as_proposals WHERE id = ?", (payload.proposal_id,))
    proposal = cursor.fetchone()
    if not proposal:
        conn.close()
        raise HTTPException(status_code=404, detail="Conflict proposal not found.")
        
    if payload.approve:
        # Close old target node's validity window
        cursor.execute("""
            UPDATE episodic_atoms_l1 
            SET valid_time_end = ?, transaction_time_end = ? 
            WHERE id = ?
        """, (now, now, proposal['target_id']))
        
        cursor.execute("UPDATE same_as_proposals SET status = 'approved' WHERE id = ?", (payload.proposal_id,))
    else:
        cursor.execute("UPDATE same_as_proposals SET status = 'rejected' WHERE id = ?", (payload.proposal_id,))
        
    conn.commit()
    conn.close()
    return {"status": "resolved", "action": "merged" if payload.approve else "independent"}

@app.delete("/forget/{atom_id}")
async def verified_forget(atom_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM episodic_atoms_l1 WHERE id = ?", (atom_id,))
    cursor.execute("DELETE FROM virtual_fts_index WHERE atom_id = ?", (atom_id,))
    cursor.execute("DELETE FROM same_as_proposals WHERE source_id = ? OR target_id = ?", (atom_id, atom_id))
    
    conn.commit()
    
    # Post-deletion VMG checks
    cursor.execute("SELECT 1 FROM episodic_atoms_l1 WHERE id = ?", (atom_id,))
    l1_res = cursor.fetchone()
    cursor.execute("SELECT 1 FROM virtual_fts_index WHERE atom_id = ?", (atom_id,))
    fts_res = cursor.fetchone()
    conn.close()
    
    if l1_res or fts_res:
        raise HTTPException(status_code=500, detail="Verified Forgetting failed. Residues detected.")
        
    return {"status": "forgotten", "atom_id": atom_id, "proof_of_erasure": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
