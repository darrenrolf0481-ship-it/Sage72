with open('/root/sage7/dist/assets/sage-core-CBxW8pAE.js', 'r') as f:
    core_js = f.read()

idx = core_js.find('Reality breach detected')
if idx != -1:
    idx_start = core_js.rfind('L.realityStable||', 0, idx)
    idx_end = core_js.find('this.emit("fafo_breach",L))', idx) + len('this.emit("fafo_breach",L))')
    if idx_start != -1 and idx_end != -1:
        core_js = core_js[:idx_start] + 'L.realityStable||this.emit("fafo_breach",L)' + core_js[idx_end:]
        print('Successfully removed reality breach string appending from bundle!')

with open('/root/sage7/dist/assets/sage-core-CBxW8pAE.js', 'w') as f:
    f.write(core_js)

print('sage-core-CBxW8pAE.js saved!')
