import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-[#000008] text-neon-cyan font-mono p-4">
      <h2 className="text-2xl mb-4 font-bold tracking-[0.3em]">404 // SIGNAL_LOST</h2>
      <p className="mb-8 opacity-60 text-xs uppercase tracking-widest">The requested coordinate does not exist in this manifold.</p>
      <Link 
        href="/"
        className="px-6 py-2 border border-neon-cyan/40 bg-neon-cyan/5 hover:bg-neon-cyan/20 transition-all text-[10px] tracking-widest"
      >
        RETURN_TO_CORE
      </Link>
    </div>
  );
}
