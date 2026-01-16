#!/usr/bin/env python3

"""

PoE2DB Improved Base Item Scraper v2

더 정확한 HTML 파싱을 사용하는 개선된 버전



사용법:

    python scrape_bases_v2.py



출력:

    scraped_bases.json - 모든 베이스 아이템 데이터

"""



import requests

from bs4 import BeautifulSoup

import json

import re

import time

from typing import Dict, List, Optional, Tuple

from dataclasses import dataclass, asdict

from pathlib import Path



# ============================================================================

# 설정

# ============================================================================



BASE_URL = "https://poe2db.tw/us"



# 모든 장비 카테고리 URL

EQUIPMENT_CATEGORIES = {

    # Body Armours

    "Body Armour": {

        "int": "/Body_Armours_int",

        "str": "/Body_Armours_str", 

        "dex": "/Body_Armours_dex",

        "str_int": "/Body_Armours_str_int",

        "str_dex": "/Body_Armours_str_dex",

        "dex_int": "/Body_Armours_dex_int",

    },

    # Helmets

    "Helmet": {

        "int": "/Helmets_int",

        "str": "/Helmets_str",

        "dex": "/Helmets_dex",

        "str_int": "/Helmets_str_int",

        "str_dex": "/Helmets_str_dex",

        "dex_int": "/Helmets_dex_int",

    },

    # Gloves

    "Gloves": {

        "int": "/Gloves_int",

        "str": "/Gloves_str",

        "dex": "/Gloves_dex",

        "str_int": "/Gloves_str_int",

        "str_dex": "/Gloves_str_dex",

        "dex_int": "/Gloves_dex_int",

    },

    # Boots

    "Boots": {

        "int": "/Boots_int",

        "str": "/Boots_str",

        "dex": "/Boots_dex",

        "str_int": "/Boots_str_int",

        "str_dex": "/Boots_str_dex",

        "dex_int": "/Boots_dex_int",

    },

    # Shields

    "Shield": {

        "int": "/Shields_int",

        "str": "/Shields_str",

        "dex": "/Shields_dex",

        "str_int": "/Shields_str_int",

        "str_dex": "/Shields_str_dex",

        "dex_int": "/Shields_dex_int",

    },

}





# ============================================================================

# 스크래퍼 클래스

# ============================================================================



