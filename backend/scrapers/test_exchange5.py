
#!/usr/bin/env python3

from selenium import webdriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC

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

        # Currency Exchange 전체 페이지로 직접 이동

        driver.get("https://poe2scout.com/economy/currency")

        time.sleep(5)

        

        body = driver.find_element(By.TAG_NAME, "body")

        text = body.text

        print("=== URL: /economy/currency ===")

        print(text[:2000])

        

        # Chaos 찾기

        if 'chaos' in text.lower():

            print("\n*** CHAOS FOUND! ***")

        

    except Exception as e:

        print(f"Error: {e}")

    finally:

        driver.quit()



if __name__ == "__main__":

    test_scrape()

