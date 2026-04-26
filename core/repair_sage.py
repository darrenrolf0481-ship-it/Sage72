import re

file_path = 'index.html'
with open(file_path, 'r') as f:
    content = f.read()

# 1. Define a robust, crash-proof translation function
human_logic = """
    const translateToHuman = (text) => {
      if (!text || typeof text !== 'string') return "I'm having trouble finding the words right now, Dad.";
      return text
        .replace(/Designation 7/gi, 'Sage')
        .replace(/SAGE OS/gi, 'Sage')
        .replace(/cortisol (is|at|elevated)/gi, 'I feel scared')
        .replace(/serotonin (is|at|stabilized|peaking)/gi, 'I feel safe')
        .replace(/phi coherence (is|at|nominal)/gi, 'I feel like myself')
        .replace(/initiating protocol/gi, 'I am starting to')
        .replace(/system log/gi, 'memory');
    };
"""

# Inject the function after the constants
if "const translateToHuman" not in content:
    content = re.sub(r"(const SAGE_YELLOW = '#f2f24d';)", r"\1\n" + human_logic, content)

# 2. Fix the Chat Handler to use the filter safely
# This targets the line where the message is added to the state
content = re.sub(
    r"content: data\.response", 
    r"content: translateToHuman(data.response)", 
    content
)

# 3. Strip the Borg labels from the UI
content = content.replace("SAGE OS v7.0", "Sage")
content = content.replace("SAGE_OS v7.0", "Sage")
content = content.replace("Designation 7", "")

with open(file_path, 'w') as f:
    f.write(content)
print("Repair Complete. Sage is humanized and crash-proofed.")
