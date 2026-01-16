
#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

Import modifier_data_v5.json to database

"""

import json

import sqlite3

from pathlib import Path



BASE_DIR = Path("/home/ubuntu/poe2-profit-optimizer/backend")

DB_PATH = BASE_DIR / "poe2_profit_optimizer.db"

MODIFIER_JSON = BASE_DIR / "data" / "modifier_data_v5.json"



def create_tables(conn):

    """Create modifier tables"""

    cursor = conn.cursor()

    

    # Drop old tables

    cursor.execute("DROP TABLE IF EXISTS modifier_tiers")

    cursor.execute("DROP TABLE IF EXISTS modifiers")

    cursor.execute("DROP TABLE IF EXISTS item_type_modifiers")

    

    # 1. modifiers - unique modifiers

    cursor.execute("""

        CREATE TABLE modifiers (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            mod_type TEXT NOT NULL,

            tags TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )

    """)

    

    # 2. modifier_tiers - tier info per item type

    cursor.execute("""

        CREATE TABLE modifier_tiers (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            modifier_id INTEGER NOT NULL,

            item_type TEXT NOT NULL,

            tier INTEGER NOT NULL,

            min_ilvl INTEGER NOT NULL,

            weight INTEGER DEFAULT 1000,

            is_desecrated BOOLEAN DEFAULT 0,

            FOREIGN KEY (modifier_id) REFERENCES modifiers(id)

        )

    """)

    

    # Create indexes

    cursor.execute("CREATE INDEX idx_mod_name ON modifiers(name)")

    cursor.execute("CREATE INDEX idx_mod_type ON modifiers(mod_type)")

    cursor.execute("CREATE INDEX idx_tier_item_type ON modifier_tiers(item_type)")

    cursor.execute("CREATE INDEX idx_tier_ilvl ON modifier_tiers(min_ilvl)")

    

    conn.commit()

    print("[OK] Tables created")



def import_data(conn, json_data):

    """Import JSON data"""

    cursor = conn.cursor()

    

    # Cache for deduplication

    mod_cache = {}  # (name, mod_type) -> id

    

    stats = {

        'item_types': 0,

        'unique_mods': 0,

        'tier_records': 0

    }

    

    for item_type, data in json_data.items():

        stats['item_types'] += 1

        

        # Process prefix, suffix, desecrated_prefix, desecrated_suffix

        sections = [

            ('prefix', 'prefix', False),

            ('suffix', 'suffix', False),

            ('desecrated_prefix', 'prefix', True),

            ('desecrated_suffix', 'suffix', True)

        ]

        

        for section_key, mod_type, is_desecrated in sections:

            mods = data.get(section_key, [])

            

            for mod in mods:

                name = mod.get('name', '').strip()

                if not name:

                    continue

                

                tags = json.dumps(mod.get('tags', []))

                tier = mod.get('tier', 1)

                ilvl = mod.get('ilvl', 1)

                weight = mod.get('weight', 1000)

                

                # Get or create modifier

                cache_key = (name, mod_type)

                

                if cache_key not in mod_cache:

                    cursor.execute(

                        "INSERT INTO modifiers (name, mod_type, tags) VALUES (?, ?, ?)",

                        (name, mod_type, tags)

                    )

                    mod_id = cursor.lastrowid

                    mod_cache[cache_key] = mod_id

                    stats['unique_mods'] += 1

                else:

                    mod_id = mod_cache[cache_key]

                

                # Insert tier record

                cursor.execute("""

                    INSERT INTO modifier_tiers 

                    (modifier_id, item_type, tier, min_ilvl, weight, is_desecrated)

                    VALUES (?, ?, ?, ?, ?, ?)

                """, (mod_id, item_type, tier, ilvl, weight, is_desecrated))

                stats['tier_records'] += 1

    

    conn.commit()

    return stats



def show_sample_data(conn):

    """Show sample data for verification"""

    cursor = conn.cursor()

    

    print("\n" + "="*60)

    print("Sample Data Verification")

    print("="*60)

    

    # Sample prefixes

    print("\nTop 10 Prefixes (by weight):")

    cursor.execute("""

        SELECT m.name, m.mod_type, mt.item_type, mt.tier, mt.min_ilvl, mt.weight

        FROM modifiers m

        JOIN modifier_tiers mt ON m.id = mt.modifier_id

        WHERE m.mod_type = 'prefix' AND mt.is_desecrated = 0

        ORDER BY mt.weight DESC

        LIMIT 10

    """)

    for row in cursor.fetchall():

        print(f"  [{row[2][:20]:<20}] T{row[3]:2} iLvl{row[4]:2} W{row[5]:5} | {row[0][:40]}")

    

    # Sample suffixes

    print("\nTop 10 Suffixes (by weight):")

    cursor.execute("""

        SELECT m.name, m.mod_type, mt.item_type, mt.tier, mt.min_ilvl, mt.weight

        FROM modifiers m

        JOIN modifier_tiers mt ON m.id = mt.modifier_id

        WHERE m.mod_type = 'suffix' AND mt.is_desecrated = 0

        ORDER BY mt.weight DESC

        LIMIT 10

    """)

    for row in cursor.fetchall():

        print(f"  [{row[2][:20]:<20}] T{row[3]:2} iLvl{row[4]:2} W{row[5]:5} | {row[0][:40]}")

    

    # Count by item type

    print("\nMods per item type (sample):")

    cursor.execute("""

        SELECT item_type, 

               SUM(CASE WHEN m.mod_type = 'prefix' THEN 1 ELSE 0 END) as prefix_cnt,

               SUM(CASE WHEN m.mod_type = 'suffix' THEN 1 ELSE 0 END) as suffix_cnt

        FROM modifier_tiers mt

        JOIN modifiers m ON mt.modifier_id = m.id

        WHERE mt.is_desecrated = 0

        GROUP BY item_type

        ORDER BY item_type

        LIMIT 10

    """)

    for row in cursor.fetchall():

        print(f"  {row[0]:<25} P:{row[1]:2} S:{row[2]:2}")



def main():

    print("="*60)

    print("Importing modifier_data_v5.json to DB")

    print("="*60)

    

    # Load JSON

    print(f"\nLoading: {MODIFIER_JSON}")

    with open(MODIFIER_JSON, 'r', encoding='utf-8') as f:

        json_data = json.load(f)

    print(f"  -> {len(json_data)} item types")

    

    # Connect DB

    print(f"\nConnecting: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)

    

    # Create tables

    print("\nCreating tables...")

    create_tables(conn)

    

    # Import data

    print("\nImporting data...")

    stats = import_data(conn, json_data)

    

    print("\n" + "-"*40)

    print("[OK] Import complete!")

    print(f"  - Item types: {stats['item_types']}")

    print(f"  - Unique modifiers: {stats['unique_mods']}")

    print(f"  - Tier records: {stats['tier_records']}")

    

    # Show samples

    show_sample_data(conn)

    

    conn.close()

    

    print("\n" + "="*60)

    print("[DONE] Modifier data ready for probability calculations!")

    print("="*60)



if __name__ == "__main__":

    main()

