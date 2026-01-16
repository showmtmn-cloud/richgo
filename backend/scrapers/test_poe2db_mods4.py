
#!/usr/bin/env python3

"""

Find actual Amulet mods URL on poe2db

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

        print("Loading Modifiers page...")

        driver.get("https://poe2db.tw/us/Modifiers")

        time.sleep(3)

        

        # Amulets 링크 찾기

        links = driver.find_elements(By.TAG_NAME, "a")

        print("\n=== Looking for Amulet links ===")

        for link in links:

            href = link.get_attribute("href") or ""

            text = link.text

            if 'amulet' in href.lower() or 'amulet' in text.lower():

                print(f"Link: {text} -> {href}")

        

        # 클릭해서 이동

        for link in links:

            if link.text == "Amulets":

                print(f"\nClicking on Amulets link...")

                link.click()

                time.sleep(3)

                print(f"Current URL: {driver.current_url}")

                

                body = driver.find_element(By.TAG_NAME, "body")

                print("\n=== Page content (first 3000 chars) ===")

                print(body.text[:3000])

                break

            

    except Exception as e:

        print(f"Error: {e}")

        import traceback

        traceback.print_exc()

    finally:

        driver.quit()



if __name__ == "__main__":

    test_scrape()

