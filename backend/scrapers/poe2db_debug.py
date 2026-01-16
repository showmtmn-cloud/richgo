
#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

Debug script to analyze poe2db.tw page structure

"""

from selenium import webdriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By

import time



def debug_page_structure():

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

        

        # Find all headers

        print("\n" + "="*60)

        print("All H5 Headers:")

        print("="*60)

        headers = driver.find_elements(By.TAG_NAME, "h5")

        for i, h in enumerate(headers):

            print(f"  [{i}] {h.text[:80] if h.text else '(empty)'}")

        

        # Find all tables and their preceding elements

        print("\n" + "="*60)

        print("Tables and their context:")

        print("="*60)

        

        js_script = """

        var tables = document.querySelectorAll('table');

        var result = [];

        tables.forEach(function(table, idx) {

            var prev = table.previousElementSibling;

            var prevText = prev ? prev.textContent.substring(0, 100) : 'none';

            var rowCount = table.querySelectorAll('tbody tr').length;

            

            // Get first row sample

            var firstRow = table.querySelector('tbody tr');

            var firstRowText = firstRow ? firstRow.textContent.substring(0, 150) : 'none';

            

            result.push({

                index: idx,

                prevElement: prev ? prev.tagName : 'none',

                prevText: prevText,

                rowCount: rowCount,

                firstRowSample: firstRowText

            });

        });

        return result;

        """

        

        tables_info = driver.execute_script(js_script)

        for t in tables_info:

            print(f"\n  Table {t['index']}:")

            print(f"    Prev element: {t['prevElement']}")

            print(f"    Prev text: {t['prevText'][:60]}...")

            print(f"    Row count: {t['rowCount']}")

            print(f"    First row: {t['firstRowSample'][:80]}...")

        

        # Check for specific class names or IDs

        print("\n" + "="*60)

        print("Looking for modifier sections:")

        print("="*60)

        

        js_script2 = """

        var result = [];

        var allElements = document.querySelectorAll('*');

        allElements.forEach(function(el) {

            var text = el.textContent.toLowerCase();

            if ((text.includes('base prefix') || text.includes('base suffix')) 

                && el.tagName !== 'BODY' && el.tagName !== 'HTML') {

                if (el.textContent.length < 200) {

                    result.push({

                        tag: el.tagName,

                        class: el.className,

                        id: el.id,

                        text: el.textContent.substring(0, 100)

                    });

                }

            }

        });

        return result.slice(0, 20);

        """

        

        sections = driver.execute_script(js_script2)

        for s in sections:

            print(f"  {s['tag']}.{s['class']}: {s['text'][:60]}...")

        

    finally:

        driver.quit()



if __name__ == "__main__":

    debug_page_structure()

