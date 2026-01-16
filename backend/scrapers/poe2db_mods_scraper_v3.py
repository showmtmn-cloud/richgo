
#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

PoE2DB Modifiers Scraper V3 - Section-based Parser

Parses Base Prefix and Base Suffix sections correctly

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



class PoE2DBModsScraperV3:

    def __init__(self):

        self.options = Options()

        self.options.add_argument('--headless')

        self.options.add_argument('--no-sandbox')

        self.options.add_argument('--disable-dev-shm-usage')

        self.options.add_argument('--disable-gpu')

        self.options.add_argument('--window-size=1920,1080')

    

    def scrape_item_type(self, item_type, url):

        driver = webdriver.Chrome(options=self.options)

        

        try:

            driver.get(url)

            time.sleep(5)

            

            # Use JavaScript to extract data based on H5 sections

            js_script = """

            var result = {prefix: [], suffix: []};

            

            // Find all H5 headers with identify-title class

            var headers = document.querySelectorAll('h5.identify-title');

            var currentSection = null;

            var prefixStart = null;

            var suffixStart = null;

            var prefixEnd = null;

            var suffixEnd = null;

            

            // Find section boundaries

            headers.forEach(function(h, idx) {

                var text = h.textContent.trim().toLowerCase();

                if (text === 'base prefix') {

                    prefixStart = h;

                } else if (text === 'base suffix') {

                    suffixStart = h;

                    if (prefixStart) {

                        prefixEnd = h;

                    }

                }

            });

            

            // Function to extract mods from a section

            function extractMods(startElement, endElement) {

                var mods = [];

                if (!startElement) return mods;

                

                var current = startElement.nextElementSibling;

                while (current && current !== endElement) {

                    // Look for accordion items which contain the mod tables

                    if (current.classList.contains('accordion')) {

                        var items = current.querySelectorAll('.accordion-item');

                        items.forEach(function(item) {

                            // Get mod name from accordion header

                            var header = item.querySelector('.accordion-header');

                            var body = item.querySelector('.accordion-body');

                            

                            if (body) {

                                var tables = body.querySelectorAll('table');

                                tables.forEach(function(table) {

                                    var rows = table.querySelectorAll('tbody tr');

                                    rows.forEach(function(row) {

                                        var cells = row.querySelectorAll('td');

                                        if (cells.length >= 4) {

                                            // Try to get tier from first cell

                                            var tierText = cells[0].textContent.trim();

                                            var tier = parseInt(tierText.replace('T', '')) || 1;

                                            

                                            // Get mod name - usually in a cell with the actual text

                                            var nameCell = cells[1];

                                            var name = '';

                                            

                                            // Check for anchor with mod name

                                            var anchor = row.querySelector('a[href*="mod"]');

                                            if (anchor) {

                                                name = anchor.textContent.trim();

                                            }

                                            

                                            // Get ilvl

                                            var ilvl = parseInt(cells[2].textContent.trim()) || 1;

                                            

                                            // Get the full mod description

                                            var descCell = cells[cells.length - 1];

                                            var desc = descCell.textContent.trim();

                                            

                                            if (desc && desc.length > 5) {

                                                mods.push({

                                                    tier: tier,

                                                    name: name || desc.substring(0, 50),

                                                    ilvl: ilvl,

                                                    description: desc,

                                                    weight: 1000

                                                });

                                            }

                                        }

                                    });

                                });

                            }

                        });

                    }

                    current = current.nextElementSibling;

                }

                return mods;

            }

            

            // Alternative: Find the main modifier table directly

            // Look for the table with Weight, Level, Tier columns

            var allTables = document.querySelectorAll('table');

            var mainTable = null;

            

            allTables.forEach(function(table) {

                var headers = table.querySelectorAll('th');

                var headerText = '';

                headers.forEach(function(h) { headerText += h.textContent; });

                if (headerText.includes('Weight') && headerText.includes('Level')) {

                    mainTable = table;

                }

            });

            

            if (mainTable) {

                var rows = mainTable.querySelectorAll('tbody tr');

                var currentType = 'prefix';

                

                rows.forEach(function(row) {

                    var cells = row.querySelectorAll('td');

                    if (cells.length >= 4) {

                        var weight = parseInt(cells[0].textContent.trim()) || 1000;

                        var ilvl = parseInt(cells[1].textContent.trim()) || 1;

                        var tier = parseInt(cells[2].textContent.trim()) || 1;

                        

                        // Get full text of last cell for mod description

                        var modCell = cells[3];

                        var modText = modCell.textContent.trim();

                        

                        // Clean up the text

                        modText = modText.replace(/\\s+/g, ' ').trim();

                        

                        if (modText && modText.length > 3) {

                            result[currentType].push({

                                weight: weight,

                                ilvl: ilvl,

                                tier: tier,

                                name: modText,

                                tags: []

                            });

                        }

                    }

                });

            }

            

            // If main table approach didnt work, try accordion approach

            if (result.prefix.length === 0 && result.suffix.length === 0) {

                // Find cards or panels with Base Prefix/Suffix headers

                var cards = document.querySelectorAll('.card, .panel, [class*="modifier"]');

                cards.forEach(function(card) {

                    var header = card.querySelector('.card-header, .panel-heading, h5');

                    if (header) {

                        var headerText = header.textContent.toLowerCase();

                        var targetArray = null;

                        

                        if (headerText.includes('base prefix')) {

                            targetArray = result.prefix;

                        } else if (headerText.includes('base suffix')) {

                            targetArray = result.suffix;

                        }

                        

                        if (targetArray !== null) {

                            var tables = card.querySelectorAll('table');

                            tables.forEach(function(table) {

                                var rows = table.querySelectorAll('tbody tr');

                                rows.forEach(function(row) {

                                    var cells = row.querySelectorAll('td');

                                    if (cells.length >= 4) {

                                        var weight = parseInt(cells[0].textContent) || 1000;

                                        var ilvl = parseInt(cells[1].textContent) || 1;

                                        var tier = parseInt(cells[2].textContent) || 1;

                                        var name = cells[3].textContent.trim();

                                        

                                        if (name && name.length > 3) {

                                            targetArray.push({

                                                weight: weight,

                                                ilvl: ilvl,

                                                tier: tier,

                                                name: name,

                                                tags: []

                                            });

                                        }

                                    }

                                });

                            });

                        }

                    }

                });

            }

            

            return result;

            """

            

            result = driver.execute_script(js_script)

            result['item_type'] = item_type

            

            # If still no data, try getting page source and parse differently

            if not result['prefix'] and not result['suffix']:

                # Get inner HTML of ModifiersCalc section

                try:

                    section = driver.find_element(By.ID, "ModifiersCalc")

                    html = section.get_attribute('innerHTML')

                    

                    # Simple regex parse for mod data

                    import re

                    

                    # Find all table rows with mod data

                    pattern = r'<tr[^>]*>.*?<td[^>]*>(\d+)</td>.*?<td[^>]*>(\d+)</td>.*?<td[^>]*>(\d+)</td>.*?<td[^>]*>(.*?)</td>.*?</tr>'

                    matches = re.findall(pattern, html, re.DOTALL)

                    

                    for match in matches:

                        weight, ilvl, tier, name_html = match

                        # Strip HTML tags

                        name = re.sub(r'<[^>]+>', '', name_html).strip()

                        name = ' '.join(name.split())

                        

                        if name and len(name) > 5:

                            result['prefix'].append({

                                'weight': int(weight),

                                'ilvl': int(ilvl),

                                'tier': int(tier),

                                'name': name,

                                'tags': []

                            })

                except:

                    pass

            

            return result

            

        except Exception as e:

            print(f"  Error: {e}")

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

                print(f"  -> Prefix: {p}, Suffix: {s}")

                

                if p > 0 or s > 0:

                    all_data[item_type] = result

                    # Show sample

                    if result['prefix']:

                        print(f"  -> Sample prefix: {result['prefix'][0]['name'][:60]}")

                    if result['suffix']:

                        print(f"  -> Sample suffix: {result['suffix'][0]['name'][:60]}")

            

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

    print("PoE2DB Modifier Scraper V3")

    print("=" * 60)

    

    if test_mode:

        print("TEST MODE: First 3 items only")

    

    scraper = PoE2DBModsScraperV3()

    

    output_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    output_file = os.path.join(output_dir, 'data', 'modifier_data_v3.json')

    

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    

    all_data = scraper.scrape_all(output_file, test_mode=test_mode)

    

    print("\n" + "=" * 60)

    print("SUMMARY")

    print("=" * 60)

    

    total_p = sum(len(d.get('prefix', [])) for d in all_data.values())

    total_s = sum(len(d.get('suffix', [])) for d in all_data.values())

    

    print(f"Items: {len(all_data)}")

    print(f"Prefixes: {total_p}")

    print(f"Suffixes: {total_s}")





if __name__ == "__main__":

    main()

