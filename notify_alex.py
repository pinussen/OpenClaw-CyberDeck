#!/usr/bin/env python3
"""Send notification to Alex via Telegram using openclaw CLI."""
import sys
import subprocess
import os

def send_message(message, to="5659520178"):
    """Send a message via openclaw CLI."""
    try:
        # Set up environment
        env = os.environ.copy()
        env['OPENCLAW_WORKSPACE'] = '/home/bjwl/.openclaw/workspace-dev'
        
        # Use openclaw CLI to send message
        result = subprocess.run(
            ['openclaw', 'message', 'send', '-t', to, '-m', message, '--channel', 'telegram'],
            capture_output=True, text=True, timeout=30,
            env=env,
            cwd='/home/bjwl/.openclaw/workspace-dev'
        )
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        print(f"returncode: {result.returncode}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("Timeout - command took too long")
        return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    if len(sys.argv) > 1:
        message = sys.argv[1]
    else:
        message = "🎲 RANDOM button pressed on CyberDeck!"
    
    success = send_message(message)
    sys.exit(0 if success else 1)
