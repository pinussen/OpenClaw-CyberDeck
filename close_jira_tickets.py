#!/usr/bin/env python3
"""Close JIRA tickets that have been completed."""
import sys
import subprocess
from datetime import datetime

# Add nagbot src to path
sys.path.insert(0, '/home/bjwl/.openclaw/workspace-dev/projects/nagbot/src')
from jira_client import mark_ticket_done, add_comment

def close_tickets(ticket_ids, comment_text="Completed by CyberDeck automation"):
    """Close the specified JIRA tickets."""
    results = []
    for ticket_id in ticket_ids:
        print(f"Closing {ticket_id}...")
        
        # Add comment first
        if add_comment(ticket_id, comment_text):
            print(f"  ✓ Comment added")
        else:
            print(f"  ✗ Failed to add comment")
        
        # Then mark as done
        if mark_ticket_done(ticket_id):
            print(f"  ✓ Marked as done")
            results.append((ticket_id, True))
        else:
            print(f"  ✗ Failed to mark as done")
            results.append((ticket_id, False))
    
    return results

if __name__ == '__main__':
    # Close all CyberDeck tickets
    tickets = ['GOR-47', 'GOR-48', 'GOR-49', 'GOR-50', 'GOR-51', 'GOR-52']
    results = close_tickets(tickets, "Completed by CyberDeck web interface MVP")
    
    success_count = sum(1 for _, success in results if success)
    print(f"\nClosed {success_count}/{len(tickets)} tickets")
    sys.exit(0 if success_count == len(tickets) else 1)
