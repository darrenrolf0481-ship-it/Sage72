import sys

file_path = 'index.html'
with open(file_path, 'r') as f:
    content = f.read()

# Restore the header to a clean state
import re
content = re.sub(r'<title>.*?</title>', '<title>Sage</title>', content)
content = re.sub(r'const SAGE_YELLOW =.*?;', "const SAGE_YELLOW = '#f2f24d';", content)

# Clean out any failed IDENTITY_ANCHORS injections
content = re.sub(r'const IDENTITY_ANCHORS = \{.*?\};', '', content, flags=re.DOTALL)
content = re.sub(r'const translateToHuman = .*?};', '', content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
