
#!/usr/bin/env python3

"""

PoE2DB Modifiers Scraper - Full Version

Scrapes all item type modifiers for crafting calculations

"""

from selenium import webdriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By

import time

import json

import os

import sys



sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



# 모든 아이템 타입 URL

ITEM_TYPE_URLS = {

    # Jewellery

    'Amulets': 'https://poe2db.tw/us/Amulets#ModifiersCalc',

    'Rings': 'https://poe2db.tw/us/Rings#ModifiersCalc',

    'Belts': 'https://poe2db.tw/us/Belts#ModifiersCalc',

    

    # Body Armours

    'Body_Armours_str': 'https://poe2db.tw/us/Body_Armours_str#ModifiersCalc',

    'Body_Armours_dex': 'https://poe2db.tw/us/Body_Armours_dex#ModifiersCalc',

    'Body_Armours_int': 'https://poe2db.tw/us/Body_Armours_int#ModifiersCalc',

    'Body_Armours_str_dex': 'https://poe2db.tw/us/Body_Armours_str_dex#ModifiersCalc',

    'Body_Armours_str_int': 'https://poe2db.tw/us/Body_Armours_str_int#ModifiersCalc',

    'Body_Armours_dex_int': 'https://poe2db.tw/us/Body_Armours_dex_int#ModifiersCalc',

    

    # Helmets

    'Helmets_str': 'https://poe2db.tw/us/Helmets_str#ModifiersCalc',

    'Helmets_dex': 'https://poe2db.tw/us/Helmets_dex#ModifiersCalc',

    'Helmets_int': 'https://poe2db.tw/us/Helmets_int#ModifiersCalc',

    'Helmets_str_dex': 'https://poe2db.tw/us/Helmets_str_dex#ModifiersCalc',

    'Helmets_str_int': 'https://poe2db.tw/us/Helmets_str_int#ModifiersCalc',

    'Helmets_dex_int': 'https://poe2db.tw/us/Helmets_dex_int#ModifiersCalc',

    

    # Gloves

    'Gloves_str': 'https://poe2db.tw/us/Gloves_str#ModifiersCalc',

    'Gloves_dex': 'https://poe2db.tw/us/Gloves_dex#ModifiersCalc',

    'Gloves_int': 'https://poe2db.tw/us/Gloves_int#ModifiersCalc',

    'Gloves_str_dex': 'https://poe2db.tw/us/Gloves_str_dex#ModifiersCalc',

    'Gloves_str_int': 'https://poe2db.tw/us/Gloves_str_int#ModifiersCalc',

    'Gloves_dex_int': 'https://poe2db.tw/us/Gloves_dex_int#ModifiersCalc',

    

    # Boots

    'Boots_str': 'https://poe2db.tw/us/Boots_str#ModifiersCalc',

    'Boots_dex': 'https://poe2db.tw/us/Boots_dex#ModifiersCalc',

    'Boots_int': 'https://poe2db.tw/us/Boots_int#ModifiersCalc',

    'Boots_str_dex': 'https://poe2db.tw/us/Boots_str_dex#ModifiersCalc',

    'Boots_str_int': 'https://poe2db.tw/us/Boots_str_int#ModifiersCalc',

    'Boots_dex_int': 'https://poe2db.tw/us/Boots_dex_int#ModifiersCalc',

    

    # Off-hand

    'Quivers': 'https://poe2db.tw/us/Quivers#ModifiersCalc',

    'Shields_str': 'https://poe2db.tw/us/Shields_str#ModifiersCalc',

    'Shields_str_dex': 'https://poe2db.tw/us/Shields_str_dex#ModifiersCalc',

    'Shields_str_int': 'https://poe2db.tw/us/Shields_str_int#ModifiersCalc',

    'Bucklers': 'https://poe2db.tw/us/Bucklers#ModifiersCalc',

    'Foci': 'https://poe2db.tw/us/Foci#ModifiersCalc',

    

    # One Handed Weapons

    'Claws': 'https://poe2db.tw/us/Claws#ModifiersCalc',

    'Daggers': 'https://poe2db.tw/us/Daggers#ModifiersCalc',

    'Wands': 'https://poe2db.tw/us/Wands#ModifiersCalc',

    'One_Hand_Swords': 'https://poe2db.tw/us/One_Hand_Swords#ModifiersCalc',

    'One_Hand_Axes': 'https://poe2db.tw/us/One_Hand_Axes#ModifiersCalc',

    'One_Hand_Maces': 'https://poe2db.tw/us/One_Hand_Maces#ModifiersCalc',

    'Sceptres': 'https://poe2db.tw/us/Sceptres#ModifiersCalc',

    'Spears': 'https://poe2db.tw/us/Spears#ModifiersCalc',

    'Flails': 'https://poe2db.tw/us/Flails#ModifiersCalc',

    

    # Two Handed Weapons

    'Bows': 'https://poe2db.tw/us/Bows#ModifiersCalc',

    'Staves': 'https://poe2db.tw/us/Staves#ModifiersCalc',

    'Two_Hand_Swords': 'https://poe2db.tw/us/Two_Hand_Swords#ModifiersCalc',

    'Two_Hand_Axes': 'https://poe2db.tw/us/Two_Hand_Axes#ModifiersCalc',

    'Two_Hand_Maces': 'https://poe2db.tw/us/Two_Hand_Maces#ModifiersCalc',

    'Quarterstaves': 'https://poe2db.tw/us/Quarterstaves#ModifiersCalc',

    'Crossbows': 'https://poe2db.tw/us/Crossbows#ModifiersCalc',

}



