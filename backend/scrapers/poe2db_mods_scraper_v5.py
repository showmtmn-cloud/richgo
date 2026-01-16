
#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

PoE2DB Modifiers Scraper V5 - Correct Structure

Uses div.mod-title instead of tables

"""

from selenium import webdriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By

import time

import json

import os



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



class PoE2DBModsScraperV5:

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

            

            # JavaScript to extract data from div.mod-title structure

            js_script = """

            var result = {

                prefix: [],

                suffix: [],

                desecrated_prefix: [],

                desecrated_suffix: []

            };

            

            var container = document.getElementById('ModifiersCalc');

            if (!container) return result;

            

            var currentSection = null;

            

            // Get all h5 headers and their following blocks

            var headers = container.querySelectorAll('h5.identify-title');

            

            headers.forEach(function(header) {

                var headerText = header.textContent.trim().toLowerCase();

                

                // Determine section type

                if (headerText === 'base prefix') {

                    currentSection = 'prefix';

                } else if (headerText === 'base suffix') {

                    currentSection = 'suffix';

                } else if (headerText.includes('desecrated') && headerText.includes('prefix')) {

                    currentSection = 'desecrated_prefix';

                } else if (headerText.includes('desecrated') && headerText.includes('suffix')) {

                    currentSection = 'desecrated_suffix';

                } else {

                    currentSection = null;

                    return;

                }

                

                // Find the next sibling div with mod-title elements

                var nextEl = header.nextElementSibling;

                while (nextEl && !nextEl.classList.contains('identify-title')) {

                    // Look for mod-title divs

                    var mods = nextEl.querySelectorAll('div.mod-title');

                    

                    mods.forEach(function(mod) {

                        // Extract badges (weight, ilvl, tier)

                        var badges = mod.querySelectorAll('span.badge.rounded-pill');

                        

                        var weight = 1000;

                        var ilvl = 1;

                        var tier = 1;

                        

                        badges.forEach(function(badge) {

                            var value = parseInt(badge.textContent.trim());

                            if (badge.classList.contains('bg-danger')) {

                                weight = value || 1000;

                            } else if (badge.classList.contains('bg-secondary')) {

                                ilvl = value || 1;

                            } else if (badge.classList.contains('bg-success')) {

                                tier = value || 1;

                            }

                        });

                        

                        // Extract mod name and tags

                        var modText = mod.textContent.trim();

                        

                        // Get tags from data-tag attributes

                        var tagElements = mod.querySelectorAll('[data-tag]');

                        var tags = [];

                        tagElements.forEach(function(te) {

                            tags.push(te.getAttribute('data-tag'));

                        });

                        

                        // Clean mod name - remove the badge numbers

                        var nameSpan = mod.querySelector(':scope > span:last-child');

                        var modName = '';

                        if (nameSpan) {

                            // Get text before the tag badges

                            var clone = nameSpan.cloneNode(true);

                            var innerBadges = clone.querySelectorAll('.badge');

                            innerBadges.forEach(function(b) { b.remove(); });

                            modName = clone.textContent.trim();

                        }

                        

                        if (!modName) {

                            // Fallback: extract from full text

                            modName = modText.replace(/\\d+/g, '').trim();

                        }

                        

                        if (modName && currentSection) {

                            result[currentSection].push({

                                name: modName,

                                weight: weight,

                                ilvl: ilvl,

                                tier: tier,

                                tags: tags

                            });

                        }

                    });

                    

                    nextEl = nextEl.nextElementSibling;

                    

                    // Stop if we hit another h5

                    if (nextEl && nextEl.tagName === 'H5') break;

                }

            });

            

            return result;

            """

            

            result = driver.execute_script(js_script)

            result['item_type'] = item_type

            

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

                        print(f"  -> Prefix sample: T{m['tier']} W{m['weight']} iLvl{m['ilvl']}")

                        print(f"     Name: {m['name'][:50]}")

                        print(f"     Tags: {m['tags']}")

                    if result['suffix']:

                        m = result['suffix'][0]

                        print(f"  -> Suffix sample: T{m['tier']} W{m['weight']} iLvl{m['ilvl']}")

                        print(f"     Name: {m['name'][:50]}")

            

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

    print("PoE2DB Modifier Scraper V5 - div.mod-title parser")

    print("=" * 60)

    

    if test_mode:

        print("TEST MODE: First 3 items only")

    else:

        print(f"Full mode: {len(ITEM_TYPE_URLS)} items")

        print("Estimated time: ~5 minutes")

    

    scraper = PoE2DBModsScraperV5()

    

    output_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    output_file = os.path.join(output_dir, 'data', 'modifier_data_v5.json')

    

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

