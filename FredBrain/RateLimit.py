from functools import wraps
import time
import requests
import os

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


class RateLimitDecorator:
    """
    A decorator to enforce rate limiting for any function, especially useful for API calls.

    Attributes:
    - calls (int): The number of calls allowed within the specified period.
    - period (int): The period (in seconds) for which the rate limit applies.
    """
    def __init__(self, calls, period=60):  # per-minute management
        self.calls = calls
        self.period = period
        self.timing = []
        self.total_calls = 0
        self.reset_time = None

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.total_calls += 1
            now = time.time()
            # If we have hit the limit and are within the reset period, sleep until the reset period is over
            if self.reset_time and now < self.reset_time:
                sleep_time = self.reset_time - now
                print(f"Rate limit exceeded. Sleeping for {sleep_time} seconds before putting workers back to work .")
                time.sleep(sleep_time)
                self.reset_time = None  # Reset the reset_time
            if len(self.timing) >= self.calls:
                self.reset_time = now + self.period
                self.timing.clear()  # Clear the timing list to start fresh after waiting
            else:
                print(f"Current call count: {len(self.timing)}, Total calls: {self.total_calls}\n")
                result = func(*args, **kwargs)
                self.timing.append(now)
                return result

        return wrapper
