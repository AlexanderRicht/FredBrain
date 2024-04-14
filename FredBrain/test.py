import os
from FredBrain import FredBrain
from bokeh.plotting import figure, show, output_file
from bokeh.models import HoverTool
from bokeh.io import output_notebook
import pandas as pd
from dotenv import load_dotenv
import mysql.connector
from powerbiclient import QuickVisualize, get_dataset_config, Report
from powerbiclient.authentication import DeviceCodeLoginAuthentication

FRED_KEY = os.environ.get("fred_api_key")
fred = FredBrain(fred_api_key=FRED_KEY)

categories = fred.get_series_from_category(1, 10)
print(categories)
categories.to_excel("categories_information.xlsx")

# load_dotenv()
#
# # Now access the variables using os.getenv
# DATABASE_HOST = os.getenv('DATABASE_HOST')
# DATABASE_USERNAME = os.getenv('DATABASE_USERNAME')
# DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
# DATABASE_NAME = os.getenv('DATABASE_NAME')
#
# try:
#     print("Connecting to the database...")
#     # Pass connection parameters as keyword arguments
#     db_manager = mysql.connector.connect(host=DATABASE_HOST, user=DATABASE_USERNAME, passwd=DATABASE_PASSWORD, db=DATABASE_NAME)
#     cursor = db_manager.cursor()
#     cursor.execute("SHOW TABLES")  # This is the correct method to list all databases
#     for db in cursor:
#         print(db)
#     print("Connected:", db_manager)
# except mysql.connector.Error as e:
#     print("Error while connecting to MySQL", e)
#
# existing_data_query = f"SELECT * FROM research.FirstReleases Where Series = 'UNRATE';"
# print(f"SQL Statement - Retrieve Existing Data:\n{existing_data_query}")
# cursor.execute(existing_data_query)
# existing_rows = cursor.fetchall()
# existing_df = pd.DataFrame()
# existing_df = pd.DataFrame(existing_rows, columns= ['sql_upload_datetime', 'Published Date', 'Reporting Date', 'Value', 'Series', 'Unique Key', 'Website URL', 'JSON URL'] )
# # Set pandas display options for large dataframes
# pd.set_option('display.max_rows', 100)  # Adjust as needed
# pd.set_option('display.max_columns', 10)  # Adjust as per your dataframe's column count
# pd.set_option('display.width', 1000)  # Set to your notebook's width
# pd.set_option('display.max_colwidth', None)  # Display full content of each column
#
# # Utilize the Styler API for a nicer display
# styled_df = existing_df.style.set_table_styles(
#     [{'selector': 'th', 'props': [('font-size', '12pt')]}]  # Header font size
# ).set_properties(**{
#     'background-color': '#f7fbff',  # Light blue background for better readability
#     'color': 'black',  # Ensure the text is black for contrast
#     'border-color': 'white'  # Set border color
# }).set_caption("UNRATE Series Data")  # Set a caption for the table
#
# # Display the styled dataframe in the notebook
# styled_df
#
# auth = DeviceCodeLoginAuthentication()
#
# # Create a Power BI report from your data
# PBI_visualize = QuickVisualize(get_dataset_config(existing_df), auth=auth)
# PBI_visualize.create_report()
