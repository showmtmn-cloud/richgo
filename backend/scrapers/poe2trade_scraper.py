
#!/usr/bin/env python3

"""

PoE2 Official Trade API Scraper - Full Version

"""

import requests

import time

import logging

from datetime import datetime

from typing import Dict, List, Optional

import pytz

import sys

import os



sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)



SYDNEY_TZ = pytz.timezone('Australia/Sydney')



CURRENCY_TO_CHAOS = {

    'transmute': 0.01,

    'augment': 0.02,

    'chance': 0.1,

    'alchemy': 0.5,

    'regal': 3,

    'chaos': 1,

    'vaal': 1.5,

    'exalted': 8.5,

    'divine': 370,

    'annul': 250,

}



class PoE2TradeScraper:

    def __init__(self):

        self.base_url = "https://www.pathofexile.com/api/trade2"

        self.league = "Fate of the Vaal"

        self.session = requests.Session()

        self.session.headers.update({

            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',

            'Accept': 'application/json',

            'Content-Type': 'application/json'

        })

        self.last_request_time = 0

        self.min_request_interval = 1.5

    

    def _rate_limit(self):

        elapsed = time.time() - self.last_request_time

        if elapsed < self.min_request_interval:

            time.sleep(self.min_request_interval - elapsed)

        self.last_request_time = time.time()

    

    def _convert_to_chaos(self, amount: float, currency: str) -> float:

        multiplier = CURRENCY_TO_CHAOS.get(currency.lower(), 1)

        return amount * multiplier

    

    def search_base_item(self, base_type: str, min_ilvl: int = None, max_results: int = 5) -> Optional[Dict]:

        self._rate_limit()

        

        query = {

            "query": {

                "type": base_type,

                "filters": {

                    "type_filters": {

                        "filters": {

                            "rarity": {"option": "nonunique"}

                        }

                    }

                }

            },

            "sort": {"price": "asc"}

        }

        

        if min_ilvl:

            query["query"]["filters"]["misc_filters"] = {

                "filters": {"ilvl": {"min": min_ilvl}}

            }

        

        try:

            url = f"{self.base_url}/search/poe2/{self.league.replace(' ', '%20')}"

            response = self.session.post(url, json=query)

            response.raise_for_status()

            data = response.json()

            

            if "error" in data:

                logger.error(f"API Error: {data['error']}")

                return None

            

            return {

                "search_id": data.get("id"),

                "total": data.get("total", 0),

                "result_ids": data.get("result", [])[:max_results]

            }

        except Exception as e:

            logger.error(f"Search error for {base_type}: {e}")

            return None

    

    def fetch_item_details(self, item_ids: List[str], search_id: str) -> Optional[List[Dict]]:

        if not item_ids:

            return []

        self._rate_limit()

        

        try:

            ids_str = ",".join(item_ids[:10])

            url = f"{self.base_url}/fetch/{ids_str}?query={search_id}"

            response = self.session.get(url)

            response.raise_for_status()

            return response.json().get("result", [])

        except Exception as e:

            logger.error(f"Fetch error: {e}")

            return None

    

    def get_base_price(self, base_type: str, min_ilvl: int = 82) -> Optional[Dict]:

        search_result = self.search_base_item(base_type, min_ilvl, max_results=5)

        if not search_result or not search_result["result_ids"]:

            return None

        

        items = self.fetch_item_details(search_result["result_ids"], search_result["search_id"])

        if not items:

            return None

        

        prices_chaos = []

        for item in items:

            try:

                price_info = item.get("listing", {}).get("price", {})

                amount = price_info.get("amount", 0)

                currency = price_info.get("currency", "chaos")

                chaos_value = self._convert_to_chaos(amount, currency)

                prices_chaos.append(chaos_value)

            except:

                pass

        

        if not prices_chaos:

            return None

        

        return {

            "base_type": base_type,

            "min_ilvl": min_ilvl,

            "total_listings": search_result["total"],

            "lowest_price_chaos": min(prices_chaos),

            "avg_price_chaos": sum(prices_chaos) / len(prices_chaos),

            "sample_size": len(prices_chaos)

        }





if __name__ == "__main__":

    scraper = PoE2TradeScraper()

    # API에 있는 실제 아이템으로 테스트

    test_bases = ["Stellar Amulet", "Gold Ring", "Leather Vest", "Glass Shank"]

    

    print("\n=== Base Item Price Test ===\n")

    for base in test_bases:

        result = scraper.get_base_price(base, min_ilvl=80)

        if result:

            print(f"{base}:")

            print(f"  Lowest: {result['lowest_price_chaos']:.2f} chaos")

            print(f"  Listings: {result['total_listings']}")

        else:

            print(f"{base}: No results")

        print()