class PoE2DBModsScraper:

    def __init__(self):

        self.options = Options()

        self.options.add_argument('--headless')

        self.options.add_argument('--no-sandbox')

        self.options.add_argument('--disable-dev-shm-usage')

        self.options.add_argument('--disable-gpu')

        self.options.add_argument('--window-size=1920,1080')

    

    def scrape_item_type(self, item_type: str, url: str) -> dict:

        driver = webdriver.Chrome(options=self.options)

        

        try:

            driver.get(url)

            time.sleep(4)

            

            body = driver.find_element(By.TAG_NAME, "body")

            text = body.text

            

            result = self._parse_modifiers(text, item_type)

            return result

            

        except Exception as e:

            print(f"  Error: {e}")

            return None

        finally:

            driver.quit()

    

    def _parse_modifiers(self, text: str, item_type: str) -> dict:

        lines = text.split('\n')

        

        modifiers = {

            'item_type': item_type,

            'prefix': [],

            'suffix': [],

            'desecrated_prefix': [],

            'desecrated_suffix': []

        }

        

        current_section = None

        i = 0

        

        while i < len(lines):

            line = lines[i].strip()

            

            if line == 'Base Prefix':

                current_section = 'prefix'

                i += 1

                continue

            elif line == 'Base Suffix':

                current_section = 'suffix'

                i += 1

                continue

            elif 'Desecrated Modifiers Prefix' in line:

                current_section = 'desecrated_prefix'

                i += 1

                continue

            elif 'Desecrated Modifiers Suffix' in line:

                current_section = 'desecrated_suffix'

                i += 1

                continue

            elif line == 'Total':

                current_section = None

                i += 1

                continue

            

            if current_section and i + 3 < len(lines):

                try:

                    weight = int(lines[i].strip())

                    ilvl = int(lines[i+1].strip())

                    tier = int(lines[i+2].strip())

                    name_line = lines[i+3].strip()

                    

                    name, tags = self._parse_name_tags(name_line)

                    

                    mod = {

                        'weight': weight,

                        'ilvl': ilvl,

                        'tier': tier,

                        'name': name,

                        'tags': tags

                    }

                    modifiers[current_section].append(mod)

                    i += 4

                    continue

                except ValueError:

                    pass

            

            i += 1

        

        return modifiers

    

    def _parse_name_tags(self, line: str) -> tuple:

        words = line.split()

        name_parts = []

        tag_parts = []

        

        for word in reversed(words):

            if self._is_tag(word) and not name_parts:

                tag_parts.insert(0, word)

            else:

                name_parts.insert(0, word)

        

        name = ' '.join(name_parts) if name_parts else line

        tags = tag_parts if tag_parts else []

        

        return name, tags

    

    def _is_tag(self, word: str) -> bool:

        known_tags = ['Life', 'Mana', 'Defences', 'Attack', 'Caster', 'Speed', 

                     'Critical', 'Damage', 'Resistance', 'Attribute', 'Elemental',

                     'Fire', 'Cold', 'Lightning', 'Chaos', 'Physical', 'Minion',

                     'Gem', 'Aura', 'DamageCaster', 'ElementalFireResistance',

                     'ElementalColdResistance', 'ElementalLightningResistance',

                     'ChaosResistance', 'CasterSpeed', 'LifeMana']

        return word in known_tags or (len(word) > 3 and word[0].isupper() and not word.startswith('#') and not word.startswith('('))

    

    def scrape_all(self, output_file: str = None):

        """Scrape all item types"""

        all_data = {}

        total = len(ITEM_TYPE_URLS)

        

        for i, (item_type, url) in enumerate(ITEM_TYPE_URLS.items()):

            print(f"[{i+1}/{total}] Scraping {item_type}...")

            

            result = self.scrape_item_type(item_type, url)

            

            if result:

                prefix_count = len(result['prefix'])

                suffix_count = len(result['suffix'])

                print(f"  -> Prefix: {prefix_count}, Suffix: {suffix_count}")

                all_data[item_type] = result

            else:

                print(f"  -> Failed")

            

            # Rate limit

            time.sleep(1)

        

        # Save to file

        if output_file:

            with open(output_file, 'w') as f:

                json.dump(all_data, f, indent=2)

            print(f"\nSaved all data to {output_file}")

        

        return all_data





def main():

    scraper = PoE2DBModsScraper()

    

    output_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    output_file = os.path.join(output_dir, 'data', 'modifier_data.json')

    

    # Create data directory if needed

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    

    print("=" * 50)

    print("PoE2DB Modifier Scraper")

    print(f"Total item types: {len(ITEM_TYPE_URLS)}")

    print(f"Estimated time: ~{len(ITEM_TYPE_URLS) * 5 // 60} minutes")

    print("=" * 50)

    

    all_data = scraper.scrape_all(output_file)

    

    # Summary

    print("\n" + "=" * 50)

    print("SUMMARY")

    print("=" * 50)

    

    total_prefix = 0

    total_suffix = 0

    

    for item_type, data in all_data.items():

        p = len(data['prefix'])

        s = len(data['suffix'])

        total_prefix += p

        total_suffix += s

        print(f"{item_type}: {p} prefix, {s} suffix")

    

    print(f"\nTotal: {total_prefix} prefixes, {total_suffix} suffixes")

    print(f"Grand total: {total_prefix + total_suffix} modifiers")





if __name__ == "__main__":

    main()

