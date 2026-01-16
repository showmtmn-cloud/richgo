
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from datetime import datetime



Base = declarative_base()



# 1. 리그

class League(Base):

    __tablename__ = 'leagues'

    id = Column(Integer, primary_key=True)

    name = Column(String(100), nullable=False)

    is_active = Column(Boolean, default=False)

    realm = Column(String(20))

    type = Column(String(10))

    created_at = Column(DateTime, default=datetime.utcnow)



# 2. 아이템 타입

class ItemType(Base):

    __tablename__ = 'item_types'

    id = Column(Integer, primary_key=True)

    name = Column(String(100), nullable=False)

    category = Column(String(50))



# 3. 베이스 아이템

class ItemBase(Base):

    __tablename__ = 'item_bases'

    id = Column(Integer, primary_key=True)

    name = Column(String(200), nullable=False)

    item_type_id = Column(Integer, ForeignKey('item_types.id'))

    required_level = Column(Integer)

    base_stats = Column(JSON)

    drop_zones = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    

    item_type = relationship("ItemType")



# 4. 모드 그룹

class ModGroup(Base):

    __tablename__ = 'mod_groups'

    id = Column(Integer, primary_key=True)

    name = Column(String(200), nullable=False)

    display_name = Column(String(200))

    is_prefix = Column(Boolean)

    tags = Column(JSON)



# 5. 모드 티어

class ModTier(Base):

    __tablename__ = 'mod_tiers'

    id = Column(Integer, primary_key=True)

    mod_group_id = Column(Integer, ForeignKey('mod_groups.id'))

    tier = Column(Integer)

    min_value = Column(Float)

    max_value = Column(Float)

    min_ilvl = Column(Integer)

    weight = Column(Integer)

    mod_text = Column(String(500))

    

    mod_group = relationship("ModGroup")



# 6. 베이스별 가능 모드

class BaseModPool(Base):

    __tablename__ = 'base_mod_pools'

    id = Column(Integer, primary_key=True)

    item_base_id = Column(Integer, ForeignKey('item_bases.id'))

    mod_group_id = Column(Integer, ForeignKey('mod_groups.id'))

    weight = Column(Integer)

    

    item_base = relationship("ItemBase")

    mod_group = relationship("ModGroup")



# 7. 커런시

class Currency(Base):

    __tablename__ = 'currencies'

    id = Column(Integer, primary_key=True)

    name = Column(String(200), nullable=False)

    name_kr = Column(String(200))

    type = Column(String(50))

    tier = Column(Integer, nullable=True)

    effect = Column(Text)

    usage = Column(Text)

    rarity = Column(String(50))



# 8. 커런시 환율

class CurrencyExchangeRate(Base):

    __tablename__ = 'currency_exchange_rates'

    id = Column(Integer, primary_key=True)

    league_id = Column(Integer, ForeignKey('leagues.id'))

    divine_to_exalt = Column(Float)

    divine_to_chaos = Column(Float)

    exalt_to_chaos = Column(Float)

    last_updated = Column(DateTime, default=datetime.utcnow)

    

    league = relationship("League")



# 9. 개별 커런시 가격

class CurrencyPrice(Base):

    __tablename__ = 'currency_prices'

    id = Column(Integer, primary_key=True)

    league_id = Column(Integer, ForeignKey('leagues.id'))

    currency_id = Column(Integer, ForeignKey('currencies.id'))

    price_chaos = Column(Float)

    price_divine = Column(Float)

    last_updated = Column(DateTime, default=datetime.utcnow)

    

    league = relationship("League")

    currency = relationship("Currency")



# 10. 베이스 가격

class BasePrice(Base):

    __tablename__ = 'base_prices'

    id = Column(Integer, primary_key=True)

    league_id = Column(Integer, ForeignKey('leagues.id'))

    item_base_id = Column(Integer, ForeignKey('item_bases.id'))

    ilvl = Column(Integer)

    price_chaos = Column(Float)

    price_divine = Column(Float)

    listings_count = Column(Integer)

    last_updated = Column(DateTime, default=datetime.utcnow)

    

    league = relationship("League")

    item_base = relationship("ItemBase")



