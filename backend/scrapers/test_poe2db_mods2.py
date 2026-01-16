
#!/usr/bin/env python3

"""

Test scraper for poe2db modifier data - Modifiers page

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

        # Amulet 모드 페이지 확인

        print("Loading Amulet Modifiers page...")

        driver.get("https://poe2db.tw/us/Modifiers#Amulet")

        time.sleep(5)

        

        body = driver.find_element(By.TAG_NAME, "body")

        text = body.text

        

        # Prefix/Suffix 찾기

        lines = text.split('\n')

        print("\n=== Looking for Prefix/Suffix ===")

        for i, line in enumerate(lines):

            if 'prefix' in line.lower() or 'suffix' in line.lower() or 'weight' in line.lower() or 'tier' in line.lower():

                print(f"[{i}] {line[:100]}")

        

        print("\n=== First 2000 chars ===")

        print(text[:2000])

            

    except Exception as e:

        print(f"Error: {e}")

        import traceback

        traceback.print_exc()

    finally:

        driver.quit()



if __name__ == "__main__":

    test_scrape()

