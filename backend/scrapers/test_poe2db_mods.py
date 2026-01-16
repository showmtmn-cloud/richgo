
#!/usr/bin/env python3

"""

Test scraper for poe2db modifier data

"""

from selenium import webdriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By

import time



def test_scrape():

    options = Options()

    options.add_argument('--headless')

    options.add_argument('--no-sandbox')

    options.add_argument('--disable-dev-shm-usage')

    options.add_argument('--disable-gpu')

    options.add_argument('--window-size=1920,1080')

    

    driver = webdriver.Chrome(options=options)

    

    try:

        print("Loading Stellar Amulet page...")

        driver.get("https://poe2db.tw/us/Stellar_Amulet")

        time.sleep(5)

        

        body = driver.find_element(By.TAG_NAME, "body")

        text = body.text

        

        print("\n=== Page Content (첫 3000자) ===")

        print(text[:3000])

        

        tables = driver.find_elements(By.TAG_NAME, "table")

        print(f"\n=== Found {len(tables)} tables ===")

        

        for i, table in enumerate(tables[:5]):

            print(f"\n--- Table {i+1} ---")

            print(table.text[:500])

            

    except Exception as e:

        print(f"Error: {e}")

        import traceback

        traceback.print_exc()

    finally:

        driver.quit()



if __name__ == "__main__":

    test_scrape()

