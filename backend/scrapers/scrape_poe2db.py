# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
PoE2DB Base Item Scraper
Scrapes base item data from poe2db.tw

Usage:
    python scrape_poe2db.py              # Full scrape
    python scrape_poe2db.py --test       # Test Body Armour INT only
    python scrape_poe2db.py --weapons    # Include weapons

Output:
    data/scraped_bases.json
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime

# ============================================================================
# Configuration
# ============================================================================

BASE_URL = "https://poe2db.tw/us"

# Armour categories
ARMOUR_PAGES = {
    # Body Armour
    "Body Armour|int": "/Body_Armours_int",
    "Body Armour|str": "/Body_Armours_str",
    "Body Armour|dex": "/Body_Armours_dex",
    "Body Armour|str_int": "/Body_Armours_str_int",
    "Body Armour|str_dex": "/Body_Armours_str_dex",
    "Body Armour|dex_int": "/Body_Armours_dex_int",
    
    # Helmet
    "Helmet|int": "/Helmets_int",
    "Helmet|str": "/Helmets_str",
    "Helmet|dex": "/Helmets_dex",
    "Helmet|str_int": "/Helmets_str_int",
    "Helmet|str_dex": "/Helmets_str_dex",
    "Helmet|dex_int": "/Helmets_dex_int",
    
    # Gloves
    "Gloves|int": "/Gloves_int",
    "Gloves|str": "/Gloves_str",
    "Gloves|dex": "/Gloves_dex",
    "Gloves|str_int": "/Gloves_str_int",
    "Gloves|str_dex": "/Gloves_str_dex",
    "Gloves|dex_int": "/Gloves_dex_int",
    
    # Boots
    "Boots|int": "/Boots_int",
    "Boots|str": "/Boots_str",
    "Boots|dex": "/Boots_dex",
    "Boots|str_int": "/Boots_str_int",
    "Boots|str_dex": "/Boots_str_dex",
    "Boots|dex_int": "/Boots_dex_int",
    
    # Shield
    "Shield|int": "/Shields_int",
    "Shield|str": "/Shields_str",
    "Shield|dex": "/Shields_dex",
    "Shield|str_int": "/Shields_str_int",
    "Shield|str_dex": "/Shields_str_dex",
    "Shield|dex_int": "/Shields_dex_int",
}

# Accessory categories
ACCESSORY_PAGES = {
    "Ring": "/Rings",
    "Amulet": "/Amulets",
    "Belt": "/Belts",
}

# Weapon categories (optional)
WEAPON_PAGES = {
    "One Hand Sword": "/One_Hand_Swords",
    "One Hand Axe": "/One_Hand_Axes",
    "One Hand Mace": "/One_Hand_Maces",
    "Dagger": "/Daggers",
    "Claw": "/Claws",
    "Wand": "/Wands",
    "Sceptre": "/Sceptres",
    "Two Hand Sword": "/Two_Hand_Swords",
    "Two Hand Axe": "/Two_Hand_Axes",
    "Two Hand Mace": "/Two_Hand_Maces",
    "Staff": "/Staves",
    "Warstaff": "/Warstaves",
    "Bow": "/Bows",
    "Crossbow": "/Crossbows",
    "Quiver": "/Quivers",
    "Focus": "/Foci",
}


# ============================================================================
# Data Class
# ============================================================================

@dataclass
class BaseItemData:
    """Base item data structure"""
    name: str
    item_type: str
    item_class: str
    required_level: int = 0
    required_str: int = 0
    required_dex: int = 0
    required_int: int = 0
    armour: int = 0
    evasion: int = 0
    energy_shield: int = 0
    movement_speed: float = 0.0
    block_chance: int = 0
    physical_damage_min: int = 0
    physical_damage_max: int = 0
    critical_strike_chance: float = 0.0
    attacks_per_second: float = 0.0
    implicit_mod: Optional[str] = None
    poe2db_url: str = ""
    scraped_at: str = ""


# ============================================================================
# Scraper Class
# ============================================================================

