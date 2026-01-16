
import requests

from bs4 import BeautifulSoup

import time

import json

from typing import List, Dict

import logging



logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)



class PoE2DBModifiersScraper:

    def __init__(self):

        self.base_url = "https://poe2db.tw/us"

        self.session = requests.Session()

        self.session.headers.update({

            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

        })

    

    def scrape_all_modifiers(self) -> List[Dict]:

        """Scrape modifiers from main page"""

        logger.info("Starting modifiers scraping from main page...")

        

        all_mods = []

        

        try:

            # Try main modifiers page

            url = f"{self.base_url}/Modifiers"

            response = self.session.get(url, timeout=10)

            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            

            # Look for modifier tables

            tables = soup.find_all('table')

            logger.info(f"Found {len(tables)} tables on page")

            

            for idx, table in enumerate(tables):

                rows = table.find_all('tr')

                logger.info(f"Table {idx+1}: {len(rows)} rows")

                

                # Skip header row

                for row in rows[1:]:

                    cols = row.find_all('td')

                    if len(cols) >= 2:

                        # Extract text from all columns

                        text_data = [col.get_text(strip=True) for col in cols]

                        

                        if text_data[0]:  # Has name

                            mod_data = {

                                'name': text_data[0],

                                'details': ' | '.join(text_data[1:]) if len(text_data) > 1 else '',

                                'source': 'poe2db_main',

                                'table_index': idx

                            }

                            all_mods.append(mod_data)

            

            logger.info(f"Total modifiers found: {len(all_mods)}")

            

        except Exception as e:

            logger.error(f"Error scraping modifiers: {e}")

        

        return all_mods



if __name__ == "__main__":

    import os

    scraper = PoE2DBModifiersScraper()

    mods = scraper.scrape_all_modifiers()

    

    os.makedirs('../data', exist_ok=True)

    

    with open('../data/scraped_modifiers_v2.json', 'w', encoding='utf-8') as f:

        json.dump(mods, f, indent=2, ensure_ascii=False)

    

    print(f"\nSaved: data/scraped_modifiers_v2.json")

    print(f"Total: {len(mods)} modifiers")

    

    # Show sample

    if mods:

        print("\nSample modifiers:")

        for mod in mods[:5]:

            print(f"  - {mod['name']}")

