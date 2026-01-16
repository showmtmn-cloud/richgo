
#!/usr/bin/env python3

"""

Check if poe.ninja supports PoE2

"""

import requests

import time



def check_poeninja():

    print("="*60)

    print("Checking poe.ninja PoE2 Support")

    print("="*60)

    

    headers = {

        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",

        "Accept": "application/json",

    }

    

    # Test endpoints

    endpoints = [

        ("PoE2 Main", "https://poe2.ninja/api"),

        ("PoE2 Economy", "https://poe2.ninja/api/data/economysearch"),

        ("PoE2 Currency", "https://poe2.ninja/api/data/currencyoverview?league=Standard&type=Currency"),

        ("PoE1 ninja (for comparison)", "https://poe.ninja/api/data/currencyoverview?league=Settlers&type=Currency"),

    ]

    

    for name, url in endpoints:

        print(f"\n[{name}]")

        print(f"  URL: {url[:60]}...")

        

        try:

            response = requests.get(url, headers=headers, timeout=15)

            print(f"  Status: {response.status_code}")

            

            if response.status_code == 200:

                data = response.json()

                if isinstance(data, dict):

                    print(f"  Keys: {list(data.keys())[:5]}")

                    if 'lines' in data:

                        print(f"  Items: {len(data.get('lines', []))}")

                elif isinstance(data, list):

                    print(f"  Items: {len(data)}")

                print("  ✅ Working!")

            else:

                print(f"  ❌ Not available")

                

        except Exception as e:

            print(f"  ❌ Error: {str(e)[:50]}")

        

        time.sleep(2)  # Rate limit protection

    

    # Also check poe2.ninja website

    print("\n" + "="*60)

    print("Checking poe2.ninja website")

    print("="*60)

    

    try:

        response = requests.get("https://poe2.ninja", headers=headers, timeout=15)

        print(f"  Status: {response.status_code}")

        if response.status_code == 200:

            print("  ✅ Website accessible!")

            if 'economy' in response.text.lower():

                print("  ✅ Has economy data!")

    except Exception as e:

        print(f"  ❌ Error: {e}")



if __name__ == "__main__":

    check_poeninja()

