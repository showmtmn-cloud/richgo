
#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

PoE2DB Modifiers Scraper V4 - Correct Parser

Table structure: [Tier, ModName, iLvl, "Weight Description Tags"]

"""

from selenium import webdriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By

import time

import json

import os

import re



ITEM_TYPE_URLS = {

    'Amulets': 'https://poe2db.tw/us/Amulets#ModifiersCalc',

    'Rings': 'https://poe2db.tw/us/Rings#ModifiersCalc',

    'Belts': 'https://poe2db.tw/us/Belts#ModifiersCalc',

    'Body_Armours_str': 'https://poe2db.tw/us/Body_Armours_str#ModifiersCalc',

    'Body_Armours_dex': 'https://poe2db.tw/us/Body_Armours_dex#ModifiersCalc',

    'Body_Armours_int': 'https://poe2db.tw/us/Body_Armours_int#ModifiersCalc',

    'Body_Armours_str_dex': 'https://poe2db.tw/us/Body_Armours_str_dex#ModifiersCalc',

    'Body_Armours_str_int': 'https://poe2db.tw/us/Body_Armours_str_int#ModifiersCalc',

    'Body_Armours_dex_int': 'https://poe2db.tw/us/Body_Armours_dex_int#ModifiersCalc',

    'Helmets_str': 'https://poe2db.tw/us/Helmets_str#ModifiersCalc',

    'Helmets_dex': 'https://poe2db.tw/us/Helmets_dex#ModifiersCalc',

    'Helmets_int': 'https://poe2db.tw/us/Helmets_int#ModifiersCalc',

    'Helmets_str_dex': 'https://poe2db.tw/us/Helmets_str_dex#ModifiersCalc',

    'Helmets_str_int': 'https://poe2db.tw/us/Helmets_str_int#ModifiersCalc',

    'Helmets_dex_int': 'https://poe2db.tw/us/Helmets_dex_int#ModifiersCalc',

    'Gloves_str': 'https://poe2db.tw/us/Gloves_str#ModifiersCalc',

    'Gloves_dex': 'https://poe2db.tw/us/Gloves_dex#ModifiersCalc',

    'Gloves_int': 'https://poe2db.tw/us/Gloves_int#ModifiersCalc',

    'Gloves_str_dex': 'https://poe2db.tw/us/Gloves_str_dex#ModifiersCalc',

    'Gloves_str_int': 'https://poe2db.tw/us/Gloves_str_int#ModifiersCalc',

    'Gloves_dex_int': 'https://poe2db.tw/us/Gloves_dex_int#ModifiersCalc',

    'Boots_str': 'https://poe2db.tw/us/Boots_str#ModifiersCalc',

    'Boots_dex': 'https://poe2db.tw/us/Boots_dex#ModifiersCalc',

    'Boots_int': 'https://poe2db.tw/us/Boots_int#ModifiersCalc',

    'Boots_str_dex': 'https://poe2db.tw/us/Boots_str_dex#ModifiersCalc',

    'Boots_str_int': 'https://poe2db.tw/us/Boots_str_int#ModifiersCalc',

    'Boots_dex_int': 'https://poe2db.tw/us/Boots_dex_int#ModifiersCalc',

    'Quivers': 'https://poe2db.tw/us/Quivers#ModifiersCalc',

    'Shields_str': 'https://poe2db.tw/us/Shields_str#ModifiersCalc',

    'Shields_str_dex': 'https://poe2db.tw/us/Shields_str_dex#ModifiersCalc',

    'Shields_str_int': 'https://poe2db.tw/us/Shields_str_int#ModifiersCalc',

    'Bucklers': 'https://poe2db.tw/us/Bucklers#ModifiersCalc',

    'Foci': 'https://poe2db.tw/us/Foci#ModifiersCalc',

    'Claws': 'https://poe2db.tw/us/Claws#ModifiersCalc',

    'Daggers': 'https://poe2db.tw/us/Daggers#ModifiersCalc',

    'Wands': 'https://poe2db.tw/us/Wands#ModifiersCalc',

    'One_Hand_Swords': 'https://poe2db.tw/us/One_Hand_Swords#ModifiersCalc',

    'One_Hand_Axes': 'https://poe2db.tw/us/One_Hand_Axes#ModifiersCalc',

    'One_Hand_Maces': 'https://poe2db.tw/us/One_Hand_Maces#ModifiersCalc',

    'Sceptres': 'https://poe2db.tw/us/Sceptres#ModifiersCalc',

    'Spears': 'https://poe2db.tw/us/Spears#ModifiersCalc',

    'Flails': 'https://poe2db.tw/us/Flails#ModifiersCalc',

    'Bows': 'https://poe2db.tw/us/Bows#ModifiersCalc',

    'Staves': 'https://poe2db.tw/us/Staves#ModifiersCalc',

    'Two_Hand_Swords': 'https://poe2db.tw/us/Two_Hand_Swords#ModifiersCalc',

    'Two_Hand_Axes': 'https://poe2db.tw/us/Two_Hand_Axes#ModifiersCalc',

    'Two_Hand_Maces': 'https://poe2db.tw/us/Two_Hand_Maces#ModifiersCalc',

    'Quarterstaves': 'https://poe2db.tw/us/Quarterstaves#ModifiersCalc',

    'Crossbows': 'https://poe2db.tw/us/Crossbows#ModifiersCalc',

}



# Known tags for parsing

KNOWN_TAGS = [

    'Life', 'Mana', 'Defences', 'Attack', 'Caster', 'Speed', 'Critical',

    'Damage', 'Resistance', 'Attribute', 'Elemental', 'Fire', 'Cold',

    'Lightning', 'Chaos', 'Physical', 'Minion', 'Gem', 'Aura', 'Resource',

    'Ailment', 'Block', 'Stun', 'Flask', 'Charge', 'Curse', 'Skill'

]



def parse_weight_desc_tags(text):

    """

    Parse: "1000 +(5-8) to Strength Attribute"

    Returns: (weight, description, tags)

    """

    text = text.strip()

    text = ' '.join(text.split())  # normalize whitespace

    

    # Extract weight (first number)

    match = re.match(r'^(\d+)\s+(.+)$', text)

    if match:

        weight = int(match.group(1))

        rest = match.group(2)

    else:

        weight = 1000

        rest = text

    

    # Try to find tags at the end

    words = rest.split()

    tags = []

    desc_words = []

    

    # Go backwards to find tags

    i = len(words) - 1

    while i >= 0:

        word = words[i]

        # Check if it looks like a tag (CamelCase or known tag)

        if word in KNOWN_TAGS or (word[0].isupper() and not word.startswith('+') and not word.startswith('-') and not word.startswith('(') and len(word) > 2 and not any(c.isdigit() for c in word)):

            tags.insert(0, word)

            i -= 1

        else:

            break

    

    desc_words = words[:i+1]

    description = ' '.join(desc_words)

    

    return weight, description, tags





class PoE2DBModsScraperV4:

    def __init__(self):

        self.options = Options()

        self.options.add_argument('--headless')

        self.options.add_argument('--no-sandbox')

        self.options.add_argument('--disable-dev-shm-usage')

        self.options.add_argument('--disable-gpu')

    

    def scrape_item_type(self, item_type, url):

        driver = webdriver.Chrome(options=self.options)

        

        try:

            driver.get(url)

            time.sleep(5)

            

            result = {

                'item_type': item_type,

                'prefix': [],

                'suffix': [],

                'desecrated_prefix': [],

                'desecrated_suffix': []

            }

            

            # JavaScript to extract all data with section tracking

            js_script = """

            var data = {

                prefix: [],

                suffix: [],

                desecrated_prefix: [],

                desecrated_suffix: [],

                essence_prefix: [],

                essence_suffix: []

            };

            

            var currentSection = null;

            

            // Get all elements in order

            var container = document.getElementById('ModifiersCalc');

            if (!container) return data;

            

            var elements = container.querySelectorAll('h5.identify-title, table');

            

            elements.forEach(function(el) {

                if (el.tagName === 'H5') {

                    var text = el.textContent.trim().toLowerCase();

                    if (text === 'base prefix') currentSection = 'prefix';

                    else if (text === 'base suffix') currentSection = 'suffix';

                    else if (text.includes('desecrated') && text.includes('prefix')) currentSection = 'desecrated_prefix';

                    else if (text.includes('desecrated') && text.includes('suffix')) currentSection = 'desecrated_suffix';

                    else if (text.includes('essence') && text.includes('prefix')) currentSection = 'essence_prefix';

                    else if (text.includes('essence') && text.includes('suffix')) currentSection = 'essence_suffix';

                    else if (text.includes('corrupted')) currentSection = null;

                    else currentSection = null;

                }

                else if (el.tagName === 'TABLE' && currentSection && data[currentSection]) {

                    var rows = el.querySelectorAll('tbody tr');

                    rows.forEach(function(row) {

                        var cells = row.querySelectorAll('td');

                        if (cells.length >= 4) {

                            var tierText = cells[0].textContent.trim();

                            var tier = parseInt(tierText.replace('T', '')) || 1;

                            var modName = cells[1].textContent.trim();

                            var ilvl = parseInt(cells[2].textContent.trim()) || 1;

                            var weightDescTags = cells[3].textContent.trim();

                            

                            data[currentSection].push({

                                tier: tier,

                                mod_name: modName,

                                ilvl: ilvl,

                                raw_text: weightDescTags

                            });

                        }

                    });

                }

            });

            

            return data;

            """

            

            raw_data = driver.execute_script(js_script)

            

            # Parse the raw data

            for section in ['prefix', 'suffix', 'desecrated_prefix', 'desecrated_suffix']:

                for item in raw_data.get(section, []):

                    weight, description, tags = parse_weight_desc_tags(item['raw_text'])

                    

                    result[section].append({

                        'tier': item['tier'],

                        'mod_name': item['mod_name'],

                        'ilvl': item['ilvl'],

                        'weight': weight,

                        'name': description,

                        'tags': tags

                    })

            

            return result

            

        except Exception as e:

            print(f"  Error: {e}")

            import traceback

            traceback.print_exc()

            return None

        finally:

            driver.quit()

    

    def scrape_all(self, output_file=None, test_mode=False):

        all_data = {}

        

        items = list(ITEM_TYPE_URLS.items())

        if test_mode:

            items = items[:3]

        

        total = len(items)

        

        for i, (item_type, url) in enumerate(items):

            print(f"\n[{i+1}/{total}] Scraping {item_type}...")

            

            result = self.scrape_item_type(item_type, url)

            

            if result:

                p = len(result.get('prefix', []))

                s = len(result.get('suffix', []))

                dp = len(result.get('desecrated_prefix', []))

                ds = len(result.get('desecrated_suffix', []))

                

                print(f"  -> Base: {p} prefix, {s} suffix")

                print(f"  -> Desecrated: {dp} prefix, {ds} suffix")

                

                if p > 0 or s > 0:

                    all_data[item_type] = result

                    

                    # Show samples

                    if result['prefix']:

                        m = result['prefix'][0]

                        print(f"  -> Sample: T{m['tier']} W{m['weight']} iLvl{m['ilvl']} | {m['name'][:50]}")

            

            time.sleep(2)

        

        if output_file:

            with open(output_file, 'w', encoding='utf-8') as f:

                json.dump(all_data, f, indent=2, ensure_ascii=False)

            print(f"\nSaved to {output_file}")

        

        return all_data





def main():

    import sys

    test_mode = '--test' in sys.argv

    

    print("=" * 60)

    print("PoE2DB Modifier Scraper V4")

    print("=" * 60)

    

    if test_mode:

        print("TEST MODE: First 3 items only")

    else:

        print(f"Full mode: {len(ITEM_TYPE_URLS)} items")

        print("Estimated time: ~5 minutes")

    

    scraper = PoE2DBModsScraperV4()

    

    output_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    output_file = os.path.join(output_dir, 'data', 'modifier_data_v4.json')

    

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    

    all_data = scraper.scrape_all(output_file, test_mode=test_mode)

    

    print("\n" + "=" * 60)

    print("SUMMARY")

    print("=" * 60)

    

    total_p = sum(len(d.get('prefix', [])) for d in all_data.values())

    total_s = sum(len(d.get('suffix', [])) for d in all_data.values())

    

    print(f"Items scraped: {len(all_data)}")

    print(f"Total prefixes: {total_p}")

    print(f"Total suffixes: {total_s}")

    print(f"Output: {output_file}")





if __name__ == "__main__":

    main()