# 11. 완성품 가격

class FinishedPrice(Base):

    __tablename__ = 'finished_prices'

    id = Column(Integer, primary_key=True)

    league_id = Column(Integer, ForeignKey('leagues.id'))

    item_base_id = Column(Integer, ForeignKey('item_bases.id'))

    target_mods = Column(JSON)

    avg_price_divine = Column(Float)

    min_price_divine = Column(Float)

    max_price_divine = Column(Float)

    sales_count_24h = Column(Integer)

    avg_sale_time_hours = Column(Float)

    last_updated = Column(DateTime, default=datetime.utcnow)

    

    league = relationship("League")

    item_base = relationship("ItemBase")



# 12. 크래프팅 확률

class CraftingProbability(Base):

    __tablename__ = 'crafting_probabilities'

    id = Column(Integer, primary_key=True)

    item_base_id = Column(Integer, ForeignKey('item_bases.id'))

    ilvl = Column(Integer)

    mod_group_id = Column(Integer, ForeignKey('mod_groups.id'))

    tier = Column(Integer)

    probability = Column(Float)

    method = Column(String(100))

    

    item_base = relationship("ItemBase")

    mod_group = relationship("ModGroup")



# 13. 수익 기회

class ProfitOpportunity(Base):

    __tablename__ = 'profit_opportunities'

    id = Column(Integer, primary_key=True)

    league_id = Column(Integer, ForeignKey('leagues.id'))

    item_base_id = Column(Integer, ForeignKey('item_bases.id'))

    ilvl = Column(Integer)

    base_cost_divine = Column(Float)

    crafting_cost_divine = Column(Float)

    expected_sale_price_divine = Column(Float)

    net_profit_divine = Column(Float)

    roi_percentage = Column(Float)

    success_probability = Column(Float)

    risk_level = Column(String(20))

    crafting_path = Column(JSON)

    calculated_at = Column(DateTime, default=datetime.utcnow)

    

    league = relationship("League")

    item_base = relationship("ItemBase")



# 14. 가격 히스토리

class PriceHistory(Base):

    __tablename__ = 'price_history'

    id = Column(Integer, primary_key=True)

    item_base_id = Column(Integer, ForeignKey('item_bases.id'))

    league_id = Column(Integer, ForeignKey('leagues.id'))

    price_type = Column(String(20))

    ilvl = Column(Integer, nullable=True)

    price_divine = Column(Float)

    recorded_at = Column(DateTime, default=datetime.utcnow)

    

    item_base = relationship("ItemBase")

    league = relationship("League")



# 15. Essence

class Essence(Base):

    __tablename__ = 'essences'

    id = Column(Integer, primary_key=True)

    name = Column(String(200), nullable=False)

    name_kr = Column(String(200))

    tier = Column(String(50))

    guaranteed_mod_group_id = Column(Integer, ForeignKey('mod_groups.id'), nullable=True)

    guaranteed_tier = Column(Integer, nullable=True)

    effect_description = Column(Text)

    

    guaranteed_mod = relationship("ModGroup")



# 데이터베이스 초기화 함수

def init_db():

    from sqlalchemy import create_engine

    from sqlalchemy.orm import sessionmaker

    

    engine = create_engine('sqlite:///poe2_profit_optimizer.db')

    Base.metadata.create_all(engine)

    

    Session = sessionmaker(bind=engine)

    session = Session()

    

    # 기본 리그 생성

    league = League(

        name="Fate of the Vaal",

        is_active=True,

        realm="PC",

        type="SC"

    )

    session.add(league)

    session.commit()

    session.close()

    

    print("✅ 데이터베이스 초기화 완료 (15개 테이블)")



if __name__ == "__main__":

    init_db()

