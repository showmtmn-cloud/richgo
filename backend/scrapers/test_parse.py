
#!/usr/bin/env python3

"""

Debug parsing

"""

from selenium import webdriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By

import time



def test():

    options = Options()

    options.add_argument('--headless')

    options.add_argument('--no-sandbox')

    options.add_argument('--disable-dev-shm-usage')

    

    driver = webdriver.Chrome(options=options)

    

    try:

        driver.get("https://poe2db.tw/us/Amulets#ModifiersCalc")

        time.sleep(5)

        

        body = driver.find_element(By.TAG_NAME, "body")

        text = body.text

        

        lines = text.split('\n')

        

        print("=== Lines around 'Base Prefix' ===")

        for i, line in enumerate(lines):

            if 'Base Prefix' in line or 'Base Suffix' in line or 'maximum Life' in line:

                print(f"[{i}] '{line}'")

                # Show nearby lines

                for j in range(max(0, i-2), min(len(lines), i+5)):

                    print(f"  [{j}] '{lines[j]}'")

                print()

                

    finally:

        driver.quit()



if __name__ == "__main__":

    test()

