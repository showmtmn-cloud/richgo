
#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

PoE2 Profit Optimizer - Step 2: Probability Calculation Engine

Calculates crafting probabilities based on modifier weights

"""

import json

import sqlite3

from pathlib import Path

from typing import Dict, List, Optional

from dataclasses import dataclass



# ============================================================

# Settings

# ============================================================

BASE_DIR = Path("/home/ubuntu/poe2-profit-optimizer/backend")

DB_PATH = BASE_DIR / "poe2_profit_optimizer.db"



# ============================================================

# Data Classes

# ============================================================

@dataclass

class Modifier:

    id: int

    name: str

    mod_type: str  # prefix or suffix

    tags: List[str]



@dataclass

class ModifierTier:

    modifier_id: int

    tier: int

    min_ilvl: int

    weight: int

    item_type: str



# ============================================================

# Probability Engine

# ============================================================

class CraftingProbabilityEngine:

    def __init__(self, db_path: Path = DB_PATH):

        self.db_path = db_path

        self.conn = None

    

    def connect(self):

        self.conn = sqlite3.connect(self.db_path)

        self.conn.row_factory = sqlite3.Row

    

    def close(self):

        if self.conn:

            self.conn.close()

    

    def get_available_mods(self, item_type: str, ilvl: int, mod_type: str = None) -> List[dict]:

        """

        Get all available modifiers for an item type at specific ilvl

        

        Args:

            item_type: e.g., "Body_Armours_int", "Amulets"

            ilvl: item level (e.g., 82)

            mod_type: "prefix", "suffix", or None for both

        

        Returns:

            List of available modifiers with weights

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

                mt.weight

            FROM modifiers m

            JOIN modifier_tiers mt ON m.id = mt.modifier_id

            WHERE mt.item_type = ?

            AND mt.min_ilvl <= ?

        """

        

        params = [item_type, ilvl]

        

        if mod_type:

            query += " AND m.mod_type = ?"

            params.append(mod_type)

        

        # Get highest tier available for each mod

        query += """

            AND mt.tier = (

                SELECT MIN(mt2.tier)

                FROM modifier_tiers mt2

                WHERE mt2.modifier_id = m.id

                AND mt2.item_type = ?

                AND mt2.min_ilvl <= ?

            )

            ORDER BY mt.weight DESC

        """

        params.extend([item_type, ilvl])

        

        cursor.execute(query, params)

        

        results = []

        for row in cursor.fetchall():

            results.append({

                'id': row['id'],

                'name': row['name'],

                'mod_type': row['mod_type'],

                'tags': json.loads(row['tags']) if row['tags'] else [],

                'tier': row['tier'],

                'min_ilvl': row['min_ilvl'],

                'weight': row['weight']

            })

        

        return results

    

    def calculate_mod_probability(self, item_type: str, ilvl: int, 

                                   target_mod_name: str, mod_type: str) -> dict:

        """

        Calculate probability of hitting a specific modifier

        

        Args:

            item_type: e.g., "Body_Armours_int"

            ilvl: item level

            target_mod_name: part of the mod name to search for

            mod_type: "prefix" or "suffix"

        

        Returns:

            Dict with probability info

        """

        available_mods = self.get_available_mods(item_type, ilvl, mod_type)

        

        if not available_mods:

            return {

                'error': f'No {mod_type} mods found for {item_type} at ilvl {ilvl}'

            }

        

        # Total weight

        total_weight = sum(m['weight'] for m in available_mods)

        

        # Find target mod

        target_mods = [m for m in available_mods if target_mod_name.lower() in m['name'].lower()]

        

        if not target_mods:

            return {

                'error': f'Modifier "{target_mod_name}" not found',

                'available_count': len(available_mods),

                'total_weight': total_weight

            }

        

        target = target_mods[0]  # Take first match

        target_weight = target['weight']

        probability = target_weight / total_weight

        

        return {

            'target_mod': target['name'],

            'tier': target['tier'],

            'weight': target_weight,

            'total_weight': total_weight,

            'probability': probability,

            'probability_pct': round(probability * 100, 4),

            'avg_attempts': round(1 / probability, 2) if probability > 0 else 0,

            'available_mods_count': len(available_mods)

        }

    

    def calculate_exalt_probability(self, item_type: str, ilvl: int,

                                     target_mod_name: str,

                                     current_prefixes: int = 0,

                                     current_suffixes: int = 0) -> dict:

        """

        Calculate probability when using Exalted Orb

        

        Exalt adds a random prefix OR suffix (equal chance if both available)

        

        Args:

            item_type: item type

            ilvl: item level

            target_mod_name: target modifier name

            current_prefixes: number of existing prefixes (0-3)

            current_suffixes: number of existing suffixes (0-3)

        """

        # Check if slots available

        prefix_slots = 3 - current_prefixes

        suffix_slots = 3 - current_suffixes

        

        if prefix_slots == 0 and suffix_slots == 0:

            return {'error': 'No slots available (6 mods already)'}

        

        # Get available mods

        prefix_mods = self.get_available_mods(item_type, ilvl, 'prefix') if prefix_slots > 0 else []

        suffix_mods = self.get_available_mods(item_type, ilvl, 'suffix') if suffix_slots > 0 else []

        

        # Determine which pool the target is in

        target_prefix = [m for m in prefix_mods if target_mod_name.lower() in m['name'].lower()]

        target_suffix = [m for m in suffix_mods if target_mod_name.lower() in m['name'].lower()]

        

        result = {

            'prefix_slots_available': prefix_slots,

            'suffix_slots_available': suffix_slots,

            'prefix_mods_count': len(prefix_mods),

            'suffix_mods_count': len(suffix_mods),

        }

        

        # Calculate prefix/suffix selection probability

        if prefix_slots > 0 and suffix_slots > 0:

            # Both available: 50/50

            prefix_chance = 0.5

            suffix_chance = 0.5

        elif prefix_slots > 0:

            prefix_chance = 1.0

            suffix_chance = 0.0

        else:

            prefix_chance = 0.0

            suffix_chance = 1.0

        

        result['prefix_selection_chance'] = prefix_chance

        result['suffix_selection_chance'] = suffix_chance

        

        # Calculate target probability

        if target_prefix:

            target = target_prefix[0]

            total_prefix_weight = sum(m['weight'] for m in prefix_mods)

            mod_prob = target['weight'] / total_prefix_weight if total_prefix_weight > 0 else 0

            final_prob = prefix_chance * mod_prob

            

            result['target_mod'] = target['name']

            result['target_type'] = 'prefix'

            result['tier'] = target['tier']

            result['mod_weight'] = target['weight']

            result['pool_total_weight'] = total_prefix_weight

            result['probability_in_pool'] = round(mod_prob * 100, 4)

            result['final_probability'] = round(final_prob * 100, 4)

            result['avg_attempts'] = round(1 / final_prob, 2) if final_prob > 0 else 0

            

        elif target_suffix:

            target = target_suffix[0]

            total_suffix_weight = sum(m['weight'] for m in suffix_mods)

            mod_prob = target['weight'] / total_suffix_weight if total_suffix_weight > 0 else 0

            final_prob = suffix_chance * mod_prob

            

            result['target_mod'] = target['name']

            result['target_type'] = 'suffix'

            result['tier'] = target['tier']

            result['mod_weight'] = target['weight']

            result['pool_total_weight'] = total_suffix_weight

            result['probability_in_pool'] = round(mod_prob * 100, 4)

            result['final_probability'] = round(final_prob * 100, 4)

            result['avg_attempts'] = round(1 / final_prob, 2) if final_prob > 0 else 0

        else:

            result['error'] = f'Target mod "{target_mod_name}" not found in available pools'

        

        return result

    

    def get_item_types(self) -> List[str]:

        """Get all available item types"""

        cursor = self.conn.cursor()

        cursor.execute("SELECT DISTINCT item_type FROM modifier_tiers ORDER BY item_type")

        return [row[0] for row in cursor.fetchall()]

    

    def get_mod_summary(self, item_type: str, ilvl: int) -> dict:

        """Get summary of available mods for an item type"""

        prefix_mods = self.get_available_mods(item_type, ilvl, 'prefix')

        suffix_mods = self.get_available_mods(item_type, ilvl, 'suffix')

        

        return {

            'item_type': item_type,

            'ilvl': ilvl,

            'prefix_count': len(prefix_mods),

            'suffix_count': len(suffix_mods),

            'total_count': len(prefix_mods) + len(suffix_mods),

            'prefix_total_weight': sum(m['weight'] for m in prefix_mods),

            'suffix_total_weight': sum(m['weight'] for m in suffix_mods),

            'top_prefixes': prefix_mods[:5],

            'top_suffixes': suffix_mods[:5]

        }





# ============================================================

# Demo / Test

# ============================================================

def main():

    print("\n" + "="*60)

    print("  PoE2 Crafting Probability Engine - Demo")

    print("="*60)

    

    engine = CraftingProbabilityEngine()

    engine.connect()

    

    # 1. Show available item types

    print("\n[1] Available Item Types:")

    print("-" * 40)

    item_types = engine.get_item_types()

    for i, it in enumerate(item_types[:10]):

        print(f"  {i+1}. {it}")

    print(f"  ... and {len(item_types) - 10} more")

    

    # 2. Test with ES Body Armour (int)

    test_item = "Body_Armours_int"

    test_ilvl = 82

    

    print(f"\n[2] Mod Summary for {test_item} at ilvl {test_ilvl}:")

    print("-" * 40)

    summary = engine.get_mod_summary(test_item, test_ilvl)

    print(f"  Prefix mods: {summary['prefix_count']}")

    print(f"  Suffix mods: {summary['suffix_count']}")

    print(f"  Total weight (prefix): {summary['prefix_total_weight']}")

    print(f"  Total weight (suffix): {summary['suffix_total_weight']}")

    

    print("\n  Top 5 Prefixes:")

    for m in summary['top_prefixes']:

        print(f"    - {m['name'][:40]:<40} W:{m['weight']} T{m['tier']}")

    

    print("\n  Top 5 Suffixes:")

    for m in summary['top_suffixes']:

        print(f"    - {m['name'][:40]:<40} W:{m['weight']} T{m['tier']}")

    

    # 3. Calculate specific mod probability

    print(f"\n[3] Probability Calculation Examples:")

    print("-" * 40)

    

    # Test: Energy Shield

    result = engine.calculate_mod_probability(test_item, test_ilvl, "Energy Shield", "prefix")

    if 'error' not in result:

        print(f"\n  Target: {result['target_mod']}")

        print(f"  Tier: {result['tier']}")

        print(f"  Weight: {result['weight']} / {result['total_weight']}")

        print(f"  Probability: {result['probability_pct']}%")

        print(f"  Avg attempts needed: {result['avg_attempts']}")

    else:

        print(f"  Error: {result['error']}")

    

    # 4. Exalt probability

    print(f"\n[4] Exalted Orb Probability (2 prefix, 1 suffix existing):")

    print("-" * 40)

    

    exalt_result = engine.calculate_exalt_probability(

        test_item, test_ilvl, "Energy Shield",

        current_prefixes=2, current_suffixes=1

    )

    

    if 'error' not in exalt_result:

        print(f"  Target: {exalt_result.get('target_mod', 'N/A')}")

        print(f"  Type: {exalt_result.get('target_type', 'N/A')}")

        print(f"  Prefix selection chance: {exalt_result['prefix_selection_chance']*100}%")

        print(f"  Suffix selection chance: {exalt_result['suffix_selection_chance']*100}%")

        print(f"  Probability in pool: {exalt_result.get('probability_in_pool', 0)}%")

        print(f"  Final probability: {exalt_result.get('final_probability', 0)}%")

        print(f"  Avg Exalts needed: {exalt_result.get('avg_attempts', 0)}")

    else:

        print(f"  Error: {exalt_result.get('error')}")

    

    engine.close()

    

    print("\n" + "="*60)

    print("[OK] Probability Engine Ready!")

    print("="*60)



if __name__ == "__main__":

    main()

