#!/usr/bin/env python3
"""
Freedom Blades Design System Token Validation Script
Scans design-prototype/css/*.css and design-prototype/*.html for var(--token) usages
and verifies that every referenced token is defined in tokens.css or another CSS file.
Exits nonzero if any referenced token is undefined.
"""

import os
import re
import sys

def get_prototype_files():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    css_dir = os.path.join(base_dir, "css")
    files = []
    
    # HTML files
    for f in os.listdir(base_dir):
        if f.endswith(".html"):
            files.append(os.path.join(base_dir, f))
            
    # CSS files
    if os.path.exists(css_dir):
        for f in os.listdir(css_dir):
            if f.endswith(".css"):
                files.append(os.path.join(css_dir, f))
                
    return base_dir, files

def scan_tokens():
    base_dir, files = get_prototype_files()
    defined_tokens = set()
    token_references = {}  # token_name -> list of (file_rel, line_num)

    def_regex = re.compile(r'(--fb-[\w-]+)\s*:')
    ref_regex = re.compile(r'var\(\s*(--fb-[\w-]+)\s*[\),]')

    for filepath in sorted(files):
        rel_path = os.path.relpath(filepath, base_dir)
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Check definitions
                for match in def_regex.finditer(line):
                    defined_tokens.add(match.group(1))
                    
                # Check references
                for match in ref_regex.finditer(line):
                    tok = match.group(1)
                    if tok not in token_references:
                        token_references[tok] = []
                    token_references[tok].append((rel_path, line_num))

    undefined_tokens = {}
    for tok, locs in token_references.items():
        if tok not in defined_tokens:
            undefined_tokens[tok] = locs

    print("=" * 80)
    print("FREEDOM BLADES PLATFORM — CSS TOKEN CONTRACT CHECK")
    print("=" * 80)
    print(f"Total Defined Custom Properties : {len(defined_tokens)}")
    print(f"Total Unique Referenced Tokens  : {len(token_references)}")
    print(f"Undefined Referenced Tokens     : {len(undefined_tokens)}")
    print("-" * 80)

    if undefined_tokens:
        print("ERROR: Found undefined CSS token references:")
        for tok in sorted(undefined_tokens.keys()):
            print(f"\n  Undefined Token: {tok}")
            for rel_path, line_num in undefined_tokens[tok]:
                print(f"    - {rel_path}:{line_num}")
        print("=" * 80)
        return False
    else:
        print("SUCCESS: All referenced CSS tokens are defined. Zero undefined references.")
        print("=" * 80)
        return True

if __name__ == "__main__":
    success = scan_tokens()
    sys.exit(0 if success else 1)
