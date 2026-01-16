
#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

Fixed Build-Based Analysis - Using correct mod names from DB

"""

import json

import sqlite3

from pathlib import Path

from typing import Dict, List



BASE_DIR = Path("/home/ubuntu/poe2-profit-optimizer/backend")

DB_PATH = BASE_DIR / "poe2_profit_optimizer.db"

OUTPUT_FILE = BASE_DIR / "data" / "build_based_opportunities.json"



# Currency values (in Exalted)

CURRENCY_TO_EXALT = {

    'divine': 150,

    'exalted': 1,

    'regal': 0.02,

    'chaos': 0.007,

    'alchemy': 0.005,

    'alch': 0.005,

    'transmute': 0.001,

    'aug': 0.001,

}



# ============================================================

# Popular Builds - FIXED with correct DB mod names

# ============================================================

POPULAR_BUILDS = {

    "ES_Caster": {

        "description": "Energy Shield 마법사 (인기: 매우 높음)",

        "demand": "very_high",

        "items": [

            {

                "slot": "Body Armour (ES)",

                "item_type": "Body_Armours_int",

                "base": "Conjurer Mantle",

                "target_mods": [

                    {"name": "# to maximum Energy Shield", "type": "prefix"},

                    {"name": "#% increased Energy Shield", "type": "prefix"},

                    {"name": "# to maximum Life", "type": "prefix"},

                    {"name": "#% to Fire Resistance", "type": "suffix"},

                    {"name": "#% to Cold Resistance", "type": "suffix"},

                ],

                "estimated_sale": 80

            },

            {

                "slot": "Helmet (ES)",

                "item_type": "Helmets_int",

                "base": "Sandsworn Tiara",

                "target_mods": [

                    {"name": "# to maximum Energy Shield", "type": "prefix"},

                    {"name": "#% increased Energy Shield", "type": "prefix"},

                    {"name": "#% to Fire Resistance", "type": "suffix"},

                ],

                "estimated_sale": 50

            }

        ]

    },

    "Life_Melee": {

        "description": "Life 근접 전사 (인기: 높음)",

        "demand": "high",

        "items": [

            {

                "slot": "Body Armour (Armour)",

                "item_type": "Body_Armours_str",

                "base": "Sacrificial Regalia",

                "target_mods": [

                    {"name": "# to maximum Life", "type": "prefix"},

                    {"name": "#% increased Armour", "type": "prefix"},

                    {"name": "#% to Fire Resistance", "type": "suffix"},

                    {"name": "#% to Cold Resistance", "type": "suffix"},

                    {"name": "#% to Lightning Resistance", "type": "suffix"},

                ],

                "estimated_sale": 60

            },

            {

                "slot": "Gloves (Armour)",

                "item_type": "Gloves_str",

                "base": "Cultist Gauntlets",

                "target_mods": [

                    {"name": "# to maximum Life", "type": "prefix"},

                    {"name": "#% to Fire Resistance", "type": "suffix"},

                ],

                "estimated_sale": 40

            }

        ]

    },

    "Evasion_Bow": {

        "description": "Evasion 활 레인저 (인기: 높음)",

        "demand": "high",

        "items": [

            {

                "slot": "Bow",

                "item_type": "Bows",

                "base": "Obliterator Bow",

                "target_mods": [

                    {"name": "Adds # to # Physical Damage", "type": "prefix"},

                    {"name": "#% increased Physical Damage", "type": "prefix"},

                ],

                "estimated_sale": 100

            },

            {

                "slot": "Boots (Evasion)",

                "item_type": "Boots_dex",

                "base": "Drakeskin Boots",

                "target_mods": [

                    {"name": "#% increased Movement Speed", "type": "prefix"},

                    {"name": "# to maximum Life", "type": "prefix"},

                    {"name": "#% to Fire Resistance", "type": "suffix"},

                ],

                "estimated_sale": 40

            }

        ]

    },

    "Spell_Caster": {

        "description": "스펠 캐스터 (인기: 높음)",

        "demand": "high",

        "items": [

            {

                "slot": "Wand",

                "item_type": "Wands",

                "base": "Dueling Wand",

                "target_mods": [

                    {"name": "#% increased Spell Damage", "type": "prefix"},

                    {"name": "# to Level of all", "type": "suffix"},

                ],

                "estimated_sale": 80

            },

            {

                "slot": "Staff",

                "item_type": "Staves",

                "base": "Voltaic Staff",

                "target_mods": [

                    {"name": "#% increased Spell Damage", "type": "prefix"},

                    {"name": "# to Level of all", "type": "suffix"},

                ],

                "estimated_sale": 100

            }

        ]

    },

    "Ring_Amulet": {

        "description": "악세서리 (인기: 매우 높음)",

        "demand": "very_high",

        "items": [

            {

                "slot": "Amulet",

                "item_type": "Amulets",

                "base": "Gold Amulet",

                "target_mods": [

                    {"name": "# to maximum Life", "type": "prefix"},

                    {"name": "#% increased maximum Life", "type": "prefix"},

                    {"name": "# to Strength", "type": "suffix"},

                ],

                "estimated_sale": 70

            },

            {

                "slot": "Ring",

                "item_type": "Rings",

                "base": "Ruby Ring",

                "target_mods": [

                    {"name": "# to maximum Life", "type": "prefix"},

                    {"name": "#% to Fire Resistance", "type": "suffix"},

                    {"name": "#% to Cold Resistance", "type": "suffix"},

                ],

                "estimated_sale": 50

            }

        ]

    }

}





class FixedAnalyzer:

    def __init__(self):

        self.conn = sqlite3.connect(DB_PATH)

        self.conn.row_factory = sqlite3.Row

        self.base_prices = self._load_base_prices()

    

    def _load_base_prices(self) -> dict:

        price_file = BASE_DIR / "data" / "profitable_items.json"

        if price_file.exists():

            with open(price_file, 'r') as f:

                data = json.load(f)

                return data.get('base_prices', {})

        return {}

    

    def get_base_price_exalt(self, base_name: str) -> float:

        """Get base price in exalted"""

        price_data = self.base_prices.get(base_name, {}).get('base_price', {})

        if not price_data:

            return 1.0

        

        amount = price_data.get('amount', 1)

        currency = price_data.get('currency', 'exalted')

        multiplier = CURRENCY_TO_EXALT.get(currency, 1)

        

        return amount * multiplier

    

    def get_mod_probability(self, item_type: str, mod_name: str, 

                            mod_type: str, ilvl: int = 82) -> dict:

        """Get probability of hitting a mod"""

        cursor = self.conn.cursor()

        

        # Get all mods for this item type

        cursor.execute("""

            SELECT m.name, mt.weight, mt.tier

            FROM modifiers m

            JOIN modifier_tiers mt ON m.id = mt.modifier_id

            WHERE mt.item_type = ?

            AND mt.min_ilvl <= ?

            AND m.mod_type = ?

            AND mt.is_desecrated = 0

        """, (item_type, ilvl, mod_type))

        

        mods = cursor.fetchall()

        if not mods:

            return {'error': f'No {mod_type} mods for {item_type}'}

        

        total_weight = sum(m['weight'] for m in mods)

        

        # Find target mod (partial match)

        for m in mods:

            # Remove # symbols for comparison

            clean_target = mod_name.replace('#', '').strip().lower()

            clean_mod = m['name'].replace('#', '').strip().lower()

            

            if clean_target in clean_mod or clean_mod in clean_target:

                prob = m['weight'] / total_weight

                return {

                    'found': True,

                    'mod': m['name'],

                    'tier': m['tier'],

                    'weight': m['weight'],

                    'total_weight': total_weight,

                    'probability': prob,

                    'avg_attempts': 1 / prob if prob > 0 else 9999

                }

        

        return {'error': f'Mod "{mod_name}" not found'}

    

    def calculate_crafting_cost(self, item_type: str, target_mods: List[dict]) -> dict:

        """

        Calculate realistic crafting cost

        

        Method: Essence for first mod, then Chaos/Annul/Exalt for rest

        """

        details = []

        

        # Separate by prefix/suffix

        prefixes = [m for m in target_mods if m['type'] == 'prefix']

        suffixes = [m for m in target_mods if m['type'] == 'suffix']

        

        # Calculate prefix probabilities

        prefix_probs = []

        for mod in prefixes:

            prob_data = self.get_mod_probability(item_type, mod['name'], 'prefix')

            if prob_data.get('found'):

                prefix_probs.append(prob_data)

                details.append({

                    'mod': prob_data['mod'],

                    'type': 'prefix',

                    'probability': round(prob_data['probability'] * 100, 2),

                    'weight': prob_data['weight']

                })

            else:

                details.append({'mod': mod['name'], 'error': prob_data.get('error')})

        

        # Calculate suffix probabilities

        suffix_probs = []

        for mod in suffixes:

            prob_data = self.get_mod_probability(item_type, mod['name'], 'suffix')

            if prob_data.get('found'):

                suffix_probs.append(prob_data)

                details.append({

                    'mod': prob_data['mod'],

                    'type': 'suffix',

                    'probability': round(prob_data['probability'] * 100, 2),

                    'weight': prob_data['weight']

                })

            else:

                details.append({'mod': mod['name'], 'error': prob_data.get('error')})

        

        # ============================================================

        # REALISTIC COST CALCULATION

        # ============================================================

        # Method: Essence spam + Annul/Exalt

        # - Essence guarantees 1 mod

        # - Need to hit other mods via RNG

        # - Chaos spam average cost = 1 / combined_probability

        

        # Combined probability for all prefixes hitting together (simplified)

        if prefix_probs:

            combined_prefix_prob = 1

            for p in prefix_probs:

                combined_prefix_prob *= p['probability']

            

            # How many chaos/essence to hit all prefixes?

            avg_attempts_prefix = 1 / combined_prefix_prob if combined_prefix_prob > 0 else 1000

        else:

            avg_attempts_prefix = 1

        

        # Combined probability for suffixes

        if suffix_probs:

            combined_suffix_prob = 1

            for p in suffix_probs:

                combined_suffix_prob *= p['probability']

            

            avg_attempts_suffix = 1 / combined_suffix_prob if combined_suffix_prob > 0 else 1000

        else:

            avg_attempts_suffix = 1

        

        # Cost calculation

        # - Essence: 2-5 exalt each

        # - Chaos: 0.007 exalt each

        # - Annulment: 3 exalt each

        # - Exalt: 1 exalt each

        

        essence_cost = 3  # Average essence cost

        chaos_cost = 0.007

        annul_cost = 3

        exalt_cost = 1

        

        # Strategy 1: Essence spam for prefixes

        prefix_craft_cost = avg_attempts_prefix * essence_cost

        

        # Strategy 2: Exalt spam for suffixes (after getting prefixes)

        # Each exalt has 50% suffix chance, then need specific mod

        if suffix_probs:

            avg_exalts_per_suffix = sum(2 / p['probability'] for p in suffix_probs)

            suffix_craft_cost = avg_exalts_per_suffix * exalt_cost

        else:

            suffix_craft_cost = 0

        

        # Total cost

        total_cost = prefix_craft_cost + suffix_craft_cost

        

        # Cap at reasonable max

        total_cost = min(total_cost, 5000)  # Max 5000 exalts

        

        return {

            'total_exalt': round(total_cost, 1),

            'total_divine': round(total_cost / CURRENCY_TO_EXALT['divine'], 2),

            'prefix_cost': round(prefix_craft_cost, 1),

            'suffix_cost': round(suffix_craft_cost, 1),

            'avg_essence_attempts': round(avg_attempts_prefix, 1),

            'details': details

        }

    

    def analyze_all(self) -> List[dict]:

        """Analyze all opportunities"""

        opportunities = []

        

        for build_name, build_info in POPULAR_BUILDS.items():

            for item in build_info['items']:

                slot = item['slot']

                item_type = item['item_type']

                base_name = item['base']

                target_mods = item['target_mods']

                estimated_sale = item['estimated_sale']

                

                # Get base price

                base_cost = self.get_base_price_exalt(base_name)

                

                # Calculate crafting cost

                craft_result = self.calculate_crafting_cost(item_type, target_mods)

                craft_cost = craft_result['total_exalt']

                

                # Calculate ROI

                total_cost = base_cost + craft_cost

                finished_value = estimated_sale * CURRENCY_TO_EXALT['divine']

                profit = finished_value - total_cost

                roi = (profit / total_cost * 100) if total_cost > 0 else 0

                

                opportunities.append({

                    'build': build_name,

                    'demand': build_info['demand'],

                    'slot': slot,

                    'base': base_name,

                    'item_type': item_type,

                    'base_cost_exalt': round(base_cost, 2),

                    'craft_cost_exalt': round(craft_cost, 1),

                    'craft_cost_divine': round(craft_cost / CURRENCY_TO_EXALT['divine'], 2),

                    'total_cost_divine': round(total_cost / CURRENCY_TO_EXALT['divine'], 2),

                    'estimated_sale_divine': estimated_sale,

                    'profit_divine': round(profit / CURRENCY_TO_EXALT['divine'], 1),

                    'roi_percent': round(roi, 1),

                    'craft_details': craft_result

                })

        

        # Sort by profit (not ROI - more realistic)

        opportunities.sort(key=lambda x: -x['profit_divine'])

        

        return opportunities

    

    def close(self):

        self.conn.close()





def main():

    print("="*70)

    print("PoE2 Build-Based Profit Analysis (Fixed)")

    print("="*70)

    

    analyzer = FixedAnalyzer()

    opportunities = analyzer.analyze_all()

    

    # Display results

    print(f"\n{'Build':<15} {'Slot':<20} {'Base':<8} {'Craft':<10} {'Sale':<8} {'Profit':<10} {'ROI':<8}")

    print("-"*80)

    

    for opp in opportunities:

        build = opp['build'][:14]

        slot = opp['slot'][:19]

        base = f"{opp['base_cost_exalt']:.0f}ex"

        craft = f"{opp['craft_cost_divine']:.1f}div"

        sale = f"{opp['estimated_sale_divine']}div"

        profit = f"{opp['profit_divine']:.1f}div"

        roi = f"{opp['roi_percent']:.0f}%"

        

        print(f"{build:<15} {slot:<20} {base:<8} {craft:<10} {sale:<8} {profit:<10} {roi:<8}")

    

    # Top 3 detailed

    print("\n" + "="*70)

    print("TOP 3 Opportunities (Detailed)")

    print("="*70)

    

    for i, opp in enumerate(opportunities[:3], 1):

        print(f"\n#{i} {opp['build']} - {opp['slot']}")

        print(f"   Base: {opp['base']} ({opp['base_cost_exalt']:.1f} exalt)")

        print(f"   Crafting cost: {opp['craft_cost_divine']:.2f} Divine ({opp['craft_cost_exalt']:.0f} exalt)")

        print(f"   Total investment: {opp['total_cost_divine']:.2f} Divine")

        print(f"   Expected sale: {opp['estimated_sale_divine']} Divine")

        print(f"   Profit: {opp['profit_divine']:.1f} Divine")

        print(f"   ROI: {opp['roi_percent']:.0f}%")

        

        print(f"\n   Mod breakdown:")

        for detail in opp['craft_details']['details']:

            if 'error' in detail:

                print(f"     ✗ {detail['mod']}: {detail['error']}")

            else:

                print(f"     ✓ {detail['mod'][:40]}: {detail['probability']}% (W:{detail['weight']})")

        

        print(f"\n   Cost breakdown:")

        print(f"     - Prefix crafting: {opp['craft_details']['prefix_cost']:.0f} exalt")

        print(f"     - Suffix crafting: {opp['craft_details']['suffix_cost']:.0f} exalt")

    

    # Save

    with open(OUTPUT_FILE, 'w') as f:

        json.dump(opportunities, f, indent=2, ensure_ascii=False)

    

    print(f"\n[SAVED] {OUTPUT_FILE}")

    analyzer.close()





if __name__ == "__main__":

    main()

