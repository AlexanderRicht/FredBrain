![Federal Reserve symbol](https://media.istockphoto.com/id/1308151210/photo/fed-federal-reserve-of-usa-sybol-and-sign.jpg?s=612x612&w=0&k=20&c=bO642TWIyj2hGte2WqW3CrWbd3DD3BA6TSRWzH6ocYg= "Federal Reserve")

**Table of Contents**
1. [Introduction](#Introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Dependencies](#dependencies)
5. [License](#license)
6. [Contributing](#contributing)
7. [Tutorial](#tutorial)
   - [Step 1: Importing and Getting Our Initial DataFrame](#step-1-importing-and-getting-our-initial-dataframe-of-fred-series-ids)
   - [Step 2: Retrieve Additional Metadata](#step-2-retrieve-additional-metadata-related)
   - [Step 3: Extract Unrevised Data Releases](#step-3-extract-unrevised-data-releases-for-each-series)
   - [Step 4: Insert DataFrame into MySQL](#step-4-insert-the-dataframe-into-a-mysql-database-for-seamless-storage)
   - [Step 5: Insert New Data into Existing MySQL Table](#step-5-inserting-new-data-into-the-existing-mysql-table)
   - [Step 6: Input DataFrame into OpenAI (GPT-4) for Insights](#step-6-input-the-dataframe-into-openai-gpt-4-for-insights)
# FredBrain: A Python Package for retrieving Federal Reserve Economic Data at Scale and feeding it to OpenAI
## Introduction
[FredBrain](https://pypi.org/project/FredBrain) is a Python package that offers a practical approach for accessing economic data from the Federal Reserve ([FRED API Documentation](https://fred.stlouisfed.org/docs/api/fred/)). It is built to assist those involved in economic research, financial analysis, and model development by providing a straightforward means of data retrieval. Additionally, it takes an experimental approach to integrating the OpenAI GPT framework into the class with the ultimate aim of creating an Ad-Hoc GPT economist expert to assist you in your analysis. Hence, why we refer to the class as `FredBrain`. The class itself will hopefully act as the Brain to power OpenAI Chat Completions. 

Utilizing familiar libraries such as `pandas`, `datetime`, `requests`, and  `openai` FredBrain facilitates the transformation of JSON responses into user-friendly `DataFrame` objects. This process is designed to be intuitive, allowing users to focus more on their analysis, less on data wrangling and to leverage OpenAI chat for analysis support and conclusions.

As FredBrain continues to develop, it seeks to maintain a balance between expanding its functionality and ensuring reliability. It strives to be a helpful resource for users who need to integrate economic data into their work, without being overwhelming or overly complex.

FredBrain invites you to streamline the way you interact with economic data, opening up possibilities for more focused research and insightful analyses.
## Features
- Efficiently navigates through FRED's series data using single or multiple filters, enhancing the user's ability to pinpoint relevant datasets.
- Streamlines the discovery and selection of economic variables by fetching extensive subsets of FRED categories and their associated series.
- Equips users with tools to instantly convert series searches or category subsets into comprehensive datasets of original or revised time-series data.
- Offers the flexibility to fetch time-series data for pre-determined sets of series or categories without additional search requirements.
- Facilitates the extraction of metadata, preserving critical details about the time-series data for informed analysis.
- Optimized for scalability, complying with the Federal Reserve's API request limits, enabling extensive data retrieval within the threshold of 1000 requests per minute
- Provide Seamless MySQL Local or Cloud Database Insertion
- *Integrating OpenAI to create an economist GPT for providing additional insights on data extracted via the FredBrain
  
*This is experimental and not guaranteed to perform well. The ambition of myself and contributors would be to design a system that feeds data to a GPT to create an Economist GPT

## Installation
Install the package using 
```sh
# or PyPI
pip install FredBrain
```
## Dependencies
- [Pandas](https://pypi.org/project/pandas/)
- [Datetime](https://docs.python.org/3/library/datetime.html)
- [Requests](https://pypi.org/project/requests/)
- [OS](https://docs.python.org/3/library/os.html)
- [MySQL Connector](https://pypi.org/project/mysql-connector-python/)
- [hashlib](https://docs.python.org/3/library/hashlib.html)
- [time](https://docs.python.org/3/library/time.html)
- [OpenAI](https://platform.openai.com/docs/libraries)
## License
[MIT License](https://github.com/AlexanderRicht/InvestmentResearch/blob/main/LICENSE.md)
## Contributing
All contributions and ideas are welcome
# A walk-through - From Search to Time-Series Data
## Step 1: Importing and getting our initial dataframe of FRED series IDs
The first thing we can do is import and then begin with a preliminary search to identify a series we want to extract. To do this, we need to import the FredBrain package and related api keys. API keys for FRED can be requested here [Fred API Keys](https://fredaccount.stlouisfed.org/apikeys). For OpenAI, keys can be created here [OpenAI API Keys](https://platform.openai.com/api-keys)
```sh
from FredBrain import FredBrain
import os
import pandas as pd

FRED_KEY = os.environ.get("fred_api_key")
OPENAI_KEY = os.environ.get("openai_api_key")

fred = FredBrain(fred_api_key=FRED_KEY)
```
Once this is done we can search for a "series" we believe is relevant to the research or questions we have. To do this, you must input a search text and optionally, enter a search and value attribute
1. Our search text "Labor"
2. Our search attributes "Popularity" or "Frequency" or both
4. Our search value is 75 (returning those series with popularity equal to or greater than 75) or "Monthly" (returning those series with a frequency of monthly)
5. We repeat this for search text "Employment" and "Wages" as shown
```sh
search_attributes = ["popularity", "frequency"]
search_values = [50, "Monthly"]
search_output_labor = fred.search_brain("Labor", search_attributes, search_values)
search_output_employment = fred.search_brain("Employment", search_attributes, search_values)
search_output_wages = fred.search_brain("Wages", search_attributes, search_values)
search_output_combined = pd.concat([search_output_labor, search_output_employment, search_output_wages], ignore_index=True)
```
| id          | notes                                                                     |
|:------------|:--------------------------------------------------------------------------|
| UNRATE      | The unemployment rate represents the number of...                         |
| UNRATENSA   | The unemployment rate represents the number of...                         |
| CIVPART     | The series comes from the 'Current Population...                          |
| U6RATE      | The series comes from the 'Current Population...                          |
| LNS11300060 | The series comes from the 'Current Population...                          |

Now we have gotten a `DataFrame` of different series ids and their related metadata
## Step 2: Retrieve additional metadata related
Now that we have a `DataFrame` of different series ids we will loop through them to extract additional metadata related to the series. To begin, we need to store the id column into a list and define the relevant metadata that we believe is interesting to retain [FRED Series Doc](https://fred.stlouisfed.org/docs/api/fred/series.html)
```sh
series_list = list(search_output_combined['id'])
relevant_info = ['title', 'frequency', 'units', 'popularity', 'notes']
series_info_data = []
for item in series_list:
    series_info_data.append(fred.fetch_series_info(series_id=item, relevant_info=relevant_info))
series_information = pd.DataFrame(series_info_data)
```
| title                                              | notes                                                                                      |
|----------------------------------------------------|--------------------------------------------------------------------------------------------|
| Unemployment Rate                                  | The unemployment rate represents the number of...                                          |
| Unemployment Rate                                  | The unemployment rate represents the number of...                                          |
| Labor Force Participation Rate                     | The series comes from the 'Current Population...                                           |
| Total Unemployed, Plus All Persons Marginally ...  | The series comes from the 'Current Population...                                           |
| Labor Force Participation Rate - 25-54 Yrs.        | The series comes from the 'Current Population...                                           |
| ...                                                | ...                                                                                        |
| Average Hourly Earnings of All Employees, Tran... | The series comes from the 'Current Employment...                                           |
| Average Hourly Earnings of All Employees, Prof... | The series comes from the 'Current Employment...                                           |
| Average Hourly Earnings of All Employees, Reta... | The series comes from the 'Current Employment...                                           |
| Average Hourly Earnings of All Employees, Priv... | The series comes from the 'Current Employment...                                           |
| Federal Funds Effective Rate                       | Averages of daily figures. \n\nFor additional ...                                          |

## Step 3: Extract Unrevised, Revised and All Data Releases for Each Series
After identifying the relevant series through the DataFrame we constructed earlier, our next step involves capturing the initial unrevised, revised and all releases of the observations for each series. This process enriches our dataset with critical metadata and preserves the authenticity of the data as it was first reported.

### Why Differentiate Unrevised from Revised Data?
In applications such as economic modeling or predictive analysis, it's essential to mitigate any potential look-ahead bias. Look-ahead bias occurs when a model inadvertently uses information that was not available at the time of prediction, leading to overfitting and unrealistic performance estimates. By utilizing unrevised data, we ensure our analyses reflect the state of knowledge available at each observation's original reporting time, maintaining the integrity of our predictive efforts. Therefore, we can extract a `DataFrame` of unrevised, revised, and all releases for each series.
## Implementation
To compile our comprehensive dataset, we iterate over each series ID, retrieving the data points along with their associated metadata. This metadata includes the series' title, frequency, and units, which are then appended to each observation, enhancing our dataset's usability and richness. Additionally, a unique Hash Key is generated automatically for each row to be used later for database insertion and to ensure data integrity and no insertion of duplicate data.
```sh
# Initialize empty DataFrames to collect data
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
```
## Step 4: Insert the DataFrame into a MySQL Database for seamless storage
After preparing your `DataFrame` object with the desired FRED data, you can insert it into either a local or cloud MySQL database for persistent storage. This step allows for the seamless integration of FRED data into your personal or organizational databases, facilitating easy access and analysis.

### Why Store Data in a MySQL Database?
Storing your data in a MySQL database offers several advantages:
1. **Data Integrity**: MySQL databases are designed to maintain data integrity, ensuring that your data remains accurate and consistent.
2. **Scalability**: MySQL databases can handle large datasets and are scalable to accommodate future growth.
3. **Data Security**: MySQL databases offer robust security features to protect your data from unauthorized access.
4. **Data Accessibility**: Once your data is stored in a MySQL database, it can be easily accessed and queried using SQL, enabling seamless integration with other applications and tools.
5. **Data Persistence**: By storing your data in a MySQL database, you ensure that it is preserved over time, even if your local environment changes.
6. **Collaboration**: Storing your data in a MySQL database allows for easy collaboration and sharing of data with other team members or stakeholders.
7. **Data Analysis**: MySQL databases provide powerful tools for data analysis and reporting, enabling you to derive valuable insights from your data.
8. **Data Integration**: MySQL databases can be integrated with other systems and applications, allowing for seamless data exchange and interoperability.
### Downloading MySQL
If you don't have MySQL installed on your local machine, you can download it from the official MySQL website: [MySQL Downloads](https://dev.mysql.com/downloads/)

Additionally, for a cloud MySQL database, you can use services such as Amazon RDS, Google Cloud SQL, or Azure Database for MySQL. I currently use a low-cost Planetscale solutions for my MySQL database: [Planetscale](https://planetscale.com/)
### Preparing MySQL Connection
Before inserting the data, you need to establish a connection with your MySQL server. Gather your MySQL credentials and determine whether you'll be connecting to an existing database or creating a new one.

To connect to your MySQL database, you'll need the following information:
1. host: The hostname or IP address of your MySQL server.
2. user: Your MySQL username.
3. passwd: Your MySQL password.
4. db_name: The name of the database you wish to connect to or create.
5. ssl: Optional. If your MySQL server requires SSL, you can specify the path to your SSL certificate.

You can securely access your credentials using environment variables:
```sh
import os
from SQLBrain import SQLBrain  # Ensure SQLBrain is correctly imported

host = os.getenv("DATABASE_HOST")
user = os.getenv("DATABASE_USERNAME")
passwd = os.getenv("DATABASE_PASSWORD")
db = os.getenv("DATABASE_NAME")
ssl_verify_identity = True
ssl_ca = "C:/ssl/certs/cacert.pem"

# Initialize the database manager and connect to MySQL
db_manager = MySQLBrain(host, user, passwd, db_name=db, ssl_verify_identity=True, ssl_ca=ssl_ca)
db_manager.list_databases()  # Optional: List all existing databases to verify the connection
db_manager.check_create_database(db_name)  # Create the database if it doesn't exist
```
### Inserting DataFrame into the Database
After establishing a connection and ensuring the desired database is ready, you can proceed to insert your `DataFrame` into the database. Specify the table name where you want to store the data. If the table does not exist, it will be created based on the DataFrame structure.
```sh
# Insert the DataFrames into the MySQL database
db_manager.fred_create_table_sql(df=collected_first_releases, table_name="First Releases")
db_manager.fred_create_table_sql(df=collected_latest_releases, table_name="Latest Releases")
db_manager.fred_create_table_sql(df=collected_all_releases, table_name="All Releases")
```
Congratulations! Your DataFrame is now stored in the specified MySQL database, making it accessible for future queries and analysis directly from SQL Workbench or any MySQL client.
## Step 5: Inserting new data into the existing MySQL Table
If you have new data that you want to append to an existing MySQL table, you can use the `fred_insert_data_sql` method to insert the new data into the table. This method will automatically only insert unique rows based on the hash key, ensuring that no duplicate data is added to the existing table. This allows you to seamlessly add new rows from a new FRED series or updated data from an existing series to your MySQL table.
```sh

db_manager.insert_new_rows( df=collected_first_releases, table_name="First Releases")
```
## Step 6: Input the DataFrame into OpenAI (GPT-4) for insights
The `DataFrame` from before can be inputted into the chatgpt method and a prompt of your choosing can be tailored. This will result in an output given by chatgpt based on the prompt and data provided
```sh
# Assuming this method returns a DataFrame
analysis = fred.analyze_with_chatgpt(all_data_observations, "Provide a summary of the key trends in this economic data.")
print(analysis)
```

Congratulations! You now have Federal Reserve Economic data stored in a Database and an LLM Powered Economist at your fingertips! Who knows what the world will have in store for you two!
![img.png](img.png)
![img_1.png](img_1.png)