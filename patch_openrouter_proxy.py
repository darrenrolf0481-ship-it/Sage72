# 1. Update dist/assets/sage-core-CBxW8pAE.js
with open('/root/sage7/dist/assets/sage-core-CBxW8pAE.js', 'r') as f:
    core_js = f.read()

start_marker = 'if(s==="openrouter"){'
end_marker = 'if(s==="local"){'

idx1 = core_js.find(start_marker)
idx2 = core_js.find(end_marker)

print('Found start:', idx1, 'Found end:', idx2)
if idx1 != -1 and idx2 != -1:
    openrouter_proxy = '''if(s==="openrouter"){const key=k||(typeof window!=="undefined"?localStorage.getItem("openrouter_api_key"):"")||"";const m=l||"anthropic/claude-3.5-sonnet";const res=await fetch("/api/openrouter/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({apiKey:key,model:m,systemPrompt:e||"",prompt:t})});if(!res.ok){throw new Error(`Substrate backend HTTP ${res.status}`);}const d=await res.json();if(d.status==="error"||!d.reply){throw new Error(d.reply||d.message||"OpenRouter request failed.");}return d.reply;}'''
    core_js = core_js[:idx1] + openrouter_proxy + core_js[idx2:]
    with open('/root/sage7/dist/assets/sage-core-CBxW8pAE.js', 'w') as f:
        f.write(core_js)
    print('Successfully patched sage-core-CBxW8pAE.js with backend proxy!')

# 2. Update dist/assets/api-CxJRvrpV.js
api_code = '''import{_ as r}from"./index-Dhcumcim.js";
async function p(e,n,t,a,s){
  if(e==="openrouter"){
    const k=(a&&a.apiKey)||(typeof window!=="undefined"?localStorage.getItem("openrouter_api_key"):"")||"";
    const m=n||"anthropic/claude-3.5-sonnet";
    const res=await fetch("/api/openrouter/chat",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({apiKey:k,model:m,systemPrompt:s||"",prompt:t})
    });
    if(!res.ok) throw new Error(`Substrate backend HTTP ${res.status}`);
    const d=await res.json();
    if(d.status==="error"||!d.reply) throw new Error(d.reply||d.message||"OpenRouter request failed.");
    return d.reply;
  }
  if(e==="google"){
    const{GoogleGenerativeAI:s_ai}=await r(async()=>{const{GoogleGenerativeAI:o}=await import("./index-wf8GzEhy.js");return{GoogleGenerativeAI:o}},[]);
    return(await(await new s_ai("").getGenerativeModel({model:n||"gemini-3-flash-preview"}).generateContent({contents:[{role:"user",parts:[{text:t}]}]})).response).text()||"";
  }
  return`[${e.toUpperCase()} SIMULATION] I processed your request: "${t.substring(0,30)}..."`;
}
export{p as generateResponse};
'''
with open('/root/sage7/dist/assets/api-CxJRvrpV.js', 'w') as f:
    f.write(api_code)
print('Successfully patched api-CxJRvrpV.js!')
