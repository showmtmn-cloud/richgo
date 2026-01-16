
#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

Safe Price Collector - Conservative rate limiting to avoid blocks

"""

import requests

import json

import sqlite3

import time

from pathlib import Path

from datetime import datetime



BASE_DIR = Path("/home/ubuntu/poe2-profit-optimizer/backend")

DB_PATH = BASE_DIR / "poe2_profit_optimizer.db"

PRICE_FILE = BASE_DIR / "data" / "collected_prices.json"



# SAFE SETTINGS

REQUEST_DELAY = 5       # 5 seconds between requests

MAX_ITEMS_PER_RUN = 10  # Only 10 items per run



class SafePriceCollector:

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update({

            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",

            "Accept": "application/json",

            "Content-Type": "application/json"

        })

        self.league = "Fate of the Vaal"

        self.base_url = "https://www.pathofexile.com/api/trade2"

        self.conn = sqlite3.connect(DB_PATH)

        self.conn.row_factory = sqlite3.Row

        self.collected = self._load_existing()

    

    def _load_existing(self) -> dict:

        """Load existing price data"""

        if PRICE_FILE.exists():

            with open(PRICE_FILE, 'r') as f:

                return json.load(f)

        return {'items': {}, 'last_update': None}

    

    def _save_progress(self):

        """Save collected data"""

        self.collected['last_update'] = datetime.now().isoformat()

        PRICE_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(PRICE_FILE, 'w') as f:

            json.dump(self.collected, f, indent=2)

    

    def get_uncollected_items(self, limit: int = MAX_ITEMS_PER_RUN) -> list:

        """Get items we haven't collected prices for yet"""

        cursor = self.conn.cursor()

        

        # Get items with their type info

        cursor.execute("""

            SELECT ib.name, it.name as type_name

            FROM item_bases ib

            LEFT JOIN item_types it ON ib.item_type_id = it.id

            ORDER BY ib.name

        """)

        

        all_items = [{'name': row['name'], 'type': row['type_name']} for row in cursor.fetchall()]

        

        # Filter out already collected

        uncollected = [

            item for item in all_items 

            if item['name'] not in self.collected['items']

        ]

        

        return uncollected[:limit]

    

    def search_single_item(self, item_name: str, min_ilvl: int = 75) -> dict:

        """Search for one item"""

        

        query = {

            "query": {

                "status": {"option": "online"},

                "term": item_name,

                "filters": {

                    "misc_filters": {

                        "filters": {

                            "ilvl": {"min": min_ilvl}

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

                timeout=20

            )

            

            if response.status_code != 200:

                return {'error': f'HTTP {response.status_code}'}

            

            data = response.json()

            result_ids = data.get('result', [])[:3]

            

            if not result_ids:

                return {'error': 'No listings'}

            

            time.sleep(2)

            

            # Fetch

            fetch_resp = self.session.get(

                f"{self.base_url}/fetch/{','.join(result_ids)}",

                params={"query": data.get('id')},

                timeout=20

            )

            

            if fetch_resp.status_code != 200:

                return {'error': f'Fetch HTTP {fetch_resp.status_code}'}

            

            items = fetch_resp.json().get('result', [])

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

                return {'success': True, 'listings': len(prices), 'lowest': prices[0], 'all_prices': prices}

            

            return {'error': 'No prices'}

            

        except Exception as e:

            return {'error': str(e)}

    

    def collect_batch(self):

        """Collect prices for a small batch"""

        print("="*60)

        print("Safe Price Collector")

        print(f"Settings: {REQUEST_DELAY}s delay, max {MAX_ITEMS_PER_RUN} items")

        print("="*60)

        

        items = self.get_uncollected_items()

        

        if not items:

            print(f"\n[INFO] All items collected! Total: {len(self.collected['items'])}")

            return

        

        print(f"\nTo collect: {len(items)}")

        print(f"Already have: {len(self.collected['items'])}")

        

        success = 0

        failed = 0

        

        for i, item in enumerate(items):

            name = item['name']

            print(f"\n[{i+1}/{len(items)}] {name}...", end=" ")

            

            result = self.search_single_item(name)

            

            if result.get('success'):

                lowest = result['lowest']

                print(f"OK: {lowest['amount']} {lowest['currency']}")

                

                self.collected['items'][name] = {

                    'type': item['type'],

                    'lowest': lowest,

                    'all_prices': result['all_prices'],

                    'collected_at': datetime.now().isoformat()

                }

                success += 1

            else:

                print(f"FAIL: {result.get('error')}")

                failed += 1

            

            self._save_progress()

            

            if i < len(items) - 1:

                print(f"  Waiting {REQUEST_DELAY}s...", end="")

                time.sleep(REQUEST_DELAY)

                print(" done")

        

        print("\n" + "="*60)

        print(f"Done: {success} success, {failed} failed")

        print(f"Total: {len(self.collected['items'])} items")

        print("="*60)

    

    def show_collected(self):

        """Show collected prices"""

        print("="*60)

        print("Collected Prices")

        print("="*60)

        

        if not self.collected['items']:

            print("No items collected yet.")

            return

        

        print(f"Total: {len(self.collected['items'])} items")

        print(f"Last update: {self.collected.get('last_update', 'N/A')}")

        

        # Show sample

        print("\nSample prices:")

        for name, data in list(self.collected['items'].items())[:10]:

            price = data['lowest']

            print(f"  {name}: {price['amount']} {price['currency']}")

    

    def close(self):

        self.conn.close()





def main():

    import sys

    collector = SafePriceCollector()

    

    if '--show' in sys.argv:

        collector.show_collected()

    else:

        collector.collect_batch()

    

    collector.close()



if __name__ == "__main__":

    main()

