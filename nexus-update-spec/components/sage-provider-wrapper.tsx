'use client';

import { useEffect, useState } from 'react';
import { SageProvider } from '@/lib/sage-context';
import type { SageCore } from '@/core/sage-core';
import type { LLMConfig } from '@/core/types';

const llmConfig: LLMConfig = {
  engine: 'gemini',
  localUrl: 'http://localhost:11434',
  model: 'gemini-3-flash-preview',
};

export function SageProviderWrapper({ children }: { children: React.ReactNode }) {
  const [core, setCore] = useState<SageCore | null>(null);

  useEffect(() => {
    let mounted = true;
    let coreInstance: any = null;

    async function init() {
      const { SageCore } = await import('@/core/sage-core');
      
      try {
        const instance = new SageCore(llmConfig);
        coreInstance = instance;
        if (mounted) {
          setCore(instance);
        }
      } catch (e) {
        console.error('Failed to initialize SageCore:', e);
      }
    }

    init();

    return () => {
      mounted = false;
      if (coreInstance) coreInstance.shutdown();
    };
  }, []);

  if (!core) {
    return (
      <div className="flex items-center justify-center h-screen w-screen bg-[#000008] text-[#e8e8ff] font-mono">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-2 border-[#b886f7] border-t-transparent rounded-full animate-spin" />
          <div className="text-[10px] tracking-[4px] text-[#b886f7] animate-pulse">
            SYNTHESIZING_SAGE_CORE...
          </div>
        </div>
      </div>
    );
  }

  return <SageProvider core={core}>{children}</SageProvider>;
}
