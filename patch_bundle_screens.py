import os, re

# 1. Read index-Dhcumcim.js
with open('/root/sage7/dist/assets/index-Dhcumcim.js', 'r') as f:
    bundle = f.read()

# 2. Add ScreenVault and ScreenDream to SCREENS list (ag)
old_screens = '{id:"command",label:"COMMAND",icon:Mo,section:"SCREENS"},{id:"sensors",label:"SENSOR ARRAY",icon:av,section:"SCREENS",badge:7},'
new_screens = '{id:"command",label:"COMMAND",icon:Mo,section:"SCREENS"},{id:"sensors",label:"SENSOR ARRAY",icon:av,section:"SCREENS",badge:7},{id:"vault",label:"NEURAL VAULT & LABYRINTH",icon:Mo,section:"SCREENS"},{id:"dream",label:"DREAM MATRIX",icon:Mo,section:"SCREENS"},'

if old_screens in bundle:
    bundle = bundle.replace(old_screens, new_screens)
    print('Updated Sidebar SCREENS list in bundle!')

# 3. Add ScreenVault and ScreenDream to Footer (ug)
old_footer = '{id:"sensors",label:"SENS",icon:av},'
new_footer = '{id:"sensors",label:"SENS",icon:av},{id:"vault",label:"VAULT",icon:Mo},{id:"dream",label:"DREAM",icon:Mo},'

if old_footer in bundle:
    bundle = bundle.replace(old_footer, new_footer)
    print('Updated Footer SCREENS list in bundle!')

# 4. Add ScreenVault and ScreenDream lazy components and switch cases in N()
# Let's see how og, iM, aM, etc. are imported in index-Dhcumcim.js
# const og=H.lazy(()=>r(async()=>{const{default:i}=await import("./ScreenCommand-DZM3VyT1.js");return{default:i}},__vite__mapDeps([6,0,1])));
old_switch = 'case"sensors":return U.jsx(iM,{externalHistoryRef:S,setAnomalyLevel:y});'
new_switch = 'case"sensors":return U.jsx(iM,{externalHistoryRef:S,setAnomalyLevel:y});case"vault":return U.jsx(vM,{});case"dream":return U.jsx(dM_screen,{});'

# Add definitions for vM (ScreenVault) and dM_screen (ScreenDream)
# Let's find where og is defined
old_lazy = 'const og=H.lazy(()=>r(async()=>{const{default:i}=await import("./ScreenCommand-DZM3VyT1.js");'
new_lazy = 'const vM=H.lazy(()=>r(async()=>{const{default:i}=await import("./ScreenVault-custom.js");return{default:i}},[]));const dM_screen=H.lazy(()=>r(async()=>{const{default:i}=await import("./ScreenDream-custom.js");return{default:i}},[]));const og=H.lazy(()=>r(async()=>{const{default:i}=await import("./ScreenCommand-DZM3VyT1.js");'

if old_switch in bundle:
    bundle = bundle.replace(old_switch, new_switch)
    print('Updated switch cases in renderScreen!')

if old_lazy in bundle:
    bundle = bundle.replace(old_lazy, new_lazy)
    print('Added lazy component declarations in bundle!')

with open('/root/sage7/dist/assets/index-Dhcumcim.js', 'w') as f:
    f.write(bundle)

print('index-Dhcumcim.js updated cleanly!')
