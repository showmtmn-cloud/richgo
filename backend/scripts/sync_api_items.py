
#!/usr/bin/env python3

"""

Sync item bases from official PoE2 Trade API

"""

import requests

import sys

import os

from datetime import datetime



sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

from models.database_models import ItemBase, ItemType



def fetch_api_items():

    """Fetch all base items from Trade API"""

    url = "https://www.pathofexile.com/api/trade2/data/items"

    

    headers = {

        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',

        'Accept': 'application/json'

    }

    

    response = requests.get(url, headers=headers)

    print(f"Status: {response.status_code}")

    

    if response.status_code != 200:

        return []

    

    data = response.json()

    

    items = []

    target_categories = ['accessory', 'armour', 'weapon', 'flask', 'jewel']

    

    for category in data['result']:

        if category['id'] not in target_categories:

            continue

        

        for entry in category['entries']:

            if 'unique' in entry.get('flags', {}):

                continue

            

            items.append({

                'name': entry['type'],

                'category_id': category['id'],

                'category_label': category['label']

            })

    

    return items



def sync_to_db():

    """Sync API items to database"""

    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'poe2_profit_optimizer.db')

    engine = create_engine(f'sqlite:///{db_path}')

    Session = sessionmaker(bind=engine)

    session = Session()

    

    try:

        api_items = fetch_api_items()

        print(f"Fetched {len(api_items)} items from API")

        

        if not api_items:

            print("No items fetched, aborting")

            return

        

        # Step 1: Create item types

        categories = {}

        for item in api_items:

            cat_id = item['category_id']

            if cat_id not in categories:

                categories[cat_id] = item['category_label']

        

        print(f"\nCreating {len(categories)} item types...")

        type_map = {}  # category_id -> ItemType.id

        

        for cat_id, cat_label in categories.items():

            existing = session.query(ItemType).filter_by(name=cat_label).first()

            if existing:

                type_map[cat_id] = existing.id

                print(f"  Existing: {cat_label} (id={existing.id})")

            else:

                new_type = ItemType(name=cat_label, category=cat_id)

                session.add(new_type)

                session.flush()

                type_map[cat_id] = new_type.id

                print(f"  Created: {cat_label} (id={new_type.id})")

        

        # Step 2: Create/Update item bases

        print(f"\nSyncing {len(api_items)} items...")

        added = 0

        updated = 0

        

        for item in api_items:

            existing = session.query(ItemBase).filter_by(name=item['name']).first()

            type_id = type_map[item['category_id']]

            

            if existing:

                existing.item_type_id = type_id

                updated += 1

            else:

                new_item = ItemBase(

                    name=item['name'],

                    item_type_id=type_id,

                    created_at=datetime.now()

                )

                session.add(new_item)

                added += 1

        

        session.commit()

        print(f"\nAdded: {added}, Updated: {updated}")

        

        total = session.query(ItemBase).count()

        print(f"Total items in DB: {total}")

        

    except Exception as e:

        print(f"Error: {e}")

        import traceback

        traceback.print_exc()

        session.rollback()

    finally:

        session.close()



if __name__ == "__main__":

    sync_to_db()