class Poe2dbScraper:
    """poe2db.tw scraper"""
    
    def __init__(self, include_weapons: bool = False):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        })
        self.include_weapons = include_weapons
        self.all_items: List[BaseItemData] = []
        self.errors: List[str] = []
        
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch page HTML"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.errors.append(f"Fetch error ({url}): {e}")
            return None
    
    def parse_items_from_html(self, html: str, item_type: str, item_class: str) -> List[BaseItemData]:
        """Extract item info from HTML"""
        items = []
        soup = BeautifulSoup(html, 'html.parser')
        full_text = soup.get_text()
        
        item_links = soup.find_all('a', href=True)
        seen = set()
        
        for link in item_links:
            name = link.get_text(strip=True)
            href = link.get('href', '')
            
            if not name or name in seen or len(name) < 3:
                continue
            if href.startswith('#') or href.startswith('http') or 'Modifier' in href:
                continue
            
            if not self._is_valid_item_name(name, item_type):
                continue
            
            seen.add(name)
            
            item_data = self._extract_item_details(soup, full_text, name, 
                                                   item_type, item_class, href)
            
            if item_data:
                items.append(item_data)
        
        return items
    
    def _is_valid_item_name(self, name: str, item_type: str) -> bool:
        """Check if valid item name"""
        if len(name) < 4 or len(name) > 50:
            return False
        
        if name.isdigit():
            return False
        
        excluded = ['Close', 'Reset', 'Import', 'Edit', 'PoE2DB', 'Total', 
                   'Modifier', 'Weight', 'Level', 'Prefix', 'Suffix', 'Craft']
        if any(ex in name for ex in excluded):
            return False
        
        keywords = {
            "Body Armour": ["Robe", "Raiment", "Vest", "Plate", "Mail", "Coat", 
                          "Brigandine", "Jacket", "Garb", "Regalia", "Hauberk", 
                          "Tunic", "Armour", "Vestment", "Doublet"],
            "Helmet": ["Helm", "Helmet", "Crown", "Cap", "Hood", "Mask", "Circlet",
                      "Casque", "Coif", "Burgonet", "Bascinet", "Sallet", "Visage",
                      "Great Helm", "Cage"],
            "Gloves": ["Gloves", "Gauntlets", "Mitts", "Wraps", "Bracers", "Grips"],
            "Boots": ["Boots", "Greaves", "Slippers", "Shoes", "Treads", 
                     "Footpads", "Leggings"],
            "Shield": ["Shield", "Tower", "Buckler", "Kite", "Spiked", "Round", "Pavise"],
            "Ring": ["Ring"],
            "Amulet": ["Amulet", "Talisman"],
            "Belt": ["Belt", "Sash", "Stygian"],
        }
        
        weapon_keywords = {
            "One Hand Sword": ["Sword", "Blade", "Sabre", "Falchion", "Cutlass"],
            "One Hand Axe": ["Axe", "Hatchet", "Tomahawk", "Cleaver"],
            "One Hand Mace": ["Mace", "Club", "Hammer", "Flail", "Sceptre"],
            "Dagger": ["Dagger", "Shiv", "Stiletto", "Kris", "Knife"],
            "Claw": ["Claw", "Fist", "Tiger", "Cat"],
            "Wand": ["Wand", "Horn", "Driftwood"],
            "Sceptre": ["Sceptre", "Void", "Crystal", "Opal"],
            "Two Hand Sword": ["Greatsword", "Longsword", "Bastard"],
            "Two Hand Axe": ["Great Axe", "Labrys", "Woodsplitter"],
            "Two Hand Mace": ["Maul", "Sledgehammer", "Colossus"],
            "Staff": ["Staff", "Quarterstaff"],
            "Warstaff": ["Warstaff", "Lathi", "Iron"],
            "Bow": ["Bow", "Longbow", "Shortbow"],
            "Crossbow": ["Crossbow", "Arbalest"],
            "Quiver": ["Quiver"],
            "Focus": ["Focus", "Censer", "Basket"],
        }
        
        all_keywords = {**keywords, **weapon_keywords}
        type_keywords = all_keywords.get(item_type, [])
        
        if type_keywords:
            return any(kw.lower() in name.lower() for kw in type_keywords)
        
        return True
    
    def _extract_item_details(self, soup: BeautifulSoup, full_text: str, 
                              name: str, item_type: str, item_class: str,
                              href: str) -> Optional[BaseItemData]:
        """Extract item details"""
        
        name_pattern = re.escape(name)
        match = re.search(name_pattern, full_text)
        
        if not match:
            return None
        
        start_idx = match.end()
        end_idx = min(len(full_text), start_idx + 500)
        context = full_text[start_idx:end_idx]
        
        # === Extract stats ===
        
        # Energy Shield
        es_match = re.search(r'Energy Shield[:\s]+(\d+)', context, re.IGNORECASE)
        energy_shield = int(es_match.group(1)) if es_match else 0
        
        # Armour
        armour_match = re.search(r'(?<![gy] )Armour[:\s]+(\d+)', context, re.IGNORECASE)
        armour = int(armour_match.group(1)) if armour_match else 0
        
        # Evasion
        evasion_match = re.search(r'Evasion(?:\s+Rating)?[:\s]+(\d+)', context, re.IGNORECASE)
        evasion = int(evasion_match.group(1)) if evasion_match else 0
        
        # Movement Speed
        ms_match = re.search(r'Movement Speed[:\s]+([-\d.]+)', context, re.IGNORECASE)
        movement_speed = float(ms_match.group(1)) if ms_match else 0.0
        
        # Block Chance
        block_match = re.search(r'Block[:\s]+(\d+)%', context, re.IGNORECASE)
        block_chance = int(block_match.group(1)) if block_match else 0
        
        # === Extract requirements ===
        
        level_match = re.search(r'Level\s+(\d+)', context)
        required_level = int(level_match.group(1)) if level_match else 0
        
        str_match = re.search(r'(\d+)\s*Str', context)
        required_str = int(str_match.group(1)) if str_match else 0
        
        dex_match = re.search(r'(\d+)\s*Dex', context)
        required_dex = int(dex_match.group(1)) if dex_match else 0
        
        int_match = re.search(r'(\d+)\s*Int', context)
        required_int = int(int_match.group(1)) if int_match else 0
        
        # === Extract implicit mod ===
        implicit_match = re.search(r'\(([\d\-]+%[^)]*)\)', context)
        implicit_mod = implicit_match.group(1) if implicit_match else None
        
        # === Weapon stats ===
        physical_min = physical_max = 0
        crit_chance = attacks_per_sec = 0.0
        
        if item_type in ["One Hand Sword", "One Hand Axe", "One Hand Mace", "Dagger",
                        "Claw", "Wand", "Sceptre", "Two Hand Sword", "Two Hand Axe",
                        "Two Hand Mace", "Staff", "Warstaff", "Bow", "Crossbow"]:
            phys_match = re.search(r'Physical Damage[:\s]+(\d+)[-]+(\d+)', context)
            if phys_match:
                physical_min = int(phys_match.group(1))
                physical_max = int(phys_match.group(2))
            
            crit_match = re.search(r'Critical[:\s]+([\d.]+)%', context)
            if crit_match:
                crit_chance = float(crit_match.group(1))
            
            aps_match = re.search(r'Attacks per Second[:\s]+([\d.]+)', context)
            if aps_match:
                attacks_per_sec = float(aps_match.group(1))
        
        # Validate - must have at least one stat
        has_defence = energy_shield > 0 or armour > 0 or evasion > 0
        has_weapon = physical_min > 0 or crit_chance > 0
        
        if not has_defence and not has_weapon and required_level == 0:
            return None
        
        return BaseItemData(
            name=name,
            item_type=item_type,
            item_class=item_class,
            required_level=required_level,
            required_str=required_str,
            required_dex=required_dex,
            required_int=required_int,
            armour=armour,
            evasion=evasion,
            energy_shield=energy_shield,
            movement_speed=movement_speed,
            block_chance=block_chance,
            physical_damage_min=physical_min,
            physical_damage_max=physical_max,
            critical_strike_chance=crit_chance,
            attacks_per_second=attacks_per_sec,
            implicit_mod=implicit_mod,
            poe2db_url=f"{BASE_URL}/{href}",
            scraped_at=datetime.now().isoformat()
        )
    
    def scrape_category(self, category_key: str, url_path: str) -> List[BaseItemData]:
        """Scrape single category"""
        parts = category_key.split("|")
        item_type = parts[0]
        item_class = parts[1] if len(parts) > 1 else "default"
        
        full_url = BASE_URL + url_path
        print(f"    -> {full_url}")
        
        html = self.fetch_page(full_url)
        if not html:
            return []
        
        items = self.parse_items_from_html(html, item_type, item_class)
        
        return items
    
    def scrape_all(self) -> List[BaseItemData]:
        """Scrape all categories"""
        print("=" * 70)
        print("  PoE2DB Base Item Scraper")
        print("  Source: poe2db.tw")
        print("=" * 70)
        
        all_items = []
        
        # Armour
        print("\n[ARMOUR]")
        print("-" * 50)
        for key, path in ARMOUR_PAGES.items():
            items = self.scrape_category(key, path)
            print(f"      Collected: {len(items)} items")
            all_items.extend(items)
            time.sleep(0.3)
        
        # Accessories
        print("\n[ACCESSORIES]")
        print("-" * 50)
        for key, path in ACCESSORY_PAGES.items():
            items = self.scrape_category(f"{key}|default", path)
            print(f"      Collected: {len(items)} items")
            all_items.extend(items)
            time.sleep(0.3)
        
        # Weapons (optional)
        if self.include_weapons:
            print("\n[WEAPONS]")
            print("-" * 50)
            for key, path in WEAPON_PAGES.items():
                items = self.scrape_category(f"{key}|default", path)
                print(f"      Collected: {len(items)} items")
                all_items.extend(items)
                time.sleep(0.3)
        
        self.all_items = all_items
        
        print(f"\n{'=' * 70}")
        print(f"  COMPLETE: {len(all_items)} base items collected")
        if self.errors:
            print(f"  Errors: {len(self.errors)}")
        print("=" * 70)
        
        return all_items
    
    def save_to_json(self, filepath: str = "data/scraped_bases.json") -> str:
        """Save to JSON file"""
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        
        type_stats = {}
        for item in self.all_items:
            key = item.item_type
            type_stats[key] = type_stats.get(key, 0) + 1
        
        data = {
            "metadata": {
                "source": "poe2db.tw",
                "scraper_version": "3.0",
                "scraped_at": datetime.now().isoformat(),
                "total_items": len(self.all_items),
                "by_type": type_stats,
                "errors": self.errors
            },
            "items": [asdict(item) for item in self.all_items]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved to: {filepath}")
        return filepath


# ============================================================================
# Test Function
# ============================================================================

def test_single_page():
    """Test with single page"""
    print("TEST MODE: Body Armour (INT) only\n")
    
    scraper = Poe2dbScraper()
    items = scraper.scrape_category("Body Armour|int", "/Body_Armours_int")
    
    print(f"\nCollected: {len(items)} items\n")
    
    for item in items:
        print(f"* {item.name}")
        stats = []
        if item.energy_shield > 0:
            stats.append(f"ES: {item.energy_shield}")
        if item.armour > 0:
            stats.append(f"Armour: {item.armour}")
        if item.evasion > 0:
            stats.append(f"Evasion: {item.evasion}")
        reqs = []
        if item.required_level > 0:
            reqs.append(f"Lv {item.required_level}")
        if item.required_int > 0:
            reqs.append(f"Int {item.required_int}")
        
        print(f"  {', '.join(stats)} | Requires: {', '.join(reqs)}")
    
    return items


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if "--test" in sys.argv:
        test_single_page()
    elif "--weapons" in sys.argv:
        scraper = Poe2dbScraper(include_weapons=True)
        scraper.scrape_all()
        scraper.save_to_json()
    else:
        scraper = Poe2dbScraper(include_weapons=False)
        scraper.scrape_all()
        scraper.save_to_json()
