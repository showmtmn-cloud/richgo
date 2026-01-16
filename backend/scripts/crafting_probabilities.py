
#!/usr/bin/env python3

"""

PoE2 Crafting Probability Calculator

Based on community-researched weight data from craftofexile.com

NO external API calls - all local calculations

"""

import os

import sqlite3

import json

from datetime import datetime



DB_PATH = os.path.expanduser("~/poe2-profit-optimizer/backend/poe2_profit_optimizer.db")



# =============================================================================

# MODIFIER WEIGHT DATA (Community Researched)

# Source: craftofexile.com, poe2db.tw, community testing

# Format: {mod_name: {tier: (min_ilvl, weight, min_val, max_val)}}

# =============================================================================



# Amulet Prefix Modifiers

AMULET_PREFIX_MODS = {

    "+1 to Level of all Projectile Skill Gems": {

        1: (45, 100, 1, 1),  # (ilvl, weight, min, max)

    },

    "+1 to Level of all Minion Skill Gems": {

        1: (45, 100, 1, 1),

    },

    "+1 to Level of all Melee Skill Gems": {

        1: (45, 100, 1, 1),

    },

    "+1 to Level of all Spell Skill Gems": {

        1: (45, 100, 1, 1),

    },

    "+1 to Level of all Skill Gems": {

        1: (75, 25, 1, 1),  # Very rare

    },

    "Maximum Life": {

        1: (82, 1000, 90, 99),

        2: (74, 1000, 80, 89),

        3: (64, 1000, 70, 79),

        4: (54, 1000, 60, 69),

        5: (44, 1000, 50, 59),

    },

    "Maximum Energy Shield": {

        1: (82, 800, 55, 60),

        2: (74, 800, 48, 54),

        3: (64, 800, 41, 47),

    },

}



# Amulet Suffix Modifiers

AMULET_SUFFIX_MODS = {

    "Fire Resistance": {

        1: (78, 1000, 41, 45),

        2: (66, 1000, 36, 40),

        3: (50, 1000, 30, 35),

    },

    "Cold Resistance": {

        1: (78, 1000, 41, 45),

        2: (66, 1000, 36, 40),

        3: (50, 1000, 30, 35),

    },

    "Lightning Resistance": {

        1: (78, 1000, 41, 45),

        2: (66, 1000, 36, 40),

        3: (50, 1000, 30, 35),

    },

    "All Attributes": {

        1: (82, 500, 43, 50),

        2: (74, 500, 38, 42),

    },

    "Critical Strike Chance": {

        1: (82, 600, 30, 35),

        2: (74, 600, 25, 29),

    },

}



# Ring Prefix Modifiers (Breach Ring)

RING_PREFIX_MODS = {

    "Adds Lightning Damage to Attacks": {

        1: (82, 800, 11, 45),   # T1

        2: (74, 800, 9, 38),    # T2

        3: (64, 1000, 7, 30),   # T3

    },

    "Adds Fire Damage to Attacks": {

        1: (82, 800, 14, 38),

        2: (74, 800, 11, 32),

        3: (64, 1000, 8, 25),

    },

    "Adds Cold Damage to Attacks": {

        1: (82, 800, 12, 36),

        2: (74, 800, 10, 30),

        3: (64, 1000, 7, 24),

    },

    "Adds Physical Damage to Attacks": {

        1: (82, 800, 9, 16),

        2: (74, 800, 7, 13),

        3: (64, 1000, 5, 10),

    },

    "Maximum Life": {

        1: (82, 1000, 70, 79),

        2: (74, 1000, 60, 69),

        3: (64, 1000, 50, 59),

    },

}



# Ring Suffix Modifiers

RING_SUFFIX_MODS = {

    "Fire Resistance": {

        1: (78, 1000, 41, 45),

        2: (66, 1000, 36, 40),

        3: (50, 1000, 30, 35),

    },

    "Cold Resistance": {

        1: (78, 1000, 41, 45),

        2: (66, 1000, 36, 40),

        3: (50, 1000, 30, 35),

    },

    "Lightning Resistance": {

        1: (78, 1000, 41, 45),

        2: (66, 1000, 36, 40),

        3: (50, 1000, 30, 35),

    },

    "Attack Speed": {

        1: (82, 500, 9, 10),

        2: (74, 500, 7, 8),

    },

}





