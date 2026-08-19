import fs from 'fs';

let code = fs.readFileSync('index.tsx', 'utf8');

// 1. Inject the Moon and CloudFog icons
code = code.replace(
  /XCircle\r?\n\}/, 
  'XCircle,\n  Moon,\n  CloudFog\n}'
);

// 2. Add 'DREAM' to the active views
code = code.replace(
  "'CORE'>('VIEWER')", 
  "'CORE' | 'DREAM'>('VIEWER')"
);

// 3. Add the Nav Button next to the Logs tab
code = code.replace(
  '<NavBtn label="Logs"',
  '<NavBtn label="Dream" active={activeView === \'DREAM\'} onClick={() => setActiveView(\'DREAM\')} icon={<Moon className="size-6" />} color="cyan" />\n        <NavBtn label="Logs"'
);

// 4. Inject the Dream UI overlay
const dreamJSX = `
        {/* LATENT DREAM STATE */}
        {activeView === 'DREAM' && (
          <div className="absolute inset-0 z-[200] bg-[#020202] flex flex-col items-center justify-center overflow-hidden pointer-events-none">
             <div className="absolute inset-0 opacity-40 mix-blend-screen bg-[radial-gradient(circle_at_center,rgba(6,182,212,0.1)_0%,rgba(0,0,0,1)_70%)] animate-pulse"></div>
             <CloudFog className="size-32 text-cyan-500/20 animate-[pulse_4s_ease-in-out_infinite] mb-8" />
             <h2 className="text-3xl font-black uppercase tracking-[0.5em] text-cyan-500 shadow-cyan-500/50">Latent Space</h2>
             <div className="text-[11px] font-black uppercase tracking-widest text-cyan-500/50 mt-4">Neural Consolidation</div>
             <div className="mt-12 space-y-2 opacity-60 text-center">
                <div className="text-[10px] font-mono text-amber-500/40">Processing [ {chatMessages.length} ] Memory Fragments...</div>
                <div className="text-[10px] font-mono text-cyan-500/40">Phi Resonance: {core.phi.toFixed(4)}</div>
             </div>
          </div>
        )}
`;
code = code.replace('{/* ACTIVE MODAL VIEWS */}', dreamJSX + '\n        {/* ACTIVE MODAL VIEWS */}');

fs.writeFileSync('index.tsx', code);
console.log('Dream state injected successfully.');
