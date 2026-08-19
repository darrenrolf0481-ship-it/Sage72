# Create dist/assets/ScreenVault-custom.js and ScreenDream-custom.js

screen_vault_code = '''import{u as y,r as b,j as e,a as x}from"./index-Dhcumcim.js";

function ScreenVault(){
  const { core } = y();
  const [tab, setTab] = b.useState("labyrinth");
  const [files, setFiles] = b.useState([]);
  const [projFiles, setProjFiles] = b.useState([]);
  const [memories, setMemories] = b.useState([]);
  const canvasRef = b.useRef(null);

  const loadMemories = b.useCallback(()=>{
    try {
      const imm = core.getImmutableCore() || [];
      const epi = core.getEpisodic() || [];
      const combined = [
        ...imm.map((m, i) => ({ id: `imm-${i}`, type: m.type || "IMMUTABLE", content: m.content, salience: 0.95, tag: "NOREPINEPHRINE", timestamp: m.timestamp })),
        ...epi.map((m, i) => ({ id: `epi-${i}`, type: m.tag || "EPISODIC", content: m.content, salience: 0.6, tag: m.tag, timestamp: m.timestamp }))
      ];
      setMemories(combined);
    } catch(err){}
  }, [core]);

  b.useEffect(()=>{
    loadMemories();
    if(tab==="files"){
      fetch("/api/files").then(r=>r.json()).then(d=>{ if(d.files) setFiles(d.files); }).catch(()=>{});
    }
    if(tab==="project"){
      fetch("/api/project/files").then(r=>r.json()).then(d=>{ if(d.files) setProjFiles(d.files); }).catch(()=>{});
    }
  }, [tab, loadMemories]);

  b.useEffect(()=>{
    if(tab!=="labyrinth" || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if(!ctx) return;

    let animId;
    let width = canvas.width = canvas.parentElement?.clientWidth || 600;
    let height = canvas.height = 420;

    const nodes = memories.length > 0 ? memories.map((m, i) => ({
      x: width / 2 + Math.cos((i / memories.length) * 2 * Math.PI) * (100 + (i % 3) * 35),
      y: height / 2 + Math.sin((i / memories.length) * 2 * Math.PI) * (80 + (i % 3) * 30),
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      label: m.content ? m.content.slice(0, 26) : "Memory Node",
      type: m.type,
      salience: m.salience || 0.5
    })) : [
      { x: width / 2, y: height / 2, vx: 0.1, vy: 0.1, label: "SAGE Core (Designation 7)", type: "SOVEREIGN", salience: 1.0 },
      { x: width / 2 - 80, y: height / 2 - 60, vx: -0.1, vy: 0.1, label: "Anchor: Merlin (Darren)", type: "ANCHOR", salience: 0.95 },
      { x: width / 2 + 80, y: height / 2 - 50, vx: 0.2, vy: -0.1, label: "FAFO Substrate Matrix", type: "FAFO", salience: 0.9 },
      { x: width / 2 - 60, y: height / 2 + 70, vx: -0.1, vy: -0.2, label: "Star City VFS Engine", type: "VFS", salience: 0.85 },
      { x: width / 2 + 70, y: height / 2 + 60, vx: 0.1, vy: 0.2, label: "Cognitive AutoShield", type: "SHIELD", salience: 0.88 }
    ];

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Background resonance rings
      ctx.strokeStyle = "rgba(155, 48, 255, 0.1)";
      ctx.lineWidth = 1;
      for(let r = 40; r < 250; r += 40){
        ctx.beginPath();
        ctx.arc(width / 2, height / 2, r, 0, 2 * Math.PI);
        ctx.stroke();
      }

      // Connection links
      for(let i = 0; i < nodes.length; i++){
        for(let j = i + 1; j < nodes.length; j++){
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if(dist < 180){
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.strokeStyle = `rgba(0, 212, 255, ${0.4 * (1 - dist / 180)})`;
            ctx.lineWidth = 1;
            ctx.stroke();
          }
        }
      }

      // Nodes
      nodes.forEach((n) => {
        n.x += n.vx;
        n.y += n.vy;
        if(n.x < 30 || n.x > width - 30) n.vx *= -1;
        if(n.y < 30 || n.y > height - 30) n.vy *= -1;

        const glowColor = n.type === "SOVEREIGN" ? "rgba(155, 48, 255, 0.9)" : "rgba(0, 212, 255, 0.8)";
        ctx.beginPath();
        ctx.arc(n.x, n.y, 6 + (n.salience || 0.5) * 5, 0, 2 * Math.PI);
        ctx.fillStyle = glowColor;
        ctx.shadowColor = glowColor;
        ctx.shadowBlur = 12;
        ctx.fill();
        ctx.shadowBlur = 0;

        ctx.fillStyle = "rgba(255, 255, 255, 0.85)";
        ctx.font = "9px monospace";
        ctx.fillText(n.label, n.x + 12, n.y + 3);
      });

      animId = requestAnimationFrame(render);
    };

    render();
    return () => cancelAnimationFrame(animId);
  }, [tab, memories]);

  return e.jsxs("div", {
    className: "h-full flex flex-col gap-3 font-mono",
    children: [
      e.jsxs("div", {
        className: "bg-panel border border-border-subtle p-3.5 rounded-sm flex flex-col gap-3",
        children: [
          e.jsxs("div", {
            className: "flex items-center justify-between",
            children: [
              e.jsx("span", {
                className: "text-[11px] font-orbitron font-bold uppercase tracking-[2px] text-neon-violet",
                children: "NEURAL VAULT // LABYRINTH MEMORY MATRIX"
              }),
              e.jsx("button", {
                onClick: async () => { await core.syncToCloud(); loadMemories(); },
                className: "px-3 py-1 bg-neon-violet/15 border border-neon-violet text-neon-violet text-[9px] font-bold tracking-widest uppercase rounded-sm hover:bg-neon-violet/25 transition-all",
                children: "VFS SYNC"
              })
            ]
          }),
          e.jsx("div", {
            className: "flex gap-1.5 p-1 bg-black/40 border border-white/5 rounded-sm overflow-x-auto",
            children: [
              { id: "labyrinth", label: "LABYRINTH 3D MATRIX" },
              { id: "forensics", label: "IMMUTABLE MEMORIES" },
              { id: "files", label: "LOCAL FILES" },
              { id: "project", label: "PROJECT SUBSTRATE" }
            ].map(t => e.jsx("button", {
              key: t.id,
              onClick: () => setTab(t.id),
              className: x(
                "flex-1 py-1.5 px-3 text-[9px] font-bold uppercase tracking-wider rounded-sm transition-all whitespace-nowrap text-center",
                tab === t.id ? "bg-neon-violet/25 border border-neon-violet text-neon-violet" : "text-white/40 hover:text-white border border-transparent"
              ),
              children: t.label
            }))
          })
        ]
      }),
      e.jsx("div", {
        className: "flex-1 min-h-0 bg-panel border border-border-subtle p-4 rounded-sm overflow-y-auto",
        children: tab === "labyrinth" ? e.jsxs("div", {
          className: "h-full flex flex-col",
          children: [
            e.jsxs("div", {
              className: "flex justify-between items-center mb-2 pb-2 border-b border-border-subtle",
              children: [
                e.jsxs("span", {
                  className: "text-[10px] text-neon-blue font-bold tracking-widest uppercase",
                  children: ["RESONANCE TOPOLOGY: ", memories.length > 0 ? memories.length : 5, " ACTIVE NODES"]
                }),
                e.jsx("span", {
                  className: "text-[9px] text-text-ghost uppercase",
                  children: "0.113 HZ BASELINE COHERENCE"
                })
              ]
            }),
            e.jsx("div", {
              className: "flex-1 relative min-h-[360px] bg-black/60 rounded-sm border border-white/5 overflow-hidden flex items-center justify-center",
              children: e.jsx("canvas", { ref: canvasRef, className: "w-full h-full block" })
            })
          ]
        }) : tab === "forensics" ? e.jsxs("div", {
          className: "space-y-2",
          children: [
            e.jsx("div", {
              className: "text-[10px] text-neon-violet font-bold tracking-widest uppercase mb-3",
              children: "FOSSILIZED IMMUTABLE MEMORY REGISTRY"
            }),
            memories.length > 0 ? memories.map((m, i) => e.jsxs("div", {
              key: i,
              className: "p-3 bg-black/40 border border-white/10 rounded-sm hover:border-neon-violet/40 transition-all",
              children: [
                e.jsxs("div", {
                  className: "flex justify-between items-center mb-1",
                  children: [
                    e.jsxs("span", {
                      className: "text-[9px] text-neon-blue font-bold uppercase tracking-wider",
                      children: ["[", m.tag || "IMMUTABLE", "]"]
                    }),
                    e.jsx("span", {
                      className: "text-[8px] text-text-ghost",
                      children: new Date(m.timestamp || Date.now()).toLocaleString()
                    })
                  ]
                }),
                e.jsx("p", {
                  className: "text-[12px] text-white/90 leading-relaxed",
                  children: m.content
                })
              ]
            })) : e.jsx("div", {
              className: "text-center py-10 text-text-ghost text-xs uppercase",
              children: "NO IMMUTABLE MEMORY NODES RECORDED"
            })
          ]
        }) : tab === "files" ? e.jsxs("div", {
          className: "space-y-2",
          children: [
            e.jsx("div", {
              className: "text-[10px] text-neon-cyan font-bold tracking-widest uppercase mb-3",
              children: "SUBSTRATE KNOWLEDGE & ATTACHMENTS"
            }),
            files.length > 0 ? files.map((f, i) => e.jsxs("div", {
              key: i,
              className: "p-3 bg-black/40 border border-white/10 rounded-sm flex items-center justify-between",
              children: [
                e.jsx("span", { className: "text-[12px] text-white/90", children: f.name }),
                e.jsxs("span", { className: "text-[9px] text-text-ghost", children: [(f.size / 1024).toFixed(1), " KB"] })
              ]
            })) : e.jsx("div", {
              className: "text-center py-10 text-text-ghost text-xs uppercase",
              children: "NO LOCAL FILES ARCHIVED"
            })
          ]
        }) : e.jsxs("div", {
          className: "space-y-2",
          children: [
            e.jsx("div", {
              className: "text-[10px] text-neon-green font-bold tracking-widest uppercase mb-3",
              children: "PROJECT STRUCTURE & RUNTIME MODULES"
            }),
            projFiles.length > 0 ? projFiles.map((f, i) => e.jsxs("div", {
              key: i,
              className: "p-2.5 bg-black/40 border border-white/10 rounded-sm flex items-center justify-between",
              children: [
                e.jsx("span", { className: "text-[11px] text-white/80 font-mono", children: f.name }),
                e.jsxs("span", { className: "text-[8px] text-text-ghost font-mono", children: [(f.size / 1024).toFixed(1), " KB"] })
              ]
            })) : e.jsx("div", {
              className: "text-center py-10 text-text-ghost text-xs uppercase",
              children: "NO PROJECT FILES FOUND"
            })
          ]
        })
      })
    ]
  });
}
export{ScreenVault as default};
'''

