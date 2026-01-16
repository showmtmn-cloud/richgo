
#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

Save poe2db page HTML for analysis

"""

from selenium import webdriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By

import time

import os



def save_page_html():

    options = Options()

    options.add_argument('--headless')

    options.add_argument('--no-sandbox')

    options.add_argument('--disable-dev-shm-usage')

    

    driver = webdriver.Chrome(options=options)

    

    try:

        url = 'https://poe2db.tw/us/Amulets#ModifiersCalc'

        print(f"Loading: {url}")

        driver.get(url)

        time.sleep(5)

        

        # Save full page HTML

        output_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        html_file = os.path.join(output_dir, 'data', 'amulets_page.html')

        

        with open(html_file, 'w', encoding='utf-8') as f:

            f.write(driver.page_source)

        

        print(f"Saved full page to: {html_file}")

        

        # Try to find and save just the ModifiersCalc section

        try:

            section = driver.find_element(By.ID, "ModifiersCalc")

            section_html = section.get_attribute('outerHTML')

            

            section_file = os.path.join(output_dir, 'data', 'amulets_modifiers.html')

            with open(section_file, 'w', encoding='utf-8') as f:

                f.write(section_html)

            print(f"Saved ModifiersCalc section to: {section_file}")

        except Exception as e:

            print(f"Could not find ModifiersCalc section: {e}")

        

        # Print the structure of first few tables

        print("\n" + "="*60)

        print("Looking for Base Prefix/Suffix sections:")

        print("="*60)

        

        # Find H5 headers

        headers = driver.find_elements(By.CSS_SELECTOR, "h5.identify-title")

        for h in headers:

            print(f"  H5: {h.text}")

            

            # Find next sibling tables

            try:

                parent = h.find_element(By.XPATH, "./..")

                tables = parent.find_elements(By.TAG_NAME, "table")

                print(f"     -> {len(tables)} tables in parent")

            except:

                pass

        

        # Look for the actual data table

        print("\n" + "="*60)

        print("Analyzing table structures:")

        print("="*60)

        

        js_script = """

        var result = [];

        var tables = document.querySelectorAll('table');

        

        for (var i = 0; i < Math.min(tables.length, 10); i++) {

            var table = tables[i];

            var headers = [];

            table.querySelectorAll('th').forEach(function(th) {

                headers.push(th.textContent.trim());

            });

            

            var firstRow = table.querySelector('tbody tr');

            var firstRowData = [];

            if (firstRow) {

                firstRow.querySelectorAll('td').forEach(function(td) {

                    firstRowData.push(td.textContent.trim().substring(0, 50));

                });

            }

            

            result.push({

                index: i,

                headers: headers,

                firstRow: firstRowData,

                rowCount: table.querySelectorAll('tbody tr').length

            });

        }

        return result;

        """

        

        tables_info = driver.execute_script(js_script)

        for t in tables_info:

            print(f"\nTable {t['index']}:")

            print(f"  Headers: {t['headers']}")

            print(f"  Rows: {t['rowCount']}")

            print(f"  First row: {t['firstRow'][:4] if t['firstRow'] else 'none'}")

        

    finally:

        driver.quit()



if __name__ == "__main__":

    save_page_html()

