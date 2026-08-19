with open('/root/sage7/dist/assets/index-Dhcumcim.js', 'r') as f:
    bundle = f.read()

# 1. Remove duplicate definition at line 0 if present
if bundle.startswith('const nn=(i,d)=>typeof i==="function"?i():i;\n'):
    bundle = bundle[len('const nn=(i,d)=>typeof i==="function"?i():i;\n'):]
    print('Removed duplicate line 0 declaration.')

# 2. Find and replace the fragile modulepreload nn function
# Find 'I1="modulepreload",tS=function(i){return"/"+i},Bp={},nn=function(a,s,o){'
target = 'I1="modulepreload",tS=function(i){return"/"+i},Bp={},nn=function(a,s,o){'
idx = bundle.find(target)
if idx != -1:
    end_marker = 'cg=H.createContext(null);'
    idx_end = bundle.find(end_marker, idx)
    if idx_end != -1:
        # Replacement for the entire modulepreload block
        clean_preload = 'I1="modulepreload",tS=function(i){return"/"+i},Bp={},nn=function(a,s,o){return typeof a==="function"?a():import(a);},'
        bundle = bundle[:idx] + clean_preload + bundle[idx_end:]
        print('Replaced fragile modulepreload function with safe direct import handler!')

with open('/root/sage7/dist/assets/index-Dhcumcim.js', 'w') as f:
    f.write(bundle)

print('Updated index-Dhcumcim.js successfully!')
