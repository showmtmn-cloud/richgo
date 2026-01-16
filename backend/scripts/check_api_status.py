
#!/usr/bin/env python3

"""Simple API status check"""

import requests



def check():

    headers = {

        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",

        "Accept": "application/json",

    }

    

    try:

        # Simple leagues endpoint (least restrictive)

        response = requests.get(

            "https://www.pathofexile.com/api/trade2/data/leagues",

            headers=headers,

            timeout=15

        )

        

        print(f"Status Code: {response.status_code}")

        

        if response.status_code == 200:

            print("✅ API OK - Not rate limited")

            data = response.json()

            print(f"   Leagues found: {len(data.get('result', []))}")

        elif response.status_code == 429:

            print("❌ RATE LIMITED (429)")

            print("   Wait 1-2 hours before trying again")

        else:

            print(f"⚠️ Other error: HTTP {response.status_code}")

            

    except Exception as e:

        print(f"❌ Connection error: {e}")



if __name__ == "__main__":

    check()

