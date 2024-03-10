from FredBrain import FredBrain
from MySQLBrain import MySQLBrain
import pandas as pd
import os
import hashlib

FRED_KEY = os.environ.get("fred_api_key")

fred = FredBrain(fred_api_key=FRED_KEY)
search_attributes = ["frequency"]
search_values = ["Monthly"]

search_output_gdp = fred.search_brain("Real GDP", search_attributes, search_values)
print(search_output_gdp)
series_list = list(search_output_gdp['id'])
relevant_info = ['title', 'frequency', 'units', 'popularity', 'notes']
series_info_data = []
for item in series_list:
    series_info_data.append(fred.fetch_series_info(series_id=item, relevant_info=relevant_info))
series_information = pd.DataFrame(series_info_data)
print(series_information)

collected_first_releases = pd.DataFrame()
collected_latest_releases = pd.DataFrame()
collected_all_releases = pd.DataFrame()

for i, item in enumerate(series_list):
    first_release = fred.retrieve_series_first_release(series_id=item)
    latest_release = fred.retrieve_series_latest_release(series_id=item)
    all_releases = fred.retrieve_series_all_releases(series_id=item)
    if first_release is not None:
        data_website_url = fred.get_website_url(series_id=item)
        data_json_url = fred.get_json_url(series_id=item)
        title = series_information.loc[i, 'title']
        frequency = series_information.loc[i, 'frequency']
        unit = series_information.loc[i, 'units']
        metadata = {
            'Category': title,
            'Frequency': frequency,
            'Units': unit,
            'Website URL': data_website_url,
            'JSON URL': data_json_url
        }
        for df in [first_release, latest_release, all_releases]:
            for key, value in metadata.items():
                df[key] = value
        collected_first_releases = pd.concat([collected_first_releases, first_release], ignore_index=True)
        collected_latest_releases = pd.concat([collected_latest_releases, latest_release], ignore_index=True)
        collected_all_releases = pd.concat([collected_all_releases, all_releases], ignore_index=True)
    else:
        print(f"No data available for series {item}.")


host = os.getenv("DATABASE_HOST")
user = os.getenv("DATABASE_USERNAME")
passwd = os.getenv("DATABASE_PASSWORD")
db = os.getenv("DATABASE_NAME")
ssl_verify_identity = True
ssl_ca = "C:/ssl/certs/cacert.pem"

db_manager = MySQLBrain(host, user, passwd, db_name=db, ssl_verify_identity=True, ssl_ca=ssl_ca)

#
# db_manager.list_databases()  # List all databases
# db_manager.check_create_database(db)
#
db_manager.fred_create_table_sql(df=collected_first_releases, table_name="First Releases")
db_manager.fred_create_table_sql(df=collected_latest_releases, table_name="Latest Releases")
db_manager.fred_create_table_sql(df=collected_all_releases, table_name="All Releases")



# db_manager.close_connection()

db_manager.insert_new_rows( df=collected_first_releases, table_name="test")
