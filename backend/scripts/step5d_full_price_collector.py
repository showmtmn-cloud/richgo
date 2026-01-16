
#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

Full Price Collector - Collects ALL items with safe rate limiting

- 3 second delay between requests

- 30 second break every 20 items

- Progress saved continuously

- Can resume if interrupted

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



# SETTINGS - Safe but reasonable

REQUEST_DELAY = 3           # 3 seconds between requests

BATCH_SIZE = 20             # Items before long break

BATCH_BREAK = 30            # 30 second break every batch

FETCH_DELAY = 1.5           # Delay between search and fetch



class FullPriceCollector:

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

        self.start_time = None

    

    def _load_existing(self) -> dict:

        """Load existing price data"""

        if PRICE_FILE.exists():

            with open(PRICE_FILE, 'r') as f:

                return json.load(f)

        return {'items': {}, 'failed': [], 'last_update': None}

    

    def _save_progress(self):

        """Save collected data"""

        self.collected['last_update'] = datetime.now().isoformat()

        PRICE_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(PRICE_FILE, 'w') as f:

            json.dump(self.collected, f, indent=2, ensure_ascii=False)

    

    def get_all_items(self) -> list:

        """Get all items from database"""

        cursor = self.conn.cursor()

        cursor.execute("""

            SELECT ib.name, it.name as type_name

            FROM item_bases ib

            LEFT JOIN item_types it ON ib.item_type_id = it.id

            ORDER BY ib.name

        """)

        return [{'name': row['name'], 'type': row['type_name']} for row in cursor.fetchall()]

    

    def get_uncollected_items(self) -> list:

        """Get items not yet collected"""

        all_items = self.get_all_items()

        collected_names = set(self.collected['items'].keys())

        failed_names = set(self.collected.get('failed', []))

        

        # Skip already collected and previously failed (no listings)

        return [item for item in all_items 

                if item['name'] not in collected_names and item['name'] not in failed_names]

    

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

            response = self.session.post(

                f"{self.base_url}/search/poe2/{self.league}",

                json=query,

                timeout=20

            )

            

            if response.status_code == 429:

                return {'error': 'RATE_LIMITED', 'retry': True}

            

            if response.status_code != 200:

                return {'error': f'HTTP {response.status_code}'}

            

            data = response.json()

            result_ids = data.get('result', [])[:3]

            

            if not result_ids:

                return {'error': 'No listings', 'no_listings': True}

            

            time.sleep(FETCH_DELAY)

            

            fetch_resp = self.session.get(

                f"{self.base_url}/fetch/{','.join(result_ids)}",

                params={"query": data.get('id')},

                timeout=20

            )

            

            if fetch_resp.status_code == 429:

                return {'error': 'RATE_LIMITED', 'retry': True}

            

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

            

            return {'error': 'No prices', 'no_listings': True}

            

        except requests.exceptions.Timeout:

            return {'error': 'Timeout', 'retry': True}

        except Exception as e:

            return {'error': str(e)}

    

    def format_time(self, seconds: float) -> str:

        """Format seconds to readable string"""

        if seconds < 60:

            return f"{int(seconds)}s"

        elif seconds < 3600:

            return f"{int(seconds/60)}m {int(seconds%60)}s"

        else:

            return f"{int(seconds/3600)}h {int((seconds%3600)/60)}m"

    

    def estimate_time(self, remaining: int) -> str:

        """Estimate time remaining"""

        # Each item: ~3s request delay + ~1.5s fetch delay = ~4.5s

        # Every 20 items: +30s break

        batches = remaining // BATCH_SIZE

        item_time = remaining * (REQUEST_DELAY + FETCH_DELAY)

        break_time = batches * BATCH_BREAK

        total = item_time + break_time

        return self.format_time(total)

    

    def collect_all(self):

        """Collect prices for all uncollected items"""

        self.start_time = time.time()

        

        all_items = self.get_all_items()

        uncollected = self.get_uncollected_items()

        

        print("="*60)

        print("Full Price Collector")

        print("="*60)

        print(f"Total items in DB: {len(all_items)}")

        print(f"Already collected: {len(self.collected['items'])}")

        print(f"Previously failed (no listings): {len(self.collected.get('failed', []))}")

        print(f"To collect: {len(uncollected)}")

        print(f"Estimated time: {self.estimate_time(len(uncollected))}")

        print("="*60)

        

        if not uncollected:

            print("\n[DONE] All items already collected!")

            return

        

        print(f"\nStarting collection...")

        print(f"Settings: {REQUEST_DELAY}s delay, {BATCH_BREAK}s break every {BATCH_SIZE} items\n")

        

        success = 0

        failed = 0

        rate_limited = 0

        

        for i, item in enumerate(uncollected):

            name = item['name']

            

            # Progress indicator

            elapsed = time.time() - self.start_time

            remaining = len(uncollected) - i

            eta = self.estimate_time(remaining)

            

            print(f"[{i+1}/{len(uncollected)}] {name[:40]:<40}", end=" ")

            

            result = self.search_single_item(name)

            

            if result.get('success'):

                lowest = result['lowest']

                print(f"✓ {lowest['amount']} {lowest['currency']}")

                

                self.collected['items'][name] = {

                    'type': item['type'],

                    'lowest': lowest,

                    'all_prices': result['all_prices'],

                    'collected_at': datetime.now().isoformat()

                }

                success += 1

                

            elif result.get('retry'):

                # Rate limited - take a long break

                print(f"⚠ RATE LIMITED - waiting 60s...")

                rate_limited += 1

                time.sleep(60)

                

                # Retry once

                result = self.search_single_item(name)

                if result.get('success'):

                    lowest = result['lowest']

                    print(f"  Retry OK: {lowest['amount']} {lowest['currency']}")

                    self.collected['items'][name] = {

                        'type': item['type'],

                        'lowest': lowest,

                        'all_prices': result['all_prices'],

                        'collected_at': datetime.now().isoformat()

                    }

                    success += 1

                else:

                    print(f"  Retry failed")

                    failed += 1

                    

            elif result.get('no_listings'):

                print(f"✗ No listings")

                if 'failed' not in self.collected:

                    self.collected['failed'] = []

                if name not in self.collected['failed']:

                    self.collected['failed'].append(name)

                failed += 1

            else:

                print(f"✗ {result.get('error', 'Unknown')}")

                failed += 1

            

            # Save progress every item

            self._save_progress()

            

            # Check if we need a batch break

            if (i + 1) % BATCH_SIZE == 0 and i < len(uncollected) - 1:

                print(f"\n--- Batch break: {BATCH_BREAK}s (collected {success}, failed {failed}) ---")

                print(f"--- Elapsed: {self.format_time(elapsed)}, ETA: {eta} ---\n")

                time.sleep(BATCH_BREAK)

            elif i < len(uncollected) - 1:

                time.sleep(REQUEST_DELAY)

        

        # Final summary

        elapsed = time.time() - self.start_time

        

        print("\n" + "="*60)

        print("COLLECTION COMPLETE")

        print("="*60)

        print(f"Success: {success}")

        print(f"Failed (no listings): {failed}")

        print(f"Rate limited events: {rate_limited}")

        print(f"Total collected: {len(self.collected['items'])}")

        print(f"Time taken: {self.format_time(elapsed)}")

        print(f"Data saved to: {PRICE_FILE}")

        print("="*60)

    

    def show_summary(self):

        """Show collected data summary"""

        print("="*60)

        print("Price Collection Summary")

        print("="*60)

        

        items = self.collected.get('items', {})

        failed = self.collected.get('failed', [])

        

        print(f"Successfully collected: {len(items)}")

        print(f"No listings (failed): {len(failed)}")

        print(f"Last update: {self.collected.get('last_update', 'N/A')}")

        

        if items:

            # Group by currency

            by_currency = {}

            for name, data in items.items():

                curr = data['lowest']['currency']

                if curr not in by_currency:

                    by_currency[curr] = []

                by_currency[curr].append((name, data['lowest']['amount']))

            

            print(f"\nBy currency:")

            for curr, item_list in sorted(by_currency.items()):

                print(f"  {curr}: {len(item_list)} items")

            

            # Most expensive items

            print(f"\nMost expensive (divine):")

            divine_items = [(n, d['lowest']['amount']) for n, d in items.items() 

                          if d['lowest']['currency'] == 'divine']

            for name, amount in sorted(divine_items, key=lambda x: -x[1])[:5]:

                print(f"  {name}: {amount} divine")

            

            print(f"\nMost expensive (exalted):")

            exalt_items = [(n, d['lowest']['amount']) for n, d in items.items() 

                         if d['lowest']['currency'] == 'exalted']

            for name, amount in sorted(exalt_items, key=lambda x: -x[1])[:5]:

                print(f"  {name}: {amount} exalted")

    

    def close(self):

        self.conn.close()





def main():

    import sys

    

    collector = FullPriceCollector()

    

    if '--show' in sys.argv:

        collector.show_summary()

    else:

        collector.collect_all()

    

    collector.close()



if __name__ == "__main__":

    main()

