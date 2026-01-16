#!/usr/bin/env python3
"""
PoE2DB Base Item Scraper
poe2db.tw에서 베이스 아이템 데이터를 수집합니다.

사용법:
    python scrape_bases.py

출력:
    scraped_bases.json - 모든 베이스 아이템 데이터
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# ============================================================================
# 데이터 클래스 정의
# ============================================================================

@dataclass
class BaseItem:
    """베이스 아이템 데이터 구조"""
    name: str                    # 아이템 이름 (영문)
    item_type: str               # 아이템 타입 (Body Armour, Helmet, etc.)
    item_class: str              # 아이템 클래스 (int, str, dex, etc.)
    required_level: int          # 요구 레벨
    required_str: int            # 요구 힘
    required_dex: int            # 요구 민첩
    required_int: int            # 요구 지능
    base_armour: int             # 기본 방어력
    base_evasion: int            # 기본 회피
    base_energy_shield: int      # 기본 에너지 실드
    base_movement_speed: float   # 기본 이동속도 (Body Armour만)
    implicit_mod: Optional[str]  # 암시 모디파이어 (있는 경우)
    poe2db_url: str              # poe2db.tw URL


# ============================================================================
# URL 정의 - 모든 장비 카테고리
# ============================================================================

BASE_URL = "https://poe2db.tw/us"

# Body Armours
BODY_ARMOUR_URLS = {
    "body_armour_int": f"{BASE_URL}/Body_Armours_int",      # Energy Shield
    "body_armour_str": f"{BASE_URL}/Body_Armours_str",      # Armour
    "body_armour_dex": f"{BASE_URL}/Body_Armours_dex",      # Evasion
    "body_armour_str_int": f"{BASE_URL}/Body_Armours_str_int",  # Armour/ES
    "body_armour_str_dex": f"{BASE_URL}/Body_Armours_str_dex",  # Armour/Evasion
    "body_armour_dex_int": f"{BASE_URL}/Body_Armours_dex_int",  # Evasion/ES
}

# Helmets
HELMET_URLS = {
    "helmet_int": f"{BASE_URL}/Helmets_int",
    "helmet_str": f"{BASE_URL}/Helmets_str",
    "helmet_dex": f"{BASE_URL}/Helmets_dex",
    "helmet_str_int": f"{BASE_URL}/Helmets_str_int",
    "helmet_str_dex": f"{BASE_URL}/Helmets_str_dex",
    "helmet_dex_int": f"{BASE_URL}/Helmets_dex_int",
}

# Gloves
GLOVE_URLS = {
    "glove_int": f"{BASE_URL}/Gloves_int",
    "glove_str": f"{BASE_URL}/Gloves_str",
    "glove_dex": f"{BASE_URL}/Gloves_dex",
    "glove_str_int": f"{BASE_URL}/Gloves_str_int",
    "glove_str_dex": f"{BASE_URL}/Gloves_str_dex",
    "glove_dex_int": f"{BASE_URL}/Gloves_dex_int",
}

# Boots
BOOT_URLS = {
    "boot_int": f"{BASE_URL}/Boots_int",
    "boot_str": f"{BASE_URL}/Boots_str",
    "boot_dex": f"{BASE_URL}/Boots_dex",
    "boot_str_int": f"{BASE_URL}/Boots_str_int",
    "boot_str_dex": f"{BASE_URL}/Boots_str_dex",
    "boot_dex_int": f"{BASE_URL}/Boots_dex_int",
}

# Shields
SHIELD_URLS = {
    "shield_int": f"{BASE_URL}/Shields_int",
    "shield_str": f"{BASE_URL}/Shields_str",
    "shield_dex": f"{BASE_URL}/Shields_dex",
    "shield_str_int": f"{BASE_URL}/Shields_str_int",
    "shield_str_dex": f"{BASE_URL}/Shields_str_dex",
    "shield_dex_int": f"{BASE_URL}/Shields_dex_int",
}

# 모든 URL 통합
ALL_ARMOUR_URLS = {
    **{f"Body Armour|{k}": v for k, v in BODY_ARMOUR_URLS.items()},
    **{f"Helmet|{k}": v for k, v in HELMET_URLS.items()},
    **{f"Gloves|{k}": v for k, v in GLOVE_URLS.items()},
    **{f"Boots|{k}": v for k, v in BOOT_URLS.items()},
    **{f"Shield|{k}": v for k, v in SHIELD_URLS.items()},
}


# ============================================================================
# 스크래퍼 클래스
# ============================================================================

class Poe2dbBaseScraper:
    """poe2db.tw 베이스 아이템 스크래퍼"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })
        self.items: List[BaseItem] = []
        
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """페이지를 가져와서 BeautifulSoup 객체로 반환"""
        try:
            print(f"  Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"  ERROR fetching {url}: {e}")
            return None
    
    def parse_requirement(self, text: str) -> Dict[str, int]:
        """
        요구사항 텍스트 파싱
        예: "Requires: Level 65, 121 Int"
        예: "Requires: Level 45, 72 Str, 72 Int"
        """
        result = {"level": 0, "str": 0, "dex": 0, "int": 0}
        
        if not text:
            return result
            
        # Level 추출
        level_match = re.search(r'Level\s*(\d+)', text)
        if level_match:
            result["level"] = int(level_match.group(1))
        
        # Str 추출
        str_match = re.search(r'(\d+)\s*Str', text)
        if str_match:
            result["str"] = int(str_match.group(1))
            
        # Dex 추출
        dex_match = re.search(r'(\d+)\s*Dex', text)
        if dex_match:
            result["dex"] = int(dex_match.group(1))
            
        # Int 추출
        int_match = re.search(r'(\d+)\s*Int', text)
        if int_match:
            result["int"] = int(int_match.group(1))
            
        return result
    
    def parse_defence_stat(self, text: str, stat_name: str) -> int:
        """
        방어 스탯 파싱
        예: "Energy Shield: 184" -> 184
        예: "Armour: 200" -> 200
        """
        pattern = rf'{stat_name}[:\s]+(\d+)'
        match = re.search(pattern, text, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    
    def parse_movement_speed(self, text: str) -> float:
        """
        이동속도 파싱
        예: "Base Movement Speed: -0.03" -> -0.03
        """
        match = re.search(r'Movement Speed[:\s]+([-\d.]+)', text, re.IGNORECASE)
        return float(match.group(1)) if match else 0.0
    
    def scrape_category(self, item_type: str, item_class: str, url: str) -> List[BaseItem]:
        """특정 카테고리의 베이스 아이템 스크래핑"""
        items = []
        soup = self.fetch_page(url)
        
        if not soup:
            return items
        
        # BaseItem 섹션 찾기
        # poe2db.tw는 각 아이템을 특정 구조로 표시
        # 아이템들은 보통 특정 div나 섹션 안에 있음
        
        # 방법 1: 모든 아이템 링크 찾기
        item_links = soup.find_all('a', href=True)
        
        # 이미 처리한 아이템 이름 추적 (중복 방지)
        processed_names = set()
        
        # 텍스트 전체에서 아이템 패턴 찾기
        page_text = soup.get_text()
        
        # 아이템 블록 패턴 찾기
        # 각 아이템은 이름, 스탯, 요구사항 순서로 나옴
        
        # 모든 잠재적 아이템 이름 찾기 (링크 텍스트에서)
        potential_items = []
        for link in item_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # 아이템 이름 후보 (영어로 된 장비 이름)
            if text and href and not href.startswith('#') and not href.startswith('http'):
                # "Robe", "Raiment", "Vest", "Plate" 등으로 끝나는 것들
                if re.search(r'(Robe|Raiment|Vest|Plate|Mail|Coat|Brigandine|Jacket|Garb|Regalia|Helm|Helmet|Crown|Cap|Hood|Mask|Circlet|Casque|Gloves|Gauntlets|Mitts|Boots|Greaves|Slippers|Shoes|Shield|Tower|Buckler)', text):
                    if text not in processed_names:
                        potential_items.append({
                            'name': text,
                            'href': href
                        })
                        processed_names.add(text)
        
        print(f"    Found {len(potential_items)} potential items")
        
        # 각 아이템의 상세 정보 파싱
        for item_info in potential_items:
            name = item_info['name']
            href = item_info['href']
            
            # 해당 아이템 주변 텍스트 찾기
            item_section = self._find_item_section(soup, name)
            
            if item_section:
                # 스탯 파싱
                armour = self.parse_defence_stat(item_section, "Armour")
                evasion = self.parse_defence_stat(item_section, "Evasion")
                energy_shield = self.parse_defence_stat(item_section, "Energy Shield")
                movement_speed = self.parse_movement_speed(item_section)
                
                # 요구사항 파싱
                req = self.parse_requirement(item_section)
                
                # 암시 모드 파싱 (괄호 안의 텍스트)
                implicit_match = re.search(r'\(([^)]+%[^)]*)\)', item_section)
                implicit_mod = implicit_match.group(1) if implicit_match else None
                
                # BaseItem 생성
                base_item = BaseItem(
                    name=name,
                    item_type=item_type,
                    item_class=item_class,
                    required_level=req["level"],
                    required_str=req["str"],
                    required_dex=req["dex"],
                    required_int=req["int"],
                    base_armour=armour,
                    base_evasion=evasion,
                    base_energy_shield=energy_shield,
                    base_movement_speed=movement_speed,
                    implicit_mod=implicit_mod,
                    poe2db_url=f"{BASE_URL}/{href}" if not href.startswith('http') else href
                )
                
                items.append(base_item)
                print(f"      + {name}: ES={energy_shield}, Armour={armour}, Evasion={evasion}, Level={req['level']}")
        
        return items
    
    def _find_item_section(self, soup: BeautifulSoup, item_name: str) -> Optional[str]:
        """아이템 이름 주변의 텍스트 섹션 찾기"""
        # 전체 텍스트에서 아이템 이름 위치 찾기
        full_text = soup.get_text()
        
        # 아이템 이름 위치 찾기
        pattern = re.escape(item_name)
        matches = list(re.finditer(pattern, full_text))
        
        if not matches:
            return None
        
        # 첫 번째 매치 주변 500자 추출
        for match in matches:
            start = max(0, match.start() - 50)
            end = min(len(full_text), match.end() + 400)
            section = full_text[start:end]
            
            # 이 섹션이 실제 아이템 정보를 포함하는지 확인
            if "Energy Shield" in section or "Armour" in section or "Evasion" in section:
                if "Requires" in section or "Level" in section:
                    return section
        
        return None
    
    def scrape_all(self):
        """모든 카테고리 스크래핑"""
        print("=" * 60)
        print("PoE2DB Base Item Scraper")
        print("=" * 60)
        
        total_items = []
        
        for category_key, url in ALL_ARMOUR_URLS.items():
            parts = category_key.split("|")
            item_type = parts[0]
            item_class = parts[1] if len(parts) > 1 else "unknown"
            
            print(f"\n[{item_type}] - {item_class}")
            print("-" * 40)
            
            items = self.scrape_category(item_type, item_class, url)
            total_items.extend(items)
            
            print(f"  -> Collected {len(items)} items")
            
            # Rate limiting
            time.sleep(1)
        
        self.items = total_items
        print(f"\n{'=' * 60}")
        print(f"TOTAL: {len(total_items)} base items collected")
        print("=" * 60)
        
        return total_items
    
    def save_to_json(self, filepath: str = "scraped_bases.json"):
        """JSON 파일로 저장"""
        data = {
            "metadata": {
                "source": "poe2db.tw",
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_items": len(self.items)
            },
            "items": [asdict(item) for item in self.items]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved to {filepath}")


# ============================================================================
# 간단한 테스트 스크래퍼 (단일 페이지용)
# ============================================================================

def quick_scrape_body_armour_int():
    """Body Armour (INT) 카테고리만 빠르게 스크래핑"""
    print("Quick scrape: Body Armour (INT)")
    print("-" * 40)
    
    url = "https://poe2db.tw/us/Body_Armours_int"
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 모든 텍스트 가져오기
        text = soup.get_text()
        
        # 아이템 패턴 찾기
        # 패턴: [아이템이름](링크) Energy Shield: 숫자 ... Requires: Level 숫자, 숫자 Int
        
        items = []
        
        # 더 정교한 파싱: HTML 구조 활용
        # poe2db.tw는 각 아이템을 특정 div 안에 넣음
        
        # 모든 이미지 링크 찾기 (아이템 아이콘)
        item_containers = soup.find_all('a', href=True)
        
        seen_names = set()
        
        for container in item_containers:
            href = container.get('href', '')
            text = container.get_text(strip=True)
            
            # Robe 또는 Raiment로 끝나는 아이템 찾기 (INT body armour)
            if text and ('Robe' in text or 'Raiment' in text):
                if text not in seen_names:
                    seen_names.add(text)
                    
                    # 이 아이템의 상세 정보 찾기
                    # 부모 요소에서 스탯 정보 추출
                    parent = container.find_parent()
                    if parent:
                        parent_text = parent.get_text()
                        
                        # Energy Shield 값 추출
                        es_match = re.search(r'Energy Shield[:\s]+(\d+)', parent_text)
                        es = int(es_match.group(1)) if es_match else 0
                        
                        # Level 추출
                        level_match = re.search(r'Level\s*(\d+)', parent_text)
                        level = int(level_match.group(1)) if level_match else 0
                        
                        # Int 추출
                        int_match = re.search(r'(\d+)\s*Int', parent_text)
                        int_req = int(int_match.group(1)) if int_match else 0
                        
                        items.append({
                            'name': text,
                            'energy_shield': es,
                            'required_level': level,
                            'required_int': int_req,
                            'url': f"https://poe2db.tw/us/{href}"
                        })
                        
                        print(f"  + {text}: ES={es}, Level={level}, Int={int_req}")
        
        print(f"\nTotal: {len(items)} items found")
        return items
        
    except Exception as e:
        print(f"Error: {e}")
        return []


# ============================================================================
# 메인 실행
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # 빠른 테스트
        quick_scrape_body_armour_int()
    else:
        # 전체 스크래핑
        scraper = Poe2dbBaseScraper()
        scraper.scrape_all()
        scraper.save_to_json()
