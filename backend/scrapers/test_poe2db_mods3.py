
#!/usr/bin/env python3

"""

Test scraper for poe2db Amulet modifiers

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

        # Amulets 모드 직접 접근

        print("Loading Amulets Modifiers page...")

        driver.get("https://poe2db.tw/us/Modifiers/Amulets")

        time.sleep(5)

        

        body = driver.find_element(By.TAG_NAME, "body")

        text = body.text

        

        print("\n=== First 4000 chars ===")

        print(text[:4000])

            

    except Exception as e:

        print(f"Error: {e}")

        import traceback

        traceback.print_exc()

    finally:

        driver.quit()



if __name__ == "__main__":

    test_scrape()

