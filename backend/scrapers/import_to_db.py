#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import scraped data to database - Fixed version
"""

import json
import sys
import os
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

class ItemType(Base):
    __tablename__ = 'item_types'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    category = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class ItemBase(Base):
    __tablename__ = 'item_bases_new'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    item_type = Column(String(50))
    item_class = Column(String(20))
    required_level = Column(Integer, default=0)
    required_str = Column(Integer, default=0)
    required_dex = Column(Integer, default=0)
    required_int = Column(Integer, default=0)
    base_armour = Column(Integer, default=0)
    base_evasion = Column(Integer, default=0)
    base_energy_shield = Column(Integer, default=0)
    movement_speed = Column(Float, default=0.0)
    implicit_mod = Column(String(500))
    poe2db_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

def main():
    db_path = "../poe2_profit_optimizer.db"
    data_file = "data/scraped_bases.json"
    
    print("=" * 60)
    print("  Import Scraped Data to Database")
    print("=" * 60)
    
    # Load JSON
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = data.get('items', [])
    print(f"\nLoaded {len(items)} items from JSON")
    
    # Connect to DB
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Clear existing
    deleted = session.query(ItemBase).delete()
    session.commit()
    print(f"Cleared {deleted} existing items")
    
    # Import
    imported = 0
    errors = 0
    for item in items:
        try:
            db_item = ItemBase(
                name=item['name'],
                item_type=item['item_type'],
                item_class=item.get('item_class', ''),
                required_level=item.get('required_level', 0),
                required_str=item.get('required_str', 0),
                required_dex=item.get('required_dex', 0),
                required_int=item.get('required_int', 0),
                base_armour=item.get('armour', 0),
                base_evasion=item.get('evasion', 0),
                base_energy_shield=item.get('energy_shield', 0),
                movement_speed=item.get('movement_speed', 0.0),
                implicit_mod=item.get('implicit_mod'),
                poe2db_url=item.get('poe2db_url', '')
            )
            session.add(db_item)
            imported += 1
        except Exception as e:
            errors += 1
            print(f"Error: {item.get('name')}: {e}")
    
    session.commit()
    
    # Verify
    count = session.query(ItemBase).count()
    
    session.close()
    
    print(f"\n" + "=" * 60)
    print(f"  COMPLETE")
    print(f"  - Imported: {imported}")
    print(f"  - Errors: {errors}")
    print(f"  - Total in DB: {count}")
    print("=" * 60)

if __name__ == "__main__":
    main()