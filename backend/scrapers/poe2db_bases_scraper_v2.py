
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

    

    def scrape_items_page(self) -> List[Dict]:

        """Scrape from main Items page"""

        logger.info("Scraping main Items page...")

        

        all_items = []

        

        try:

            url = f"{self.base_url}/Items"

            response = self.session.get(url, timeout=10)

            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            

            # Find all links to item categories

            links = soup.find_all('a', href=True)

            

            item_categories = []

            for link in links:

                href = link['href']

                text = link.get_text(strip=True)

                

                # Look for item type links

                if any(keyword in href for keyword in [

                    'Body_Armour', 'Helmet', 'Glove', 'Boot', 

                    'Ring', 'Amulet', 'Belt', 'Shield',

                    'Sword', 'Axe', 'Mace', 'Bow', 'Wand'

                ]):

                    if text and len(text) > 2:

                        item_categories.append({

                            'url': href if href.startswith('http') else f"{self.base_url}{href}",

                            'name': text

                        })

            

            logger.info(f"Found {len(item_categories)} item categories")

            

            # Scrape each category

            for cat in item_categories[:5]:  # Limit to 5 for testing

                logger.info(f"Scraping category: {cat['name']}")

                items = self._scrape_category(cat['url'], cat['name'])

                all_items.extend(items)

                time.sleep(1)

            

        except Exception as e:

            logger.error(f"Error scraping items page: {e}")

        

        return all_items

    

    def _scrape_category(self, url: str, category: str) -> List[Dict]:

        """Scrape a specific category page"""

        items = []

        

        try:

            response = self.session.get(url, timeout=10)

            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            

            # Look for item tables

            tables = soup.find_all('table')

            

            for table in tables:

                rows = table.find_all('tr')

                

                for row in rows[1:]:  # Skip header

                    cols = row.find_all('td')

                    if cols:

                        name = cols[0].get_text(strip=True)

                        

                        # Filter out headers and invalid names

                        if name and len(name) > 2 and name not in ['Name', 'Type', 'Level']:

                            item_data = {

                                'name': name,

                                'category': category,

                                'url': url,

                                'raw_data': ' | '.join([c.get_text(strip=True) for c in cols])

                            }

                            items.append(item_data)

            

        except Exception as e:

            logger.error(f"Error scraping {category}: {e}")

        

        return items



if __name__ == "__main__":

    import os

    scraper = PoE2DBBasesScraper()

    items = scraper.scrape_items_page()

    

    os.makedirs('../data', exist_ok=True)

    

    with open('../data/scraped_bases_v2.json', 'w', encoding='utf-8') as f:

        json.dump(items, f, indent=2, ensure_ascii=False)

    

    print(f"\nSaved: data/scraped_bases_v2.json")

    print(f"Total: {len(items)} base items")

    

    # Show sample

    if items:

        print("\nSample items:")

        for item in items[:10]:

            print(f"  - {item['name']} ({item['category']})")

