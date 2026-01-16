
from apscheduler.schedulers.background import BackgroundScheduler

from apscheduler.triggers.interval import IntervalTrigger

from datetime import datetime

import logging

import sys

import os

import pytz



# 경로 설정

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)



SYDNEY_TZ = pytz.timezone('Australia/Sydney')



class DataScheduler:

    def __init__(self):

        self.scheduler = BackgroundScheduler()

    

    def start(self):

        """Start the scheduler"""

        self.scheduler.add_job(

            self.update_exchange_rates,

            trigger=IntervalTrigger(minutes=5),

            id='exchange_rates',

            name='Update exchange rates',

            replace_existing=True

        )

        

        self.scheduler.add_job(

            self.update_base_prices,

            trigger=IntervalTrigger(minutes=15),

            id='base_prices',

            name='Update base prices',

            replace_existing=True

        )

        

        self.scheduler.add_job(

            self.calculate_profits,

            trigger=IntervalTrigger(minutes=30),

            id='profit_calc',

            name='Calculate profits',

            replace_existing=True

        )

        

        self.scheduler.start()

        logger.info("Scheduler started successfully")

        logger.info(f"Jobs: {len(self.scheduler.get_jobs())}")

        

        # 시작하자마자 환율 업데이트

        self.update_exchange_rates()

    

    def update_exchange_rates(self):

        """Update currency exchange rates"""

        logger.info("=" * 50)

        logger.info("Updating exchange rates...")

        

        try:

            from scrapers.poe2scout_exchange_scraper import PoE2ScoutExchangeScraper

            from sqlalchemy import create_engine

            from sqlalchemy.orm import sessionmaker

            from models.database_models import CurrencyExchangeRate, League

            

            scraper = PoE2ScoutExchangeScraper()

            rates = scraper.get_exchange_rates()

            

            if rates:

                db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'poe2_profit_optimizer.db')

                engine = create_engine(f'sqlite:///{db_path}')

                Session = sessionmaker(bind=engine)

                session = Session()

                

                try:

                    league = session.query(League).filter_by(is_active=True).first()

                    if league:

                        sydney_time = datetime.now(SYDNEY_TZ)

                        rate = CurrencyExchangeRate(

                            league_id=league.id,

                            divine_to_exalt=rates['divine_to_exalt'],

                            divine_to_chaos=rates['divine_to_chaos'],

                            exalt_to_chaos=rates['exalt_to_chaos'],

                            last_updated=sydney_time

                        )

                        session.add(rate)

                        session.commit()

                        logger.info(f"Exchange rates updated: Divine={rates['divine_to_exalt']} Exalt")

                    else:

                        logger.error("No active league found")

                finally:

                    session.close()

            else:

                logger.error("Failed to fetch exchange rates")

                

        except Exception as e:

            logger.error(f"Error updating exchange rates: {e}")

            import traceback

            traceback.print_exc()

        

        logger.info("=" * 50)

    

    def update_base_prices(self):

        logger.info("Updating base prices... (not implemented yet)")

    

    def calculate_profits(self):

        logger.info("Calculating profit opportunities... (not implemented yet)")

    

    def stop(self):

        self.scheduler.shutdown()

        logger.info("Scheduler stopped")





if __name__ == "__main__":

    scheduler = DataScheduler()

    scheduler.start()

    

    import time

    try:

        while True:

            time.sleep(1)

    except KeyboardInterrupt:

        scheduler.stop()

