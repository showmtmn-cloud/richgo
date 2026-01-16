
#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

Step 7: Popular Builds Analysis

- Identify high-demand items based on popular builds

- Calculate crafting costs and ROI

"""

import json

import sqlite3

from pathlib import Path

from typing import Dict, List



BASE_DIR = Path("/home/ubuntu/poe2-profit-optimizer/backend")

DB_PATH = BASE_DIR / "poe2_profit_optimizer.db"

OUTPUT_FILE = BASE_DIR / "data" / "build_based_opportunities.json"



# ============================================================

# Popular Builds Data (PoE2 Current Meta)

# ============================================================

POPULAR_BUILDS = {

    "Witch_ES_Caster": {

        "description": "Energy Shield 기반 마법사 (인기도: 매우 높음)",

        "demand": "very_high",

        "items": {

            "Body Armour": {

                "base": "Exquisite Leather",  # ES base

                "priority_mods": [

                    {"name": "maximum Energy Shield", "type": "prefix", "tier": 1},

                    {"name": "increased Energy Shield", "type": "prefix", "tier": 1},

                    {"name": "maximum Life", "type": "prefix", "tier": 2},

                    {"name": "Fire Resistance", "type": "suffix", "tier": 2},

                    {"name": "Cold Resistance", "type": "suffix", "tier": 2},

                ],

                "estimated_value": 80  # Divine

            },

            "Helmet": {

                "base": "Sandsworn Tiara",

                "priority_mods": [

                    {"name": "maximum Energy Shield", "type": "prefix", "tier": 1},

                    {"name": "increased Energy Shield", "type": "prefix", "tier": 1},

                    {"name": "Fire Resistance", "type": "suffix", "tier": 2},

                ],

                "estimated_value": 50

            }

        }

    },

    "Warrior_Life_Melee": {

        "description": "Life 기반 근접 전사 (인기도: 높음)",

        "demand": "high",

        "items": {

            "Body Armour": {

                "base": "Sacrificial Regalia",

                "priority_mods": [

                    {"name": "maximum Life", "type": "prefix", "tier": 1},

                    {"name": "increased Armour", "type": "prefix", "tier": 1},

                    {"name": "Fire Resistance", "type": "suffix", "tier": 2},

                    {"name": "Cold Resistance", "type": "suffix", "tier": 2},

                    {"name": "Lightning Resistance", "type": "suffix", "tier": 2},

                ],

                "estimated_value": 60

            },

            "Gloves": {

                "base": "Cultist Gauntlets",

                "priority_mods": [

                    {"name": "Physical Damage", "type": "prefix", "tier": 1},

                    {"name": "maximum Life", "type": "prefix", "tier": 2},

                    {"name": "Attack Speed", "type": "suffix", "tier": 2},

                ],

                "estimated_value": 40

            }

        }

    },

    "Ranger_Evasion_Bow": {

        "description": "Evasion 기반 활 레인저 (인기도: 높음)",

        "demand": "high",

        "items": {

            "Bow": {

                "base": "Obliterator Bow",

                "priority_mods": [

                    {"name": "Physical Damage", "type": "prefix", "tier": 1},

                    {"name": "increased Physical Damage", "type": "prefix", "tier": 1},

                    {"name": "Critical", "type": "suffix", "tier": 2},

                    {"name": "Attack Speed", "type": "suffix", "tier": 2},

                ],

                "estimated_value": 100

            },

            "Boots": {

                "base": "Drakeskin Boots",

                "priority_mods": [

                    {"name": "Movement Speed", "type": "prefix", "tier": 1},

                    {"name": "maximum Life", "type": "prefix", "tier": 2},

                    {"name": "Fire Resistance", "type": "suffix", "tier": 2},

                ],

                "estimated_value": 40

            }

        }

    },

    "Monk_Attack_Speed": {

        "description": "공격 속도 기반 몽크 (인기도: 매우 높음)",

        "demand": "very_high",

        "items": {

            "Amulet": {

                "base": "Gold Amulet",

                "priority_mods": [

                    {"name": "maximum Life", "type": "prefix", "tier": 1},

                    {"name": "Physical Damage", "type": "prefix", "tier": 2},

                    {"name": "Attack Speed", "type": "suffix", "tier": 1},

                    {"name": "Critical", "type": "suffix", "tier": 2},

                ],

                "estimated_value": 70

            },

            "Ring": {

                "base": "Ruby Ring",

                "priority_mods": [

                    {"name": "Physical Damage", "type": "prefix", "tier": 1},

                    {"name": "maximum Life", "type": "prefix", "tier": 2},

                    {"name": "Attack Speed", "type": "suffix", "tier": 2},

                ],

                "estimated_value": 50

            }

        }

    },

    "Sorceress_Spell_Damage": {

        "description": "스펠 데미지 소서리스 (인기도: 높음)",

        "demand": "high",

        "items": {

            "Wand": {

                "base": "Dueling Wand",

                "priority_mods": [

                    {"name": "Spell Damage", "type": "prefix", "tier": 1},

                    {"name": "Extra Fire Damage", "type": "prefix", "tier": 1},

                    {"name": "Cast Speed", "type": "suffix", "tier": 1},

                ],

                "estimated_value": 80

            },

            "Staff": {

                "base": "Voltaic Staff",

                "priority_mods": [

                    {"name": "Spell Damage", "type": "prefix", "tier": 1},

                    {"name": "Extra Lightning Damage", "type": "prefix", "tier": 1},

                    {"name": "Cast Speed", "type": "suffix", "tier": 1},

                ],

                "estimated_value": 100

            }

        }

    }

}



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





class BuildBasedAnalyzer:

    def __init__(self):

        self.conn = sqlite3.connect(DB_PATH)

        self.conn.row_factory = sqlite3.Row

        self.base_prices = self._load_base_prices()

    

    def _load_base_prices(self) -> dict:

        """Load collected base prices"""

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

            return 1.0  # Default 1 exalt if unknown

        

        amount = price_data.get('amount', 1)

        currency = price_data.get('currency', 'exalted')

        multiplier = CURRENCY_TO_EXALT.get(currency, 1)

        

        return amount * multiplier

    

    def get_mod_probability(self, item_type: str, mod_name: str, 

                            mod_type: str, ilvl: int = 82) -> dict:

        """Get probability of hitting a mod"""

        cursor = self.conn.cursor()

        

        # Find matching item type in DB

        cursor.execute("""

            SELECT DISTINCT item_type FROM modifier_tiers

        """)

        available_types = [r[0] for r in cursor.fetchall()]

        

        # Try to match item type

        matched_type = None

        item_type_lower = item_type.lower()

        

        for t in available_types:

            if item_type_lower in t.lower() or t.lower() in item_type_lower:

                matched_type = t

                break

        

        if not matched_type:

            # Try partial match

            if 'armour' in item_type_lower or 'body' in item_type_lower:

                matched_type = 'Body_Armours_str'

            elif 'helmet' in item_type_lower:

                matched_type = 'Helmets_str'

            elif 'glove' in item_type_lower:

                matched_type = 'Gloves_str'

            elif 'boot' in item_type_lower:

                matched_type = 'Boots_str'

            elif 'amulet' in item_type_lower:

                matched_type = 'Amulets'

            elif 'ring' in item_type_lower:

                matched_type = 'Rings'

            elif 'belt' in item_type_lower:

                matched_type = 'Belts'

            elif 'wand' in item_type_lower:

                matched_type = 'Wands'

            elif 'staff' in item_type_lower:

                matched_type = 'Staves'

            elif 'bow' in item_type_lower:

                matched_type = 'Bows'

        

        if not matched_type:

            return {'error': f'Unknown item type: {item_type}'}

        

        # Get all mods

        cursor.execute("""

            SELECT m.name, mt.weight, mt.tier

            FROM modifiers m

            JOIN modifier_tiers mt ON m.id = mt.modifier_id

            WHERE mt.item_type = ?

            AND mt.min_ilvl <= ?

            AND m.mod_type = ?

            AND mt.is_desecrated = 0

        """, (matched_type, ilvl, mod_type))

        

        mods = cursor.fetchall()

        if not mods:

            return {'error': f'No mods for {matched_type}'}

        

        total_weight = sum(m['weight'] for m in mods)

        

        # Find target mod (partial match)

        for m in mods:

            if mod_name.lower() in m['name'].lower():

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

        

        return {'error': f'Mod "{mod_name}" not found in {matched_type}'}

    

    def calculate_crafting_cost(self, item_type: str, 

                                 priority_mods: List[dict]) -> dict:

        """Calculate expected crafting cost for target mods"""

        total_cost = 0

        mod_details = []

        

        # Simplified approach: 

        # - First mod via Essence (guaranteed) = 2 exalt

        # - Additional mods via Exalt = depends on probability

        

        for i, mod in enumerate(priority_mods):

            mod_name = mod.get('name', '')

            mod_type = mod.get('type', 'prefix')

            tier = mod.get('tier', 2)

            

            prob_data = self.get_mod_probability(item_type, mod_name, mod_type)

            

            if prob_data.get('error'):

                mod_details.append({

                    'mod': mod_name,

                    'error': prob_data['error'],

                    'cost': 0

                })

                continue

            

            # First mod: Essence (cheaper)

            if i == 0:

                cost = 3  # Essence cost ~3 exalt

                method = "Essence"

            else:

                # Exalt: 50% prefix/suffix chance, then mod probability

                base_prob = prob_data['probability']

                

                # Adjust for slot selection (50% prefix or suffix)

                final_prob = base_prob * 0.5

                avg_attempts = 1 / final_prob if final_prob > 0 else 100

                

                # Each exalt = 1 exalt

                cost = avg_attempts * 1

                method = "Exalt"

            

            total_cost += cost

            mod_details.append({

                'mod': prob_data.get('mod', mod_name),

                'method': method,

                'probability': round(prob_data.get('probability', 0) * 100, 2),

                'cost_exalt': round(cost, 1)

            })

        

        return {

            'total_exalt': round(total_cost, 1),

            'total_divine': round(total_cost / CURRENCY_TO_EXALT['divine'], 2),

            'details': mod_details

        }

    

    def analyze_all_builds(self) -> List[dict]:

        """Analyze all popular builds and find opportunities"""

        opportunities = []

        

        for build_name, build_info in POPULAR_BUILDS.items():

            for slot, item_info in build_info['items'].items():

                base_name = item_info['base']

                priority_mods = item_info['priority_mods']

                estimated_value = item_info['estimated_value']

                

                # Get base price

                base_cost = self.get_base_price_exalt(base_name)

                

                # Calculate crafting cost

                craft_result = self.calculate_crafting_cost(slot, priority_mods)

                craft_cost = craft_result['total_exalt']

                

                # Calculate ROI

                total_cost = base_cost + craft_cost

                finished_value = estimated_value * CURRENCY_TO_EXALT['divine']

                profit = finished_value - total_cost

                roi = (profit / total_cost * 100) if total_cost > 0 else 0

                

                opportunities.append({

                    'build': build_name,

                    'build_demand': build_info['demand'],

                    'slot': slot,

                    'base': base_name,

                    'base_cost_exalt': round(base_cost, 2),

                    'craft_cost_exalt': round(craft_cost, 1),

                    'craft_cost_divine': round(craft_cost / CURRENCY_TO_EXALT['divine'], 2),

                    'total_cost_exalt': round(total_cost, 1),

                    'total_cost_divine': round(total_cost / CURRENCY_TO_EXALT['divine'], 2),

                    'estimated_sale_divine': estimated_value,

                    'profit_exalt': round(profit, 1),

                    'profit_divine': round(profit / CURRENCY_TO_EXALT['divine'], 1),

                    'roi_percent': round(roi, 1),

                    'craft_details': craft_result['details'],

                    'target_mods': [m['name'] for m in priority_mods]

                })

        

        # Sort by ROI

        opportunities.sort(key=lambda x: -x['roi_percent'])

        

        return opportunities

    

    def close(self):

        self.conn.close()





def main():

    print("="*70)

    print("PoE2 Build-Based Profit Analysis")

    print("="*70)

    

    analyzer = BuildBasedAnalyzer()

    

    print("\n[1] Analyzing popular builds...\n")

    

    opportunities = analyzer.analyze_all_builds()

    

    # Display results

    print(f"{'Build':<25} {'Slot':<15} {'Base Cost':<12} {'Craft':<12} {'Sale':<10} {'Profit':<10} {'ROI':<8}")

    print("-"*92)

    

    for opp in opportunities:

        build = opp['build'][:24]

        slot = opp['slot'][:14]

        base = f"{opp['base_cost_exalt']:.0f} ex"

        craft = f"{opp['craft_cost_divine']:.1f} div"

        sale = f"{opp['estimated_sale_divine']} div"

        profit = f"{opp['profit_divine']:.1f} div"

        roi = f"{opp['roi_percent']:.0f}%"

        

        print(f"{build:<25} {slot:<15} {base:<12} {craft:<12} {sale:<10} {profit:<10} {roi:<8}")

    

    # Top 3 detailed

    print("\n" + "="*70)

    print("TOP 3 Best Opportunities (Detailed)")

    print("="*70)

    

    for i, opp in enumerate(opportunities[:3], 1):

        print(f"\n#{i} {opp['build']} - {opp['slot']}")

        print(f"   Base: {opp['base']} ({opp['base_cost_exalt']:.0f} exalt)")

        print(f"   Craft cost: {opp['craft_cost_divine']:.2f} Divine")

        print(f"   Expected sale: {opp['estimated_sale_divine']} Divine")

        print(f"   Profit: {opp['profit_divine']:.1f} Divine")

        print(f"   ROI: {opp['roi_percent']:.0f}%")

        print(f"   Demand: {opp['build_demand']}")

        print(f"   Target mods: {', '.join(opp['target_mods'][:3])}")

        

        print(f"\n   Crafting breakdown:")

        for detail in opp['craft_details'][:4]:

            if 'error' in detail:

                print(f"     - {detail['mod']}: {detail['error']}")

            else:

                print(f"     - {detail['mod']}: {detail['method']}, {detail['probability']}% prob, {detail['cost_exalt']:.1f} ex")

    

    # Save results

    with open(OUTPUT_FILE, 'w') as f:

        json.dump(opportunities, f, indent=2, ensure_ascii=False)

    

    print(f"\n[SAVED] {OUTPUT_FILE}")

    

    analyzer.close()

    

    print("\n" + "="*70)

    print("Analysis complete!")

    print("="*70)





if __name__ == "__main__":

    main()

