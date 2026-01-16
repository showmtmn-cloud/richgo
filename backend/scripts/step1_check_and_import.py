
#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

PoE2 Profit Optimizer - Step 1: API Check + Modifier Data Import

"""

import json

import sqlite3

import requests

import time

from pathlib import Path

from datetime import datetime



# ============================================================

# Settings

# ============================================================

BASE_DIR = Path("/home/ubuntu/poe2-profit-optimizer/backend")

DB_PATH = BASE_DIR / "poe2_profit_optimizer.db"

MODIFIER_JSON = BASE_DIR / "data" / "modifier_data.json"



# ============================================================

# Part 1: API Status Check

# ============================================================

def check_api_status():

    """Check Trade API status"""

    print("\n" + "="*60)

    print("[Part 1] Trade API Status Check")

    print("="*60)

    

    headers = {

        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",

        "Accept": "application/json",

    }

    

    try:

        print("\nTesting Leagues API...")

        response = requests.get(

            "https://www.pathofexile.com/api/trade2/data/leagues",

            headers=headers, timeout=15

        )

        

        if response.status_code == 200:

            data = response.json()

            print(f"  [OK] Success! Leagues: {len(data.get('result', []))}")

            return True

        elif response.status_code == 403:

            print(f"  [BLOCKED] HTTP 403 - Cloudflare")

            return False

        elif response.status_code == 429:

            print(f"  [RATE LIMITED] HTTP 429")

            return False

        else:

            print(f"  [WARNING] HTTP {response.status_code}")

            return False

            

    except Exception as e:

        print(f"  [ERROR] {e}")

        return False



# ============================================================

# Part 2: Modifier Data Import

# ============================================================

def create_modifier_tables(conn):

    """Create modifier tables"""

    cursor = conn.cursor()

    

    # Drop existing tables

    cursor.execute("DROP TABLE IF EXISTS modifier_tiers")

    cursor.execute("DROP TABLE IF EXISTS modifiers")

    cursor.execute("DROP TABLE IF EXISTS item_type_modifiers")

    

    # 1. modifiers table

    cursor.execute("""

        CREATE TABLE modifiers (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            mod_type TEXT NOT NULL,

            tags TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )

    """)

    

    # 2. modifier_tiers table

    cursor.execute("""

        CREATE TABLE modifier_tiers (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            modifier_id INTEGER NOT NULL,

            tier INTEGER NOT NULL,

            min_ilvl INTEGER NOT NULL,

            weight INTEGER DEFAULT 1000,

            item_type TEXT NOT NULL,

            FOREIGN KEY (modifier_id) REFERENCES modifiers(id)

        )

    """)

    

    # 3. item_type_modifiers table

    cursor.execute("""

        CREATE TABLE item_type_modifiers (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            item_type TEXT NOT NULL,

            modifier_id INTEGER NOT NULL,

            is_desecrated BOOLEAN DEFAULT 0,

            FOREIGN KEY (modifier_id) REFERENCES modifiers(id)

        )

    """)

    

    # Create indexes

    cursor.execute("CREATE INDEX idx_mod_name ON modifiers(name)")

    cursor.execute("CREATE INDEX idx_mod_type ON modifiers(mod_type)")

    cursor.execute("CREATE INDEX idx_tier_item ON modifier_tiers(item_type)")

    cursor.execute("CREATE INDEX idx_itm_type ON item_type_modifiers(item_type)")

    

    conn.commit()

    print("  [OK] Tables created")



def import_modifiers(conn, json_data):

    """Import JSON data to DB"""

    cursor = conn.cursor()

    

    mod_cache = {}

    

    stats = {

        'total_mods': 0,

        'total_tiers': 0,

        'item_types': 0

    }

    

    for item_type, data in json_data.items():

        stats['item_types'] += 1

        

        for section in ['prefix', 'suffix', 'desecrated_prefix', 'desecrated_suffix']:

            if section not in data:

                continue

                

            mod_type = 'prefix' if 'prefix' in section else 'suffix'

            is_desecrated = 'desecrated' in section

            

            for mod in data[section]:

                name = mod.get('name', '')

                if not name:

                    continue

                

                tags = json.dumps(mod.get('tags', []))

                tier = mod.get('tier', 1)

                ilvl = mod.get('ilvl', 1)

                weight = mod.get('weight', 1000)

                

                cache_key = f"{name}_{mod_type}"

                

                if cache_key not in mod_cache:

                    cursor.execute(

                        "INSERT INTO modifiers (name, mod_type, tags) VALUES (?, ?, ?)",

                        (name, mod_type, tags)

                    )

                    mod_id = cursor.lastrowid

                    mod_cache[cache_key] = mod_id

                    stats['total_mods'] += 1

                else:

                    mod_id = mod_cache[cache_key]

                

                cursor.execute("""

                    INSERT INTO modifier_tiers 

                    (modifier_id, tier, min_ilvl, weight, item_type)

                    VALUES (?, ?, ?, ?, ?)

                """, (mod_id, tier, ilvl, weight, item_type))

                stats['total_tiers'] += 1

                

                cursor.execute("""

                    INSERT INTO item_type_modifiers 

                    (item_type, modifier_id, is_desecrated)

                    VALUES (?, ?, ?)

                """, (item_type, mod_id, is_desecrated))

    

    conn.commit()

    return stats



def import_modifier_data():

    """Import modifier data from JSON to SQLite"""

    print("\n" + "="*60)

    print("[Part 2] Modifier Data Import")

    print("="*60)

    

    if not MODIFIER_JSON.exists():

        print(f"  [ERROR] File not found: {MODIFIER_JSON}")

        print("  -> Run poe2db_mods_scraper.py first")

        return False

    

    print(f"\nLoading JSON: {MODIFIER_JSON}")

    with open(MODIFIER_JSON, 'r') as f:

        json_data = json.load(f)

    print(f"  -> Found {len(json_data)} item types")

    

    print(f"\nConnecting DB: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)

    

    print("\nCreating tables...")

    create_modifier_tables(conn)

    

    print("\nImporting data...")

    stats = import_modifiers(conn, json_data)

    

    conn.close()

    

    print("\n" + "-"*40)

    print("[OK] Modifier data imported!")

    print(f"   - Item types: {stats['item_types']}")

    print(f"   - Unique mods: {stats['total_mods']}")

    print(f"   - Tier records: {stats['total_tiers']}")

    

    return True



# ============================================================

# Part 3: DB Status Check

# ============================================================

def check_db_status():

    """Print current DB status"""

    print("\n" + "="*60)

    print("[Part 3] Current DB Status")

    print("="*60)

    

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    

    tables = [

        ('leagues', 'Leagues'),

        ('item_bases', 'Base Items'),

        ('modifiers', 'Modifiers'),

        ('modifier_tiers', 'Mod Tiers'),

        ('item_type_modifiers', 'Item-Mod Map'),

    ]

    

    print("\nRecord counts:")

    for table, desc in tables:

        try:

            cursor.execute(f"SELECT COUNT(*) FROM {table}")

            count = cursor.fetchone()[0]

            print(f"  - {desc} ({table}): {count}")

        except:

            print(f"  - {desc} ({table}): N/A")

    

    print("\nSample modifiers (top 10 by weight):")

    try:

        cursor.execute("""

            SELECT m.name, m.mod_type, mt.tier, mt.min_ilvl, mt.weight, mt.item_type

            FROM modifiers m

            JOIN modifier_tiers mt ON m.id = mt.modifier_id

            ORDER BY mt.weight DESC

            LIMIT 10

        """)

        for row in cursor.fetchall():

            name = row[0][:35] if len(row[0]) > 35 else row[0]

            print(f"  [{row[1]:6}] {name:<35} T{row[2]} iLvl{row[3]:2} W{row[4]}")

    except Exception as e:

        print(f"  Error: {e}")

    

    conn.close()



# ============================================================

# Main

# ============================================================

def main():

    print("\n" + "="*60)

    print("  PoE2 Profit Optimizer - Step 1")

    print("="*60)

    

    # 1. API status check

    api_ok = check_api_status()

    

    # 2. Import modifier data

    import_modifier_data()

    

    # 3. DB status check

    check_db_status()

    

    # Summary

    print("\n" + "="*60)

    print("[SUMMARY]")

    print("="*60)

    

    if api_ok:

        print("[OK] Trade API: Available - can collect prices")

        print("   -> Next: run step2_price_collector.py")

    else:

        print("[BLOCKED] Trade API: Blocked - retry in 1-2 hours")

        print("   -> Continue with probability engine in step2")

    

    print("\n[OK] Modifier data: Imported to DB")

    print("   -> Ready for crafting probability calculations")



if __name__ == "__main__":

    main()

