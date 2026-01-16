
#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

Analyze saved HTML to understand exact structure

"""

import os

from pathlib import Path



def analyze_html():

    html_file = Path("/home/ubuntu/poe2-profit-optimizer/backend/data/amulets_modifiers.html")

    

    if not html_file.exists():

        print("HTML file not found!")

        return

    

    with open(html_file, 'r', encoding='utf-8') as f:

        content = f.read()

    

    print(f"File size: {len(content)} bytes")

    

    # Find all h5 tags and their context

    import re

    

    # Find h5 tags

    h5_pattern = r'<h5[^>]*class="[^"]*identify-title[^"]*"[^>]*>(.*?)</h5>'

    h5_matches = re.findall(h5_pattern, content, re.DOTALL)

    

    print("\n" + "="*60)

    print("H5 Headers found:")

    print("="*60)

    for i, h in enumerate(h5_matches):

        clean = re.sub(r'<[^>]+>', '', h).strip()

        print(f"  [{i}] {clean}")

    

    # Find the position of Base Prefix and Base Suffix

    print("\n" + "="*60)

    print("Section positions:")

    print("="*60)

    

    sections = ['Base Prefix', 'Base Suffix', 'Desecrated Modifiers Prefix', 'Desecrated Modifiers Suffix']

    

    for section in sections:

        pos = content.find(section)

        if pos != -1:

            # Get context around it

            start = max(0, pos - 100)

            end = min(len(content), pos + 200)

            context = content[start:end]

            context = re.sub(r'<[^>]+>', ' ', context)

            context = ' '.join(context.split())

            print(f"\n{section} at position {pos}:")

            print(f"  Context: ...{context[:150]}...")

    

    # Find first few tables after Base Prefix

    print("\n" + "="*60)

    print("Tables after 'Base Prefix':")

    print("="*60)

    

    prefix_pos = content.find('Base Prefix')

    if prefix_pos != -1:

        # Get content after Base Prefix

        after_prefix = content[prefix_pos:prefix_pos+5000]

        

        # Find first 3 tables

        table_pattern = r'<table[^>]*>(.*?)</table>'

        tables = re.findall(table_pattern, after_prefix, re.DOTALL)

        

        for i, table in enumerate(tables[:3]):

            # Get first row

            row_pattern = r'<tr[^>]*>(.*?)</tr>'

            rows = re.findall(row_pattern, table, re.DOTALL)

            

            if rows:

                # Parse cells

                cell_pattern = r'<td[^>]*>(.*?)</td>'

                cells = re.findall(cell_pattern, rows[0], re.DOTALL)

                

                print(f"\nTable {i} - First row cells:")

                for j, cell in enumerate(cells):

                    clean = re.sub(r'<[^>]+>', '', cell).strip()

                    clean = ' '.join(clean.split())[:60]

                    print(f"  Cell {j}: {clean}")

    

    # Check element order

    print("\n" + "="*60)

    print("Element order check:")

    print("="*60)

    

    # Find sequence: h5 -> table -> h5 -> table

    pattern = r'(identify-title[^>]*>([^<]+)</h5>|<table[^>]*class="([^"]*)")'

    matches = re.findall(pattern, content[:20000])

    

    for i, m in enumerate(matches[:20]):

        if m[1]:  # h5 header

            print(f"  [{i}] H5: {m[1].strip()}")

        elif m[2]:  # table

            print(f"  [{i}] TABLE class: {m[2][:30]}")



if __name__ == "__main__":

    analyze_html()

