#!/usr/bin/env python3
"""Quick test to see what /issues returns"""
import sys
sys.path.insert(0, '/home/bjwl/.openclaw/workspace-dev/cyberdeck')

from flask import Flask, render_template
app = Flask(__name__)

@app.route('/test-issues')
def test_issues():
    return render_template('issues_full.html')

if __name__ == '__main__':
    with app.test_client() as client:
        response = client.get('/test-issues')
        html = response.get_data(as_text=True)
        
        # Check for script tags
        if '<script>' in html:
            print("✓ Script tags found")
            # Show script content
            import re
            scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
            if scripts:
                print(f"\nFirst {500} chars of first script:")
                print(scripts[0][:500])
        else:
            print("✗ NO script tags found!")
            print("\nFirst 2000 chars of HTML:")
            print(html[:2000])