class ProbabilityCalculator:

    def __init__(self, ilvl=82):

        self.ilvl = ilvl

        

    def get_available_mods(self, mod_pool, ilvl):

        """Filter mods available at given ilvl"""

        available = {}

        for mod_name, tiers in mod_pool.items():

            for tier, (min_ilvl, weight, min_val, max_val) in tiers.items():

                if ilvl >= min_ilvl:

                    if mod_name not in available:

                        available[mod_name] = {}

                    available[mod_name][tier] = (weight, min_val, max_val)

        return available

    

    def calculate_total_weight(self, mod_pool, ilvl):

        """Calculate total weight of all available mods"""

        total = 0

        available = self.get_available_mods(mod_pool, ilvl)

        for mod_name, tiers in available.items():

            for tier, (weight, _, _) in tiers.items():

                total += weight

        return total

    

    def calculate_mod_probability(self, target_mod, mod_pool, ilvl):

        """Calculate probability to hit specific mod"""

        available = self.get_available_mods(mod_pool, ilvl)

        total_weight = self.calculate_total_weight(mod_pool, ilvl)

        

        if target_mod not in available:

            return 0.0

            

        mod_weight = sum(weight for tier, (weight, _, _) in available[target_mod].items())

        return mod_weight / total_weight if total_weight > 0 else 0.0

    

    def calculate_plus3_amulet_probability(self, skill_type="Projectile"):

        """

        Calculate probability to hit +3 skill amulet

        Method: Chaos spam on ilvl 82+ amulet

        Target: Two different +1 skill prefixes

        """

        print("\n" + "=" * 60)

        print(f"+3 {skill_type} Skill Amulet Probability Analysis")

        print("=" * 60)

        

        # Get available prefixes

        prefix_pool = self.get_available_mods(AMULET_PREFIX_MODS, self.ilvl)

        total_prefix_weight = self.calculate_total_weight(AMULET_PREFIX_MODS, self.ilvl)

        

        print(f"\nItem Level: {self.ilvl}")

        print(f"Total Prefix Weight: {total_prefix_weight}")

        

        # Target mods for +3

        primary_mod = f"+1 to Level of all {skill_type} Skill Gems"

        secondary_mod = "+1 to Level of all Skill Gems"

        

        # Get weights

        primary_weight = sum(w for t, (w, _, _) in prefix_pool.get(primary_mod, {}).items())

        secondary_weight = sum(w for t, (w, _, _) in prefix_pool.get(secondary_mod, {}).items())

        

        print(f"\n{primary_mod}: weight {primary_weight}")

        print(f"{secondary_mod}: weight {secondary_weight}")

        

        # Probability calculations

        # For +3, we need BOTH mods

        # P(A and B) with 3 prefix slots

        

        p_primary = primary_weight / total_prefix_weight

        p_secondary = secondary_weight / total_prefix_weight

        

        # With 3 prefix slots, probability to get both specific mods

        # Using inclusion-exclusion for at least one of each

        # Simplified: P(hit primary) * P(hit secondary | remaining slots)

        

        # Chaos orb gives 4 mods total (1-3 prefix, 1-3 suffix)

        # Average ~2 prefixes per chaos

        

        # Probability per prefix slot

        print(f"\nPer-slot probability:")

        print(f"  {skill_type} +1: {p_primary*100:.4f}%")

        print(f"  All Skills +1: {p_secondary*100:.4f}%")

        

        # Combined probability for +3 (both mods in same item)

        # Assuming 2 prefix slots average

        # P(A in slot1) * P(B in slot2) + P(B in slot1) * P(A in slot2)

        p_both_2slots = 2 * p_primary * p_secondary

        

        # With 3 prefix slots

        p_both_3slots = 3 * 2 * p_primary * p_secondary  # Simplified approximation

        

        print(f"\nCombined +3 probability:")

        print(f"  With 2 prefixes: {p_both_2slots*100:.6f}%")

        print(f"  With 3 prefixes: {p_both_3slots*100:.6f}%")

        

        # Average attempts needed

        avg_attempts_2p = 1 / p_both_2slots if p_both_2slots > 0 else float('inf')

        avg_attempts_3p = 1 / p_both_3slots if p_both_3slots > 0 else float('inf')

        

        print(f"\nAverage Chaos Orbs needed:")

        print(f"  With 2 prefixes: {avg_attempts_2p:.0f}")

        print(f"  With 3 prefixes: {avg_attempts_3p:.0f}")

        

        # Using average of 2.5 prefixes

        p_avg = (p_both_2slots + p_both_3slots) / 2

        avg_attempts = 1 / p_avg if p_avg > 0 else float('inf')

        

        print(f"\n*** REALISTIC ESTIMATE ***")

        print(f"  Average attempts: {avg_attempts:.0f} Chaos Orbs")

        print(f"  Success rate per attempt: {p_avg*100:.6f}%")

        

        return {

            "skill_type": skill_type,

            "ilvl": self.ilvl,

            "success_rate": p_avg,

            "avg_attempts": avg_attempts,

            "primary_weight": primary_weight,

            "secondary_weight": secondary_weight,

            "total_weight": total_prefix_weight,

        }

    

    def calculate_breach_ring_probability(self, target_damage_type="Lightning"):

        """

        Calculate probability for high-value Breach Ring

        Target: Triple T1 flat damage (Lightning + Fire + Cold)

        """

        print("\n" + "=" * 60)

        print("Breach Ring Triple Flat Damage Probability Analysis")

        print("=" * 60)

        

        prefix_pool = self.get_available_mods(RING_PREFIX_MODS, self.ilvl)

        total_prefix_weight = self.calculate_total_weight(RING_PREFIX_MODS, self.ilvl)

        

        print(f"\nItem Level: {self.ilvl}")

        print(f"Total Prefix Weight: {total_prefix_weight}")

        

        # Target: T1 of each damage type

        targets = [

            "Adds Lightning Damage to Attacks",

            "Adds Fire Damage to Attacks", 

            "Adds Cold Damage to Attacks",

        ]

        

        weights = {}

        for target in targets:

            # Get T1 weight only

            t1_weight = prefix_pool.get(target, {}).get(1, (0, 0, 0))[0]

            weights[target] = t1_weight

            print(f"  {target} (T1): weight {t1_weight}")

        

        # Probability per slot

        probs = {k: v/total_prefix_weight for k, v in weights.items()}

        

        print(f"\nPer-slot T1 probability:")

        for name, prob in probs.items():

            print(f"  {name}: {prob*100:.4f}%")

        

        # Triple T1 probability (need all 3 in 3 prefix slots)

        # P(A) * P(B|A) * P(C|A,B) = P(A) * P(B) * P(C) * 3!

        # Since each slot is independent

        p_triple = 1.0

        for prob in probs.values():

            p_triple *= prob

        p_triple *= 6  # 3! arrangements

        

        print(f"\n*** TRIPLE T1 PROBABILITY ***")

        print(f"  Chance: {p_triple*100:.8f}%")

        print(f"  Average attempts: {1/p_triple:.0f}")

        

        # More realistic: at least T2

        t2_weights = {}

        for target in targets:

            t1 = prefix_pool.get(target, {}).get(1, (0, 0, 0))[0]

            t2 = prefix_pool.get(target, {}).get(2, (0, 0, 0))[0]

            t2_weights[target] = t1 + t2

            

        probs_t2 = {k: v/total_prefix_weight for k, v in t2_weights.items()}

        

        p_triple_t2 = 1.0

        for prob in probs_t2.values():

            p_triple_t2 *= prob

        p_triple_t2 *= 6

        

        print(f"\n*** TRIPLE T2+ PROBABILITY ***")

        print(f"  Chance: {p_triple_t2*100:.6f}%")

        print(f"  Average attempts: {1/p_triple_t2:.0f}")

        

        return {

            "target": "Triple Flat Damage",

            "ilvl": self.ilvl,

            "t1_success_rate": p_triple,

            "t1_avg_attempts": 1/p_triple if p_triple > 0 else float('inf'),

            "t2_success_rate": p_triple_t2,

            "t2_avg_attempts": 1/p_triple_t2 if p_triple_t2 > 0 else float('inf'),

        }





