
#!/usr/bin/env python3

"""

PoE2 Profit Analyzer - Uses existing DB schema

"""

import os

import sqlite3

import json

from datetime import datetime



DB_PATH = os.path.expanduser("~/poe2-profit-optimizer/backend/poe2_profit_optimizer.db")

LEAGUE_ID = 1





class ProfitAnalyzer:

    def __init__(self):

        self.conn = sqlite3.connect(DB_PATH)

        self.conn.row_factory = sqlite3.Row

        self.load_prices()

        

    def close(self):

        self.conn.close()

        

    def load_prices(self):

        cursor = self.conn.cursor()

        

        # Load exchange rate

        cursor.execute("""

            SELECT divine_to_exalt, divine_to_chaos 

            FROM currency_exchange_rates 

            WHERE league_id = ? 

            ORDER BY last_updated DESC LIMIT 1

        """, (LEAGUE_ID,))

        row = cursor.fetchone()

        self.divine_to_exalt = row[0] if row else 80

        self.divine_to_chaos = row[1] if row else 200

        

        # Load currency prices

        self.currency_prices = {}

        cursor.execute("""

            SELECT c.name, cp.price_divine

            FROM currency_prices cp

            JOIN currencies c ON cp.currency_id = c.id

            WHERE cp.league_id = ?

        """, (LEAGUE_ID,))

        for row in cursor.fetchall():

            self.currency_prices[row[0]] = row[1]

            

        # Load base prices

        self.base_prices = {}

        cursor.execute("""

            SELECT ib.name, bp.price_divine

            FROM base_prices bp

            JOIN item_bases ib ON bp.item_base_id = ib.id

            WHERE bp.league_id = ?

        """, (LEAGUE_ID,))

        for row in cursor.fetchall():

            self.base_prices[row[0]] = row[1]

            

    def get_currency_price(self, name):

        return self.currency_prices.get(name, 0)

        

    def get_base_price(self, name):

        return self.base_prices.get(name, 0)

        

    def analyze_breach_ring(self):

        """Breach Ring crafting analysis"""

        print("\n" + "=" * 50)

        print("Breach Ring Crafting Analysis")

        print("=" * 50)

        

        base_cost = self.get_base_price("Breach Ring")

        if base_cost == 0:

            base_cost = 0.3

            

        # Materials cost

        essence_cost = self.get_currency_price("Essence of Rage")

        if essence_cost == 0:

            essence_cost = 0.6

            

        omen_cost = self.get_currency_price("Omen of Sinistral Exaltation")

        if omen_cost == 0:

            omen_cost = 3.0

            

        exalt_cost = self.get_currency_price("Exalted Orb") * 2

        catalyst_cost = 0.25  # Lightning Catalyst x50

        

        # Total investment

        total_cost = base_cost + essence_cost + omen_cost + exalt_cost + catalyst_cost

        

        # Expected outcomes

        prob_t9_triple = 0.02

        prob_t9_double = 0.08

        prob_t8_single = 0.20

        prob_sellable = 0.40

        prob_vendor = 0.30

        

        # Expected prices

        price_t9_triple = 55

        price_t9_double = 25

        price_t8_single = 8

        price_sellable = 2

        price_vendor = 0.1

        

        expected_value = (

            prob_t9_triple * price_t9_triple +

            prob_t9_double * price_t9_double +

            prob_t8_single * price_t8_single +

            prob_sellable * price_sellable +

            prob_vendor * price_vendor

        )

        

        profit = expected_value - total_cost

        roi = (profit / total_cost) * 100 if total_cost > 0 else 0

        

        print("\nCost Breakdown:")

        print("  Base (Breach Ring): {:.2f} Divine".format(base_cost))

        print("  Greater Essence: {:.2f} Divine".format(essence_cost))

        print("  Omen: {:.2f} Divine".format(omen_cost))

        print("  Exalted Orb x2: {:.4f} Divine".format(exalt_cost))

        print("  Catalyst: {:.2f} Divine".format(catalyst_cost))

        print("  ----------------------")

        print("  Total Investment: {:.2f} Divine".format(total_cost))

        

        print("\nExpected Outcomes:")

        print("  T9 Triple (2%): {} Divine".format(price_t9_triple))

        print("  T9 Double (8%): {} Divine".format(price_t9_double))

        print("  T8 Single (20%): {} Divine".format(price_t8_single))

        print("  Sellable (40%): {} Divine".format(price_sellable))

        print("  Vendor (30%): {} Divine".format(price_vendor))

        

        print("\nResults:")

        print("  Expected Value: {:.2f} Divine".format(expected_value))

        print("  Expected Profit: {:.2f} Divine".format(profit))

        print("  ROI: {:.1f}%".format(roi))

        

        if roi > 50:

            print("  Status: PROFITABLE")

        elif roi > 0:

            print("  Status: MARGINAL")

        else:

            print("  Status: NOT PROFITABLE")

            

        return {

            "recipe": "Breach Ring Triple Flat",

            "investment": total_cost,

            "expected_value": expected_value,

            "profit": profit,

            "roi": roi,

        }

        

    def analyze_plus3_amulet(self, skill_type="Projectile"):

        """Plus 3 Skill Amulet analysis"""

        print("\n" + "=" * 50)

        print("+3 {} Skill Amulet Analysis".format(skill_type))

        print("=" * 50)

        

        base_cost = self.get_base_price("Tenebrous Ring")

        if base_cost == 0:

            base_cost = 1.5

            

        # Chaos spam method

        chaos_cost = self.get_currency_price("Chaos Orb") * 500

        omen_cost = self.get_currency_price("Omen of Sinistral Exaltation")

        if omen_cost == 0:

            omen_cost = 3.0

        catalyst_cost = 0.375

        

        total_cost = base_cost + chaos_cost + omen_cost + catalyst_cost

        

        # Expected sale prices by type

        sale_prices = {

            "Projectile": 120,

            "Minion": 80,

            "Melee": 60,

            "Spell": 70,

        }

        expected_price = sale_prices.get(skill_type, 70)

        

        profit = expected_price - total_cost

        roi = (profit / total_cost) * 100 if total_cost > 0 else 0

        

        print("\nCost Breakdown:")

        print("  Base (Tenebrous Amulet): {:.2f} Divine".format(base_cost))

        print("  Chaos Orb x500: {:.2f} Divine".format(chaos_cost))

        print("  Omen: {:.2f} Divine".format(omen_cost))

        print("  Catalyst: {:.2f} Divine".format(catalyst_cost))

        print("  ----------------------")

        print("  Total Investment: {:.2f} Divine".format(total_cost))

        

        print("\nExpected Sale: {} Divine".format(expected_price))

        

        print("\nResults:")

        print("  Expected Profit: {:.2f} Divine".format(profit))

        print("  ROI: {:.1f}%".format(roi))

        

        return {

            "recipe": "+3 {} Amulet".format(skill_type),

            "investment": total_cost,

            "expected_value": expected_price,

            "profit": profit,

            "roi": roi,

        }

        

    def save_opportunities(self, results):

        """Save to profit_opportunities table"""

        cursor = self.conn.cursor()

        

        for r in results:

            cursor.execute("""

                INSERT INTO profit_opportunities 

                (league_id, base_cost_divine, crafting_cost_divine, expected_sale_price_divine,

                 net_profit_divine, roi_percentage, risk_level, crafting_path, calculated_at)

                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

            """, (

                LEAGUE_ID,

                r["investment"] * 0.3,  # base portion

                r["investment"] * 0.7,  # crafting portion

                r["expected_value"],

                r["profit"],

                r["roi"],

                "Medium" if r["roi"] > 50 else "High",

                json.dumps({"recipe": r["recipe"]}),

                datetime.now()

            ))

        

        self.conn.commit()

        print("\n[OK] Saved {} opportunities to database".format(len(results)))





