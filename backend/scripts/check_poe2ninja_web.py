
#!/usr/bin/env python3

"""

Check poe2.ninja website structure and available data

"""

import requests

import re

import time



def check_website():

    print("="*60)

    print("Analyzing poe2.ninja Website Structure")

    print("="*60)

    

    headers = {

        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",

        "Accept": "text/html,application/xhtml+xml",

    }

    

    # Check main pages

    pages = [

        ("Main", "https://poe2.ninja"),

        ("Economy", "https://poe2.ninja/economy"),

        ("Currency", "https://poe2.ninja/economy/currency"),

        ("Items", "https://poe2.ninja/economy/item"),

        ("Builds", "https://poe2.ninja/builds"),

    ]

    

    for name, url in pages:

        print(f"\n[{name}]")

        print(f"  URL: {url}")

        

        try:

            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)

            print(f"  Status: {response.status_code}")

            print(f"  Final URL: {response.url}")

            

            if response.status_code == 200:

                # Look for data patterns

                text = response.text

                

                # Check for league names

                leagues = re.findall(r'(Fate of the Vaal|Standard|Hardcore)', text)

                if leagues:

                    print(f"  Leagues found: {list(set(leagues))}")

                

                # Check for API calls in JavaScript

                api_calls = re.findall(r'api/data/(\w+)', text)

                if api_calls:

                    print(f"  API endpoints: {list(set(api_calls))[:5]}")

                

                # Check for JSON data

                if '__NEXT_DATA__' in text:

                    print("  ✅ Has embedded JSON data!")

                

                # Check content length

                print(f"  Content length: {len(text)} bytes")

                

        except Exception as e:

            print(f"  ❌ Error: {str(e)[:50]}")

        

        time.sleep(2)

    

    # Try different API patterns

    print("\n" + "="*60)

    print("Testing Alternative API Patterns")

    print("="*60)

    

    api_tests = [

        "https://poe2.ninja/api/data/itemoverview?league=Fate%20of%20the%20Vaal&type=UniqueWeapon",

        "https://poe2.ninja/api/data/itemoverview?league=Standard&type=BaseType",

        "https://poe2.ninja/economy/fate-of-the-vaal/currency",

        "https://poe2.ninja/economy/standard/currency",

    ]

    

    for url in api_tests:

        print(f"\n  Testing: {url[:65]}...")

        try:

            response = requests.get(url, headers=headers, timeout=10)

            print(f"  Status: {response.status_code}")

            if response.status_code == 200:

                content_type = response.headers.get('content-type', '')

                print(f"  Content-Type: {content_type}")

                if 'json' in content_type:

                    data = response.json()

                    print(f"  ✅ JSON Data! Keys: {list(data.keys())[:3]}")

        except Exception as e:

            print(f"  Error: {str(e)[:40]}")

        

        time.sleep(2)



if __name__ == "__main__":

    check_website()

