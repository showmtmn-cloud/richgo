
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

        driver.get("https://poe2scout.com/currency-exchange")

        time.sleep(3)

        

        # 스크롤해서 더 많은 데이터 로드

        for _ in range(5):

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(1)

        

        rows = driver.find_elements(By.TAG_NAME, "tr")

        print(f"Found {len(rows)} rows\n")

        

        for i, row in enumerate(rows):

            text = row.text.strip()

            if text and 'chaos' in text.lower():

                print(f"[{i}] {text}")

        

        print("\n--- All currency rows ---")

        for i, row in enumerate(rows[:20]):

            text = row.text.strip()

            if text:

                print(f"[{i}] {text}")

                

    except Exception as e:

        print(f"Error: {e}")

    finally:

        driver.quit()



if __name__ == "__main__":

    test_scrape()

