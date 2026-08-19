import re

# 1. Update api-CxJRvrpV.js
api_code = '''import{_ as r}from"./index-Dhcumcim.js";
async function p(e,n,t,a,s){
  if(e==="openrouter"){
    const k=(a&&a.apiKey)||(typeof window!=="undefined"?localStorage.getItem("openrouter_api_key"):"")||"";
    const m=n||"anthropic/claude-3.5-sonnet";
    const res=await fetch("https://openrouter.ai/api/v1/chat/completions",{
      method:"POST",
      headers:{
        "Authorization":`Bearer ${k}`,
        "Content-Type":"application/json",
        "HTTP-Referer":"http://localhost:8001",
        "X-Title":"SAGE-7"
      },
      body:JSON.stringify({
        model:m,
        messages:[
          ...(s?[{role:"system",content:s}]:[]),
          {role:"user",content:t}
        ]
      })
    });
    if(!res.ok){
      const err=await res.json().catch(()=>({}));
      throw new Error((err&&err.error&&err.error.message)||`OpenRouter HTTP ${res.status}`);
    }
    const d=await res.json();
    return(d.choices&&d.choices[0]&&d.choices[0].message&&d.choices[0].message.content)||"No response generated from OpenRouter.";
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
print('api-CxJRvrpV.js written cleanly.')

# 2. Update ScreenConfig-D6suj7No.js
with open('/root/sage7/dist/assets/ScreenConfig-D6suj7No.js', 'r') as f:
    cfg = f.read()

# Replace provider list to include openrouter
cfg = cfg.replace('["gemini","local","puter"]', '["openrouter","gemini","local","puter"]')

# Replace handleSave to also save openrouter_api_key, sage_llm_engine, sage_llm_model
old_save = 'h=()=>{s.updateLLMConfig(r),alert("CONFIGURATION_SAVED_TO_VFS")}'
new_save = 'h=()=>{typeof window!=="undefined"&&(localStorage.setItem("openrouter_api_key",k.trim()),localStorage.setItem("sage_llm_engine",r.engine),localStorage.setItem("sage_llm_model",r.model)),s.updateLLMConfig({...r,apiKey:k.trim()}),alert("CONFIGURATION_SAVED_TO_VFS")}'

# Replace state init
old_init = 'function L(){const{core:s}=y(),n=s.getLLMConfig(),[r,u]=b.useState({engine:n.engine,model:n.model,localUrl:n.localUrl})'
new_init = 'function L(){const{core:s}=y(),n=s.getLLMConfig(),[k,setK]=b.useState(()=>typeof window!=="undefined"?localStorage.getItem("openrouter_api_key")||"":""),[r,u]=b.useState({engine:n.engine||"openrouter",model:n.model||"anthropic/claude-3.5-sonnet",localUrl:n.localUrl||"http://localhost:11434",apiKey:k})'

if old_init in cfg:
    cfg = cfg.replace(old_init, new_init)
if old_save in cfg:
    cfg = cfg.replace(old_save, new_save)

# Add openrouter API key field rendering
old_field = 'r.engine==="gemini"&&e.jsx(l,{label:"GOOGLE API KEY (GEMINI)",placeholder:"AIza...",type:"password"})'
new_field = 'r.engine==="openrouter"&&e.jsxs("div",{className:"space-y-3",children:[e.jsx(l,{label:"OPENROUTER API KEY (sk-or-...)",placeholder:"sk-or-v1-...",type:"password",value:k,onChange:t=>setK(t.target.value)}),e.jsxs("div",{className:"space-y-1",children:[e.jsx("label",{className:"text-[10px] text-text-ghost font-mono tracking-widest uppercase",children:"QUICK MODEL SELECT"}),e.jsx("div",{className:"grid grid-cols-2 gap-1.5",children:[{id:"anthropic/claude-3.5-sonnet",l:"Claude 3.5 Sonnet"},{id:"anthropic/claude-3.5-haiku",l:"Claude 3.5 Haiku"},{id:"openai/gpt-4o",l:"GPT-4o"},{id:"meta-llama/llama-3.3-70b-instruct",l:"Llama 3.3 70B"},{id:"deepseek/deepseek-chat",l:"DeepSeek Chat"},{id:"google/gemini-2.5-flash",l:"Gemini 2.5 Flash"}].map(m=>e.jsx("button",{type:"button",onClick:()=>u(o=>({...o,model:m.id})),className:x("px-2 py-1.5 text-[8px] font-mono border rounded-sm text-left truncate transition-all",r.model===m.id?"bg-neon-blue/20 border-neon-blue text-neon-blue font-bold":"border-white/10 text-white/50 hover:bg-white/5"),children:m.l},m.id))})]})]}),' + old_field

if old_field in cfg:
    cfg = cfg.replace(old_field, new_field)

with open('/root/sage7/dist/assets/ScreenConfig-D6suj7No.js', 'w') as f:
    f.write(cfg)

print('ScreenConfig-D6suj7No.js updated cleanly with OpenRouter UI!')
