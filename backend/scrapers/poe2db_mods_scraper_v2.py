
#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

PoE2DB Modifiers Scraper V2 - Fixed Parser

Properly extracts modifier names from poe2db.tw

"""

from selenium import webdriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC

import time

import json

import os

import re



# Item type URLs

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



class PoE2DBModsScraperV2:

    def __init__(self):

        self.options = Options()

        self.options.add_argument('--headless')

        self.options.add_argument('--no-sandbox')

        self.options.add_argument('--disable-dev-shm-usage')

        self.options.add_argument('--disable-gpu')

        self.options.add_argument('--window-size=1920,1080')

    

    def scrape_item_type(self, item_type, url):

        """Scrape modifiers for a single item type using HTML parsing"""

        driver = webdriver.Chrome(options=self.options)

        

        try:

            print(f"  Loading page...")

            driver.get(url)

            time.sleep(3)

            

            # Wait for table to load

            WebDriverWait(driver, 10).until(

                EC.presence_of_element_located((By.CSS_SELECTOR, "table"))

            )

            time.sleep(2)

            

            result = {

                'item_type': item_type,

                'prefix': [],

                'suffix': [],

                'desecrated_prefix': [],

                'desecrated_suffix': []

            }

            

            # Find all tables

            tables = driver.find_elements(By.CSS_SELECTOR, "table.table")

            

            current_section = None

            

            # Find section headers and tables

            page_source = driver.page_source

            

            # Parse using table rows

            for table in tables:

                try:

                    # Get table header to determine section

                    prev_element = table.find_element(By.XPATH, "./preceding-sibling::*[1]")

                    header_text = prev_element.text.lower()

                    

                    if 'prefix' in header_text and 'desecrated' not in header_text:

                        current_section = 'prefix'

                    elif 'suffix' in header_text and 'desecrated' not in header_text:

                        current_section = 'suffix'

                    elif 'desecrated' in header_text and 'prefix' in header_text:

                        current_section = 'desecrated_prefix'

                    elif 'desecrated' in header_text and 'suffix' in header_text:

                        current_section = 'desecrated_suffix'

                    else:

                        continue

                    

                    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")

                    

                    for row in rows:

                        try:

                            cells = row.find_elements(By.TAG_NAME, "td")

                            if len(cells) >= 4:

                                # Extract data from cells

                                weight = int(cells[0].text.strip()) if cells[0].text.strip().isdigit() else 1000

                                ilvl = int(cells[1].text.strip()) if cells[1].text.strip().isdigit() else 1

                                tier = int(cells[2].text.strip()) if cells[2].text.strip().isdigit() else 1

                                

                                # Get full mod name from the last cell

                                mod_cell = cells[3]

                                mod_name = mod_cell.text.strip()

                                

                                # Extract tags from class or data attributes

                                tags = []

                                try:

                                    tag_elements = mod_cell.find_elements(By.CSS_SELECTOR, "span.tag, span.badge")

                                    tags = [t.text.strip() for t in tag_elements if t.text.strip()]

                                except:

                                    pass

                                

                                if mod_name and len(mod_name) > 3:

                                    result[current_section].append({

                                        'name': mod_name,

                                        'weight': weight,

                                        'ilvl': ilvl,

                                        'tier': tier,

                                        'tags': tags

                                    })

                        except Exception as e:

                            continue

                            

                except Exception as e:

                    continue

            

            return result

            

        except Exception as e:

            print(f"  Error: {e}")

            return None

        finally:

            driver.quit()

    

    def scrape_with_js(self, item_type, url):

        """Alternative: Use JavaScript to extract table data"""

        driver = webdriver.Chrome(options=self.options)

        

        try:

            driver.get(url)

            time.sleep(4)

            

            # Execute JavaScript to extract modifier data

            js_script = """

            var result = {prefix: [], suffix: [], desecrated_prefix: [], desecrated_suffix: []};

            var currentSection = null;

            

            // Find all h5 headers and tables

            var elements = document.querySelectorAll('h5, table.table');

            

            elements.forEach(function(el) {

                if (el.tagName === 'H5') {

                    var text = el.textContent.toLowerCase();

                    if (text.includes('prefix') && !text.includes('desecrated')) {

                        currentSection = 'prefix';

                    } else if (text.includes('suffix') && !text.includes('desecrated')) {

                        currentSection = 'suffix';

                    } else if (text.includes('desecrated') && text.includes('prefix')) {

                        currentSection = 'desecrated_prefix';

                    } else if (text.includes('desecrated') && text.includes('suffix')) {

                        currentSection = 'desecrated_suffix';

                    }

                } else if (el.tagName === 'TABLE' && currentSection) {

                    var rows = el.querySelectorAll('tbody tr');

                    rows.forEach(function(row) {

                        var cells = row.querySelectorAll('td');

                        if (cells.length >= 4) {

                            var weight = parseInt(cells[0].textContent.trim()) || 1000;

                            var ilvl = parseInt(cells[1].textContent.trim()) || 1;

                            var tier = parseInt(cells[2].textContent.trim()) || 1;

                            var name = cells[3].textContent.trim();

                            

                            // Get tags

                            var tags = [];

                            var tagEls = cells[3].querySelectorAll('.tag, .badge, span[class*="tag"]');

                            tagEls.forEach(function(t) {

                                if (t.textContent.trim()) tags.push(t.textContent.trim());

                            });

                            

                            if (name && name.length > 3) {

                                result[currentSection].push({

                                    name: name,

                                    weight: weight,

                                    ilvl: ilvl,

                                    tier: tier,

                                    tags: tags

                                });

                            }

                        }

                    });

                }

            });

            

            return result;

            """

            

            result = driver.execute_script(js_script)

            result['item_type'] = item_type

            return result

            

        except Exception as e:

            print(f"  JS Error: {e}")

            return None

        finally:

            driver.quit()

    

    def scrape_all(self, output_file=None, test_mode=False):

        """Scrape all item types"""

        all_data = {}

        

        items_to_scrape = list(ITEM_TYPE_URLS.items())

        if test_mode:

            items_to_scrape = items_to_scrape[:3]  # Only first 3 for testing

        

        total = len(items_to_scrape)

        

        for i, (item_type, url) in enumerate(items_to_scrape):

            print(f"\n[{i+1}/{total}] Scraping {item_type}...")

            

            # Try JS method first

            result = self.scrape_with_js(item_type, url)

            

            if result:

                prefix_count = len(result.get('prefix', []))

                suffix_count = len(result.get('suffix', []))

                print(f"  -> Prefix: {prefix_count}, Suffix: {suffix_count}")

                

                if prefix_count > 0 or suffix_count > 0:

                    all_data[item_type] = result

                    

                    # Show sample

                    if result['prefix']:

                        sample = result['prefix'][0]

                        print(f"  -> Sample: {sample['name'][:60]}")

                else:

                    print(f"  -> No data found, trying alternate method...")

            else:

                print(f"  -> Failed")

            

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

    print("PoE2DB Modifier Scraper V2")

    print("=" * 60)

    

    if test_mode:

        print("TEST MODE: Only scraping first 3 item types")

    else:

        print(f"Full scrape: {len(ITEM_TYPE_URLS)} item types")

        print("Estimated time: ~5-7 minutes")

    

    print("=" * 60)

    

    scraper = PoE2DBModsScraperV2()

    

    output_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    output_file = os.path.join(output_dir, 'data', 'modifier_data_v2.json')

    

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    

    all_data = scraper.scrape_all(output_file, test_mode=test_mode)

    

    # Summary

    print("\n" + "=" * 60)

    print("SUMMARY")

    print("=" * 60)

    

    total_prefix = 0

    total_suffix = 0

    

    for item_type, data in all_data.items():

        p = len(data.get('prefix', []))

        s = len(data.get('suffix', []))

        total_prefix += p

        total_suffix += s

    

    print(f"Item types scraped: {len(all_data)}")

    print(f"Total prefixes: {total_prefix}")

    print(f"Total suffixes: {total_suffix}")

    print(f"Output: {output_file}")





if __name__ == "__main__":

    main()

