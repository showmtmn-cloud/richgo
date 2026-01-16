
#!/usr/bin/env python3

"""

PoE2 Price Fetcher from poe.ninja API

- Fetches real-time currency prices

- Caches to local SQLite database

- Rate limit safe: designed for hourly updates only

"""

import os

import sqlite3

import json

import time

from datetime import datetime

from urllib.request import urlopen, Request

from urllib.error import URLError, HTTPError



DB_PATH = os.path.expanduser("~/poe2-profit-optimizer/backend/poe2_profit_optimizer.db")

LEAGUE_ID = 1

LEAGUE_NAME = "Fate of the Vaal"



# API Endpoints (discovered from community research)

POE_NINJA_BASE = "https://poe.ninja/poe2/api/economy"



ENDPOINTS = {

    "currency": f"{POE_NINJA_BASE}/currencyexchange/overview?leagueName={LEAGUE_NAME.replace(' ', '%20')}&overviewName=Currency",

    "essence": f"{POE_NINJA_BASE}/currencyexchange/overview?leagueName={LEAGUE_NAME.replace(' ', '%20')}&overviewName=Essence",

    "omen": f"{POE_NINJA_BASE}/currencyexchange/overview?leagueName={LEAGUE_NAME.replace(' ', '%20')}&overviewName=Omen",

}



# Minimum delay between API calls (seconds)

API_DELAY = 2





def fetch_api(url, timeout=30):

    """Fetch data from poe.ninja API with proper error handling"""

    headers = {

        "User-Agent": "PoE2-Profit-Optimizer/1.0 (Educational Project)",

        "Accept": "application/json",

    }

    

    try:

        req = Request(url, headers=headers)

        with urlopen(req, timeout=timeout) as response:

            data = response.read().decode("utf-8")

            return json.loads(data)

    except HTTPError as e:

        print(f"  [ERROR] HTTP {e.code}: {e.reason}")

        return None

    except URLError as e:

        print(f"  [ERROR] URL Error: {e.reason}")

        return None

    except Exception as e:

        print(f"  [ERROR] {type(e).__name__}: {e}")

        return None





def parse_currency_data(data):

    """Parse poe.ninja currency response"""

    if not data:

        return {}

    

    prices = {}

    

    # PoE2 API structure: lines + items

    lines = data.get("lines", [])

    items = {item["id"]: item for item in data.get("items", [])}

    

    for line in lines:

        item_id = line.get("id")

        if item_id and item_id in items:

            name = items[item_id].get("name", "Unknown")

            # primaryValue is in Chaos equivalent

            chaos_value = line.get("primaryValue", 0)

            if chaos_value and chaos_value > 0:

                prices[name] = chaos_value

    

    return prices





def update_database(prices, divine_chaos_rate):

    """Update database with fetched prices"""

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    

    updated_count = 0

    

    for name, chaos_value in prices.items():

        # Calculate divine value

        divine_value = chaos_value / divine_chaos_rate if divine_chaos_rate > 0 else 0

        

        # Try to find currency in our database

        cursor.execute("SELECT id FROM currencies WHERE name = ?", (name,))

        result = cursor.fetchone()

        

        if result:

            currency_id = result[0]

            # Update or insert price

            cursor.execute("""

                DELETE FROM currency_prices 

                WHERE currency_id = ? AND league_id = ?

            """, (currency_id, LEAGUE_ID))

            

            cursor.execute("""

                INSERT INTO currency_prices 

                (league_id, currency_id, price_chaos, price_divine, last_updated)

                VALUES (?, ?, ?, ?, ?)

            """, (LEAGUE_ID, currency_id, chaos_value, divine_value, datetime.now()))

            

            updated_count += 1

    

    # Update exchange rate

    if divine_chaos_rate > 0:

        cursor.execute("""

            INSERT INTO currency_exchange_rates 

            (league_id, divine_to_exalt, divine_to_chaos, exalt_to_chaos, last_updated)

            VALUES (?, ?, ?, ?, ?)

        """, (LEAGUE_ID, divine_chaos_rate / 2.5, divine_chaos_rate, 2.5, datetime.now()))

    

    conn.commit()

    conn.close()

    

    return updated_count





def main():

    print("=" * 60)

    print("PoE2 poe.ninja Price Fetcher")

    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"League: {LEAGUE_NAME}")

    print("=" * 60)

    

    all_prices = {}

    divine_chaos_rate = 200  # Default fallback

    

    # Fetch each category

    for category, url in ENDPOINTS.items():

        print(f"\n[{category.upper()}] Fetching from poe.ninja...")

        print(f"  URL: {url[:80]}...")

        

        data = fetch_api(url)

        

        if data:

            prices = parse_currency_data(data)

            print(f"  [OK] Found {len(prices)} items")

            

            # Show sample prices

            for name, value in list(prices.items())[:5]:

                print(f"      - {name}: {value:.2f} Chaos")

            if len(prices) > 5:

                print(f"      ... and {len(prices) - 5} more")

            

            all_prices.update(prices)

            

            # Get Divine Orb rate if available

            if "Divine Orb" in prices:

                divine_chaos_rate = prices["Divine Orb"]

                print(f"\n  Divine Orb rate: {divine_chaos_rate:.2f} Chaos")

        else:

            print(f"  [WARN] Failed to fetch {category}")

        

        # Rate limit protection

        time.sleep(API_DELAY)

    

    # Summary

    print("\n" + "=" * 60)

    print("FETCH SUMMARY")

    print("=" * 60)

    print(f"Total items fetched: {len(all_prices)}")

    print(f"Divine Orb rate: {divine_chaos_rate:.2f} Chaos")

    

    # Update database

    if all_prices:

        print("\n[DB] Updating database...")

        updated = update_database(all_prices, divine_chaos_rate)

        print(f"[OK] Updated {updated} currency prices in database")

    else:

        print("\n[WARN] No prices fetched, database not updated")

    

    # Show final stats

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM currency_prices WHERE league_id = ?", (LEAGUE_ID,))

    total = cursor.fetchone()[0]

    conn.close()

    

    print(f"\n[DB] Total currency prices in database: {total}")

    print("\n" + "=" * 60)

    print("Fetch Complete!")

    print("=" * 60)





if __name__ == "__main__":

    main()

