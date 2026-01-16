
#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

PoE2 Crafting Probability Engine V2

Updated to work with new modifier data structure

"""

import json

import sqlite3

from pathlib import Path

from typing import List, Dict, Optional



BASE_DIR = Path("/home/ubuntu/poe2-profit-optimizer/backend")

DB_PATH = BASE_DIR / "poe2_profit_optimizer.db"



class CraftingProbabilityEngine:

    def __init__(self):

        self.conn = sqlite3.connect(DB_PATH)

        self.conn.row_factory = sqlite3.Row

    

    def close(self):

        self.conn.close()

    

    def get_item_types(self) -> List[str]:

        """Get all available item types"""

        cursor = self.conn.cursor()

        cursor.execute("""

            SELECT DISTINCT item_type FROM modifier_tiers ORDER BY item_type

        """)

        return [row[0] for row in cursor.fetchall()]

    

    def get_available_mods(self, item_type: str, ilvl: int, 

                           mod_type: str = None, include_desecrated: bool = False) -> List[dict]:

        """

        Get available modifiers for item type at ilvl

        Returns highest tier available for each mod

        """

        cursor = self.conn.cursor()

        

        query = """

            SELECT 

                m.id,

                m.name,

                m.mod_type,

                m.tags,

                mt.tier,

                mt.min_ilvl,

                mt.weight,

                mt.is_desecrated

            FROM modifiers m

            JOIN modifier_tiers mt ON m.id = mt.modifier_id

            WHERE mt.item_type = ?

            AND mt.min_ilvl <= ?

        """

        params = [item_type, ilvl]

        

        if mod_type:

            query += " AND m.mod_type = ?"

            params.append(mod_type)

        

        if not include_desecrated:

            query += " AND mt.is_desecrated = 0"

        

        query += " ORDER BY mt.weight DESC"

        

        cursor.execute(query, params)

        

        # Group by modifier, keep best tier (lowest number)

        mods_by_id = {}

        for row in cursor.fetchall():

            mod_id = row['id']

            if mod_id not in mods_by_id or row['tier'] < mods_by_id[mod_id]['tier']:

                mods_by_id[mod_id] = {

                    'id': row['id'],

                    'name': row['name'],

                    'mod_type': row['mod_type'],

                    'tags': json.loads(row['tags']) if row['tags'] else [],

                    'tier': row['tier'],

                    'min_ilvl': row['min_ilvl'],

                    'weight': row['weight'],

                    'is_desecrated': bool(row['is_desecrated'])

                }

        

        return sorted(mods_by_id.values(), key=lambda x: -x['weight'])

    

    def calculate_mod_probability(self, item_type: str, ilvl: int,

                                   target_name: str, mod_type: str) -> dict:

        """

        Calculate probability of hitting specific mod with Chaos/Exalt

        """

        mods = self.get_available_mods(item_type, ilvl, mod_type)

        

        if not mods:

            return {'error': f'No {mod_type} mods for {item_type} at ilvl {ilvl}'}

        

        total_weight = sum(m['weight'] for m in mods)

        

        # Find target

        target = None

        for m in mods:

            if target_name.lower() in m['name'].lower():

                target = m

                break

        

        if not target:

            return {

                'error': f'Mod "{target_name}" not found',

                'available': [m['name'] for m in mods[:10]]

            }

        

        prob = target['weight'] / total_weight

        

        return {

            'target_mod': target['name'],

            'mod_type': mod_type,

            'tier': target['tier'],

            'min_ilvl': target['min_ilvl'],

            'weight': target['weight'],

            'total_weight': total_weight,

            'total_mods': len(mods),

            'probability': round(prob * 100, 4),

            'avg_attempts': round(1 / prob, 2) if prob > 0 else 0,

            'tags': target['tags']

        }

    

    def calculate_exalt_probability(self, item_type: str, ilvl: int,

                                     target_name: str,

                                     current_prefixes: int = 0,

                                     current_suffixes: int = 0) -> dict:

        """

        Calculate Exalted Orb probability considering slots

        """

        prefix_slots = 3 - current_prefixes

        suffix_slots = 3 - current_suffixes

        

        if prefix_slots <= 0 and suffix_slots <= 0:

            return {'error': 'No open slots (6 mods already)'}

        

        # Get available mods

        prefix_mods = self.get_available_mods(item_type, ilvl, 'prefix') if prefix_slots > 0 else []

        suffix_mods = self.get_available_mods(item_type, ilvl, 'suffix') if suffix_slots > 0 else []

        

        # Determine selection probability

        if prefix_slots > 0 and suffix_slots > 0:

            prefix_chance = 0.5

            suffix_chance = 0.5

        elif prefix_slots > 0:

            prefix_chance = 1.0

            suffix_chance = 0.0

        else:

            prefix_chance = 0.0

            suffix_chance = 1.0

        

        result = {

            'item_type': item_type,

            'ilvl': ilvl,

            'current_prefixes': current_prefixes,

            'current_suffixes': current_suffixes,

            'prefix_slots': prefix_slots,

            'suffix_slots': suffix_slots,

            'prefix_selection_chance': prefix_chance,

            'suffix_selection_chance': suffix_chance,

            'prefix_pool_size': len(prefix_mods),

            'suffix_pool_size': len(suffix_mods)

        }

        

        # Find target in pools

        target_prefix = next((m for m in prefix_mods if target_name.lower() in m['name'].lower()), None)

        target_suffix = next((m for m in suffix_mods if target_name.lower() in m['name'].lower()), None)

        

        if target_prefix:

            total_weight = sum(m['weight'] for m in prefix_mods)

            pool_prob = target_prefix['weight'] / total_weight

            final_prob = prefix_chance * pool_prob

            

            result.update({

                'target_mod': target_prefix['name'],

                'target_type': 'prefix',

                'tier': target_prefix['tier'],

                'weight': target_prefix['weight'],

                'pool_total_weight': total_weight,

                'probability_in_pool': round(pool_prob * 100, 4),

                'final_probability': round(final_prob * 100, 4),

                'avg_exalts': round(1 / final_prob, 2) if final_prob > 0 else 0

            })

        elif target_suffix:

            total_weight = sum(m['weight'] for m in suffix_mods)

            pool_prob = target_suffix['weight'] / total_weight

            final_prob = suffix_chance * pool_prob

            

            result.update({

                'target_mod': target_suffix['name'],

                'target_type': 'suffix',

                'tier': target_suffix['tier'],

                'weight': target_suffix['weight'],

                'pool_total_weight': total_weight,

                'probability_in_pool': round(pool_prob * 100, 4),

                'final_probability': round(final_prob * 100, 4),

                'avg_exalts': round(1 / final_prob, 2) if final_prob > 0 else 0

            })

        else:

            result['error'] = f'Target "{target_name}" not found in either pool'

        

        return result

    

    def get_mod_summary(self, item_type: str, ilvl: int) -> dict:

        """Get summary of available mods"""

        prefixes = self.get_available_mods(item_type, ilvl, 'prefix')

        suffixes = self.get_available_mods(item_type, ilvl, 'suffix')

        

        return {

            'item_type': item_type,

            'ilvl': ilvl,

            'prefix_count': len(prefixes),

            'suffix_count': len(suffixes),

            'prefix_total_weight': sum(m['weight'] for m in prefixes),

            'suffix_total_weight': sum(m['weight'] for m in suffixes),

            'top_prefixes': prefixes[:5],

            'top_suffixes': suffixes[:5]

        }





def demo():

    """Demo the probability engine"""

    print("="*60)

    print("PoE2 Crafting Probability Engine V2 - Demo")

    print("="*60)

    

    engine = CraftingProbabilityEngine()

    

    # Test cases

    test_cases = [

        ('Body_Armours_int', 82, 'Energy Shield', 'prefix'),

        ('Body_Armours_int', 82, 'maximum Life', 'prefix'),

        ('Amulets', 82, 'maximum Life', 'prefix'),

        ('Amulets', 82, 'Strength', 'suffix'),

        ('One_Hand_Swords', 82, 'Physical Damage', 'prefix'),

    ]

    

    print("\n[1] Basic Probability Tests")

    print("-"*60)

    

    for item_type, ilvl, target, mod_type in test_cases:

        result = engine.calculate_mod_probability(item_type, ilvl, target, mod_type)

        

        if 'error' in result:

            print(f"\n{item_type} ({mod_type}): {result['error']}")

        else:

            print(f"\n{item_type} @ ilvl {ilvl} -> '{target}' ({mod_type})")

            print(f"  Found: {result['target_mod']}")

            print(f"  Tier: T{result['tier']} (min ilvl {result['min_ilvl']})")

            print(f"  Weight: {result['weight']} / {result['total_weight']} ({result['total_mods']} mods)")

            print(f"  Probability: {result['probability']}%")

            print(f"  Avg attempts: {result['avg_attempts']}")

    

    print("\n" + "="*60)

    print("[2] Exalted Orb Probability Test")

    print("-"*60)

    

    # Test: Body Armour with 2 prefix, 1 suffix

    result = engine.calculate_exalt_probability(

        'Body_Armours_int', 82, 'Energy Shield',

        current_prefixes=2, current_suffixes=1

    )

    

    print(f"\nScenario: Body_Armours_int @ ilvl 82")

    print(f"Current: 2 prefixes, 1 suffix")

    print(f"Target: Energy Shield")

    print(f"\nResult:")

    

    if 'error' in result:

        print(f"  Error: {result['error']}")

    else:

        print(f"  Open slots: {result['prefix_slots']} prefix, {result['suffix_slots']} suffix")

        print(f"  Selection: {result['prefix_selection_chance']*100}% prefix, {result['suffix_selection_chance']*100}% suffix")

        print(f"  Target: {result.get('target_mod', 'N/A')} ({result.get('target_type', 'N/A')})")

        print(f"  In-pool prob: {result.get('probability_in_pool', 0)}%")

        print(f"  Final prob: {result.get('final_probability', 0)}%")

        print(f"  Avg Exalts needed: {result.get('avg_exalts', 0)}")

    

    print("\n" + "="*60)

    print("[3] Item Type Summary")

    print("-"*60)

    

    summary = engine.get_mod_summary('Body_Armours_int', 82)

    print(f"\n{summary['item_type']} @ ilvl {summary['ilvl']}")

    print(f"  Prefixes: {summary['prefix_count']} (total weight: {summary['prefix_total_weight']})")

    print(f"  Suffixes: {summary['suffix_count']} (total weight: {summary['suffix_total_weight']})")

    

    print("\n  Top Prefixes:")

    for m in summary['top_prefixes']:

        print(f"    W{m['weight']:5} T{m['tier']:2} | {m['name'][:45]}")

    

    print("\n  Top Suffixes:")

    for m in summary['top_suffixes']:

        print(f"    W{m['weight']:5} T{m['tier']:2} | {m['name'][:45]}")

    

    engine.close()

    

    print("\n" + "="*60)

    print("[OK] Probability Engine V2 Ready!")

    print("="*60)



if __name__ == "__main__":

    demo()

