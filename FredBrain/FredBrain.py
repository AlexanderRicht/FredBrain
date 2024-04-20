# Class for designing methods to extract first versions of released figures from the Fred API - Alexander Richt
import os
from datetime import date
import pandas as pd
import requests
import openai
import hashlib
from RateLimit import RateLimitDecorator
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures


def check_rate_limit(url):
    response = requests.get(url)
    if response.status_code == 200:
        limit = response.headers.get('x-rate-limit-limit')
        remaining = response.headers.get('x-rate-limit-remaining')
        print(f"Rate Limit: {limit}, Remaining: {remaining}")
    else:
        print("Failed to fetch data:", response.status_code)


class FredBrain:
    earliest_realtime_start = '1776-07-04'
    latest_realtime_end = date.today()
    nan_char = '.'
    calls_per_minute = 90
    root_url = 'https://api.stlouisfed.org/fred'

    def __init__(self, fred_api_key=None, openai_api_key=None):
        """
        Initialize an instance of the FredBrain class to interact with the FRED API.

        The constructor allows for an API key to be passed directly or retrieved from an environment variable.
        Providing an API key is necessary to authenticate requests to the FRED API.

        Parameters:
        - api_key (str, optional): A string that represents your FRED API key. If no API key is provided, the
          constructor will attempt to retrieve it from an environment variable named 'FRED_API_KEY'.

        Usage:
        - To use an API key directly: fred = FredBrain(api_key='your_api_key_here')
        - To use an API key from an environment variable: fred = FredBrain()

        Notes:
        - You can obtain an API key by registering on the FRED website.
        - To set an environment variable for your API key, you can use the export command in Unix/Linux/macOS
          or setx in Windows. For example, in Unix/Linux/macOS terminal: export FRED_API_KEY='your_api_key_here'
        """
        self.fred_api_key = fred_api_key or os.environ.get('FRED_API_KEY')
        self.openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        openai.api_key = self.openai_api_key

    @RateLimitDecorator(calls=calls_per_minute)
    def search_brain(self, search_text, filter_attributes=None, filter_values=None):
        """
        Searches for FRED series based on a given search text and applies optional filtering based on specified criteria.
        The function is capable of filtering search results according to various data attributes as present in the FRED series
        metadata. Filterable attributes include, but are not limited to, 'popularity', 'frequency', 'units', and 'seasonal_adjustment'.

        Parameters:
        - search_text (str): The text to use for searching the FRED series.
        - filter_attributes (list of str, optional): A list of attributes to filter on. Each attribute should correspond to a column in the FRED series data.
          Examples of filterable attributes include:
          'id', 'title', 'frequency', 'units', 'seasonal_adjustment', 'popularity', etc.
        - filter_values (list of various, optional): A list of values to use for filtering. Each value should correspond to an attribute in `filter_attributes`.
          This could be a string, integer, or other types based on the attribute. For example, it could be an integer
          threshold for 'popularity' such as 75 or a string such as 'Quarterly' for 'frequency'.

        Returns:
        - pandas.DataFrame: A DataFrame containing the search results, optionally filtered based on the provided criteria.
          The DataFrame columns correspond to the metadata attributes of the FRED series.

        Usage Examples:
        - To filter search results to only include series with 'popularity' greater than or equal to 75:
          search_output_popularity = fred.search_brain("GDP", "popularity", 75)

        - To filter search results where 'frequency' is 'Monthly':
          search_output_frequency = fred.search_brain("GDP", "frequency", "monthly")

        - To filter search results where 'popularity' is greater than or equal to 75 and 'frequency' is 'Monthly':
          search_attributes = ["popularity", "frequency"]
          search_values = [75, "Monthly"]
          search_output_multiple = fred.search_brain("GDP", search_attributes, search_values)
          print(search_output_multiple)

        Note:
        The function queries the FRED series using an API, and the search is performed on the server side.
        The filtering is then applied to the results returned from the API call.
        Ensure that the 'filter_attribute' matches the exact column name as found in the FRED series metadata for correct operation.
        """
        # https://api.stlouisfed.org/fred/series/search?search_text=monetary+service+index&api_key=abcdefghijklmnopqrstuvwxyz123456
        # Ensure filter_attributes and filter_values are lists for uniform processing
        formatted_search_text = '+'.join(search_text.split())
        url = f"{self.root_url}/series/search?search_text={formatted_search_text}&api_key={self.fred_api_key}&file_type=json"
        # Make the API call
        response = requests.get(url)
        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            try:
                # Parse JSON response
                data = response.json()
                # The information you want is under the 'seriess' key, which is a list of dictionaries
                series_data = data.get('seriess', [])  # Adjust based on actual JSON response structure
                df = pd.DataFrame(series_data)
                # Apply filters if both filter_attributes and filter_values are provided and not empty
                if filter_attributes and filter_values:
                    # Ensure filter_attributes and filter_values are lists for uniform processing
                    if not isinstance(filter_attributes, list):
                        filter_attributes = [filter_attributes]
                    if not isinstance(filter_values, list):
                        filter_values = [filter_values]
                    # Validate that filter lists are of equal length
                    if len(filter_attributes) != len(filter_values):
                        raise ValueError("Length of filter_attributes must match length of filter_values.")
                    # Apply each filter sequentially
                    for attribute, value in zip(filter_attributes, filter_values):
                        if isinstance(value, str):
                            df = df[df[attribute].str.contains(value, case=False, na=False)]
                        else:  # Assuming numeric filtering
                            df = df[df[attribute] >= value]
                # Return the dataframe with or without filters applied
                return df
            except ValueError as e:
                print("Response is not in JSON format.")
                print("Response content:", response.text)
                return None
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            print("Response content:", response.text)
            return None

    @RateLimitDecorator(calls=calls_per_minute)
    def get_categories_range(self, start_id, end_id=None):
        """
        Retrieves a range of categories from the FRED database, each potentially related to multiple series.
        This method is designed to store categories for later reference to efficiently retrieve all related series.

        This functionality is crucial for linking categories to their respective series lists, allowing for
        systematic data retrieval and management. Particularly useful for populating databases with FRED categories
        for subsequent series and observation extraction.

        Parameters:
        - start_id (int): The starting ID of the category range to retrieve, corresponding to the first category
                          in the desired range.
        - end_id (int, optional): The ending ID of the category range from which to retrieve series. If not specified,
                                  the method will only retrieve series for the start_id category.

        Returns:
        - pandas.DataFrame: Contains all categories within the specified range present in the FRED database.
                            Returns an empty DataFrame if no categories data is collected.

        Notes:
        - Iterates over the specified range of category IDs, making API requests to FRED for each category data.
        - Appends successful category data fetches to a list of DataFrame pieces.
        - Handles and prints error messages for nonexistent categories or other encountered request errors.
        - Concatenates all collected DataFrame pieces into a single DataFrame.
        - Advises on using iterative fetching in increments of 1000 to comply with FRED's rate limits, thus avoiding '429 Too Many Requests' errors.

        Usage:
            fred = FredBrain(api_key="your_fred_api_key")
            all_categories = fred.get_categories_range(0, 15)
            print(all_categories)
            all_categories.to_excel("FRED_categories.xlsx", index=False)
        """
        if end_id is None:
            end_id = start_id
        categories = []  # This will collect DataFrame pieces
        for category_id in range(start_id, end_id + 1):  # Ensure end_id is included
            url = f"{self.root_url}/category?category_id={category_id}&api_key={self.fred_api_key}&file_type=json"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                # Check if response contains 'categories' data
                if 'categories' in data and data['categories']:
                    df = pd.DataFrame(data['categories'])
                    categories.append(df)  # Append DataFrame to the list
                else:
                    print(f"No data for category_id={category_id}")
            else:
                # Check for error message in response and print it
                error_info = response.json()
                if 'error_message' in error_info:
                    print(f"Error for category_id={category_id}: {error_info['error_message']}")
                else:
                    print(f"Failed to fetch data for category_id={category_id}, status code: {response.status_code}")
        # Concatenate all DataFrame pieces into one DataFrame after collecting them
        if categories:  # Check if the list is not empty
            all_categories = pd.concat(categories, ignore_index=True)
            return all_categories
        else:
            print("No categories data collected.")
            return pd.DataFrame()

    def get_series_from_category(self, start_id, end_id=None):
        """
        Retrieves series data from the FRED database for a specified range of category IDs. This method leverages
        the get_categories_range method to first fetch details of the categories within the specified range and then
        retrieves the series associated with each category. It enhances the series data with the category ID and
        category title, facilitating easier identification and categorization of the series data.

        Parameters:
        - start_id (int): The starting ID of the category range from which to retrieve series.
        - end_id (int, optional): The ending ID of the category range from which to retrieve series. If not specified,
                                  the method will only retrieve series for the start_id category.

        Returns:
        - pandas.DataFrame: A DataFrame containing the series data for the specified category range. Each row represents
                            a series, enriched with the category ID and category title. Returns an empty DataFrame if no
                            series data is collected.

        Notes:
        - This method is particularly useful for bulk-fetching series data categorized under specific FRED categories,
          enabling a comprehensive analysis of related economic indicators.
        - It minimizes the number of API calls by first collecting category details for the specified range and then
          fetching the series data, reducing the likelihood of hitting rate limits.
        - Handles and prints error messages for categories or series that cannot be fetched due to errors or because they
          do not exist in the FRED database.

        Usage:
            fred = FredBrain(api_key="your_fred_api_key")
            all_series_data = fred.get_series_from_category(1, 100)
            print(all_series_data)
            all_series_data.to_excel("FRED_series_data.xlsx", index=False)

        The resulting DataFrame provides a holistic view of series across multiple categories, useful for data analysis,
        research, and database population tasks.
        """
        if end_id is None:
            end_id = start_id
        all_categories = self.get_categories_range(start_id, end_id)
        series_list = []
        for _, category_row in all_categories.iterrows():
            category_id = category_row['id']
            series_url = f"{self.root_url}/category/series?category_id={category_id}&api_key={self.fred_api_key}&file_type=json"
            response = requests.get(series_url)
            if response.status_code == 200:
                series_data = response.json()
                if 'seriess' in series_data and series_data['seriess']:
                    df_series = pd.DataFrame(series_data['seriess'])
                    df_series['category_id'] = category_row['id']
                    df_series['category_title'] = category_row['name']
                    series_list.append(df_series)
                else:
                    print(f"No series data for category_id={category_id}")
            else:
                print(f"Failed to fetch series for category_id={category_id}, status code: {response.status_code}")
        if series_list:
            return pd.concat(series_list, ignore_index=True)
        else:
            print("No series data collected.")
            return pd.DataFrame()

    @RateLimitDecorator(calls=calls_per_minute)
    def fetch_single_series_info(self, series_id, relevant_info):
        """
        Fetch that is leveraged by the fetch_series_info method to execute concurrent requests for
        series information by using the ThreadPoolExecutor for synchronous requests.
        """
        url = f"{self.root_url}/series?series_id={series_id}&api_key={self.fred_api_key}&file_type=json"
        try:
            response_api = requests.get(url)
            if response_api.status_code == 200:
                data = response_api.json()
                series_info = data['seriess'][0]  # Get the first item from the list
                filtered_info = {key: series_info[key] for key in relevant_info if key in series_info}
                filtered_info = pd.Series(filtered_info).astype(str)
                concatenated_string = str(filtered_info['id']) + str(filtered_info['frequency']) + str(filtered_info['units'])
                filtered_info['Unique Key'] = hashlib.sha256(concatenated_string.encode()).hexdigest()
                return filtered_info
            else:
                print(f"Failed to fetch {series_id}: Status {response_api.status_code}")
                return pd.Series({"error": f"HTTP Status {response_api.status_code}"})
        except Exception as e:
            print(f"Exception while fetching {series_id}: {str(e)}")
            return pd.Series({"error": str(e)})

    def fetch_series_info(self, series_ids, relevant_info):
        """
        Fetches and returns detailed information for a list of FRED series IDs, filtering the results based on a list of relevant information fields specified by the user. This method leverages the FRED API to access and extract series metadata. It utilizes concurrent threads to efficiently manage multiple synchronous API requests, enhancing the speed of data retrieval and processing. This concurrency is particularly useful for augmenting data analysis, populating DataFrame columns, adjusting column headers, or for export purposes.

        The method uses Python's `concurrent.futures.ThreadPoolExecutor` to manage a pool of threads, each of which handles a request for series information. This approach allows for significant performance improvements when fetching data for multiple series IDs concurrently compared to sequential requests.

        Parameters:
        - series_id (str): The unique identifier for the FRED series from which information is to be retrieved.
        - relevant_info (list of str): Specifies the keys of information to fetch from the series data. This list should contain strings that match the desired data fields, such as 'id', 'title', 'frequency', 'units', 'popularity', and 'notes'.

        Returns:
        - pandas.Series: Contains the requested information for the specified series. Each index of the Series corresponds to an item in `relevant_info`, with its value from the FRED series metadata. Returns None if an error occurs or the requested information is not available.

        Raises:
        - ValueError: Thrown when the API response is not in JSON format, indicating a failure to fetch or parse the requested data.

        Example Usage:
        This example demonstrates how to use the `fetch_series_info` method to retrieve and compile  metadata for a list of series IDs. It showcases the efficiency gains from using concurrent threads to gather series information and compiling it into a comprehensive DataFrame.

        import pandas as pd
        from your_module import YourClass # Assuming YourClass contains these methods

        API_KEY = 'your_api_key_here'
        fred = YourClass(api_key=API_KEY)

        relevant_info = ['title', 'frequency', 'units', 'popularity', 'notes']
        series_ids = ['UNRATE', 'GDP']  # Example series IDs

        series_information = fred.fetch_series_info(series_ids, relevant_info)
        print(series_information)

        Note: Ensure your API_KEY is correctly set to use this example effectively. This approach is scalable for
        multiple series IDs, allowing for extensive data collection and analysis from the FRED database.
        """
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_series_id = {executor.submit(self.fetch_single_series_info, series_id, relevant_info): series_id
                                   for series_id in series_ids}
            for future in concurrent.futures.as_completed(future_to_series_id):
                series_id = future_to_series_id[future]
                try:
                    data = future.result()
                    if data is not None:
                        results.append(data)
                    if "error" not in data:
                        print(f"Series ID {series_id} fetched successfully.")
                    else:
                        print(f"Error fetching series ID {series_id}: {data['error']}")
                except Exception as exc:
                    print(f"Series ID {series_id} generated an exception: {exc}")
        return pd.DataFrame(results)

    def transform_series(self, response_api, series_id, include_realtime=False):
        """
        Transforms an API response into a structured pandas DataFrame.

        This method processes a JSON-formatted response from the FRED API, specifically handling the 'observations' key. It converts
        the 'date' field to datetime objects for temporal analysis and the 'value' field to numeric types, facilitating numerical
        computations and graphing. Non-numeric 'value' entries are converted to NaN, ensuring the DataFrame remains usable for
        further analysis.

        Parameters:
        - response_api (Response): The response object from the requests library, containing the JSON data from the FRED API.

        Returns:
        - pandas.DataFrame: A DataFrame with columns 'date' and 'value', where 'date' is formatted as datetime objects and 'value'
          as floats. If the response doesn't contain 'observations' or is not in JSON format, an empty DataFrame is returned.

        Example:
            response = requests.get("FRED_API_URL")
            df = transform_series(response)
            print(df.head())
        """
        try:
            # Attempt to parse the JSON data
            data = response_api.json()
        except ValueError:
            # Handle the case where the response is not in JSON format
            print("Response is not in JSON format.")
            return pd.DataFrame()  # Return an empty DataFrame
        # Check if 'observations' key is in the data
        if 'observations' in data:
            # Extract observations data into a DataFrame
            observations = data['observations']
            df = pd.DataFrame(observations)
            # Convert 'date' column to datetime objects
            df['realtime_start'] = pd.to_datetime(df['realtime_start'])
            df['realtime_end'] = pd.to_datetime(df['realtime_end'])
            df['date'] = pd.to_datetime(df['date'])
            # Convert 'value' column to numeric, set errors='coerce' to handle any conversion issues
            df['value'] = pd.to_numeric(df['value'], errors='coerce').astype(float).round(5)
            df['series'] = str(series_id)
            if include_realtime:
                df['hash_key'] = (df['realtime_start'].astype(str) + df['date'].astype(str) +
                                  df['value'].astype(str) + df['series'].astype(str))
            else:
                df['hash_key'] = (df['date'].astype(str) + df['value'].astype(str) + df['series'].astype(str))

            df['hash_key'] = df['hash_key'].apply(lambda x: hashlib.sha256(x.encode()).hexdigest())
            return df
        else:
            # If 'observations' key is not present, return an empty DataFrame
            print("'observations' key not found in the response.")
            return pd.DataFrame()

    @RateLimitDecorator(calls=calls_per_minute)
    def retrieve_single_series_latest_release(self, series_id):
        """
        Retrieve that is leveraged by the retrieve_series_latest_release method to execute concurrent requests for
        series information by using the ThreadPoolExecutor for synchronous requests.
        """
        url = f"{self.root_url}/series/observations?series_id={series_id}&api_key={self.fred_api_key}&file_type=json"
        url_website = "https://fred.stlouisfed.org/series/%s" % series_id
        response_api = requests.get(url)
        if response_api.status_code == 200:
            try:
                df = self.transform_series(response_api, series_id)
                if not df.empty:
                    df['Website URL'] = url_website
                    df['JSON URL'] = url
                    latest_release = df[['realtime_start', 'date', 'value', 'series', 'hash_key', 'Website URL', 'JSON URL']]
                    latest_release = latest_release.rename(columns={
                        "realtime_start": "Published Date",
                        "date": "Reporting Date",
                        "value": "Value",
                        "series": "Series",
                        "hash_key": "Unique Key"
                    })
                    return latest_release
            except ValueError:
                print("Response is not in JSON format.")
                print("Response content:", response_api.text)
                return None
        else:
            print(f"Failed to fetch data. Status code: {response_api.status_code}")
            print("Response content:", response_api.text)
            return None

    def retrieve_series_latest_release(self, series_ids):
        """
             Retrieves the latest release/publication of time series data for a specified FRED series identifier. Leverages concurrent threads to efficiently manage multiple synchronous API requests, enhancing the speed of data retrieval and processing. This concurrency is particularly useful for augmenting data analysis, populating DataFrame columns, adjusting column headers, or for export purposes.

             This method queries the FRED API to obtain observation data for the series specified by `series_id`. The observations include dates and corresponding values, which are returned as a pandas DataFrame for ease of analysis and manipulation. This function is essential for economic and financial analysis, allowing users to access a wide range of economic data provided by the Federal Reserve Bank of St. Louis.

             Parameters:
             - series_id (str): The unique identifier for the FRED series from which to retrieve observation data. Example series IDs include 'GDP' for Gross Domestic Product, 'UNRATE' for Unemployment Rate, etc.

             Returns:
             - pandas.DataFrame: A DataFrame containing two columns, 'date' and 'value', representing the time series data of the specified FRED series. Each row corresponds to an observation date and its associated value.

             Raises:
             - ValueError: If the API response is not in JSON format, indicating an issue with the request or the FRED API ervice. This exception includes a message detailing the nature of the error and the content of the response.

             Example Usage:
                 fred_api = FredAPI('your_api_key_here')
                 gdp_data = fred_api.retrieve_fred_series_data('GDP')
                 print(gdp_data.head())

             Notes:
             - The method ensures that the API response is in JSON format before attempting to parse it. If the response is not in JSON format, or if the API call fails (e.g., due to an incorrect series ID or network issues), an appropriate message is printed, and None is returned.
             - Users should ensure that the provided `series_id` is valid and corresponds to a series available in the FRED database. A list of valid series IDs can be found on the FRED website.
            """
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_series_id = {executor.submit(self.retrieve_single_series_latest_release, series_id): series_id
                                   for series_id in series_ids}
            for future in concurrent.futures.as_completed(future_to_series_id):
                series_id = future_to_series_id[future]
                try:
                    data = future.result()
                    if data is not None:
                        results.append(data)
                    else:
                        print(f'Error fetching series ID {series_id}: No data returned.')
                except Exception as exc:
                    print(f"Series ID {series_id} generated an exception: {exc}")
        if results:
            return pd.concat(results, ignore_index=True)
        else:
            return pd.DataFrame()

    @RateLimitDecorator(calls=calls_per_minute)
    def retrieve_single_series_all_releases(self, series_id, realtime_start=None, realtime_end=None):
        """
        Retrieve that is leveraged by the retrieve_series_all_releases method to execute concurrent requests for
        series information by using the ThreadPoolExecutor for synchronous requests.
        """
        realtime_start = realtime_start or self.earliest_realtime_start
        realtime_end = realtime_end or self.latest_realtime_end
        url = f"{self.root_url}/series/observations?series_id={series_id}&realtime_start={realtime_start}&realtime_end={realtime_end}&api_key={self.fred_api_key}&file_type=json"
        url_website = "https://fred.stlouisfed.org/series/%s" % series_id
        response_api = requests.get(url)
        if response_api.status_code == 200:
            try:
                df = self.transform_series(response_api, series_id, include_realtime=True)
                if not df.empty:
                    df['Website URL'] = url_website
                    df['JSON URL'] = url
                    all_releases = df[['realtime_start', 'realtime_end', 'date', 'value', 'series', 'hash_key', 'Website URL', 'JSON URL']]
                    all_releases = all_releases.rename(columns={
                        "realtime_start": "Published Date",
                        "realtime_end": "Validity Date",
                        "date": "Reporting Date",
                        "value": "Value",
                        "series": "Series",
                        "hash_key": "Unique Key"
                    })
                    return all_releases
            except ValueError:
                print("Response is not in JSON format.")
                print("Response content:", response_api.text)
                return None
        else:
            print(f"Failed to fetch data. Status code: {response_api.status_code}")
            print("Response content:", response_api.text)
            return None

    def retrieve_series_all_releases(self, series_ids):
        """
        Retrieves all historical data releases for a given FRED series ID, including initial releases and subsequent revisions. Leverages concurrent threads to efficiently manage multiple synchronous API requests, enhancing the speed of data retrieval and processing. This concurrency is particularly useful for augmenting data analysis, populating DataFrame columns, adjusting column headers, or for export purposes.

        This method constructs a URL to query the FRED API for a given series ID, with optional parameters for the start and end of the realtime period. It returns a DataFrame containing each release of the data point, including the observation date, the date of release (realtime start), and the reported value.

        Parameters:
        - series_id (str): The FRED series ID for which to retrieve the data.
        - realtime_start (str, optional): The start of the realtime period for which to retrieve data. Defaults to the earliest available data.
        - realtime_end (str, optional): The end of the realtime period for which to retrieve data. Defaults to the latest available data.

        Returns:
        - pandas.DataFrame: A DataFrame with columns 'date', 'realtime_start', and 'value', where 'date' is the observation date and 'realtime_start' is the date when the corresponding value was first released or revised.

        If the API call fails, or the response is not in JSON format, the method prints an error message and returns None.
        """
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_series_id = {executor.submit(self.retrieve_single_series_all_releases, series_id): series_id
                                   for series_id in series_ids}
            for future in concurrent.futures.as_completed(future_to_series_id):
                series_id = future_to_series_id[future]
                try:
                    data = future.result()
                    if data is not None:
                        results.append(data)
                    else:
                        print(f"Error fetching series ID {series_id}: No data returned.")
                except Exception as exc:
                    print(f"Series ID {series_id} generated an exception: {exc}")
        if results:
            return pd.concat(results, ignore_index=True)
        else:
            return pd.DataFrame()

    @RateLimitDecorator(calls=calls_per_minute)
    def retrieve_single_series_first_release(self, series_id):
        """
        Retrieve that is leveraged by the retrieve_series_first_releases method to execute concurrent requests for
        series information by using the ThreadPoolExecutor for synchronous requests.
        """
        df = self.retrieve_single_series_all_releases(series_id)
        if not df.empty:
            # Group by the observation date and take the first release for each group
            first_release = df.groupby(['Reporting Date']).first().reset_index()
            # Select only the relevant columns and rename them
            first_release = first_release[['Published Date', 'Reporting Date', 'Value', 'Series', 'Unique Key', 'Website URL', 'JSON URL']]
            return first_release
        else:
            # If the DataFrame is empty, return it as is or handle the case as appropriate
            print(f"No data available for series {series_id}.")
            return df

    def retrieve_series_first_release(self, series_ids):
        """
        Retrieves the initial release data for a specified FRED series ID, focusing exclusively on the data as it was first published, and excluding any subsequent revisions. This method is particularly useful for analyses that require understanding the initial impact of economic indicators before any revisions are made, allowing for a comparison between initial estimates and later revised data.

        Leverages concurrent threads to efficiently manage multiple synchronous API requests, enhancing the speed of data retrieval and processing. This concurrency is particularly useful for augmenting data analysis, populating DataFrame columns, adjusting column headers, or for export purposes.

        Utilizing the comprehensive data retrieval capabilities of the `retrieve_series_all_releases` method, this function filters the dataset to present only the first instance of each observation. This enables researchers, analysts, and enthusiasts to examine the initial figures reported for key economic indicators, such as GDP, inflation rates, or employment figures, offering insights into initial estimations versus revised figures.

        Parameters:
        - series_id (str): The unique identifier for the desired FRED series, which specifies the particular dataset to be retrieved. This ID corresponds to a wide range of economic data series provided by the Federal Reserve Bank of St. Louis.

        Returns:
        - pandas.DataFrame: A structured DataFrame that includes three key columns: 'Published Date' (indicating when the data was first released), 'Reporting Date' (the date to which the data pertains), and 'Value' (the initial value as first reported). This DataFrame facilitates direct analysis and comparison of initial economic data releases.

        Example Usage:
            fred = FredAPI("your_api_key")
            initial_gdp_release = fred.retrieve_series_first_release("GDP")
            print(initial_gdp_release.head())

        This method is instrumental in performing historical accuracy assessments, evaluating forecasting models, or conducting academic research that scrutinizes the reliability and revisions of economic data. By isolating the first release, users can assess how initial perceptions of economic conditions are later adjusted and what factors contribute to these revisions.

        Note:
        - The method assumes the availability of a comprehensive dataset for the specified series ID, spanning all releases. In scenarios where no data is available or the series ID is incorrect, the method will indicate the absence of data accordingly.
        - This approach is particularly valuable in research contexts where the initial reaction to economic indicators is of interest, allowing for a nuanced understanding of economic dynamics as perceived at different points in time.
        """
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_series_id = {executor.submit(self.retrieve_single_series_first_release, series_id): series_id
                                   for series_id in series_ids}
            for future in concurrent.futures.as_completed(future_to_series_id):
                series_id = future_to_series_id[future]
                try:
                    data = future.result()
                    if data is not None:
                        results.append(data)
                    else:
                        print(f"Error fetching series ID {series_id}: No data returned.")
                except Exception as exc:
                    print(f"Series ID {series_id} generated an exception: {exc}")
        if results:
            return pd.concat(results, ignore_index=True)
        else:
            return pd.DataFrame()

    @RateLimitDecorator(calls=calls_per_minute)
    def get_single_website_url(self, series_id):
        url = "%s/series/observations?series_id=%s&api_key=%s&file_type=json" % (
            self.root_url, series_id, self.fred_api_key)
        url_website = "https://fred.stlouisfed.org/series/%s" % series_id
        response_api = requests.get(url)
        if response_api.status_code == 200:
            try:
                return url_website
            except ValueError:
                print("Response is not in JSON format.")
                print("Response content:", response_api.text)
                return None
        else:
            print(f"Failed to fetch data. Status code: {response_api.status_code}")
            print("Response content:", response_api.text)
            return None

    def _summarize_dataframe(self, data_frame):
        """
        Helper method to convert a DataFrame into a summarized text format that ChatGPT can understand.

        Parameters:
        - data_frame (pandas.DataFrame): The DataFrame to summarize.

        Returns:
        - str: A string summary of the DataFrame.
        """
        # Implement a method to summarize the DataFrame as needed, this could be a simple CSV conversion,
        # or more complex text summarization depending on the context and the need.
        # This is just a placeholder for the actual implementation.
        return data_frame.to_csv()

    def analyze_with_chatgpt(self, data_frame, question):
        """
        Uses OpenAI's ChatGPT to analyze a pandas DataFrame.

        Parameters:
        - data_frame (pandas.DataFrame): The DataFrame to analyze.
        - question (str): A question or prompt for ChatGPT related to the analysis of the DataFrame.

        Returns:
        - str: The response from ChatGPT.
        """
        # Convert the DataFrame to a format that can be understood by ChatGPT (e.g., CSV, text summary, etc.)
        data_summary = self._summarize_dataframe(data_frame)

        # Ensure your OpenAI API key is set in your environment variables or set it directly
        openai.api_key = self.openai_api_key
        # Send the question and the data summary to ChatGPT
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",  # Or another model version
                messages=[
                    {"role": "system",
                     "content": "You are an expert level economist trained to analyze and present conclusions based on economic and financial data."},
                    {"role": "user", "content": f"{question}\n\n{data_summary}"}
                ]
            )
            # Return the text response
            return response['choices'][0]['message']['content']
        except Exception as e:  # General exception handling, consider specifying the exception
            print("An error occurred while querying the OpenAI API:", e)
            return None