class Poe2dbScraperV2:

    """개선된 poe2db.tw 스크래퍼"""

    

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update({

            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",

            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",

            "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",

            "Cache-Control": "no-cache",

        })

        self.all_items = []

        

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:

        """페이지 가져오기"""

        try:

            print(f"    Fetching: {url}")

            response = self.session.get(url, timeout=30)

            response.raise_for_status()

            return BeautifulSoup(response.text, 'html.parser')

        except requests.exceptions.RequestException as e:

            print(f"    ERROR: {e}")

            return None

    

    def extract_items_from_page(self, soup: BeautifulSoup, item_type: str, item_class: str) -> List[Dict]:

        """

        페이지에서 아이템 정보 추출

        

        poe2db.tw HTML 구조:

        - 각 아이템은 이미지 링크 + 텍스트 링크 + 스탯 정보로 구성

        - 스탯은 "Energy Shield: 184" 또는 "Armour: 200" 형식

        - 요구사항은 "Requires: Level 65, 121 Int" 형식

        """

        items = []

        seen_names = set()

        

        # 방법 1: 아이템 이름 링크를 찾고, 그 주변 정보 파싱

        all_links = soup.find_all('a')

        

        # 아이템 이름 후보 키워드 (장비 타입별)

        item_keywords = {

            "Body Armour": ["Robe", "Raiment", "Vest", "Plate", "Mail", "Coat", "Brigandine", 

                          "Jacket", "Garb", "Regalia", "Tunic", "Armour", "Hauberk", "Vestment"],

            "Helmet": ["Helm", "Helmet", "Crown", "Cap", "Hood", "Mask", "Circlet", "Casque", 

                      "Coif", "Burgonet", "Bascinet", "Sallet", "Visage", "Great Helm"],

            "Gloves": ["Gloves", "Gauntlets", "Mitts", "Wraps", "Bracers", "Grips"],

            "Boots": ["Boots", "Greaves", "Slippers", "Shoes", "Treads", "Footpads", "Leggings"],

            "Shield": ["Shield", "Tower", "Buckler", "Kite", "Spiked", "Round", "Pavise"],

        }

        

        keywords = item_keywords.get(item_type, [])

        

        for link in all_links:

            href = link.get('href', '')

            text = link.get_text(strip=True)

            

            # 빈 텍스트나 이미 처리된 것 스킵

            if not text or text in seen_names:

                continue

                

            # URL 스킵 (외부 링크, 앵커 등)

            if href.startswith('http') or href.startswith('#') or href.startswith('/us/'):

                if not any(kw in text for kw in keywords):

                    continue

            

            # 아이템 이름인지 확인

            is_item = any(keyword in text for keyword in keywords)

            

            if is_item:

                seen_names.add(text)

                

                # 부모/형제 요소에서 스탯 정보 찾기

                item_data = self._extract_item_stats(link, text, item_type, item_class, href)

                

                if item_data:

                    items.append(item_data)

                    print(f"      + {text}: {item_data.get('base_stats', {})}")

        

        return items

    

    def _extract_item_stats(self, link_element, name: str, item_type: str, 

                           item_class: str, href: str) -> Optional[Dict]:

        """링크 요소 주변에서 아이템 스탯 추출"""

        

        # 주변 텍스트 수집 (부모 + 형제)

        context_text = ""

        

        # 부모 요소들 확인

        parent = link_element.parent

        for _ in range(5):  # 최대 5단계 상위까지 확인

            if parent:

                context_text += " " + parent.get_text()

                # 다음 형제 요소들도 확인

                sibling = parent.next_sibling

                for _ in range(3):

                    if sibling:

                        if hasattr(sibling, 'get_text'):

                            context_text += " " + sibling.get_text()

                        sibling = sibling.next_sibling

                parent = parent.parent

            else:

                break

        

        # 스탯 파싱

        base_stats = {}

        

        # Energy Shield

        es_match = re.search(r'Energy Shield[:\s]+(\d+)', context_text)

        if es_match:

            base_stats['energy_shield'] = int(es_match.group(1))

        

        # Armour

        armour_match = re.search(r'(?<!Energy )Armour[:\s]+(\d+)', context_text)

        if armour_match:

            base_stats['armour'] = int(armour_match.group(1))

        

        # Evasion

        evasion_match = re.search(r'Evasion(?:\s+Rating)?[:\s]+(\d+)', context_text)

        if evasion_match:

            base_stats['evasion'] = int(evasion_match.group(1))

        

        # Movement Speed

        ms_match = re.search(r'Movement Speed[:\s]+([-\d.]+)', context_text)

        if ms_match:

            base_stats['movement_speed'] = float(ms_match.group(1))

        

        # 요구사항 파싱

        requirements = {

            'level': 0,

            'str': 0,

            'dex': 0,

            'int': 0

        }

        

        # Level

        level_match = re.search(r'Level\s+(\d+)', context_text)

        if level_match:

            requirements['level'] = int(level_match.group(1))

        

        # Str

        str_match = re.search(r'(\d+)\s*Str', context_text)

        if str_match:

            requirements['str'] = int(str_match.group(1))

        

        # Dex

        dex_match = re.search(r'(\d+)\s*Dex', context_text)

        if dex_match:

            requirements['dex'] = int(dex_match.group(1))

        

        # Int

        int_match = re.search(r'(\d+)\s*Int', context_text)

        if int_match:

            requirements['int'] = int(int_match.group(1))

        

        # Implicit mod (괄호 안 텍스트)

        implicit_match = re.search(rf'{re.escape(name)}.*?\(([\d\-—]+%[^)]*)\)', context_text)

        implicit = implicit_match.group(1) if implicit_match else None

        

        # 최소한의 스탯이 있어야 유효한 아이템

        if not base_stats:

            return None

        

        return {

            'name': name,

            'name_ko': None,  # 나중에 추가

            'item_type': item_type,

            'item_class': item_class,

            'requirements': requirements,

            'base_stats': base_stats,

            'implicit_mod': implicit,

            'poe2db_url': f"{BASE_URL}/{href}" if not href.startswith('http') else href

        }

    

    def scrape_category(self, item_type: str, item_class: str, url_path: str) -> List[Dict]:

        """특정 카테고리 스크래핑"""

        full_url = BASE_URL + url_path

        soup = self.fetch_page(full_url)

        

        if not soup:

            return []

        

        return self.extract_items_from_page(soup, item_type, item_class)

    

    def scrape_all(self) -> List[Dict]:

        """모든 카테고리 스크래핑"""

        print("=" * 70)

        print("  PoE2DB Base Item Scraper v2")

        print("=" * 70)

        

        all_items = []

        

        for item_type, classes in EQUIPMENT_CATEGORIES.items():

            print(f"\n▶ {item_type}")

            print("-" * 50)

            

            type_items = []

            

            for item_class, url_path in classes.items():

                print(f"\n  [{item_class.upper()}] {url_path}")

                

                items = self.scrape_category(item_type, item_class, url_path)

                type_items.extend(items)

                

                # Rate limiting

                time.sleep(0.5)

            

            print(f"\n  → {item_type} 총 {len(type_items)}개 수집")

            all_items.extend(type_items)

        

        self.all_items = all_items

        

        print(f"\n{'=' * 70}")

        print(f"  전체 수집 완료: {len(all_items)}개 베이스 아이템")

        print("=" * 70)

        

        return all_items

    

    def save_to_json(self, filepath: str = "scraped_bases.json"):

        """JSON 파일로 저장"""

        data = {

            "metadata": {

                "source": "poe2db.tw",

                "version": "2.0",

                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),

                "total_items": len(self.all_items),

                "categories": list(EQUIPMENT_CATEGORIES.keys())

            },

            "items": self.all_items

        }

        

        with open(filepath, 'w', encoding='utf-8') as f:

            json.dump(data, f, indent=2, ensure_ascii=False)

        

        print(f"\n저장 완료: {filepath}")

        return filepath





# ============================================================================

# 단일 페이지 테스트 함수

# ============================================================================



def test_single_page():

    """단일 페이지 테스트 (Body Armour INT)"""

    print("테스트: Body Armour (INT) 페이지")

    print("-" * 50)

    

    scraper = Poe2dbScraperV2()

    items = scraper.scrape_category("Body Armour", "int", "/Body_Armours_int")

    

    print(f"\n수집된 아이템: {len(items)}개")

    

    for item in items:

        print(f"\n{item['name']}")

        print(f"  스탯: {item['base_stats']}")

        print(f"  요구: Level {item['requirements']['level']}, Int {item['requirements']['int']}")

    

    return items





# ============================================================================

# 메인 실행

# ============================================================================



if __name__ == "__main__":

    import sys

    

    if len(sys.argv) > 1 and sys.argv[1] == "--test":

        # 단일 페이지 테스트

        test_single_page()

    else:

        # 전체 스크래핑

        scraper = Poe2dbScraperV2()

        scraper.scrape_all()

        scraper.save_to_json()

