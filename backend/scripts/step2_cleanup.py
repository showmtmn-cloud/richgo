
#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

PoE2 Profit Optimizer - Step 2-1: Cleanup & Data Quality Check

- Set current league to Fate of Vaal only

- Check modifier data quality

"""

import json

import sqlite3

from pathlib import Path



BASE_DIR = Path("/home/ubuntu/poe2-profit-optimizer/backend")

DB_PATH = BASE_DIR / "poe2_profit_optimizer.db"

MODIFIER_JSON = BASE_DIR / "data" / "modifier_data.json"



def setup_current_league():

    """Set up Fate of Vaal as the only active league"""

    print("\n" + "="*60)

    print("[1] Setting up Current League: Fate of Vaal")

    print("="*60)

    

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    

    # Clear existing leagues

    cursor.execute("DELETE FROM leagues")

    

    # Insert only Fate of Vaal

    cursor.execute("""

        INSERT INTO leagues (name, is_active, realm, type, created_at)

        VALUES ('Fate of Vaal', 1, 'PC', 'SC', datetime('now'))

    """)

    

    conn.commit()

    

    # Verify

    cursor.execute("SELECT * FROM leagues")

    row = cursor.fetchone()

    print(f"  League ID: {row[0]}")

    print(f"  Name: {row[1]}")

    print(f"  Active: {row[2]}")

    print(f"  Realm: {row[3]}")

    print(f"  Type: {row[4]}")

    

    conn.close()

    print("\n[OK] League set to Fate of Vaal only")



def check_modifier_json_quality():

    """Check raw JSON data quality"""

    print("\n" + "="*60)

    print("[2] Checking modifier_data.json Quality")

    print("="*60)

    

    with open(MODIFIER_JSON, 'r') as f:

        data = json.load(f)

    

    print(f"\nTotal item types: {len(data)}")

    

    # Check sample data

    sample_types = ['Body_Armours_int', 'Amulets', 'One_Hand_Swords']

    

    for item_type in sample_types:

        if item_type not in data:

            print(f"\n[SKIP] {item_type} not found")

            continue

            

        print(f"\n--- {item_type} ---")

        item_data = data[item_type]

        

        print(f"  Prefixes: {len(item_data.get('prefix', []))}")

        print(f"  Suffixes: {len(item_data.get('suffix', []))}")

        

        # Show first 3 prefixes

        print("\n  Sample Prefixes:")

        for mod in item_data.get('prefix', [])[:3]:

            name = mod.get('name', 'N/A')

            weight = mod.get('weight', 0)

            ilvl = mod.get('ilvl', 0)

            tier = mod.get('tier', 0)

            tags = mod.get('tags', [])

            print(f"    - [{weight:5}] T{tier:2} iLvl{ilvl:2} | {name}")

            print(f"              Tags: {tags}")

        

        # Show first 3 suffixes

        print("\n  Sample Suffixes:")

        for mod in item_data.get('suffix', [])[:3]:

            name = mod.get('name', 'N/A')

            weight = mod.get('weight', 0)

            ilvl = mod.get('ilvl', 0)

            tier = mod.get('tier', 0)

            tags = mod.get('tags', [])

            print(f"    - [{weight:5}] T{tier:2} iLvl{ilvl:2} | {name}")

            print(f"              Tags: {tags}")



def check_db_modifier_quality():

    """Check DB modifier data quality"""

    print("\n" + "="*60)

    print("[3] Checking DB Modifier Quality")

    print("="*60)

    

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    

    # Check for truncated names

    cursor.execute("""

        SELECT name, mod_type, COUNT(*) as cnt

        FROM modifiers

        WHERE name LIKE '#%' OR name LIKE '% #%' OR LENGTH(name) < 15

        GROUP BY name

        ORDER BY cnt DESC

        LIMIT 20

    """)

    

    print("\nPotentially truncated mod names:")

    for row in cursor.fetchall():

        print(f"  [{row[1]:6}] {row[0][:50]:<50} (count: {row[2]})")

    

    # Check good names

    cursor.execute("""

        SELECT name, mod_type

        FROM modifiers

        WHERE LENGTH(name) > 30

        LIMIT 10

    """)

    

    print("\nLonger mod names (likely complete):")

    for row in cursor.fetchall():

        print(f"  [{row[1]:6}] {row[0]}")

    

    conn.close()



def show_original_scrape_sample():

    """Show raw scrape data to understand format"""

    print("\n" + "="*60)

    print("[4] Raw JSON Sample (Body_Armours_int)")

    print("="*60)

    

    with open(MODIFIER_JSON, 'r') as f:

        data = json.load(f)

    

    if 'Body_Armours_int' in data:

        item = data['Body_Armours_int']

        print("\nFull prefix data (first 5):")

        for i, mod in enumerate(item.get('prefix', [])[:5]):

            print(f"\n  [{i+1}] Full mod object:")

            print(f"      {json.dumps(mod, indent=8)}")



def main():

    setup_current_league()

    check_modifier_json_quality()

    check_db_modifier_quality()

    show_original_scrape_sample()

    

    print("\n" + "="*60)

    print("[SUMMARY]")

    print("="*60)

    print("1. League set to: Fate of Vaal (SC)")

    print("2. Check the mod data above")

    print("   - If names are truncated, we need to re-scrape")

    print("   - If names are complete, the import script needs fixing")



if __name__ == "__main__":

    main()

