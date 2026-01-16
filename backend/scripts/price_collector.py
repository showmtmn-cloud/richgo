
#!/usr/bin/env python3

"""

PoE2 Price Collector - Correct Schema Version

Uses existing table structure with proper FK references

"""

import os

import sqlite3

from datetime import datetime



DB_PATH = os.path.expanduser("~/poe2-profit-optimizer/backend/poe2_profit_optimizer.db")

LEAGUE_ID = 1  # Fate of Vaal



# Currency prices in Divine

CURRENCY_PRICES_DATA = {

    "Divine Orb": 1.0,

    "Exalted Orb": 0.0125,

    "Chaos Orb": 0.005,

    "Regal Orb": 0.04,

    "Orb of Alchemy": 0.006,

    "Orb of Annulment": 0.5,

    "Orb of Scouring": 0.02,

    "Vaal Orb": 0.1,

    "Essence of Woe": 0.5,

    "Essence of Rage": 0.6,

    "Perfect Essence": 2.0,

    "Omen of Greater Exaltation": 5.0,

    "Omen of Sinistral Exaltation": 3.0,

    "Omen of Dextral Exaltation": 3.0,

    "Flesh Catalyst": 0.15,

}



# Base item prices in Divine

BASE_PRICES_DATA = {

    "Breach Ring": 0.3,

    "Dusk Ring": 0.1,

    "Gloam Ring": 0.1,

    "Penumbra Ring": 0.15,

    "Tenebrous Ring": 0.2,

    "Jade Amulet": 0.5,

    "Gold Amulet": 0.3,

}



# Exchange rates

DIVINE_TO_EXALT = 80

DIVINE_TO_CHAOS = 200





def main():

    print("=" * 50)

    print("PoE2 Price Collector (Correct Schema)")

    print("=" * 50)

    

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    

    # Step 1: Save currency exchange rates

    print("\n[Step 1] Currency Exchange Rates")

    print("-" * 40)

    

    cursor.execute("""

        INSERT INTO currency_exchange_rates (league_id, divine_to_exalt, divine_to_chaos, exalt_to_chaos, last_updated)

        VALUES (?, ?, ?, ?, ?)

    """, (LEAGUE_ID, DIVINE_TO_EXALT, DIVINE_TO_CHAOS, DIVINE_TO_CHAOS / DIVINE_TO_EXALT, datetime.now()))

    conn.commit()

    print("  1 Divine = {} Exalt = {} Chaos".format(DIVINE_TO_EXALT, DIVINE_TO_CHAOS))

    

    # Step 2: Save currency prices (using currency_id FK)

    print("\n[Step 2] Currency Prices")

    print("-" * 40)

    

    saved_currencies = 0

    for name, price_divine in CURRENCY_PRICES_DATA.items():

        # Find currency_id from currencies table

        cursor.execute("SELECT id FROM currencies WHERE name = ?", (name,))

        result = cursor.fetchone()

        

        if result:

            currency_id = result[0]

            price_chaos = price_divine * DIVINE_TO_CHAOS

            

            # Delete existing and insert new

            cursor.execute("DELETE FROM currency_prices WHERE currency_id = ? AND league_id = ?", (currency_id, LEAGUE_ID))

            cursor.execute("""

                INSERT INTO currency_prices (league_id, currency_id, price_chaos, price_divine, last_updated)

                VALUES (?, ?, ?, ?, ?)

            """, (LEAGUE_ID, currency_id, price_chaos, price_divine, datetime.now()))

            

            saved_currencies += 1

            print("  [OK] {}: {} Divine".format(name, price_divine))

        else:

            print("  [--] {}: not in currencies table".format(name))

    

    conn.commit()

    print("  Saved: {}/{}".format(saved_currencies, len(CURRENCY_PRICES_DATA)))

    

    # Step 3: Save base prices (using item_base_id FK)

    print("\n[Step 3] Base Item Prices")

    print("-" * 40)

    

    saved_bases = 0

    for name, price_divine in BASE_PRICES_DATA.items():

        # Find item_base_id from item_bases table

        cursor.execute("SELECT id FROM item_bases WHERE name = ?", (name,))

        result = cursor.fetchone()

        

        if result:

            item_base_id = result[0]

            price_chaos = price_divine * DIVINE_TO_CHAOS

            

            # Delete existing and insert new

            cursor.execute("DELETE FROM base_prices WHERE item_base_id = ? AND league_id = ?", (item_base_id, LEAGUE_ID))

            cursor.execute("""

                INSERT INTO base_prices (league_id, item_base_id, ilvl, price_chaos, price_divine, listings_count, last_updated)

                VALUES (?, ?, ?, ?, ?, ?, ?)

            """, (LEAGUE_ID, item_base_id, 82, price_chaos, price_divine, 10, datetime.now()))

            

            saved_bases += 1

            print("  [OK] {}: {} Divine".format(name, price_divine))

        else:

            print("  [--] {}: not in item_bases table".format(name))

    

    conn.commit()

    print("  Saved: {}/{}".format(saved_bases, len(BASE_PRICES_DATA)))

    

    # Step 4: Show stats

    print("\n" + "=" * 50)

    print("DONE! Database Stats:")

    print("=" * 50)

    

    cursor.execute("SELECT COUNT(*) FROM currency_exchange_rates")

    print("  Exchange rates: {}".format(cursor.fetchone()[0]))

    

    cursor.execute("SELECT COUNT(*) FROM currency_prices")

    print("  Currency prices: {}".format(cursor.fetchone()[0]))

    

    cursor.execute("SELECT COUNT(*) FROM base_prices")

    print("  Base prices: {}".format(cursor.fetchone()[0]))

    

    conn.close()

    print("\n[OK] All done!")





if __name__ == "__main__":

    main()

