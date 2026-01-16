
#!/usr/bin/env python3

"""

Check poe.ninja/poe2 endpoints

"""

import requests

import time

import json



def check():

    print("="*60)

    print("Checking poe.ninja/poe2 Endpoints")

    print("="*60)

    

    headers = {

        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",

        "Accept": "application/json",

    }

    

    # Current PoE2 league

    league = "Fate of the Vaal"

    league_url = "Fate%20of%20the%20Vaal"

    

    # API endpoints to test

    endpoints = [

        # Currency

        f"https://poe.ninja/api/data/poe2/GetCurrencyOverview?league={league_url}&type=Currency",

        f"https://poe.ninja/api/data/poe2/currencyoverview?league={league_url}&type=Currency",

        

        # Items

        f"https://poe.ninja/api/data/poe2/GetItemOverview?league={league_url}&type=UniqueWeapon",

        f"https://poe.ninja/api/data/poe2/itemoverview?league={league_url}&type=UniqueWeapon",

        f"https://poe.ninja/api/data/poe2/itemoverview?league={league_url}&type=BaseType",

        

        # General

        "https://poe.ninja/api/data/poe2/getindexstate",

        "https://poe.ninja/api/data/getindexstate?variant=poe2",

    ]

    

    for url in endpoints:

        short_url = url.replace("https://poe.ninja/api/data/", "").replace(league_url, "LEAGUE")

        print(f"\n[{short_url[:55]}]")

        

        try:

            response = requests.get(url, headers=headers, timeout=15)

            print(f"  Status: {response.status_code}")

            

            if response.status_code == 200:

                try:

                    data = response.json()

                    if isinstance(data, dict):

                        print(f"  Keys: {list(data.keys())}")

                        if 'lines' in data:

                            print(f"  ✅ Items: {len(data['lines'])}")

                            if data['lines']:

                                sample = data['lines'][0]

                                print(f"  Sample keys: {list(sample.keys())[:5]}")

                        if 'currencyDetails' in data:

                            print(f"  ✅ Currency details: {len(data['currencyDetails'])}")

                    print("  ✅ Working!")

                except:

                    print(f"  Response: {response.text[:100]}")

            

        except Exception as e:

            print(f"  ❌ Error: {str(e)[:50]}")

        

        time.sleep(3)  # Safe rate limit



if __name__ == "__main__":

    check()

