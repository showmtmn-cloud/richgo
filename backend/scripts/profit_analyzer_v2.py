
#!/usr/bin/env python3

"""

PoE2 Profit Analyzer V2 - With Realistic Probabilities

"""

import os

import sqlite3

from datetime import datetime



DB_PATH = os.path.expanduser("~/poe2-profit-optimizer/backend/poe2_profit_optimizer.db")

LEAGUE_ID = 1



# Realistic probability data (from crafting_probabilities.py)

CRAFT_DATA = {

    "+3 Projectile Amulet": {

        "avg_chaos_needed": 6123,

        "success_rate": 0.00016332,

        "sale_price_divine": 120,

    },

    "+3 Minion Amulet": {

        "avg_chaos_needed": 6123,

        "success_rate": 0.00016332,

        "sale_price_divine": 80,

    },

    "+3 Melee Amulet": {

        "avg_chaos_needed": 6123,

        "success_rate": 0.00016332,

        "sale_price_divine": 60,

    },

    "Breach Ring T2+ Triple": {

        "avg_attempts": 98,

        "success_rate": 0.01021402,

        "sale_price_divine": 25,

    },

    "Breach Ring T1 Triple": {

        "avg_attempts": 783,

        "success_rate": 0.00127675,

        "sale_price_divine": 55,

    },

}





def load_prices():

    """Load current prices from DB"""

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    

    # Exchange rate

    cursor.execute("""

        SELECT divine_to_chaos FROM currency_exchange_rates 

        WHERE league_id = ? ORDER BY last_updated DESC LIMIT 1

    """, (LEAGUE_ID,))

    row = cursor.fetchone()

    divine_to_chaos = row[0] if row else 200

    

    # Currency prices

    prices = {}

    cursor.execute("""

        SELECT c.name, cp.price_divine

        FROM currency_prices cp

        JOIN currencies c ON cp.currency_id = c.id

        WHERE cp.league_id = ?

    """, (LEAGUE_ID,))

    for row in cursor.fetchall():

        prices[row[0]] = row[1]

    

    # Base prices

    cursor.execute("""

        SELECT ib.name, bp.price_divine

        FROM base_prices bp

        JOIN item_bases ib ON bp.item_base_id = ib.id

        WHERE bp.league_id = ?

    """, (LEAGUE_ID,))

    for row in cursor.fetchall():

        prices[row[0]] = row[1]

    

    conn.close()

    return divine_to_chaos, prices





def analyze_amulet(name, data, divine_to_chaos, prices):

    """Analyze +3 amulet crafting with realistic probabilities"""

    print(f"\n{'='*60}")

    print(f"{name} - REALISTIC Analysis")

    print("="*60)

    

    # Costs

    base_cost = prices.get("Tenebrous Ring", 0.2)

    chaos_price = prices.get("Chaos Orb", 0.005)

    omen_cost = prices.get("Omen of Sinistral Exaltation", 3.0)

    catalyst_cost = 0.375

    

    # Chaos needed (realistic)

    avg_chaos = data["avg_chaos_needed"]

    chaos_cost_divine = avg_chaos * chaos_price

    

    # Total cost

    total_cost = base_cost + chaos_cost_divine + omen_cost + catalyst_cost

    

    # Expected sale

    sale_price = data["sale_price_divine"]

    

    # Profit

    profit = sale_price - total_cost

    roi = (profit / total_cost) * 100 if total_cost > 0 else 0

    

    print(f"\nCost Breakdown:")

    print(f"  Base (Tenebrous): {base_cost:.2f} Divine")

    print(f"  Chaos Orb x{avg_chaos}: {chaos_cost_divine:.2f} Divine")

    print(f"  Omen: {omen_cost:.2f} Divine")

    print(f"  Catalyst: {catalyst_cost:.2f} Divine")

    print(f"  ----------------------")

    print(f"  Total Investment: {total_cost:.2f} Divine")

    

    print(f"\nExpected Sale: {sale_price} Divine")

    print(f"\nResults:")

    print(f"  Net Profit: {profit:.2f} Divine")

    print(f"  ROI: {roi:.1f}%")

    

    if roi > 50:

        status = "PROFITABLE"

    elif roi > 0:

        status = "MARGINAL"

    else:

        status = "NOT PROFITABLE"

    print(f"  Status: {status}")

    

    return {

        "recipe": name,

        "investment": total_cost,

        "expected_value": sale_price,

        "profit": profit,

        "roi": roi,

        "status": status,

    }





