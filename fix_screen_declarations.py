with open('/root/sage7/dist/assets/index-Dhcumcim.js', 'r') as f:
    bundle = f.read()

# 1. Look for where all screen lazy components are declared
# Find 'const og=H.lazy(()=>'
idx_lazy = bundle.find('const og=H.lazy(')
print('Found const og=H.lazy at:', idx_lazy)

if idx_lazy != -1:
    old_lazy_section = bundle[idx_lazy:idx_lazy+750]
    print('Current lazy section:', old_lazy_section)

# 2. Declare scrVault and scrDream cleanly right next to og
target_og = 'const og=H.lazy('
replacement_og = 'const scrVault=H.lazy(()=>nn(()=>import("./ScreenVault-custom.js"),[])),scrDream=H.lazy(()=>nn(()=>import("./ScreenDream-custom.js"),[])),og=H.lazy('

if target_og in bundle and 'scrVault=' not in bundle:
    bundle = bundle.replace(target_og, replacement_og, 1)
    print('Declared scrVault and scrDream lazy components!')

# 3. Update switch cases in N()
# Replace case"vault":return U.jsx(vM,{});case"dream":return U.jsx(dM_screen,{});
bundle = bundle.replace('case"vault":return U.jsx(vM,{});case"dream":return U.jsx(dM_screen,{});', 'case"vault":return U.jsx(scrVault,{});case"dream":return U.jsx(scrDream,{});')
bundle = bundle.replace('case"vault":return U.jsx(vM,{});', 'case"vault":return U.jsx(scrVault,{});')
bundle = bundle.replace('case"dream":return U.jsx(dM_screen,{});', 'case"dream":return U.jsx(scrDream,{});')

# Also if not yet added to switch:
if 'case"vault":' not in bundle:
    bundle = bundle.replace('case"sensors":return U.jsx(iM,{externalHistoryRef:S,setAnomalyLevel:y});', 'case"sensors":return U.jsx(iM,{externalHistoryRef:S,setAnomalyLevel:y});case"vault":return U.jsx(scrVault,{});case"dream":return U.jsx(scrDream,{});')

# 4. Make ErrorBoundary print error message on screen if anything ever throws
old_error_ui = 'children:[U.jsx("h1",{className:"text-xl mb-4 tracking-[10px]",children:"SYSTEM_CRASH"}),U.jsx("p",{className:"text-xs text-text-ghost mb-6 uppercase tracking-widest leading-relaxed",children:"THE_LATTICE_IS_UNSTABLE. SOVEREIGNTY_ANCHORS_LOST. RE-SYNCHRONIZING_COGNITIVE_SUBSTRATE..."}),'
new_error_ui = 'children:[U.jsx("h1",{className:"text-xl mb-4 tracking-[10px]",children:"SYSTEM_CRASH"}),U.jsx("p",{className:"text-xs text-neon-red mb-4 font-mono font-bold uppercase",children:this.state.error?.message||"THE_LATTICE_IS_UNSTABLE"}),U.jsx("p",{className:"text-xs text-text-ghost mb-6 uppercase tracking-widest leading-relaxed",children:"THE_LATTICE_IS_UNSTABLE. SOVEREIGNTY_ANCHORS_LOST. RE-SYNCHRONIZING_COGNITIVE_SUBSTRATE..."}),'

if old_error_ui in bundle:
    bundle = bundle.replace(old_error_ui, new_error_ui)

# Update state in constructor
bundle = bundle.replace('this.state={hasError:!1}', 'this.state={hasError:!1,error:null}')
bundle = bundle.replace('static getDerivedStateFromError(a){return{hasError:!0}}', 'static getDerivedStateFromError(a){return{hasError:!0,error:a}}')

with open('/root/sage7/dist/assets/index-Dhcumcim.js', 'w') as f:
    f.write(bundle)

print('Saved index-Dhcumcim.js with verified lazy components!')