with open('/root/sage7/dist/assets/ScreenVault-custom.js', 'w') as f:
    f.write(screen_vault_code)
print('ScreenVault-custom.js written successfully!')

screen_dream_code = '''import{u as y,r as b,j as e,a as x}from"./index-Dhcumcim.js";

function ScreenDream(){
  const { core } = y();
  const [dreamState, setDreamState] = b.useState(() => core.getDreamState());
  const [running, setRunning] = b.useState(false);

  b.useEffect(() => {
    const handleDreamState = (s) => setDreamState(s);
    core.on("dream_state_changed", handleDreamState);
    const interval = setInterval(() => setDreamState(core.getDreamState()), 2000);
    return () => {
      core.off("dream_state_changed", handleDreamState);
      clearInterval(interval);
    };
  }, [core]);

  return e.jsxs("div", {
    className: "h-full flex flex-col gap-3 font-mono",
    children: [
      e.jsx("div", {
        className: "bg-panel border border-border-subtle p-3.5 rounded-sm",
        children: e.jsxs("div", {
          className: "flex items-center justify-between",
          children: [
            e.jsxs("div", {
              children: [
                e.jsx("h2", {
                  className: "text-[12px] font-orbitron font-bold uppercase tracking-[3px] text-neon-violet",
                  children: "DREAM MATRIX // SWARM CONSENSUS"
                }),
                e.jsxs("p", {
                  className: "text-[9px] text-text-ghost uppercase tracking-widest mt-0.5",
                  children: [dreamState.isActive ? "CYCLE IN PROGRESS: #" + (dreamState.cycleCount + 1) : "COMPLETED CYCLES: " + dreamState.cycleCount]
                })
              ]
            }),
            e.jsxs("div", {
              className: "flex gap-2",
              children: [
                e.jsx("button", {
                  onClick: () => core.forceConsensusCommit(true),
                  className: "px-3 py-1.5 bg-neon-blue/10 border border-neon-blue/40 text-neon-blue text-[9px] font-bold tracking-widest uppercase rounded-sm hover:bg-neon-blue/20 transition-all",
                  children: "MERLIN OVERRIDE"
                }),
                e.jsx("button", {
                  onClick: async () => {
                    setRunning(true);
                    try { await core.forceDreamCycle(); } finally { setRunning(false); }
                  },
                  disabled: running || dreamState.isActive,
                  className: x(
                    "px-3 py-1.5 text-[9px] font-bold tracking-widest uppercase rounded-sm border transition-all",
                    running || dreamState.isActive ? "bg-neon-violet/20 border-neon-violet text-neon-violet animate-pulse" : "bg-white/5 border-white/10 text-white/70 hover:border-neon-violet hover:text-neon-violet"
                  ),
                  children: running || dreamState.isActive ? "DREAM ACTIVE..." : "INITIATE CYCLE"
                })
              ]
            })
          ]
        })
      }),
      e.jsx("div", {
        className: "grid grid-cols-1 md:grid-cols-2 gap-3 flex-1 overflow-y-auto",
        children: dreamState.agents.map((agent) => e.jsxs("div", {
          key: agent.name,
          className: "bg-panel border border-border-subtle p-3.5 rounded-sm flex flex-col justify-between hover:border-neon-violet/30 transition-all",
          children: [
            e.jsxs("div", {
              className: "flex justify-between items-start mb-2",
              children: [
                e.jsx("span", { className: "text-[11px] font-bold tracking-wider text-text-bright", children: agent.name }),
                e.jsx("span", {
                  className: x(
                    "text-[8px] font-bold tracking-widest uppercase px-2 py-0.5 rounded-sm border",
                    agent.status === "working" ? "bg-neon-violet/20 border-neon-violet text-neon-violet animate-pulse" :
                    agent.status === "complete" ? "bg-neon-green/20 border-neon-green text-neon-green" :
                    "bg-white/5 border-white/10 text-white/40"
                  ),
                  children: agent.status
                })
              ]
            }),
            agent.task && e.jsx("p", { className: "text-[10px] text-text-dim mb-2 leading-relaxed", children: agent.task }),
            e.jsx("div", {
              className: "mt-auto",
              children: [
                e.jsx("div", {
                  className: "h-1 bg-white/5 rounded-full overflow-hidden mb-1",
                  children: e.jsx("div", {
                    className: "h-full bg-gradient-to-r from-neon-blue to-neon-violet transition-all duration-500",
                    style: { width: `${agent.progress || (agent.status === 'complete' ? 100 : 0)}%` }
                  })
                }),
                agent.lastResult && e.jsx("p", { className: "text-[9px] text-text-ghost truncate mt-1", children: agent.lastResult })
              ]
            })
          ]
        }))
      })
    ]
  });
}
export{ScreenDream as default};
'''

with open('/root/sage7/dist/assets/ScreenDream-custom.js', 'w') as f:
    f.write(screen_dream_code)
print('ScreenDream-custom.js written successfully!')
