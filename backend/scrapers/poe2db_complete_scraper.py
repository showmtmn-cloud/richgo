
"""

PoE2DB Complete Scraper - v3

"""

import requests

from bs4 import BeautifulSoup

import json

import time

import re

import os

import sys

from datetime import datetime



sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)





class PoE2DBCompleteScraper:

    BASE_URL = "https://poe2db.tw"

    

    ITEM_CATEGORIES = {

        "body_armours": ["Body_Armours_str", "Body_Armours_dex", "Body_Armours_int", "Body_Armours_str_dex", "Body_Armours_str_int", "Body_Armours_dex_int"],

        "helmets": ["Helmets_str", "Helmets_dex", "Helmets_int", "Helmets_str_dex", "Helmets_str_int", "Helmets_dex_int"],

        "gloves": ["Gloves_str", "Gloves_dex", "Gloves_int", "Gloves_str_dex", "Gloves_str_int", "Gloves_dex_int"],

        "boots": ["Boots_str", "Boots_dex", "Boots_int", "Boots_str_dex", "Boots_str_int", "Boots_dex_int"],

        "shields": ["Shields_str", "Shields_str_dex", "Shields_str_int", "Bucklers", "Foci", "Quivers"],

        "jewellery": ["Rings", "Amulets", "Belts"],

        "one_hand": ["Claws", "Daggers", "Wands", "One_Hand_Swords", "One_Hand_Axes", "One_Hand_Maces", "Sceptres", "Spears", "Flails"],

        "two_hand": ["Bows", "Staves", "Two_Hand_Swords", "Two_Hand_Axes", "Two_Hand_Maces", "Quarterstaves", "Crossbows"],

    }

    

    def __init__(self, lang="us"):

        self.lang = lang

        self.session = requests.Session()

        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

        self.base_items = []

        self.modifiers = {}

    

    def fetch_page(self, path):

        url = f"{self.BASE_URL}/{self.lang}/{path}"

        for attempt in range(3):

            try:

                logger.info(f"Fetching: {url}")

                r = self.session.get(url, timeout=30)

                r.raise_for_status()

                time.sleep(1.5)

                return BeautifulSoup(r.content, 'lxml')

            except Exception as e:

                logger.error(f"Error (attempt {attempt+1}): {e}")

                if attempt < 2: time.sleep(2 ** attempt)

        return None

    

    def parse_base_items(self, soup, category, subcategory):

        items = []

        for a in soup.find_all('a', href=True):

            href = a.get('href', '')

            if not href or href.startswith('#') or '/us/' not in href:

                continue

            

            text = a.get_text(separator='\n', strip=True)

            lines = [l.strip() for l in text.split('\n') if l.strip()]

            

            if not lines or len(lines) < 2:

                continue

            

            # Skip navigation links

            if lines[0] in ['Item', 'Gem', 'Modifiers', 'Quest', 'Patreon']:

                continue

            

            item = {'name': lines[0], 'category': category, 'subcategory': subcategory, 'stats': {}}

            

            for line in lines[1:]:

                if 'Energy Shield:' in line:

                    m = re.search(r'Energy Shield:\s*(\d+)', line)

                    if m: item['stats']['energy_shield'] = int(m.group(1))

                elif 'Armour:' in line:

                    m = re.search(r'Armour:\s*(\d+)', line)

                    if m: item['stats']['armour'] = int(m.group(1))

                elif 'Evasion' in line:

                    m = re.search(r'Evasion.*?:\s*(\d+)', line)

                    if m: item['stats']['evasion'] = int(m.group(1))

                elif 'Level' in line:

                    m = re.search(r'Level\s*(\d+)', line)

                    if m: item['stats']['required_level'] = int(m.group(1))

            

            if item['stats']:

                items.append(item)

        

        return items

    

    def scrape_all(self):

        for category, subcats in self.ITEM_CATEGORIES.items():

            logger.info(f"\n{'='*50}\nCategory: {category}\n{'='*50}")

            for subcat in subcats:

                soup = self.fetch_page(subcat)

                if soup:

                    items = self.parse_base_items(soup, category, subcat)

                    logger.info(f"  [{subcat}]: {len(items)} items")

                    self.base_items.extend(items)

        return self.base_items

    

    def save_json(self, output_dir='../data'):

        os.makedirs(output_dir, exist_ok=True)

        

        out_file = os.path.join(output_dir, 'poe2db_base_items_latest.json')

        with open(out_file, 'w', encoding='utf-8') as f:

            json.dump({

                'scraped_at': datetime.now().isoformat(),

                'total': len(self.base_items),

                'items': self.base_items

            }, f, indent=2, ensure_ascii=False)

        

        logger.info(f"Saved {len(self.base_items)} items to {out_file}")

        return out_file

    

    def save_to_db(self):

        try:

            from models.database_models import SessionLocal, ItemBase

            db = SessionLocal()

            added = 0

            for item in self.base_items:

                existing = db.query(ItemBase).filter(ItemBase.name == item['name']).first()

                if not existing:

                    db.add(ItemBase(

                        name=item['name'],

                        type=item['category'],

                        subtype=item['subcategory'],

                        required_level=item['stats'].get('required_level', 1),

                        base_stats=json.dumps(item['stats'])

                    ))

                    added += 1

            db.commit()

            db.close()

            logger.info(f"Added {added} items to database")

        except Exception as e:

            logger.error(f"DB error: {e}")





def main():

    print("\n" + "="*60)

    print("  PoE2DB Complete Scraper v3")

    print("="*60 + "\n")

    

    scraper = PoE2DBCompleteScraper()

    items = scraper.scrape_all()

    

    print(f"\nTotal items: {len(items)}")

    

    scraper.save_json()

    scraper.save_to_db()

    

    print("\nDone!")





if __name__ == "__main__":

    main()

