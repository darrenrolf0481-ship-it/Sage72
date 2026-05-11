'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-[#000008] text-neon-red font-mono p-4">
      <h2 className="text-2xl mb-4 font-bold tracking-[0.3em]">500 // CRITICAL_SYSTEM_FAILURE</h2>
      <p className="mb-8 opacity-60 text-xs uppercase tracking-widest max-w-md text-center">
        {error.message || 'An unexpected anomaly has occurred in the neural substrate.'}
      </p>
      <button
        onClick={() => reset()}
        className="px-6 py-2 border border-neon-red/40 bg-neon-red/5 hover:bg-neon-red/20 transition-all text-[10px] tracking-widest uppercase"
      >
        ATTEMPT_REBOOT
      </button>
    </div>
  );
}