def analyze_breach_ring(name, data, prices):

    """Analyze Breach Ring crafting"""

    print(f"\n{'='*60}")

    print(f"{name} - REALISTIC Analysis")

    print("="*60)

    

    # Costs per attempt

    base_cost = prices.get("Breach Ring", 0.3)

    essence_cost = prices.get("Essence of Rage", 0.6)

    omen_cost = prices.get("Omen of Sinistral Exaltation", 3.0)

    exalt_cost = prices.get("Exalted Orb", 0.0125) * 2

    catalyst_cost = 0.25

    

    cost_per_attempt = base_cost + essence_cost + omen_cost + exalt_cost + catalyst_cost

    

    # Average attempts needed

    avg_attempts = data["avg_attempts"]

    total_cost = cost_per_attempt * avg_attempts

    

    # Expected sale

    sale_price = data["sale_price_divine"]

    

    # Profit

    profit = sale_price - total_cost

    roi = (profit / total_cost) * 100 if total_cost > 0 else 0

    

    print(f"\nCost Per Attempt:")

    print(f"  Base + Essence + Omen + Exalt + Catalyst")

    print(f"  = {cost_per_attempt:.2f} Divine")

    

    print(f"\nAverage Attempts: {avg_attempts}")

    print(f"Total Investment: {total_cost:.2f} Divine")

    print(f"\nExpected Sale: {sale_price} Divine")

    

    print(f"\nResults:")

    print(f"  Net Profit: {profit:.2f} Divine")

    print(f"  ROI: {roi:.1f}%")

    

    if roi > 50:

        status = "PROFITABLE"

    elif roi > 0:

        status = "MARGINAL"

    else:

        status = "NOT PROFITABLE"

    print(f"  Status: {status}")

    

    return {

        "recipe": name,

        "investment": total_cost,

        "expected_value": sale_price,

        "profit": profit,

        "roi": roi,

        "status": status,

    }





def main():

    print("="*60)

    print("PoE2 Profit Analyzer V2 - REALISTIC PROBABILITIES")

    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("="*60)

    

    divine_to_chaos, prices = load_prices()

    

    print(f"\nLoaded: 1 Divine = {divine_to_chaos} Chaos")

    print(f"Prices loaded: {len(prices)} items")

    

    results = []

    

    # Analyze amulets

    for name in ["+3 Projectile Amulet", "+3 Minion Amulet", "+3 Melee Amulet"]:

        result = analyze_amulet(name, CRAFT_DATA[name], divine_to_chaos, prices)

        results.append(result)

    

    # Analyze breach rings

    for name in ["Breach Ring T2+ Triple", "Breach Ring T1 Triple"]:

        result = analyze_breach_ring(name, CRAFT_DATA[name], prices)

        results.append(result)

    

    # Summary

    print("\n" + "="*60)

    print("FINAL RANKING (by ROI)")

    print("="*60)

    

    sorted_results = sorted(results, key=lambda x: x["roi"], reverse=True)

    

    for i, r in enumerate(sorted_results, 1):

        print(f"\n#{i} {r['recipe']}")

        print(f"   Investment: {r['investment']:.2f} Divine")

        print(f"   Expected Sale: {r['expected_value']:.2f} Divine")

        print(f"   Profit: {r['profit']:.2f} Divine")

        print(f"   ROI: {r['roi']:.1f}%")

        print(f"   Status: {r['status']}")

    

    print("\n" + "="*60)

    print("Analysis Complete!")

    print("="*60)





if __name__ == "__main__":

    main()

