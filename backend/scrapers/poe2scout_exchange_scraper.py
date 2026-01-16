
#!/usr/bin/env python3

"""

PoE2Scout Exchange Rate Scraper - Fixed Version

"""

from selenium import webdriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By

from datetime import datetime

from typing import Dict, Optional

import logging

import re



logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)



class PoE2ScoutExchangeScraper:

    def __init__(self):

        self.url = "https://poe2scout.com/economy/currency"

    

    def _create_driver(self):

        options = Options()

        options.add_argument('--headless')

        options.add_argument('--no-sandbox')

        options.add_argument('--disable-dev-shm-usage')

        options.add_argument('--disable-gpu')

        options.add_argument('--window-size=1920,1080')

        return webdriver.Chrome(options=options)

    

    def get_exchange_rates(self, league: str = "Fate of the Vaal") -> Optional[Dict]:

        """Get exchange rates from poe2scout.com"""

        driver = self._create_driver()

        

        try:

            logger.info(f"Fetching exchange rates from {self.url}")

            driver.get(self.url)

            

            import time

            time.sleep(5)

            

            body = driver.find_element(By.TAG_NAME, "body")

            text = body.text

            

            # 정확한 매칭을 위해 줄 단위로 파싱

            lines = text.split('\n')

            

            divine_price = None

            chaos_price = None

            

            for i, line in enumerate(lines):

                line = line.strip()

                

                # "Divine Orb" 정확히 매칭 (Perfect Divine Orb 제외)

                if line == "Divine Orb" and i + 1 < len(lines):

                    next_line = lines[i + 1].strip()

                    try:

                        divine_price = float(next_line.replace(',', '').split()[0])

                        logger.info(f"Found Divine Orb: {divine_price}")

                    except:

                        pass

                

                # "Chaos Orb" 정확히 매칭 (Perfect/Greater Chaos Orb 제외)

                if line == "Chaos Orb" and i + 1 < len(lines):

                    next_line = lines[i + 1].strip()

                    try:

                        chaos_price = float(next_line.replace(',', '').split()[0])

                        logger.info(f"Found Chaos Orb: {chaos_price}")

                    except:

                        pass

            

            if divine_price is None:

                logger.error("Could not find Divine Orb price")

                return None

            

            if chaos_price is None:

                logger.error("Could not find Chaos Orb price")

                return None

            

            # 환율 계산 (모든 가격은 Exalt 기준)

            divine_to_exalt = divine_price

            divine_to_chaos = divine_price / chaos_price

            exalt_to_chaos = 1.0 / chaos_price

            

            rates = {

                'divine_to_exalt': round(divine_to_exalt, 2),

                'divine_to_chaos': round(divine_to_chaos, 2),

                'exalt_to_chaos': round(exalt_to_chaos, 2),

                'timestamp': datetime.now().isoformat()

            }

            

            logger.info(f"Exchange rates: Divine={rates['divine_to_exalt']} Exalt, "

                       f"Divine={rates['divine_to_chaos']} Chaos, "

                       f"Exalt={rates['exalt_to_chaos']} Chaos")

            

            return rates

            

        except Exception as e:

            logger.error(f"Error fetching exchange rates: {e}")

            import traceback

            traceback.print_exc()

            return None

        finally:

            driver.quit()





def update_database(rates: Dict):

    """Update database with new rates"""

    from sqlalchemy import create_engine

    from sqlalchemy.orm import sessionmaker

    import sys

    sys.path.insert(0, '..')

    from models.database_models import CurrencyExchangeRate

    

    engine = create_engine('sqlite:///../poe2_profit_optimizer.db')

    Session = sessionmaker(bind=engine)

    session = Session()

    

    try:

        new_rate = CurrencyExchangeRate(

            league_id=1,

            divine_to_exalt=rates['divine_to_exalt'],

            divine_to_chaos=rates['divine_to_chaos'],

            exalt_to_chaos=rates['exalt_to_chaos'],

            last_updated=datetime.now()

        )

        session.add(new_rate)

        session.commit()

        logger.info("Database updated successfully")

    except Exception as e:

        logger.error(f"Database error: {e}")

        session.rollback()

    finally:

        session.close()





if __name__ == "__main__":

    scraper = PoE2ScoutExchangeScraper()

    rates = scraper.get_exchange_rates()

    

    if rates:

        print(f"\n=== Exchange Rates ===")

        print(f"Divine to Exalt: {rates['divine_to_exalt']}")

        print(f"Divine to Chaos: {rates['divine_to_chaos']}")

        print(f"Exalt to Chaos: {rates['exalt_to_chaos']}")

        print(f"Timestamp: {rates['timestamp']}")

        

        update_database(rates)

    else:

        print("Failed to fetch exchange rates")

