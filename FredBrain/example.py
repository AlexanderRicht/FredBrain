from FredBrain import FredBrain
from MySQLBrain import MySQLBrain
import os
import pandas as pd

FRED_KEY = os.environ.get("fred_api_key")
OPENAI_KEY = os.environ.get("openai_api_key")

fred = FredBrain(fred_api_key=FRED_KEY)

search_attributes = ["popularity", "frequency"]
search_values = [50, "Annual"]
search_output_labor = fred.search_brain("Labor", search_attributes, search_values)
search_output_employment = fred.search_brain("Employment", search_attributes, search_values)
search_output_wages = fred.search_brain("Wages", search_attributes, search_values)
search_output_combined = pd.concat([search_output_labor, search_output_employment, search_output_wages],
                                   ignore_index=True)

series_list = list(search_output_combined['id'])
print(series_list)
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

db_manager = MySQLBrain(host, user, passwd, db_name=db)
print(collected_first_releases.columns)
#
# db_manager.list_databases()  # List all databases
# db_manager.check_create_database(db)
#
#db_manager.fred_create_table_sql(df=collected_first_releases, table_name="UnrevisedReleases")
#db_manager.fred_create_table_sql(df=collected_latest_releases, table_name="RevisedReleases")
#db_manager.fred_create_table_sql(df=collected_all_releases, table_name="AllReleaseVersion")
# db_manager.close_connection()

db_manager.insert_new_rows( df=collected_first_releases, table_name="UnrevisedReleases")
db_manager.insert_new_rows( df=collected_latest_releases, table_name="RevisedReleases")

# Assuming this method returns a DataFrame
# analysis = fred.analyze_with_chatgpt(all_data_observations, "Provide a summary of the key trends in this economic data.")
# print(analysis)
