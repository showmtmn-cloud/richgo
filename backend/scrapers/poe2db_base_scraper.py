
"""

PoE2DB Base Scraper

"""

import time

import requests

from bs4 import BeautifulSoup

from typing import Optional

import logging



logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)





class Poe2DBScraper:

    BASE_URL = "https://poe2db.tw"

    

    def __init__(self, lang: str = "us"):

        self.lang = lang

        self.session = requests.Session()

        self.session.headers.update({

            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

        })

        

    def get_url(self, path: str) -> str:

        return f"{self.BASE_URL}/{self.lang}/{path}"

    

    def fetch_page(self, path: str) -> Optional[BeautifulSoup]:

        try:

            url = self.get_url(path)

            logger.info(f"Fetching {url}")

            response = self.session.get(url, timeout=30)

            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            time.sleep(1)

            return soup

        except Exception as e:

            logger.error(f"Error: {e}")

            return None

    

    def close(self):

        self.session.close()

