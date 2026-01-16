
#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

Step 5: Check API status and proceed accordingly

- If API OK: Start price collection

- If API blocked: Build profit calculation algorithm

"""

import requests

import json

import sqlite3

import time

from pathlib import Path

from typing import Dict, List, Optional



BASE_DIR = Path("/home/ubuntu/poe2-profit-optimizer/backend")

DB_PATH = BASE_DIR / "poe2_profit_optimizer.db"



# =============================================================================

# Part 1: API Status Check

# =============================================================================

def check_api_status() -> bool:

    """Check if Trade API is accessible"""

    print("="*60)

    print("[1] Checking Trade API Status...")

    print("="*60)

    

    headers = {

        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",

        "Accept": "application/json",

    }

    

    try:

        response = requests.get(

            "https://www.pathofexile.com/api/trade2/data/leagues",

            headers=headers,

            timeout=15

        )

        

        if response.status_code == 200:

            data = response.json()

            leagues = data.get('result', [])

            print(f"[OK] API accessible! Found {len(leagues)} leagues")

            

            # Find current league

            for league in leagues:

                if 'vaal' in league.get('id', '').lower():

                    print(f"  -> Current league: {league['id']}")

            return True

        else:

            print(f"[BLOCKED] HTTP {response.status_code}")

            return False

            

    except Exception as e:

        print(f"[ERROR] {e}")

        return False



# =============================================================================

# Part 2A: Price Collection (if API OK)

# =============================================================================

class PriceCollector:

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update({

            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",

            "Accept": "application/json",

            "Content-Type": "application/json"

        })

        self.league = "Fate of the Vaal"

        self.base_url = "https://www.pathofexile.com/api/trade2"

    

    def get_currency_prices(self) -> Dict:

        """Get currency exchange rates from trade"""

        print("\n[2A] Collecting Currency Prices...")

        print("-"*40)

        

        # Get static data for currency IDs

        try:

            response = self.session.get(

                f"{self.base_url}/data/static",

                timeout=15

            )

            

            if response.status_code != 200:

                print(f"  [ERROR] HTTP {response.status_code}")

                return {}

            

            data = response.json()

            currencies = {}

            

            # Find currency category

            for group in data.get('result', []):

                if group.get('id') == 'Currency':

                    for item in group.get('entries', []):

                        currencies[item.get('id')] = item.get('text')

            

            print(f"  Found {len(currencies)} currency types")

            return currencies

            

        except Exception as e:

            print(f"  [ERROR] {e}")

            return {}

    

    def search_base_item_price(self, base_name: str, min_ilvl: int = 80) -> Optional[Dict]:

        """Search for base item prices"""

        print(f"\n  Searching: {base_name} (ilvl {min_ilvl}+)")

        

        query = {

            "query": {

                "status": {"option": "online"},

                "type": base_name,

                "filters": {

                    "misc_filters": {

                        "filters": {

                            "ilvl": {"min": min_ilvl}

                        }

                    },

                    "type_filters": {

                        "filters": {

                            "rarity": {"option": "nonunique"}

                        }

                    }

                }

            },

            "sort": {"price": "asc"}

        }

        

        try:

            # Search

            response = self.session.post(

                f"{self.base_url}/search/poe2/{self.league}",

                json=query,

                timeout=15

            )

            

            if response.status_code != 200:

                print(f"    [ERROR] Search failed: HTTP {response.status_code}")

                return None

            

            search_data = response.json()

            result_ids = search_data.get('result', [])[:5]  # Get first 5

            

            if not result_ids:

                print(f"    No results found")

                return None

            

            # Fetch item details

            time.sleep(1)  # Rate limit

            

            fetch_response = self.session.get(

                f"{self.base_url}/fetch/{','.join(result_ids)}",

                params={"query": search_data.get('id')},

                timeout=15

            )

            

            if fetch_response.status_code != 200:

                print(f"    [ERROR] Fetch failed: HTTP {fetch_response.status_code}")

                return None

            

            items = fetch_response.json().get('result', [])

            

            # Extract prices

            prices = []

            for item in items:

                listing = item.get('listing', {})

                price = listing.get('price', {})

                if price:

                    prices.append({

                        'amount': price.get('amount'),

                        'currency': price.get('currency'),

                        'ilvl': item.get('item', {}).get('ilvl')

                    })

            

            if prices:

                print(f"    Found {len(prices)} listings")

                print(f"    Lowest: {prices[0]['amount']} {prices[0]['currency']}")

                return {'base': base_name, 'prices': prices}

            

            return None

            

        except Exception as e:

            print(f"    [ERROR] {e}")

            return None

    

    def collect_sample_prices(self):

        """Collect sample prices for testing"""

        print("\n" + "="*60)

        print("[2A] Collecting Sample Prices")

        print("="*60)

        

        # Sample base items to check

        sample_bases = [

            "Expert Vile Robe",      # ES Body Armour

            "Expert Runic Hauberk",  # Armour Body  

            "Stellar Amulet",        # Amulet

            "Sapphire Ring",         # Ring

        ]

        

        results = []

        for base in sample_bases:

            result = self.search_base_item_price(base, min_ilvl=80)

            if result:

                results.append(result)

            time.sleep(3)  # Rate limit between searches

        

        return results



# =============================================================================

# Part 2B: Profit Calculation Algorithm (if API blocked)

# =============================================================================

class ProfitCalculator:

    def __init__(self):

        self.conn = sqlite3.connect(DB_PATH)

        self.conn.row_factory = sqlite3.Row

        

        # Default currency values (in Chaos)

        # Will be updated with real prices when available

        self.currency_values = {

            'divine': 150,      # 1 Divine = 150 Chaos

            'exalt': 1,         # 1 Exalt = 1 Chaos (base unit for PoE2)

            'chaos': 0.007,     # relative to exalt

            'alchemy': 0.05,

            'transmute': 0.01,

            'augment': 0.01,

            'regal': 2,

            'annul': 3,

            'essence_lesser': 0.5,

            'essence_greater': 2,

            'essence_perfect': 10,

        }

    

    def get_mod_probability(self, item_type: str, ilvl: int, 

                            target_name: str, mod_type: str) -> Dict:

        """Get probability of hitting a mod"""

        cursor = self.conn.cursor()

        

        # Get all mods for this item type

        cursor.execute("""

            SELECT m.name, mt.weight, mt.tier, mt.min_ilvl

            FROM modifiers m

            JOIN modifier_tiers mt ON m.id = mt.modifier_id

            WHERE mt.item_type = ?

            AND mt.min_ilvl <= ?

            AND m.mod_type = ?

            AND mt.is_desecrated = 0

        """, (item_type, ilvl, mod_type))

        

        mods = cursor.fetchall()

        total_weight = sum(m['weight'] for m in mods)

        

        # Find target

        for m in mods:

            if target_name.lower() in m['name'].lower():

                prob = m['weight'] / total_weight if total_weight > 0 else 0

                return {

                    'name': m['name'],

                    'weight': m['weight'],

                    'total_weight': total_weight,

                    'probability': prob,

                    'avg_attempts': 1/prob if prob > 0 else 999

                }

        

        return {'error': f'Mod "{target_name}" not found'}

    

    def calculate_crafting_cost(self, method: str, target_mods: List[Dict],

                                 item_type: str, ilvl: int) -> Dict:

        """

        Calculate expected cost for a crafting method

        

        Methods:

        - chaos_spam: Use Chaos Orbs until hitting target

        - essence: Use Essence for guaranteed mod, then Exalt

        - transmute_regal: Transmute -> Aug -> Regal -> Exalt

        """

        

        if method == 'chaos_spam':

            return self._calc_chaos_spam(target_mods, item_type, ilvl)

        elif method == 'essence':

            return self._calc_essence_method(target_mods, item_type, ilvl)

        elif method == 'transmute_regal':

            return self._calc_transmute_regal(target_mods, item_type, ilvl)

        else:

            return {'error': f'Unknown method: {method}'}

    

    def _calc_chaos_spam(self, target_mods: List[Dict], item_type: str, ilvl: int) -> Dict:

        """Calculate cost of chaos spamming"""

        # For chaos spam, we need ALL target mods to hit

        # Probability = product of individual probabilities * combinatorial factor

        

        prefix_targets = [m for m in target_mods if m.get('type') == 'prefix']

        suffix_targets = [m for m in target_mods if m.get('type') == 'suffix']

        

        # Simplified: calculate for 1 target mod

        if len(target_mods) == 1:

            target = target_mods[0]

            prob_data = self.get_mod_probability(

                item_type, ilvl, target['name'], target['type']

            )

            

            if 'error' in prob_data:

                return prob_data

            

            avg_chaos = prob_data['avg_attempts']

            cost_exalts = avg_chaos * self.currency_values['chaos']

            

            return {

                'method': 'chaos_spam',

                'target': target['name'],

                'probability': prob_data['probability'],

                'avg_attempts': avg_chaos,

                'cost_exalts': round(cost_exalts, 2),

                'cost_divine': round(cost_exalts / self.currency_values['divine'], 3)

            }

        

        # Multiple targets - much more complex

        # Simplified approximation

        total_prob = 1

        for target in target_mods:

            prob_data = self.get_mod_probability(

                item_type, ilvl, target['name'], target['type']

            )

            if 'probability' in prob_data:

                total_prob *= prob_data['probability']

        

        avg_attempts = 1 / total_prob if total_prob > 0 else 99999

        cost_exalts = avg_attempts * self.currency_values['chaos']

        

        return {

            'method': 'chaos_spam',

            'targets': [t['name'] for t in target_mods],

            'combined_probability': total_prob,

            'avg_attempts': round(avg_attempts, 2),

            'cost_exalts': round(cost_exalts, 2),

            'cost_divine': round(cost_exalts / self.currency_values['divine'], 3),

            'note': 'This is a simplified estimate. Real probability is more complex.'

        }

    

    def _calc_essence_method(self, target_mods: List[Dict], item_type: str, ilvl: int) -> Dict:

        """Calculate cost using Essence method"""

        # Essence guarantees 1 mod, then Exalt for others

        

        if not target_mods:

            return {'error': 'No target mods specified'}

        

        # Assume first target is essence-guaranteed

        essence_mod = target_mods[0]

        remaining_mods = target_mods[1:]

        

        # Essence cost

        essence_cost = self.currency_values['essence_greater']

        

        # Exalt costs for remaining mods

        exalt_costs = []

        for mod in remaining_mods:

            prob_data = self.get_mod_probability(

                item_type, ilvl, mod['name'], mod['type']

            )

            if 'avg_attempts' in prob_data:

                # Exalt has 50% chance to hit prefix vs suffix

                exalt_multiplier = 2 if mod['type'] else 1

                avg_exalts = prob_data['avg_attempts'] * exalt_multiplier

                exalt_costs.append({

                    'mod': mod['name'],

                    'avg_exalts': avg_exalts,

                    'cost': avg_exalts * 1  # 1 Exalt = 1 Exalt

                })

        

        total_exalt_cost = sum(e['cost'] for e in exalt_costs)

        total_cost = essence_cost + total_exalt_cost

        

        return {

            'method': 'essence',

            'essence_mod': essence_mod['name'],

            'essence_cost': essence_cost,

            'exalt_details': exalt_costs,

            'total_exalt_cost': round(total_exalt_cost, 2),

            'total_cost_exalts': round(total_cost, 2),

            'cost_divine': round(total_cost / self.currency_values['divine'], 3)

        }

    

    def _calc_transmute_regal(self, target_mods: List[Dict], item_type: str, ilvl: int) -> Dict:

        """Calculate cost for Transmute -> Aug -> Regal -> Exalt method"""

        

        # Step costs

        transmute_cost = self.currency_values['transmute']

        aug_cost = self.currency_values['augment']

        regal_cost = self.currency_values['regal']

        

        # This method works best for 1-2 target mods

        if not target_mods:

            return {'error': 'No target mods'}

        

        # Calculate probability of hitting first mod with transmute

        first_mod = target_mods[0]

        prob1 = self.get_mod_probability(item_type, ilvl, first_mod['name'], first_mod['type'])

        

        if 'error' in prob1:

            return prob1

        

        avg_transmutes = prob1['avg_attempts']

        transmute_total = avg_transmutes * transmute_cost

        

        # After Regal, we have 3 mods. Then Exalt for remaining

        exalt_cost = 0

        for mod in target_mods[1:]:

            prob = self.get_mod_probability(item_type, ilvl, mod['name'], mod['type'])

            if 'avg_attempts' in prob:

                exalt_cost += prob['avg_attempts'] * 2  # 50% prefix/suffix

        

        total_cost = transmute_total + aug_cost + regal_cost + exalt_cost

        

        return {

            'method': 'transmute_regal',

            'steps': {

                'transmute': {'avg_attempts': round(avg_transmutes, 2), 'cost': round(transmute_total, 2)},

                'augment': {'cost': aug_cost},

                'regal': {'cost': regal_cost},

                'exalts': {'cost': round(exalt_cost, 2)}

            },

            'total_cost_exalts': round(total_cost, 2),

            'cost_divine': round(total_cost / self.currency_values['divine'], 3)

        }

    

    def compare_methods(self, item_type: str, ilvl: int, target_mods: List[Dict]) -> Dict:

        """Compare different crafting methods"""

        print("\n" + "="*60)

        print(f"Comparing Crafting Methods")

        print(f"Item: {item_type} @ ilvl {ilvl}")

        print(f"Targets: {[m['name'] for m in target_mods]}")

        print("="*60)

        

        methods = ['chaos_spam', 'essence', 'transmute_regal']

        results = {}

        

        for method in methods:

            result = self.calculate_crafting_cost(method, target_mods, item_type, ilvl)

            results[method] = result

            

            print(f"\n{method.upper()}:")

            if 'error' in result:

                print(f"  Error: {result['error']}")

            else:

                print(f"  Cost: {result.get('total_cost_exalts', result.get('cost_exalts', 'N/A'))} Exalts")

                print(f"  Cost: {result.get('cost_divine', 'N/A')} Divine")

        

        # Find best method

        valid_results = {k: v for k, v in results.items() if 'cost_divine' in v}

        if valid_results:

            best = min(valid_results.items(), key=lambda x: x[1]['cost_divine'])

            print(f"\n[BEST] {best[0]} - {best[1]['cost_divine']} Divine")

        

        return results

    

    def close(self):

        self.conn.close()





def run_profit_demo():

    """Demo the profit calculator"""

    print("\n" + "="*60)

    print("[2B] Profit Calculation Algorithm Demo")

    print("="*60)

    

    calc = ProfitCalculator()

    

    # Test case: ES Body Armour with Life and ES

    target_mods = [

        {'name': 'maximum Life', 'type': 'prefix'},

        {'name': 'Energy Shield', 'type': 'prefix'},

    ]

    

    calc.compare_methods('Body_Armours_int', 82, target_mods)

    

    # Test case 2: Amulet with Life

    print("\n")

    target_mods2 = [

        {'name': 'maximum Life', 'type': 'prefix'},

    ]

    

    calc.compare_methods('Amulets', 82, target_mods2)

    

    calc.close()





# =============================================================================

# Main

# =============================================================================

def main():

    print("\n" + "="*60)

    print("PoE2 Profit Optimizer - Step 5")

    print("="*60)

    

    # Check API status

    api_ok = check_api_status()

    

    if api_ok:

        print("\n[OK] API accessible - Starting price collection")

        collector = PriceCollector()

        

        # Get currency info

        currencies = collector.get_currency_prices()

        

        # Collect sample prices

        prices = collector.collect_sample_prices()

        

        print("\n" + "="*60)

        print("[DONE] Price collection complete")

        print("="*60)

        

        if prices:

            print(f"Collected prices for {len(prices)} items")

    else:

        print("\n[BLOCKED] API not accessible - Running profit algorithm demo")

        run_profit_demo()

    

    print("\n" + "="*60)

    print("[COMPLETE] Step 5 finished")

    print("="*60)



if __name__ == "__main__":

    main()