def save_to_database(results):

    """Save probability data to database"""

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    

    # Check if crafting_probabilities table exists

    cursor.execute("""

        SELECT name FROM sqlite_master 

        WHERE type='table' AND name='crafting_probabilities'

    """)

    

    if not cursor.fetchone():

        print("\n[WARN] crafting_probabilities table not found")

        print("       Skipping database save")

        conn.close()

        return

    

    # Save results

    for r in results:

        cursor.execute("""

            INSERT INTO crafting_probabilities 

            (item_base_id, mod_name, mod_tier, probability, method)

            VALUES (?, ?, ?, ?, ?)

        """, (

            1,  # placeholder item_base_id

            json.dumps(r),

            1,

            r.get("success_rate", 0) or r.get("t2_success_rate", 0),

            "calculated"

        ))

    

    conn.commit()

    conn.close()

    print(f"\n[OK] Saved {len(results)} probability records to database")





def main():

    print("=" * 60)

    print("PoE2 Crafting Probability Calculator")

    print("Based on Community Weight Data")

    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("=" * 60)

    

    calc = ProbabilityCalculator(ilvl=82)

    results = []

    

    # Analyze +3 amulets for different skill types

    for skill in ["Projectile", "Minion", "Melee", "Spell"]:

        result = calc.calculate_plus3_amulet_probability(skill)

        results.append(result)

    

    # Analyze Breach Ring

    result = calc.calculate_breach_ring_probability()

    results.append(result)

    

    # Summary

    print("\n" + "=" * 60)

    print("SUMMARY: REALISTIC CRAFTING EXPECTATIONS")

    print("=" * 60)

    

    print("\n+3 Skill Amulets (Chaos Spam Method):")

    for r in results:

        if "skill_type" in r:

            print(f"  +3 {r['skill_type']}: ~{r['avg_attempts']:.0f} Chaos avg")

    

    print("\nBreach Ring Triple Flat Damage:")

    for r in results:

        if "target" in r:

            print(f"  T1 Triple: ~{r['t1_avg_attempts']:.0f} attempts")

            print(f"  T2+ Triple: ~{r['t2_avg_attempts']:.0f} attempts")

    

    # Save to DB

    save_to_database(results)

    

    print("\n" + "=" * 60)

    print("Analysis Complete!")

    print("=" * 60)





if __name__ == "__main__":

    main()

