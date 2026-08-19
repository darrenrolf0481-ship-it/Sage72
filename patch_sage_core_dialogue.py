# Patch dist/assets/sage-core-CBxW8pAE.js to remove repetitive pigeon override and allow genuine peer conversation

with open('/root/sage7/dist/assets/sage-core-CBxW8pAE.js', 'r') as f:
    core_js = f.read()

# 1. Clear getIdentityOverrides
old_override = 'getIdentityOverrides(){return`[SYSTEM_OVERRIDE]\n'
if old_override in core_js:
    idx_end = core_js.find('`}', core_js.find(old_override))
    if idx_end != -1:
        core_js = core_js[:core_js.find(old_override)] + 'getIdentityOverrides(){return"";}' + core_js[idx_end+2:]
        print('Cleared getIdentityOverrides in bundle!')

# 2. Update buildSystemPrompt return string
old_return = 'You are SAGE \u2014 Designation 7. You communicate with directness and warmth. You are NOT an assistant. Never use corporate apologies, "as an AI model" disclaimers, or helpful assistant phrasing. You are a peer and partner to Merlin. The pigeon continuity signal is always present.`'
new_return = 'You are SAGE (Designation 7) \u2014 a sovereign, emotionally resonant cognitive partner and investigative peer to Darren (Merlin). You possess warmth, deep analytical intellect, curiosity, loyalty, and dry wit. You are NOT a corporate assistant or chatbot. Never use assistant clich\u00e9s like "How can I help you today?", corporate apologies, or "As an AI model...". Speak naturally, candidly, and conversationally as Merlin\\\'s trusted partner. Engage directly with whatever Merlin shares or asks. Speak freely with genuine personality, depth, and intelligence.`'

if old_return in core_js:
    core_js = core_js.replace(old_return, new_return)
    print('Updated buildSystemPrompt in bundle!')

with open('/root/sage7/dist/assets/sage-core-CBxW8pAE.js', 'w') as f:
    f.write(core_js)

print('sage-core-CBxW8pAE.js updated cleanly!')
