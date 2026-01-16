
import requests

from bs4 import BeautifulSoup

import time

import json

from typing import List, Dict

import logging



logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)



class PoE2DBBasesScraper:

    def __init__(self):

        self.base_url = "https://poe2db.tw/us"

        self.session = requests.Session()

        self.session.headers.update({

            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

        })

    

    def scrape_all_bases(self) -> List[Dict]:

        """Scrape all base items"""

        logger.info("Starting base items scraping...")

        

        all_bases = []

        

        categories = [

            'Body Armours',

            'Helmets',

            'Gloves',

            'Boots',

            'Shields',

            'Weapons',

            'Rings',

            'Amulets',

            'Belts'

        ]

        

        for category in categories:

            safe_category = category.replace(' ', '_')

            url = f"{self.base_url}/{safe_category}"

            

            bases = self._scrape_category(url, category)

            all_bases.extend(bases)

            logger.info(f"  [{category}]: {len(bases)} bases")

            time.sleep(1)

        

        logger.info(f"Total: {len(all_bases)} base items collected")

        return all_bases

    

    def _scrape_category(self, url: str, category: str) -> List[Dict]:

        """Scrape bases by category"""

        try:

            response = self.session.get(url, timeout=10)

            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            

            bases = []

            items = soup.find_all('div', class_='item') or soup.find_all('tr')

            

            for item in items:

                name_elem = item.find('a') or item.find('td')

                if not name_elem:

                    continue

                

                name = name_elem.text.strip()

                

                if not name or name in ['Name', 'Type', 'Level']:

                    continue

                

                base_data = {

                    'name': name,

                    'type': category,

                    'category': self._get_category(category),

                    'required_level': self._extract_level(item),

                    'base_stats': {},

                    'drop_zones': ""

                }

                

                bases.append(base_data)

            

            return bases

            

        except Exception as e:

            logger.error(f"Error scraping {category}: {e}")

            return []

    

    def _get_category(self, item_type: str) -> str:

        """Categorize item type"""

        armour_types = ['Body Armours', 'Helmets', 'Gloves', 'Boots', 'Shields']

        weapon_types = ['Weapons']

        accessory_types = ['Rings', 'Amulets', 'Belts']

        

        if item_type in armour_types:

            return 'Armour'

        elif item_type in weapon_types:

            return 'Weapon'

        elif item_type in accessory_types:

            return 'Accessory'

        return 'Other'

    

    def _extract_level(self, element) -> int:

        """Extract level requirement"""

        text = element.text

        if 'Level' in text or 'Lvl' in text:

            try:

                return int(''.join(filter(str.isdigit, text)))

            except:

                pass

        return 1



if __name__ == "__main__":

    import os

    scraper = PoE2DBBasesScraper()

    bases = scraper.scrape_all_bases()

    

    os.makedirs('../data', exist_ok=True)

    

    with open('../data/scraped_bases.json', 'w', encoding='utf-8') as f:

        json.dump(bases, f, indent=2, ensure_ascii=False)

    

    print(f"\nSaved: data/scraped_bases.json")

    print(f"Total: {len(bases)} base items")

