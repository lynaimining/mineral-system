#!/usr/bin/env python3
"""Render HTML to PNG using Playwright"""
import sys
from playwright.sync_api import sync_playwright

def render_html_to_png(html_path, output_path, width=720, height=405):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': width, 'height': height})
        page.goto(f'file://{html_path}')
        page.screenshot(path=output_path, full_page=False)
        browser.close()
        print(f"Rendered {html_path} to {output_path}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: render_html.py <html_file> <output_png>")
        sys.exit(1)

    html_file = sys.argv[1]
    output_file = sys.argv[2]
    render_html_to_png(html_file, output_file)
