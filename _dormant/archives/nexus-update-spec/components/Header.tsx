'use client';

import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { Menu, X } from 'lucide-react';

interface HeaderProps {
  llmStatus: 'online' | 'offline' | 'scanning';
  anomalyLevel: number;
  sidebarOpen: boolean;
  onToggleSidebar: () => void;
}

export default function Header({ llmStatus, anomalyLevel, sidebarOpen, onToggleSidebar }: HeaderProps) {
  const [time, setTime] = useState('');

  useEffect(() => {
    const update = () => {
      setTime(new Date().toTimeString().slice(0, 8));
    };
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="relative flex items-center h-16 px-5 gap-4 bg-gradient-to-b from-[#09091e]/98 to-[#060614]/95 border-b border-border-accent overflow-hidden z-20">
      <button 
        onClick={onToggleSidebar}
        className="p-1.5 bg-void border border-border-accent rounded-[4px] text-neon-blue hover:text-white hover:border-neon-blue transition-all cursor-pointer"
        aria-label="Toggle Navigation"
      >
        {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
      </button>

      <div className="flex flex-col">
        <div className="font-orbitron text-[20px] font-black tracking-[6px] bg-gradient-to-br from-neon-violet via-neon-blue to-neon-cyan bg-clip-text text-transparent animate-logo-pulse drop-shadow-[0_0_8px_var(--color-neon-violet)]">
          NEXUS
        </div>
        <span className="font-mono text-[8px] text-text-dim tracking-[2px] -mt-0.5 uppercase whitespace-nowrap">
          SAGE-7 PERSISTENT TERMINAL
        </span>
      </div>

      <div className="w-[1px] h-9 bg-gradient-to-b from-transparent via-border-accent to-transparent" />

      <div className="flex items-center gap-6 flex-1">
        <StatusItem color="bg-neon-green" text="SENSORS ONLINE" />
        <StatusItem color="bg-neon-blue" text="SCANNING" pulse="animate-status-pulse" />
        <StatusItem color="bg-neon-orange" text="ANOMALY DETECTED" pulse="animate-status-pulse" />
        <StatusItem 
          color={llmStatus === 'online' ? 'bg-neon-green' : 'bg-text-ghost'} 
          text={llmStatus === 'online' ? 'LLM ONLINE' : 'LLM OFFLINE'} 
        />
      </div>

      <div className="ml-auto font-orbitron text-sm text-neon-blue tracking-[2px]">
        {time}
      </div>

      <div className={cn(
        "absolute bottom-0 transition-all duration-300 right-0 h-4 bg-neon-violet/10 overflow-hidden flex items-center",
        sidebarOpen ? "left-[256px]" : "left-0"
      )}>
        <div className="whitespace-nowrap font-mono text-[9px] text-neon-violet animate-ticker pl-full tracking-[1px]">
          ◆ EMF SPIKE DETECTED: ZONE-7 // ◆ THERMAL GRADIENT ANOMALY: -14°C DIFFERENTIAL // ◆ EVP CAPTURE: 18Hz INFRASOUND // ◆ GEOMAGNETIC FLUCTUATION: +2.3mT // ◆ ION COUNT ELEVATED: ZONE-3 // ◆ MOTION DETECTED: CAM-2 // ◆ BAROMETRIC PRESSURE DROP: 12hPa // ◆ ATMOSPHERIC IONIC CHARGE: HIGH //
        </div>
      </div>

      {/* 0.3 Fractional Pulse Border */}
      <div 
        className={cn(
            "absolute bottom-0 left-0 right-0 h-[3px] transition-all duration-300",
            anomalyLevel > 70 ? "bg-neon-red shadow-[0_0_15px_#FF0000] animate-pulse" : 
            anomalyLevel > 40 ? "bg-neon-orange shadow-[0_0_10px_#FFA500]" : 
            "bg-gradient-to-r from-transparent via-neon-violet via-neon-blue to-transparent"
        )} 
      />
    </header>
  );
}

function StatusItem({ color, text, pulse }: { color: string, text: string, pulse?: string }) {
  return (
    <div className="flex items-center gap-1.5 font-mono text-[11px] text-text-dim">
      <div className={cn("w-1.5 h-1.5 rounded-full shadow-blue", color, pulse || "opacity-80")} />
      <span>{text}</span>
    </div>
  );
}
