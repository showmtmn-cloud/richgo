
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

import sys

import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))



from models.database_models import Base, Currency



def init_currencies():

    """기본 커런시 데이터 삽입"""

    engine = create_engine('sqlite:///poe2_profit_optimizer.db')

    Session = sessionmaker(bind=engine)

    session = Session()

    

    # 기본 오브 (Orb)

    orbs = [

        {'name': 'Divine Orb', 'name_kr': '신성한 오브', 'type': 'Orb', 'rarity': 'Very Rare'},

        {'name': 'Exalted Orb', 'name_kr': '숭고한 오브', 'type': 'Orb', 'rarity': 'Very Rare'},

        {'name': 'Chaos Orb', 'name_kr': '혼돈의 오브', 'type': 'Orb', 'rarity': 'Rare'},

        {'name': 'Regal Orb', 'name_kr': '왕실의 오브', 'type': 'Orb', 'rarity': 'Rare'},

        {'name': 'Orb of Alchemy', 'name_kr': '연금술의 오브', 'type': 'Orb', 'rarity': 'Common'},

        {'name': 'Orb of Transmutation', 'name_kr': '변화의 오브', 'type': 'Orb', 'rarity': 'Common'},

        {'name': 'Orb of Augmentation', 'name_kr': '확장의 오브', 'type': 'Orb', 'rarity': 'Common'},

        {'name': 'Orb of Annulment', 'name_kr': '소멸의 오브', 'type': 'Orb', 'rarity': 'Rare'},

        {'name': 'Orb of Scouring', 'name_kr': '세척의 오브', 'type': 'Orb', 'rarity': 'Common'},

        {'name': 'Vaal Orb', 'name_kr': '발 오브', 'type': 'Orb', 'rarity': 'Rare'},

    ]

    

    # Essence

    essences = [

        {'name': 'Essence of Woe', 'name_kr': '비애의 에센스', 'type': 'Essence', 'tier': 3},

        {'name': 'Essence of Rage', 'name_kr': '분노의 에센스', 'type': 'Essence', 'tier': 3},

        {'name': 'Perfect Essence', 'name_kr': '완벽한 에센스', 'type': 'Essence', 'tier': 4},

    ]

    

    # Omen

    omens = [

        {'name': 'Omen of Greater Exaltation', 'name_kr': '상급 승격의 징조', 'type': 'Omen', 'rarity': 'Very Rare'},

        {'name': 'Omen of Sinistral Exaltation', 'name_kr': '좌측 승격의 징조', 'type': 'Omen', 'rarity': 'Rare'},

        {'name': 'Omen of Dextral Exaltation', 'name_kr': '우측 승격의 징조', 'type': 'Omen', 'rarity': 'Rare'},

    ]

    

    # Catalyst

    catalysts = [

        {'name': "Tul's Catalyst", 'name_kr': '툴의 촉매', 'type': 'Catalyst', 'rarity': 'Common'},

        {'name': "Esh's Catalyst", 'name_kr': '에쉬의 촉매', 'type': 'Catalyst', 'rarity': 'Common'},

        {'name': 'Flesh Catalyst', 'name_kr': '살점 촉매', 'type': 'Catalyst', 'rarity': 'Common'},

    ]

    

    all_currencies = orbs + essences + omens + catalysts

    

    for curr_data in all_currencies:

        currency = Currency(**curr_data)

        session.add(currency)

    

    session.commit()

    print(f"✅ {len(all_currencies)}개 커런시 데이터 초기화 완료")

    session.close()



if __name__ == "__main__":

    init_currencies()

