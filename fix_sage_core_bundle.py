with open('/root/sage7/dist/assets/sage-core-CBxW8pAE.js', 'r') as f:
    core_js = f.read()

start_marker = 'if(s==="openrouter"){'
end_marker = 'if(s==="local"){'

idx1 = core_js.find(start_marker)
idx2 = core_js.find(end_marker)

print('Found start:', idx1, 'Found end:', idx2)
if idx1 != -1 and idx2 != -1:
    openrouter_inline = '''if(s==="openrouter"){const key=k||(typeof window!=="undefined"?localStorage.getItem("openrouter_api_key"):"")||"";const m=l||"anthropic/claude-3.5-sonnet";const res=await fetch("https://openrouter.ai/api/v1/chat/completions",{method:"POST",headers:{"Authorization":`Bearer ${key}`,"Content-Type":"application/json","HTTP-Referer":"http://localhost:8001","X-Title":"SAGE-7"},body:JSON.stringify({model:m,messages:[...(e?[{role:"system",content:e}]:[]),{role:"user",content:t}]})});if(!res.ok){const err=await res.json().catch(()=>({}));throw new Error((err&&err.error&&err.error.message)||`OpenRouter HTTP ${res.status}`);}const d=await res.json();return(d.choices&&d.choices[0]&&d.choices[0].message&&d.choices[0].message.content)||"No response generated from OpenRouter.";}'''
    core_js = core_js[:idx1] + openrouter_inline + core_js[idx2:]
    with open('/root/sage7/dist/assets/sage-core-CBxW8pAE.js', 'w') as f:
        f.write(core_js)
    print('Successfully patched sage-core-CBxW8pAE.js with direct OpenRouter fetch!')
