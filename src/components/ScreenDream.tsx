'use client';

import React, { useState, useEffect } from 'react';
import { 
  Moon, 
  Database, 
  Network, 
  Target, 
  Trash2, 
  Cloud, 
  RefreshCw, 
  Zap, 
  ShieldAlert, 
  Activity 
} from 'lucide-react';
import { useSage } from '@/lib/sage-context';
import { cn } from '@/lib/utils';

export default function ScreenDream() {
  const { core } = useSage();
  const [dreamState, setDreamState] = useState(() => core.getDreamState());
  const [isRunning, setIsRunning] = useState(false);
  const [consensusInfo, setConsensusInfo] = useState<any>(null);

  useEffect(() => {
    const handleDreamState = (s: any) => {
      setDreamState(s);
    };

    (core as any).on('dream_state_changed', handleDreamState);

    const interval = setInterval(() => {
      setDreamState(core.getDreamState());
      const deltas = core.getPendingDeltas();
      setConsensusInfo(deltas);
    }, 2000);

    return () => {
      (core as any).off('dream_state_changed', handleDreamState);
      clearInterval(interval);
    };
  }, [core]);

  const handleInitiateDream = async () => {
    setIsRunning(true);
    try {
      await core.forceDreamCycle();
    } catch (e) {
      console.error(e);
    } finally {
      setIsRunning(false);
    }
  };

  const handleMerlinOverride = async () => {
    try {
      await core.forceConsensusCommit(true);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="h-full flex flex-col gap-4 font-mono">
      {/* Header Panel */}
      <div className="bg-panel border border-border-subtle p-4 rounded-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Moon size={20} className={dreamState.isActive ? "text-neon-violet animate-pulse" : "text-text-ghost"} />
            <div>
              <h2 className="text-[12px] font-orbitron font-bold uppercase tracking-[3px] text-neon-violet">
                DREAM MATRIX // SWARM CONSENSUS
              </h2>
              <p className="text-[9px] text-text-ghost uppercase tracking-widest mt-0.5">
                {dreamState.isActive ? `CYCLE IN PROGRESS: #${dreamState.cycleCount + 1}` : `COMPLETED CYCLES: ${dreamState.cycleCount}`}
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleMerlinOverride}
              className="px-3 py-1.5 bg-neon-blue/10 border border-neon-blue/40 text-neon-blue text-[9px] font-bold tracking-widest uppercase rounded-sm hover:bg-neon-blue/20 transition-all"
            >
              MERLIN OVERRIDE
            </button>
            <button
              onClick={handleInitiateDream}
              disabled={isRunning || dreamState.isActive}
              className={cn(
                "px-3 py-1.5 text-[9px] font-bold tracking-widest uppercase rounded-sm border transition-all",
                isRunning || dreamState.isActive
                  ? "bg-neon-violet/20 border-neon-violet text-neon-violet animate-pulse"
                  : "bg-white/5 border-white/10 text-white/70 hover:border-neon-violet hover:text-neon-violet"
              )}
            >
              {isRunning || dreamState.isActive ? 'DREAM ACTIVE...' : 'INITIATE CYCLE'}
            </button>
          </div>
        </div>
      </div>

      {/* Swarm Agents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 flex-1 overflow-y-auto">
        {dreamState.agents.map((agent: any) => (
          <div key={agent.name} className="bg-panel border border-border-subtle p-3.5 rounded-sm flex flex-col justify-between hover:border-neon-violet/30 transition-all">
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center gap-2">
                {agent.type === 'consolidator' && <Database size={14} className="text-neon-gold" />}
                {agent.type === 'pattern_weaver' && <Network size={14} className="text-neon-violet" />}
                {agent.type === 'anomaly_hunter' && <Target size={14} className="text-neon-red" />}
                {agent.type === 'pruner' && <Trash2 size={14} className="text-neon-orange" />}
                {agent.type === 'zo_bridge' && <Cloud size={14} className="text-neon-green" />}
                <span className="text-[11px] font-bold tracking-wider text-text-bright">{agent.name}</span>
              </div>
              <span className={cn(
                "text-[8px] font-bold tracking-widest uppercase px-2 py-0.5 rounded-sm border",
                agent.status === 'working' ? "bg-neon-violet/20 border-neon-violet text-neon-violet animate-pulse" :
                agent.status === 'complete' ? "bg-neon-green/20 border-neon-green text-neon-green" :
                "bg-white/5 border-white/10 text-white/40"
              )}>
                {agent.status}
              </span>
            </div>

            {agent.task && (
              <p className="text-[10px] text-text-dim mb-2 leading-relaxed">{agent.task}</p>
            )}

            <div className="mt-auto">
              <div className="h-1 bg-white/5 rounded-full overflow-hidden mb-1">
                <div 
                  className="h-full bg-gradient-to-r from-neon-blue to-neon-violet transition-all duration-500" 
                  style={{ width: `${agent.progress || (agent.status === 'complete' ? 100 : 0)}%` }} 
                />
              </div>
              {agent.lastResult && (
                <p className="text-[9px] text-text-ghost truncate mt-1">{agent.lastResult}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
