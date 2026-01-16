
#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

Smart Price Tracker

1. Find expensive finished items (100+ Divine)

2. Identify their base items

3. Track only valuable bases

"""

import requests

import json

import time

from pathlib import Path

from datetime import datetime



BASE_DIR = Path("/home/ubuntu/poe2-profit-optimizer/backend")

DATA_FILE = BASE_DIR / "data" / "profitable_items.json"



# Safe rate limiting

REQUEST_DELAY = 4

FETCH_DELAY = 2



class SmartPriceTracker:

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update({

            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",

            "Accept": "application/json",

            "Content-Type": "application/json"

        })

        self.league = "Fate of the Vaal"

        self.base_url = "https://www.pathofexile.com/api/trade2"

        self.data = self._load_existing()

    

    def _load_existing(self) -> dict:

        if DATA_FILE.exists():

            with open(DATA_FILE, 'r') as f:

                return json.load(f)

        return {

            'expensive_items': [],

            'valuable_bases': {},

            'base_prices': {},

            'last_update': None

        }

    

    def _save(self):

        self.data['last_update'] = datetime.now().isoformat()

        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(DATA_FILE, 'w') as f:

            json.dump(self.data, f, indent=2, ensure_ascii=False)

    

    def search_expensive_items(self, min_divine: int = 50, category: str = None) -> list:

        """Search for expensive items on trade"""

        print(f"\nSearching items {min_divine}+ Divine...")

        

        query = {

            "query": {

                "status": {"option": "online"},

                "filters": {

                    "trade_filters": {

                        "filters": {

                            "price": {

                                "min": min_divine,

                                "option": "divine"

                            }

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

        

        # Add category filter if specified

        if category:

            query["query"]["filters"]["type_filters"]["filters"]["category"] = {"option": category}

        

        try:

            response = self.session.post(

                f"{self.base_url}/search/poe2/{self.league}",

                json=query,

                timeout=20

            )

            

            if response.status_code != 200:

                print(f"  Error: HTTP {response.status_code}")

                return []

            

            data = response.json()

            result_ids = data.get('result', [])[:10]  # Get first 10

            total = data.get('total', 0)

            

            print(f"  Found {total} items, fetching top 10...")

            

            if not result_ids:

                return []

            

            time.sleep(FETCH_DELAY)

            

            # Fetch details

            fetch_resp = self.session.get(

                f"{self.base_url}/fetch/{','.join(result_ids)}",

                params={"query": data.get('id')},

                timeout=20

            )

            

            if fetch_resp.status_code != 200:

                print(f"  Fetch error: HTTP {fetch_resp.status_code}")

                return []

            

            items = fetch_resp.json().get('result', [])

            results = []

            

            for item in items:

                item_data = item.get('item', {})

                listing = item.get('listing', {})

                price = listing.get('price', {})

                

                results.append({

                    'name': item_data.get('name', ''),

                    'base_type': item_data.get('baseType', ''),

                    'type_line': item_data.get('typeLine', ''),

                    'ilvl': item_data.get('ilvl', 0),

                    'price_amount': price.get('amount', 0),

                    'price_currency': price.get('currency', ''),

                    'mods': {

                        'explicit': item_data.get('explicitMods', []),

                        'implicit': item_data.get('implicitMods', [])

                    }

                })

            

            return results

            

        except Exception as e:

            print(f"  Error: {e}")

            return []

    

    def search_base_price(self, base_type: str, min_ilvl: int = 80) -> dict:

        """Search for base item price"""

        print(f"  Searching base: {base_type} (ilvl {min_ilvl}+)...", end=" ")

        

        query = {

            "query": {

                "status": {"option": "online"},

                "type": base_type,

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

            response = self.session.post(

                f"{self.base_url}/search/poe2/{self.league}",

                json=query,

                timeout=20

            )

            

            if response.status_code != 200:

                print(f"HTTP {response.status_code}")

                return {'error': f'HTTP {response.status_code}'}

            

            data = response.json()

            result_ids = data.get('result', [])[:5]

            

            if not result_ids:

                print("No listings")

                return {'error': 'No listings'}

            

            time.sleep(FETCH_DELAY)

            

            fetch_resp = self.session.get(

                f"{self.base_url}/fetch/{','.join(result_ids)}",

                params={"query": data.get('id')},

                timeout=20

            )

            

            if fetch_resp.status_code != 200:

                print(f"Fetch error")

                return {'error': 'Fetch failed'}

            

            items = fetch_resp.json().get('result', [])

            

            for item in items:

                listing = item.get('listing', {})

                price = listing.get('price', {})

                if price:

                    result = {

                        'amount': price.get('amount'),

                        'currency': price.get('currency'),

                        'ilvl': item.get('item', {}).get('ilvl')

                    }

                    print(f"{result['amount']} {result['currency']}")

                    return result

            

            print("No price")

            return {'error': 'No price found'}

            

        except Exception as e:

            print(f"Error: {e}")

            return {'error': str(e)}

    

    def find_profitable_bases(self):

        """Main function: Find expensive items and their bases"""

        print("="*60)

        print("Smart Price Tracker - Finding Profitable Bases")

        print("="*60)

        

        # Categories to search

        categories = [

            ("armour.chest", "Body Armour"),

            ("armour.helmet", "Helmet"),

            ("armour.gloves", "Gloves"),

            ("armour.boots", "Boots"),

            ("accessory.amulet", "Amulet"),

            ("accessory.ring", "Ring"),

            ("accessory.belt", "Belt"),

            ("weapon.bow", "Bow"),

            ("weapon.staff", "Staff"),

            ("weapon.wand", "Wand"),

        ]

        

        all_expensive = []

        

        # Step 1: Find expensive items in each category

        print("\n[Step 1] Searching expensive finished items (50+ Divine)...\n")

        

        for cat_id, cat_name in categories:

            print(f"\n--- {cat_name} ---")

            items = self.search_expensive_items(min_divine=50, category=cat_id)

            

            for item in items:

                print(f"  {item['price_amount']} {item['price_currency']}: {item['base_type'] or item['type_line']}")

                if item.get('mods', {}).get('explicit'):

                    print(f"    Mods: {item['mods']['explicit'][:2]}")

            

            all_expensive.extend(items)

            time.sleep(REQUEST_DELAY)

        

        self.data['expensive_items'] = all_expensive

        self._save()

        

        # Step 2: Extract unique base types

        print("\n" + "="*60)

        print("[Step 2] Extracting valuable base types...")

        print("="*60)

        

        base_types = {}

        for item in all_expensive:

            base = item.get('base_type') or item.get('type_line')

            if base and base not in base_types:

                base_types[base] = {

                    'finished_price': item['price_amount'],

                    'finished_currency': item['price_currency'],

                    'sample_mods': item.get('mods', {}).get('explicit', [])[:3]

                }

        

        print(f"\nFound {len(base_types)} unique valuable bases:")

        for base, info in sorted(base_types.items(), key=lambda x: -x[1]['finished_price'])[:20]:

            print(f"  {base}: {info['finished_price']} {info['finished_currency']}")

        

        self.data['valuable_bases'] = base_types

        self._save()

        

        # Step 3: Get base item prices

        print("\n" + "="*60)

        print("[Step 3] Getting base item prices...")

        print("="*60 + "\n")

        

        base_prices = {}

        

        for i, (base, info) in enumerate(list(base_types.items())[:30]):  # Limit to 30

            price = self.search_base_price(base, min_ilvl=80)

            

            if not price.get('error'):

                base_prices[base] = {

                    'base_price': price,

                    'finished_price': {

                        'amount': info['finished_price'],

                        'currency': info['finished_currency']

                    },

                    'sample_mods': info['sample_mods']

                }

            

            time.sleep(REQUEST_DELAY)

        

        self.data['base_prices'] = base_prices

        self._save()

        

        # Step 4: Calculate profit potential

        print("\n" + "="*60)

        print("[Step 4] Profit Potential Analysis")

        print("="*60 + "\n")

        

        print(f"{'Base Item':<35} {'Base':<15} {'Finished':<15} {'Diff':<10}")

        print("-"*75)

        

        for base, data in sorted(base_prices.items(), 

                                  key=lambda x: -x[1]['finished_price']['amount']):

            base_p = data['base_price']

            fin_p = data['finished_price']

            

            base_str = f"{base_p['amount']} {base_p['currency']}"

            fin_str = f"{fin_p['amount']} {fin_p['currency']}"

            

            print(f"{base[:35]:<35} {base_str:<15} {fin_str:<15}")

        

        print("\n" + "="*60)

        print(f"Data saved to: {DATA_FILE}")

        print("="*60)

    

    def show_summary(self):

        """Show current data summary"""

        print("="*60)

        print("Profitable Items Summary")

        print("="*60)

        

        print(f"\nExpensive items found: {len(self.data.get('expensive_items', []))}")

        print(f"Valuable bases: {len(self.data.get('valuable_bases', {}))}")

        print(f"Bases with prices: {len(self.data.get('base_prices', {}))}")

        print(f"Last update: {self.data.get('last_update', 'N/A')}")

        

        if self.data.get('base_prices'):

            print("\nTop opportunities:")

            for base, data in sorted(self.data['base_prices'].items(),

                                      key=lambda x: -x[1]['finished_price']['amount'])[:10]:

                base_p = data['base_price']

                fin_p = data['finished_price']

                print(f"  {base[:40]}")

                print(f"    Base: {base_p['amount']} {base_p['currency']} → Finished: {fin_p['amount']} {fin_p['currency']}")





def main():

    import sys

    

    tracker = SmartPriceTracker()

    

    if '--show' in sys.argv:

        tracker.show_summary()

    else:

        tracker.find_profitable_bases()



if __name__ == "__main__":

    main()

