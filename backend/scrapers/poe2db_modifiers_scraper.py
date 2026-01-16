
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

        """Scrape all modifiers from poe2db.tw"""

        logger.info("Starting modifiers scraping...")

        

        all_mods = []

        

        # Main modifier categories

        categories = [

            ('Life', True),           # Prefix

            ('Mana', True),

            ('EnergyShield', True),

            ('Armour', True),

            ('Evasion', True),

            ('Damage', True),

            ('Resistances', False),   # Suffix

            ('Attributes', False),

            ('CriticalStrike', False),

        ]

        

        for category, is_prefix in categories:

            url = f"{self.base_url}/Modifiers/{category}"

            mods = self._scrape_category(url, category, is_prefix)

            all_mods.extend(mods)

            logger.info(f"  [{category}]: {len(mods)} modifiers")

            time.sleep(1)

        

        logger.info(f"Total: {len(all_mods)} modifiers collected")

        return all_mods

    

    def _scrape_category(self, url: str, category: str, is_prefix: bool) -> List[Dict]:

        """Scrape modifiers by category"""

        try:

            response = self.session.get(url, timeout=10)

            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            

            mods = []

            tables = soup.find_all('table')

            

            for table in tables:

                rows = table.find_all('tr')[1:]

                

                for row in rows:

                    cols = row.find_all('td')

                    

                    if len(cols) >= 4:

                        mod_data = {

                            'category': category,

                            'name': cols[0].text.strip(),

                            'tier': self._parse_tier(cols[0].text),

                            'mod_text': cols[1].text.strip() if len(cols) > 1 else "",

                            'min_ilvl': self._parse_ilvl(cols),

                            'weight': 1000,

                            'is_prefix': is_prefix,

                            'tags': [category.lower()]

                        }

                        

                        mods.append(mod_data)

            

            return mods

            

        except Exception as e:

            logger.error(f"Error scraping {category}: {e}")

            return []

    

    def _parse_tier(self, text: str) -> int:

        """Extract tier number"""

        if 'T1' in text or 'Tier 1' in text:

            return 1

        elif 'T2' in text or 'Tier 2' in text:

            return 2

        elif 'T3' in text or 'Tier 3' in text:

            return 3

        return 99

    

    def _parse_ilvl(self, cols) -> int:

        """Extract ilvl requirement"""

        for col in cols:

            text = col.text.strip()

            if 'ilvl' in text.lower() or 'level' in text.lower():

                try:

                    return int(''.join(filter(str.isdigit, text)))

                except:

                    pass

        return 1



if __name__ == "__main__":

    import os

    scraper = PoE2DBModifiersScraper()

    mods = scraper.scrape_all_modifiers()

    

    os.makedirs('../data', exist_ok=True)

    

    with open('../data/scraped_modifiers.json', 'w', encoding='utf-8') as f:

        json.dump(mods, f, indent=2, ensure_ascii=False)

    

    print(f"\nSaved: data/scraped_modifiers.json")

    print(f"Total: {len(mods)} modifiers")

