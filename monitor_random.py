#!/usr/bin/env python3
"""Monitor CyberDeck RANDOM button and do something useful."""
import os
import sys
import time
import random
from datetime import datetime

# Add workspace to path
sys.path.insert(0, '/home/bjwl/.openclaw/workspace-dev')

NOTIFICATION_FILE = '/tmp/cyberdeck_notifications.txt'
LAST_CHECK_FILE = '/tmp/cyberdeck_last_check.txt'

# Fun things to do when RANDOM is pressed
RANDOM_ACTIONS = [
    "🎲 RANDOM activated! Checking JIRA queue...",
    "🎲 RANDOM! Here's a fun fact: The first computer bug was an actual moth found in a relay in 1947.",
    "🎲 RANDOM! Did you know? The term 'robot' comes from the Czech word 'robota', meaning forced labor.",
    "🎲 RANDOM! Time for a quick status check...",
    "🎲 RANDOM activated! Spinning the wheel of productivity...",
]

def get_last_check_time():
    """Get the last time we checked the file."""
    try:
        if os.path.exists(LAST_CHECK_FILE):
            with open(LAST_CHECK_FILE, 'r') as f:
                return float(f.read().strip())
    except:
        pass
    return 0

def set_last_check_time(timestamp):
    """Set the last time we checked the file."""
    try:
        with open(LAST_CHECK_FILE, 'w') as f:
            f.write(str(timestamp))
    except:
        pass

def check_notifications():
    """Check for new notifications and do something useful."""
    if not os.path.exists(NOTIFICATION_FILE):
        return []
    
    last_check = get_last_check_time()
    new_notifications = []
    
    try:
        with open(NOTIFICATION_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Parse timestamp from line format: [2026-02-22T09:48:31.612814] Message
                if line.startswith('['):
                    end_bracket = line.find(']')
                    if end_bracket > 0:
                        timestamp_str = line[1:end_bracket]
                        try:
                            from datetime import datetime
                            timestamp = datetime.fromisoformat(timestamp_str).timestamp()
                            if timestamp > last_check:
                                message = line[end_bracket+2:]
                                new_notifications.append((timestamp_str, message))
                        except:
                            pass
    except Exception as e:
        print(f"Error reading notifications: {e}")
    
    # Update last check time
    if new_notifications:
        set_last_check_time(time.time())
    
    return new_notifications

def do_something_useful(message):
    """Do something useful based on the message."""
    print(f"🎯 Doing something useful for: {message}", flush=True)
    
    if "RANDOM" in message:
        # Check JIRA queue first
        try:
            sys.path.insert(0, '/home/bjwl/.openclaw/workspace-dev/projects/nagbot/src')
            from jira_client import get_today_tickets
            
            tickets = get_today_tickets()
            if tickets:
                ticket_list = ", ".join([t['key'] for t in tickets[:5]])
                result = f"📋 Found {len(tickets)} JIRA tickets: {ticket_list}"
                print(f"  → {result}", flush=True)
                
                # Send result back to CyberDeck via notification file
                send_response_to_cyberdeck(result)
                return result
        except Exception as e:
            print(f"  Error checking JIRA: {e}", flush=True)
        
        # If no tickets or error, give a random tip
        tips = [
            "💡 Tip: Take a 5-minute break every 25 minutes (Pomodoro technique).",
            "💡 Tip: Drink water! Hydration improves focus and cognitive function.",
            "💡 Tip: Stand up and stretch - your back will thank you.",
            "💡 Tip: The 2-minute rule: If it takes less than 2 minutes, do it now.",
            "💡 Tip: Close unused browser tabs to reduce mental clutter.",
            "💡 Tip: Natural light boosts productivity - open those blinds!",
            "💡 Tip: Deep breathing for 1 minute reduces stress and improves focus.",
        ]
        result = random.choice(tips)
        print(f"  → {result}", flush=True)
        
        # Send result back to CyberDeck
        send_response_to_cyberdeck(result)
        
        # Also send to Telegram so user sees it immediately
        send_message_to_telegram(f"🎲 RANDOM pressed! {result}")
        
        return result
    
    return "Message received"

def send_response_to_cyberdeck(message):
    """Send a response back to CyberDeck via the notification file."""
    try:
        response_file = '/tmp/cyberdeck_responses.txt'
        timestamp = datetime.now().isoformat()
        
        with open(response_file, 'a') as f:
            f.write(f"[{timestamp}] Alex: {message}\n")
        
        print(f"   📤 Response sent to CyberDeck: {message[:50]}...", flush=True)
    except Exception as e:
        print(f"   Error sending response: {e}", flush=True)

def send_message_to_telegram(message, to="5659520178"):
    """Send a message to Telegram via openclaw CLI."""
    try:
        import subprocess
        result = subprocess.run(
            ['openclaw', 'message', 'send', '-t', to, '-m', message, '--channel', 'telegram'],
            capture_output=True, text=True, timeout=30,
            cwd='/home/bjwl/.openclaw/workspace-dev'
        )
        if result.returncode == 0:
            print(f"   ✅ Message sent to Telegram", flush=True)
            return True
        else:
            print(f"   Error sending to Telegram: {result.stderr}", flush=True)
            return False
    except Exception as e:
        print(f"   Error: {e}", flush=True)
        return False

def main():
    """Main loop to monitor notifications."""
    print("🔍 Monitoring CyberDeck notifications...", flush=True)
    print(f"   Watching: {NOTIFICATION_FILE}", flush=True)
    
    # Process any existing messages immediately
    print("   Checking for existing messages...", flush=True)
    initial_notifications = check_notifications()
    if initial_notifications:
        print(f"   Found {len(initial_notifications)} existing messages to process", flush=True)
        for timestamp, message in initial_notifications:
            print(f"\n📨 [{timestamp}] {message}", flush=True)
            result = do_something_useful(message)
            print(f"   → {result}", flush=True)
    else:
        print("   No existing messages found", flush=True)
    
    print("\n   Starting monitoring loop...", flush=True)
    while True:
        notifications = check_notifications()
        
        for timestamp, message in notifications:
            print(f"\n📨 [{timestamp}] {message}", flush=True)
            result = do_something_useful(message)
            print(f"   → {result}", flush=True)
        
        time.sleep(5)  # Check every 5 seconds

def send_response_to_cyberdeck(message):
    """Send a response back to CyberDeck via the notification file."""
    try:
        response_file = '/tmp/cyberdeck_responses.txt'
        timestamp = datetime.now().isoformat()
        
        with open(response_file, 'a') as f:
            f.write(f"[{timestamp}] Alex: {message}\n")
        
        print(f"   📤 Response sent to CyberDeck: {message[:50]}...", flush=True)
    except Exception as e:
        print(f"   Error sending response to CyberDeck: {e}", flush=True)

def send_message_to_telegram(message, to="5659520178"):
    """Send a message to Telegram via openclaw CLI."""
    try:
        import subprocess
        result = subprocess.run(
            ['openclaw', 'message', 'send', '-t', to, '-m', message, '--channel', 'telegram'],
            capture_output=True, text=True, timeout=30,
            cwd='/home/bjwl/.openclaw/workspace-dev'
        )
        if result.returncode == 0:
            print(f"   ✅ Message sent to Telegram", flush=True)
            return True
        else:
            print(f"   Error sending to Telegram: {result.stderr}", flush=True)
            return False
    except Exception as e:
        print(f"   Error: {e}", flush=True)
        return False

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Stopping monitor")
        sys.exit(0)
