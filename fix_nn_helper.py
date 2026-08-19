with open('/root/sage7/dist/assets/index-Dhcumcim.js', 'r') as f:
    bundle = f.read()

# Add definition of nn at the top of index-Dhcumcim.js
preload_helper = 'const nn=(i,d)=>typeof i==="function"?i():i;'

if 'const nn=' not in bundle and 'var nn=' not in bundle and 'function nn(' not in bundle:
    bundle = preload_helper + '\n' + bundle
    print('Added preload helper nn to index-Dhcumcim.js!')

with open('/root/sage7/dist/assets/index-Dhcumcim.js', 'w') as f:
    f.write(bundle)

print('Saved index-Dhcumcim.js!')
