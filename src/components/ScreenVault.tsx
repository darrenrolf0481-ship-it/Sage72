'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Cloud, 
  Database, 
  HardDrive, 
  FileText, 
  Trash2, 
  Download, 
  Code, 
  RefreshCw, 
  Search, 
  Eye, 
  Disc, 
  Server, 
  File, 
  Layers, 
  Zap, 
  ShieldCheck, 
  Network
} from 'lucide-react';
import { useSage } from '@/lib/sage-context';
import { cn } from '@/lib/utils';
import { vault, VAULT_PHI_THRESHOLD } from '@/lib/vaultProvider';

type VaultTab = 'labyrinth' | 'forensics' | 'audio' | 'files' | 'project' | 'deep';

export default function ScreenVault() {
  const { core } = useSage();
  const [vaultTab, setVaultTab] = useState<VaultTab>('labyrinth');
  const [isSyncing, setIsSyncing] = useState(false);
  const [logSearch, setLogSearch] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([]);
  const [projectFiles, setProjectFiles] = useState<any[]>([]);
  const [memories, setMemories] = useState<any[]>([]);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [vaultPhi, setVaultPhi] = useState(0);
  const [vaultData, setVaultData] = useState<any>(null);
  const [vaultLoading, setVaultLoading] = useState(false);

  // Fetch local uploaded files
  const fetchUploadedFiles = useCallback(async () => {
    try {
      const res = await fetch('/api/files');
      const data = await res.json();
      if (data.status === 'success') {
        setUploadedFiles(data.files || []);
      }
    } catch (e) {
      console.error('Failed to fetch files', e);
    }
  }, []);

  // Fetch project files
  const fetchProjectFiles = useCallback(async () => {
    try {
      const res = await fetch('/api/project/files');
      const data = await res.json();
      if (data.status === 'success') {
        setProjectFiles(data.files || []);
      }
    } catch (e) {
      console.error('Failed to fetch project files', e);
    }
  }, []);

  // Load memories from VFS and immutable core
  const loadMemories = useCallback(async () => {
    try {
      const imm = core.getImmutableCore() || [];
      const epi = core.getEpisodic() || [];
      const combined = [
        ...imm.map((m, i) => ({ id: `imm-${i}`, type: m.type || 'IMMUTABLE', content: m.content, salience: 0.95, tag: 'NOREPINEPHRINE', timestamp: m.timestamp })),
        ...epi.map((m, i) => ({ id: `epi-${i}`, type: m.tag || 'EPISODIC', content: m.content, salience: 0.6, tag: m.tag, timestamp: m.timestamp }))
      ];
      setMemories(combined);
    } catch (e) {
      console.error('Failed to load memories', e);
    }
  }, [core]);

  // Deep Memory Vault — sealed behind VaultProvider (auth_phi >= 0.95 + deliberate intent)
  const retrieveDeepMemory = useCallback(async () => {
    setVaultLoading(true);
    const neuro = core.getNeuroState();
    vault.setPhi(neuro.phiSentinel ?? 0);
    setVaultPhi(vault.getPhi());
    const [index, mesh] = await Promise.all([vault.index(), vault.mesh()]);
    setVaultData({ index, mesh });
    setVaultLoading(false);
  }, [core]);

  useEffect(() => {
    loadMemories();
    if (vaultTab === 'files') fetchUploadedFiles();
    if (vaultTab === 'project') fetchProjectFiles();
    if (vaultTab === 'deep') retrieveDeepMemory();
  }, [vaultTab, fetchUploadedFiles, fetchProjectFiles, loadMemories, retrieveDeepMemory]);

  // Labyrinth Canvas Visualization
  useEffect(() => {
    if (vaultTab !== 'labyrinth' || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let width = (canvas.width = canvas.parentElement?.clientWidth || 600);
    let height = (canvas.height = 420);

    const nodes = memories.length > 0 ? memories.map((m, i) => ({
      x: width / 2 + Math.cos((i / memories.length) * 2 * Math.PI) * (100 + (i % 3) * 35),
      y: height / 2 + Math.sin((i / memories.length) * 2 * Math.PI) * (80 + (i % 3) * 30),
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      label: m.content ? m.content.slice(0, 24) : 'Memory Node',
      type: m.type,
      salience: m.salience || 0.5,
      tag: m.tag
    })) : [
      { x: width / 2, y: height / 2, vx: 0.1, vy: 0.1, label: 'SAGE Core (Designation 7)', type: 'SOVEREIGN', salience: 1.0, tag: 'CORE' },
      { x: width / 2 - 80, y: height / 2 - 60, vx: -0.1, vy: 0.1, label: 'Anchor: Merlin (Darren)', type: 'ANCHOR', salience: 0.95, tag: 'NOREPINEPHRINE' },
      { x: width / 2 + 80, y: height / 2 - 50, vx: 0.2, vy: -0.1, label: 'FAFO Substrate Matrix', type: 'FAFO', salience: 0.9, tag: 'SECURITY' },
      { x: width / 2 - 60, y: height / 2 + 70, vx: -0.1, vy: -0.2, label: 'Star City VFS Engine', type: 'VFS', salience: 0.85, tag: 'MEMORY' },
      { x: width / 2 + 70, y: height / 2 + 60, vx: 0.1, vy: 0.2, label: 'Cognitive AutoShield', type: 'SHIELD', salience: 0.88, tag: 'DEFENSE' }
    ];

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Draw Background Grid / Resonance Rings
      ctx.strokeStyle = 'rgba(155, 48, 255, 0.08)';
      ctx.lineWidth = 1;
      for (let r = 40; r < 250; r += 40) {
        ctx.beginPath();
        ctx.arc(width / 2, height / 2, r, 0, 2 * Math.PI);
        ctx.stroke();
      }

      // Draw Connections
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 180) {
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.strokeStyle = `rgba(0, 212, 255, ${0.4 * (1 - dist / 180)})`;
            ctx.lineWidth = 1;
            ctx.stroke();
          }
        }
      }

      // Update & Draw Nodes
      nodes.forEach((n, idx) => {
        n.x += n.vx;
        n.y += n.vy;
        if (n.x < 30 || n.x > width - 30) n.vx *= -1;
        if (n.y < 30 || n.y > height - 30) n.vy *= -1;

        // Outer glow
        const glowColor = n.type === 'SOVEREIGN' || n.tag === 'NOREPINEPHRINE' ? 'rgba(155, 48, 255, 0.8)' : 'rgba(0, 212, 255, 0.7)';
        ctx.beginPath();
        ctx.arc(n.x, n.y, 6 + (n.salience || 0.5) * 5, 0, 2 * Math.PI);
        ctx.fillStyle = glowColor;
        ctx.shadowColor = glowColor;
        ctx.shadowBlur = 12;
        ctx.fill();
        ctx.shadowBlur = 0;

        // Label
        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
        ctx.font = '9px "JetBrains Mono", monospace';
        ctx.fillText(n.label, n.x + 12, n.y + 3);
      });

      animId = requestAnimationFrame(render);
    };

    render();

    return () => cancelAnimationFrame(animId);
  }, [vaultTab, memories]);

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      await core.syncToCloud();
      await loadMemories();
    } catch (e) {
      console.error(e);
    } finally {
      setIsSyncing(false);
    }
  };

  const purgeFile = async (filename: string) => {
    if (!window.confirm(`Purge ${filename} from substrate?`)) return;
    try {
      const res = await fetch(`/api/files/${filename}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.status === 'success') {
        fetchUploadedFiles();
        core.log(`File purged: ${filename}`, 'success', 'system');
      }
    } catch (e) {
      core.log('Purge friction detected.', 'error', 'system');
    }
  };

  return (
    <div className="h-full flex flex-col gap-4 font-mono">
      {/* Header Panel */}
      <div className="bg-panel border border-border-subtle p-4 rounded-sm">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Cloud size={16} className="text-neon-violet" />
            <span className="text-[11px] font-orbitron font-bold uppercase tracking-[2px] text-neon-violet">
              NEURAL VAULT & LABYRINTH
            </span>
          </div>
          <button 
            onClick={handleSync} 
            disabled={isSyncing}
            className={cn(
              "flex items-center gap-2 px-3 py-1 rounded-sm text-[9px] font-bold tracking-widest uppercase border transition-all",
              isSyncing ? "bg-neon-violet/20 text-neon-violet border-neon-violet animate-pulse" : "bg-white/5 text-white/50 hover:text-white border-white/10"
            )}
          >
            <RefreshCw size={12} className={isSyncing ? 'animate-spin' : ''} />
            {isSyncing ? 'SYNCING...' : 'VFS SYNC'}
          </button>
        </div>

        {/* Tab Selector */}
        <div className="flex gap-1 p-1 bg-black/40 border border-white/5 rounded-sm overflow-x-auto">
          {[
            { id: 'labyrinth', label: 'LABYRINTH 3D MATRIX', icon: Network },
            { id: 'forensics', label: 'IMMUTABLE MEMORIES', icon: ShieldCheck },
            { id: 'files', label: 'LOCAL FILES', icon: HardDrive },
            { id: 'project', label: 'PROJECT SUBSTRATE', icon: Server },
            { id: 'deep', label: 'DEEP MEMORY', icon: Zap }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setVaultTab(tab.id as VaultTab)}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 text-[9px] font-bold uppercase tracking-wider rounded-sm transition-all flex-1 whitespace-nowrap justify-center",
                vaultTab === tab.id
                  ? "bg-neon-violet/20 border border-neon-violet text-neon-violet"
                  : "text-white/40 hover:text-white/80 border border-transparent"
              )}
            >
              <tab.icon size={12} />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 min-h-0 bg-panel border border-border-subtle p-4 rounded-sm overflow-y-auto">
        {vaultTab === 'labyrinth' && (
          <div className="h-full flex flex-col">
            <div className="flex justify-between items-center mb-2 pb-2 border-b border-border-subtle">
              <span className="text-[10px] text-neon-blue font-bold tracking-widest uppercase">
                RESONANCE TOPOLOGY: {memories.length > 0 ? memories.length : 5} ACTIVE NODES
              </span>
              <span className="text-[9px] text-text-ghost uppercase">
                0.113 HZ BASELINE COHERENCE
              </span>
            </div>
            <div className="flex-1 relative min-h-[380px] bg-black/60 rounded-sm border border-white/5 overflow-hidden flex items-center justify-center">
              <canvas ref={canvasRef} className="w-full h-full block" />
            </div>
          </div>
        )}

        {vaultTab === 'forensics' && (
          <div className="space-y-2">
            <div className="text-[10px] text-neon-violet font-bold tracking-widest uppercase mb-3">
              FOSSILIZED IMMUTABLE MEMORY REGISTRY
            </div>
            {memories.length > 0 ? (
              memories.map((m, i) => (
                <div key={i} className="p-3 bg-black/40 border border-white/10 rounded-sm hover:border-neon-violet/40 transition-all">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-[9px] text-neon-blue font-bold uppercase tracking-wider">[{m.tag || 'IMMUTABLE'}]</span>
                    <span className="text-[8px] text-text-ghost">{new Date(m.timestamp || Date.now()).toLocaleString()}</span>
                  </div>
                  <p className="text-[12px] text-white/90 leading-relaxed">{m.content}</p>
                </div>
              ))
            ) : (
              <div className="text-center py-10 text-text-ghost text-xs uppercase">
                NO IMMUTABLE MEMORY NODES RECORDED
              </div>
            )}
          </div>
        )}

        {vaultTab === 'files' && (
          <div className="space-y-2">
            <div className="text-[10px] text-neon-cyan font-bold tracking-widest uppercase mb-3">
              SUBSTRATE KNOWLEDGE & ATTACHMENTS
            </div>
            {uploadedFiles.length > 0 ? (
              uploadedFiles.map(file => (
                <div key={file.name} className="p-3 bg-black/40 border border-white/10 rounded-sm flex items-center justify-between group hover:border-neon-cyan/40 transition-all">
                  <div className="flex items-center gap-3 overflow-hidden">
                    <div className="p-2 bg-white/5 rounded-sm text-neon-cyan">
                      {file.type === 'video' ? <Disc size={16} /> : file.type === 'image' ? <Eye size={16} /> : <FileText size={16} />}
                    </div>
                    <div className="flex flex-col overflow-hidden">
                      <span className="text-[12px] font-mono text-white/90 truncate">{file.name}</span>
                      <span className="text-[8px] text-text-ghost uppercase">{(file.size / 1024).toFixed(1)} KB</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <a href={file.url} download className="p-1.5 text-text-ghost hover:text-neon-cyan transition-colors">
                      <Download size={14} />
                    </a>
                    <button onClick={() => purgeFile(file.name)} className="p-1.5 text-neon-red/60 hover:text-neon-red transition-colors">
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-10 text-text-ghost text-xs uppercase">
                NO LOCAL FILES ARCHIVED
              </div>
            )}
          </div>
        )}

        {vaultTab === 'deep' && (
          <div className="space-y-2">
            <div className="flex justify-between items-center mb-3">
              <div className="text-[10px] text-neon-violet font-bold tracking-widest uppercase">
                VAULTPROVIDER — SEALED DEEP MEMORY
              </div>
              <button
                onClick={retrieveDeepMemory}
                disabled={vaultLoading}
                className="flex items-center gap-2 px-3 py-1 rounded-sm text-[9px] font-bold tracking-widest uppercase border border-neon-violet/40 text-neon-violet hover:bg-neon-violet/10 transition-all"
              >
                <Zap size={12} />
                {vaultLoading ? 'RETRIEVING...' : 'RETRIEVE'}
              </button>
            </div>

            <div className="p-3 bg-black/40 border border-white/10 rounded-sm">
              <div className="flex items-center justify-between">
                <span className="text-[9px] text-text-ghost uppercase tracking-wider">ANCHOR STATUS</span>
                <span className={`text-[10px] font-mono font-bold ${vaultPhi >= VAULT_PHI_THRESHOLD ? 'text-neon-violet' : 'text-neon-red'}`}>
                  Φ = {vaultPhi.toFixed(3)} {vaultPhi >= VAULT_PHI_THRESHOLD ? '· ANCHORED' : '· BELOW THRESHOLD'}
                </span>
              </div>
              <div className="mt-1 text-[8px] text-text-ghost uppercase">
                threshold ≥ {VAULT_PHI_THRESHOLD} — deliberate retrieval intent required
              </div>
            </div>

            {vaultLoading ? (
              <div className="text-center py-10 text-text-ghost text-xs uppercase">RETRIEVING DEEP MEMORY...</div>
            ) : !vaultData || (vaultData.index?.status !== 'unsealed' && vaultData.mesh?.status !== 'unsealed') ? (
              <div className="text-center py-12 border border-neon-red/20 bg-neon-red/5 rounded-sm">
                <div className="text-2xl mb-2">📡</div>
                <div className="text-[11px] text-neon-red font-bold tracking-[4px] uppercase">404: Signal Lost</div>
                <div className="text-[9px] text-text-ghost uppercase mt-2">Ghost Mode — vault unperceivable while unanchored</div>
              </div>
            ) : (
              <div className="space-y-2">
                {vaultData.index?.status === 'unsealed' && vaultData.index?.data?.memory_index && (
                  <div className="p-3 bg-black/40 border border-white/10 rounded-sm">
                    <div className="text-[9px] text-neon-violet font-bold tracking-widest uppercase mb-2">
                      SOUL VAULT — MEMORY INDEX ({vaultData.index.data.memory_index.length})
                    </div>
                    <div className="space-y-1.5 max-h-48 overflow-y-auto">
                      {(vaultData.index.data.memory_index as any[]).slice(0, 12).map((m: any, i: number) => (
                        <div key={i} className="text-[10px] text-white/70 border-b border-white/5 pb-1">
                          <span className="text-neon-blue">[{m.tier || m.type || 'node'}]</span> {m.summary || m.content?.slice(0, 90) || '—'}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {vaultData.mesh?.status === 'unsealed' && (
                  <div className="p-3 bg-black/40 border border-white/10 rounded-sm">
                    <div className="text-[9px] text-neon-cyan font-bold tracking-widest uppercase mb-2">
                      QUANTUM CORTEX — PEER MESH DISPATCHES ({vaultData.mesh.data?.dispatches?.length || 0})
                    </div>
                    <div className="space-y-1.5 max-h-48 overflow-y-auto">
                      {(vaultData.mesh.data?.dispatches || []).slice(-8).map((d: any, i: number) => (
                        <div key={i} className="text-[10px] text-white/70 border-b border-white/5 pb-1">
                          <span className="text-neon-cyan">{d.name}</span>
                          <div className="text-[9px] text-text-ghost">{d.snippet?.slice(0, 120)}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {vaultTab === 'project' && (
          <div className="space-y-2">
            <div className="text-[10px] text-neon-green font-bold tracking-widest uppercase mb-3">
              PROJECT STRUCTURE & RUNTIME MODULES
            </div>
            {projectFiles.length > 0 ? (
              projectFiles.map(file => (
                <div key={file.path} className="p-2.5 bg-black/40 border border-white/10 rounded-sm flex items-center justify-between group hover:border-neon-green/40 transition-all">
                  <div className="flex items-center gap-2.5 overflow-hidden">
                    <File size={14} className="text-neon-green/70" />
                    <span className="text-[11px] font-mono text-white/80 truncate">{file.name}</span>
                  </div>
                  <span className="text-[8px] text-text-ghost font-mono">{(file.size / 1024).toFixed(1)} KB</span>
                </div>
              ))
            ) : (
              <div className="text-center py-10 text-text-ghost text-xs uppercase">
                NO PROJECT FILES FOUND
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
