#!/usr/bin/env python3
"""Inbox checker for CyberDeck - checks abc.se and Gmail via IMAP."""

import imaplib
import json
import os
import ssl
from datetime import datetime, timedelta
from email import message_from_bytes
from email.utils import parsedate_tz
from pathlib import Path
from typing import List, Dict, Optional


class InboxChecker:
    """Check email inboxes for unread/important messages."""
    
    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or os.path.expanduser('~/.openclaw-dev/credentials')
        self.abc_config = self._load_config('abc-imap.json')
        self.gmail_config = self._load_config('gmail-imap.json')
    
    def _load_config(self, filename: str) -> Optional[Dict]:
        """Load email config from JSON file."""
        path = Path(self.config_dir) / filename
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return None
    
    def check_abc(self, since_hours: int = 24) -> List[Dict]:
        """Check abc.se inbox for recent unread messages."""
        if not self.abc_config:
            return []
        
        try:
            host = self.abc_config['imap']['host']
            port = self.abc_config['imap']['port']
            username = self.abc_config['username']
            password = self.abc_config['password']
            
            # Connect via SSL
            mail = imaplib.IMAP4_SSL(host, port)
            mail.login(username, password)
            mail.select('INBOX')
            
            # Search for unread messages from last N hours
            since_date = (datetime.now() - timedelta(hours=since_hours)).strftime('%d-%b-%Y')
            
            # Just count UNSEEN (much faster than fetching all)
            result, data = mail.search(None, 'UNSEEN')
            
            total_unseen = len(data[0].split()) if data[0] else 0
            
            # Get latest 5 messages only (using BODY.PEEK for speed)
            messages = []
            if total_unseen > 0:
                # Get last 5 message IDs only
                msg_ids = data[0].split()[-5:]
                for msg_id in msg_ids:
                    result, msg_data = mail.fetch(msg_id, '(BODY.PEEK[HEADER.FIELDS (From Subject Date)])')
                    if msg_data and msg_data[0]:
                        msg = message_from_bytes(msg_data[0][1])
                        # Handle encoding issues
                        subject = msg.get('Subject', '(No subject)')
                        if isinstance(subject, bytes):
                            subject = subject.decode('utf-8', 'replace')
                        sender = msg.get('From', 'Unknown')
                        if isinstance(sender, bytes):
                            sender = sender.decode('utf-8', 'replace')
                        messages.append({
                            'sender': sender,
                            'subject': subject,
                            'date': msg.get('Date', '')
                        })
            
            mail.close()
            mail.logout()
            return messages
            
        except Exception as e:
            print(f'[InboxChecker] abc.se error: {e}')
            return []
    
    def check_gmail(self, since_hours: int = 24) -> List[Dict]:
        """Check Gmail inbox for recent unread messages."""
        if not self.gmail_config:
            return []
        
        try:
            host = self.gmail_config.get('imap', {}).get('host', 'imap.gmail.com')
            port = self.gmail_config.get('imap', {}).get('port', 993)
            username = self.gmail_config.get('username')
            password = self.gmail_config.get('password')
            
            if not username or not password:
                return []
            
            mail = imaplib.IMAP4_SSL(host, port)
            mail.login(username, password)
            mail.select('INBOX')
            
            # Fast count + peek latest
            result, data = mail.search(None, 'UNSEEN')
            total_unseen = len(data[0].split()) if data[0] else 0
            
            messages = []
            if total_unseen > 0:
                msg_ids = data[0].split()[-5:]
                for msg_id in msg_ids:
                    result, msg_data = mail.fetch(msg_id, '(BODY.PEEK[HEADER.FIELDS (From Subject Date)])')
                    if msg_data and msg_data[0]:
                        msg = message_from_bytes(msg_data[0][1])
                        # Handle encoding issues
                        subject = msg.get('Subject', '(No subject)')
                        if isinstance(subject, bytes):
                            subject = subject.decode('utf-8', 'replace')
                        sender = msg.get('From', 'Unknown')
                        if isinstance(sender, bytes):
                            sender = sender.decode('utf-8', 'replace')
                        messages.append({
                            'sender': sender,
                            'subject': subject,
                            'date': msg.get('Date', '')
                        })
            
            mail.close()
            mail.logout()
            return messages
            
        except Exception as e:
            print(f'[InboxChecker] Gmail error: {e}')
            return []
    
    def check_all(self, since_hours: int = 24) -> Dict:
        """Check all inboxes and return summary."""
        abc = self.check_abc(since_hours)
        gmail = self.check_gmail(since_hours)
        
        # Get actual unseen counts (fast)
        abc_total = self._get_unseen_count_abc() if self.abc_config else 0
        gmail_total = self._get_unseen_count_gmail() if self.gmail_config else 0
        
        return {
            'total': abc_total + gmail_total,
            'abc': {'count': abc_total, 'messages': abc},
            'gmail': {'count': gmail_total, 'messages': gmail},
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_unseen_count_abc(self) -> int:
        """Quickly get unread count only."""
        try:
            host = self.abc_config['imap']['host']
            port = self.abc_config['imap']['port']
            mail = imaplib.IMAP4_SSL(host, port)
            mail.login(self.abc_config['username'], self.abc_config['password'])
            mail.select('INBOX')
            result, data = mail.search(None, 'UNSEEN')
            mail.close()
            mail.logout()
            return len(data[0].split()) if data[0] else 0
        except:
            return 0
    
    def _get_unseen_count_gmail(self) -> int:
        """Quickly get unread count only."""
        try:
            cfg = self.gmail_config
            if not cfg or not cfg.get('username') or not cfg.get('password'):
                return 0
            mail = imaplib.IMAP4_SSL(cfg.get('imap', {}).get('host', 'imap.gmail.com'), cfg.get('imap', {}).get('port', 993))
            mail.login(cfg['username'], cfg['password'])
            mail.select('INBOX')
            result, data = mail.search(None, 'UNSEEN')
            mail.close()
            mail.logout()
            return len(data[0].split()) if data[0] else 0
        except:
            return 0
    
    def get_summary_text(self, since_hours: int = 24) -> str:
        """Get human-readable summary of unread messages."""
        result = self.check_all(since_hours)
        
        if result['total'] == 0:
            return "No unread messages"
        
        lines = [f"📧 {result['total']} unread messages"]
        
        if result['abc']['count'] > 0:
            lines.append(f"  abc.se: {result['abc']['count']}")
        if result['gmail']['count'] > 0:
            lines.append(f"  Gmail: {result['gmail']['count']}")
        
        return "\n".join(lines)


if __name__ == '__main__':
    checker = InboxChecker()
    result = checker.check_all(since_hours=24)
    print(json.dumps(result, indent=2))
    print("\nSummary:")
    print(checker.get_summary_text())
