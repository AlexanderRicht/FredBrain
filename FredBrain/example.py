import time
from FredBrain import FredBrain
from MySQLBrain import MySQLBrain
import os
import pandas as pd
from mysql.connector import Error


FRED_KEY = os.environ.get("fred_api_key")
OPENAI_KEY = os.environ.get("openai_api_key")

fred = FredBrain(fred_api_key=FRED_KEY)

search_attributes = ["popularity"]
search_values = [10]
search_output_labor = fred.search_brain("Labor", search_attributes, search_values)
search_output_employment = fred.search_brain("Employment", search_attributes, search_values)
search_output_wages = fred.search_brain("Wages", search_attributes, search_values)
search_output_salary = fred.search_brain("Salary", search_attributes, search_values)
search_output_income = fred.search_brain("Income", search_attributes, search_values)
search_output_housing = fred.search_brain("Housing", search_attributes, search_values)
search_output_age = fred.search_brain("Vacancies", search_attributes, search_values)


search_output_combined = pd.concat([search_output_income, search_output_employment, search_output_wages, search_output_salary, search_output_income, search_output_housing, search_output_age],
                                   ignore_index=True)
search_output_combined = search_output_combined.drop_duplicates(subset=['id'])


series_list = list(set(search_output_age['id']))
print(len(series_list))
print(series_list)

print("Sleeping for 60 seconds before continuing to ensure rate limit is not exceeded as method was previously called.")
time.sleep(60)
collected_first_releases = fred.retrieve_series_first_release(series_ids=series_list)
collected_first_releases.to_excel("first_releases.xlsx")

# print("Sleeping for 60 seconds before continuing to ensure rate limit is not exceeded as method was previously called.")
# time.sleep(60)
# collected_latest_releases = fred.retrieve_series_latest_release(series_ids=series_list)
# collected_latest_releases.to_excel("latest_releases.xlsx")

#
# print("Sleeping for 60 seconds before continuing to ensure rate limit is not exceeded as method was previously called.")
# time.sleep(60)
# collected_all_releases = fred.retrieve_series_all_releases(series_ids=series_list)


#
# print("Sleeping for 60 seconds before continuing to ensure rate limit is not exceeded as previous method was called.")
# time.sleep(60)
# relevant_info = ['id', "realtime_start", "realtime_end", 'title', 'frequency', 'units', "seasonal_adjustment", "last_updated", 'popularity', 'notes']
# series_info_data = fred.fetch_series_info(series_ids=series_list, relevant_info=relevant_info)
# series_information = pd.DataFrame(series_info_data)
# series_information.to_excel("series_information.xlsx")

# categories = fred.get_series_from_category(1, 1000000)


host = os.getenv("DATABASE_HOST")
user = os.getenv("DATABASE_USERNAME")
passwd = os.getenv("DATABASE_PASSWORD")
db = os.getenv("DATABASE_NAME")


db_manager = MySQLBrain(host, user, passwd, db_name=db)
#
# try:
    # db_manager.fred_create_table_sql(df=collected_first_releases, table_name="FirstReleases")
    # db_manager.fred_create_table_sql(df=collected_latest_releases, table_name="LatestReleases")
    # db_manager.fred_create_table_sql(df=collected_all_releases, table_name="AllReleases")db_manager.fred_create_table_sql(df=series_information, table_name="SeriesMetaData")
#     print("Connected:", db_manager)
# except Error as e:
#     print("Error while connecting to MySQL", e)


# db_manager.fred_create_table_sql(df=collected_first_releases, table_name="FirstReleases")
# db_manager.fred_create_table_sql(df=collected_latest_releases, table_name="LatestReleases")
# db_manager.fred_create_table_sql(df=collected_all_releases, table_name="AllReleaseVersion")
# db_manager.fred_create_table_sql(df=series_information, table_name="SeriesMetaData")
# db_manager.fred_create_table_sql(df=categories, table_name="Categories")

# db_manager.close_connection()

db_manager.insert_new_rows( df=collected_first_releases, table_name="FirstReleases")
# db_manager.insert_new_rows( df=collected_latest_releases, table_name="LatestReleases")
# db_manager.insert_new_rows( df=collected_all_releases, table_name="AllReleases")
# db_manager.insert_new_rows( df=series_information, table_name="SeriesMetaData")

# # Assuming this method returns a DataFrame
# # analysis = fred.analyze_with_chatgpt(all_data_observations, "Provide a summary of the key trends in this economic data.")
# # print(analysis)
