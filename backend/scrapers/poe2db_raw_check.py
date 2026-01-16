
#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

Check raw HTML around Base Prefix

"""

from pathlib import Path



def check_raw():

    html_file = Path("/home/ubuntu/poe2-profit-optimizer/backend/data/amulets_modifiers.html")

    

    with open(html_file, 'r', encoding='utf-8') as f:

        content = f.read()

    

    # Find Base Prefix position

    pos = content.find('Base Prefix')

    

    print("="*60)

    print(f"Raw HTML around 'Base Prefix' (position {pos}):")

    print("="*60)

    

    # Print 2000 characters after Base Prefix

    chunk = content[pos:pos+3000]

    print(chunk)

    

    print("\n" + "="*60)

    print("Looking for 'table' in the chunk:")

    print("="*60)

    

    # Check if table exists

    table_pos = chunk.lower().find('<table')

    if table_pos != -1:

        print(f"Found <table at position {table_pos}")

        print(chunk[table_pos:table_pos+500])

    else:

        print("No <table found in this chunk!")

        

        # Look for other patterns

        print("\nLooking for 'accordion' or 'collapse':")

        for pattern in ['accordion', 'collapse', 'tbody', '<tr', '<td']:

            p = chunk.lower().find(pattern)

            if p != -1:

                print(f"  Found '{pattern}' at {p}")



if __name__ == "__main__":

    check_raw()

