from __init__ import FredBrain
from MySQLBrain import MySQLBrain
import pandas as pd
import os

FRED_KEY = os.environ.get("fred_api_key")

fred = FredBrain(fred_api_key=FRED_KEY)
search_attributes = ["frequency"]
search_values = ["Monthly"]
# Perform searches for different terms
search_output_gdp = fred.search_brain("Real GDP", search_attributes, search_values)
print(search_output_gdp)
series_list = list(search_output_gdp['id'])
relevant_info = ['title', 'frequency', 'units', 'popularity', 'notes']
series_info_data = []
for item in series_list:
    series_info_data.append(fred.fetch_series_info(series_id=item, relevant_info=relevant_info))
series_information = pd.DataFrame(series_info_data)
print(series_information)

all_data_observations = pd.DataFrame()
for i, item in enumerate(series_list):
    data_observations = fred.retrieve_series_first_release(series_id=item)
    data_website_url = fred.get_website_url(series_id=item)
    data_json_url = fred.get_json_url(series_id=item)
    if data_observations is not None:
        title = series_information.loc[i, 'title']
        frequency = series_information.loc[i, 'frequency']
        unit = series_information.loc[i, 'units']
        data_observations['Category'] = title
        data_observations['Frequency'] = frequency
        data_observations['Units'] = unit
        data_observations['Website URL'] = data_website_url
        data_observations['JSON URL'] = data_json_url
        if all_data_observations.empty:
            all_data_observations = data_observations
        else:
            all_data_observations = all_data_observations._append(data_observations, ignore_index=True)
    else:
        print(f"No data available for series {item}.")

host = os.getenv("DATABASE_HOST")
user = os.getenv("DATABASE_USERNAME")
passwd = os.getenv("DATABASE_PASSWORD")
db = os.getenv("DATABASE_NAME")
ssl_verify_identity = True
ssl_ca = "C:/ssl/certs/cacert.pem"

db_manager = MySQLBrain(host, user, passwd, db_name=db, ssl_verify_identity=True, ssl_ca=ssl_ca)


print(db_manager)
db_manager.list_databases()  # List all databases
db_manager.check_create_database(db)

db_manager.fred_create_table_sql(df=all_data_observations, table_name="test")
