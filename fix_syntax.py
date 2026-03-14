#!/usr/bin/env python3
with open('/home/bjwl/.openclaw/workspace-dev/cyberdeck/templates/cyberdeck.html', 'r') as f:
    lines = f.readlines()

# Fix line 357 (0-indexed: 356)
old_line = lines[356]
print('Before:', repr(old_line))

# Replace the problematic pattern
new_line = old_line.replace('"\x27\x3e\x27 +', '\x22\x3e\x27 +')
lines[356] = new_line
print('After:', repr(new_line))

with open('/home/bjwl/.openclaw/workspace-dev/cyberdeck/templates/cyberdeck.html', 'w') as f:
    f.writelines(lines)
print('Done!')
