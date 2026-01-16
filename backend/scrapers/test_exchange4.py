
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

        time.sleep(5)

        

        # 전체 페이지 텍스트 출력

        body = driver.find_element(By.TAG_NAME, "body")

        text = body.text

        

        print("=== FULL PAGE TEXT ===")

        print(text[:3000])

        

    except Exception as e:

        print(f"Error: {e}")

    finally:

        driver.quit()



if __name__ == "__main__":

    test_scrape()

