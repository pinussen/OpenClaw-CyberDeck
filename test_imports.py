#!/usr/bin/env python3
"""Test imports for web modules (avoiding __init__.py)."""

import sys
import importlib.util
from pathlib import Path

ui_dir = Path(__file__).parent / 'ui'

def load_module(name, rel_path):
    """Load a module directly from file."""
    spec = importlib.util.spec_from_file_location(name, Path(__file__).parent / rel_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

# Load theme first (dependency)
CyberpunkThemeMod = load_module('ui.cyberpunk_theme_web', 'ui/cyberpunk_theme_web.py')
print('✓ cyberpunk_theme_web OK')
print(f'  - Cyan: {CyberpunkThemeMod.COLORS["neon_cyan"]}')

# Load Molty
MoltyMod = load_module('ui.molty_web', 'ui/molty_web.py')
print('✓ molty_web OK')

m = MoltyMod.Molty()
m.set_state(MoltyMod.MoltyState.WORKING)
print(f'  - State: {m.get_state()}')
print(f'  - SVG size: {len(m.render_svg())} chars')

# Load ActivityFeed
ActivityMod = load_module('ui.activity_feed_web', 'ui/activity_feed_web.py')
print('✓ activity_feed_web OK')

af = ActivityMod.ActivityFeed()
af.add_entry('tool', 'Test', 'Test detail')
print(f'  - Entries: {len(af.entries)}')

print('\n✿ All web modules loading correctly!')