def main():

    print("=" * 50)

    print("PoE2 Profit Analyzer")

    print("Time: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    print("=" * 50)

    

    analyzer = ProfitAnalyzer()

    

    print("\nLoaded Prices:")

    print("  Exchange: 1 Divine = {} Exalt".format(analyzer.divine_to_exalt))

    print("  Currencies: {}".format(len(analyzer.currency_prices)))

    print("  Base items: {}".format(len(analyzer.base_prices)))

    

    results = []

    

    # Analyze recipes

    results.append(analyzer.analyze_breach_ring())

    

    for skill in ["Projectile", "Minion", "Melee"]:

        results.append(analyzer.analyze_plus3_amulet(skill))

    

    # Summary

    print("\n" + "=" * 50)

    print("TOP OPPORTUNITIES (by ROI)")

    print("=" * 50)

    

    sorted_results = sorted(results, key=lambda x: x["roi"], reverse=True)

    for i, r in enumerate(sorted_results, 1):

        print("\n#{} {}".format(i, r["recipe"]))

        print("   Investment: {:.2f} Divine".format(r["investment"]))

        print("   Expected: {:.2f} Divine".format(r["expected_value"]))

        print("   Profit: {:.2f} Divine".format(r["profit"]))

        print("   ROI: {:.1f}%".format(r["roi"]))

    

    # Save to DB

    analyzer.save_opportunities(sorted_results)

    analyzer.close()

    

    print("\n" + "=" * 50)

    print("Analysis Complete!")

    print("=" * 50)





if __name__ == "__main__":

    main()

