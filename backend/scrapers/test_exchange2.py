
#!/usr/bin/env python3

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

        print("Navigating to poe2scout.com/currency-exchange...")

        driver.get("https://poe2scout.com/currency-exchange")

        time.sleep(5)

        

        rows = driver.find_elements(By.TAG_NAME, "tr")

        print(f"Found {len(rows)} rows\n")

        

        print("--- ALL ROWS ---")

        for i, row in enumerate(rows):

            text = row.text.strip()

            if text:

                print(f"[{i}] {text}")

        

    except Exception as e:

        print(f"Error: {e}")

    finally:

        driver.quit()



if __name__ == "__main__":

    test_scrape()

