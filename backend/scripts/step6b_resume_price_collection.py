
#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

Resume Price Collection - Balanced rate limiting

"""

import requests

import json

import time

from pathlib import Path

from datetime import datetime



BASE_DIR = Path("/home/ubuntu/poe2-profit-optimizer/backend")

DATA_FILE = BASE_DIR / "data" / "profitable_items.json"



# BALANCED SETTINGS

REQUEST_DELAY = 5       # 5 seconds between requests

FETCH_DELAY = 2         # 2 seconds before fetch

BATCH_SIZE = 10         # 10 items before break

BATCH_BREAK = 45        # 45 second break



class ResumePriceCollector:

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

        return {'valuable_bases': {}, 'base_prices': {}}

    

    def _save(self):

        self.data['last_update'] = datetime.now().isoformat()

        with open(DATA_FILE, 'w') as f:

            json.dump(self.data, f, indent=2, ensure_ascii=False)

    

    def search_base_price(self, base_type: str, min_ilvl: int = 80) -> dict:

        """Search for base item price"""

        query = {

            "query": {

                "status": {"option": "online"},

                "type": base_type,

                "filters": {

                    "misc_filters": {"filters": {"ilvl": {"min": min_ilvl}}},

                    "type_filters": {"filters": {"rarity": {"option": "nonunique"}}}

                }

            },

            "sort": {"price": "asc"}

        }

        

        try:

            response = self.session.post(

                f"{self.base_url}/search/poe2/{self.league}",

                json=query,

                timeout=30

            )

            

            if response.status_code == 429:

                return {'error': 'RATE_LIMITED', 'fatal': True}

            

            if response.status_code != 200:

                return {'error': f'HTTP {response.status_code}'}

            

            data = response.json()

            result_ids = data.get('result', [])[:3]

            

            if not result_ids:

                return {'error': 'No listings'}

            

            time.sleep(FETCH_DELAY)

            

            fetch_resp = self.session.get(

                f"{self.base_url}/fetch/{','.join(result_ids)}",

                params={"query": data.get('id')},

                timeout=30

            )

            

            if fetch_resp.status_code == 429:

                return {'error': 'RATE_LIMITED', 'fatal': True}

            

            if fetch_resp.status_code != 200:

                return {'error': f'Fetch HTTP {fetch_resp.status_code}'}

            

            items = fetch_resp.json().get('result', [])

            

            for item in items:

                listing = item.get('listing', {})

                price = listing.get('price', {})

                if price:

                    return {

                        'success': True,

                        'amount': price.get('amount'),

                        'currency': price.get('currency'),

                        'ilvl': item.get('item', {}).get('ilvl')

                    }

            

            return {'error': 'No price found'}

            

        except Exception as e:

            return {'error': str(e)}

    

    def resume_collection(self):

        """Resume collecting base prices"""

        print("="*60)

        print("Resume Price Collection")

        print(f"Settings: {REQUEST_DELAY}s delay, {BATCH_BREAK}s break every {BATCH_SIZE} items")

        print("="*60)

        

        valuable_bases = self.data.get('valuable_bases', {})

        already_collected = set(self.data.get('base_prices', {}).keys())

        

        to_collect = [b for b in valuable_bases.keys() if b not in already_collected]

        

        print(f"\nTotal valuable bases: {len(valuable_bases)}")

        print(f"Already collected: {len(already_collected)}")

        print(f"Remaining: {len(to_collect)}")

        

        if not to_collect:

            print("\n✅ All bases already collected!")

            return

        

        # Estimate time

        est_seconds = len(to_collect) * (REQUEST_DELAY + FETCH_DELAY)

        est_seconds += (len(to_collect) // BATCH_SIZE) * BATCH_BREAK

        print(f"Estimated time: ~{est_seconds // 60} minutes\n")

        

        success = 0

        failed = 0

        

        for i, base_name in enumerate(to_collect):

            print(f"[{i+1}/{len(to_collect)}] {base_name[:40]:<40}", end=" ")

            

            result = self.search_base_price(base_name)

            

            if result.get('fatal'):

                print(f"\n\n❌ RATE LIMITED! Stopping.")

                print(f"   Collected {success} items. Run again in 1 hour.")

                self._save()

                return

            

            if result.get('success'):

                print(f"✓ {result['amount']} {result['currency']}")

                

                base_info = valuable_bases.get(base_name, {})

                self.data['base_prices'][base_name] = {

                    'base_price': {

                        'amount': result['amount'],

                        'currency': result['currency'],

                        'ilvl': result.get('ilvl')

                    },

                    'finished_price': {

                        'amount': base_info.get('finished_price', 0),

                        'currency': base_info.get('finished_currency', '')

                    },

                    'sample_mods': base_info.get('sample_mods', [])

                }

                success += 1

            else:

                print(f"✗ {result.get('error')}")

                failed += 1

            

            self._save()

            

            # Batch break

            if (i + 1) % BATCH_SIZE == 0 and (i + 1) < len(to_collect):

                print(f"\n--- Break: {BATCH_BREAK}s (collected: {success}) ---\n")

                time.sleep(BATCH_BREAK)

            elif (i + 1) < len(to_collect):

                time.sleep(REQUEST_DELAY)

        

        print("\n" + "="*60)

        print(f"DONE: {success} success, {failed} failed")

        print(f"Total collected: {len(self.data.get('base_prices', {}))}")

        print("="*60)





if __name__ == "__main__":

    ResumePriceCollector().resume_collection()

