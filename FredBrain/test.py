import os
import time
import requests

# Assuming you have set these environment variables
FRED_KEY = os.environ.get("fred_api_key")
root_url = 'https://api.stlouisfed.org/fred'
series_id = 'UNRATE'

def check_rate_limit(url):
    response = requests.get(url)
    if response.status_code == 200:
        limit = response.headers.get('x-rate-limit-limit')
        remaining = response.headers.get('x-rate-limit-remaining')
        print(f"Rate Limit: {limit}, Remaining: {remaining}")
        return int(limit), int(remaining)
    else:
        print("Failed to fetch data:", response.status_code)

url = f"{root_url}/series?series_id={series_id}&api_key={FRED_KEY}&file_type=json"

url = f"{root_url}/series?series_id={series_id}&api_key={FRED_KEY}&file_type=json"
Calls_Used = check_rate_limit(url) - 1
print(Calls_Used)
