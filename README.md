![Federal Reserve symbol](https://media.istockphoto.com/id/1308151210/photo/fed-federal-reserve-of-usa-sybol-and-sign.jpg?s=612x612&w=0&k=20&c=bO642TWIyj2hGte2WqW3CrWbd3DD3BA6TSRWzH6ocYg= "Federal Reserve")

**Table of Contents**
1. [Introduction](#Introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Dependencies](#dependencies)
5. [License](#license)
6. [Contributing](#contributing)
7. [Tutorial](#tutorial)
   - [Step 1: Importing and Initiating Preliminary Search for FRED Series IDs](#step-1-importing-and-initiating-preliminary-search-for-fred-series-ids)
   - [Step 2: Search for Relevant Series IDs](#step-2-search-for-relevant-series-ids)
   - [Step 3: Retrieve Additional Metadata](#step-3-retrieve-additional-metadata-related)
   - [Step 4: Extract Unrevised, Revised and All Data Releases for Each Series](#step-4-extract-unrevised-revised-and-all-data-releases-for-each-series)
   - [Step 5: Insert DataFrame into MySQL](#step-5-insert-the-dataframe-into-a-mysql-database-for-seamless-storage)
   - [Step 6: Insert New Data into Existing MySQL Table](#step-6-inserting-new-data-into-the-existing-mysql-table)
   - [Step 7: Input DataFrame into OpenAI (GPT-4) for Insights](#step-7-input-the-dataframe-into-openai-gpt-4-for-insights)
# FredBrain: A Python Package for retrieving Federal Reserve Economic Data at ScaleWhat i
## Introduction
[FredBrain](https://pypi.org/project/FredBrain) is a Python package that offers a practical approach for accessing economic data from the Federal Reserve ([FRED API Documentation](https://fred.stlouisfed.org/docs/api/fred/)).  It was created to offer a straightforward way for enthusiasts and professionals alike to access economic data from the Federal Reserve. This Python package simplifies the process of fetching, storing, and analyzing economic information, making it a valuable tool for anyone engaged in economic research, financial analysis, or model development. Additionally, it takes an experimental approach to integrating the OpenAI GPT framework into the class with the ultimate aim of creating an Ad-Hoc GPT economist expert to assist you in your analysis. Hence, why we refer to the class as `FredBrain`. The class itself will hopefully act as a catalyst to your retrieval of FRED data as well as the Brain to power OpenAI Chat Completions. 

FredBrain brings several benefits to your workflow:
- It facilitates easy access to a wealth of economic data via the FRED API, retrieving the data with asynchronous concurrent requests immensely improving the speed of data retrieval and then directly storing it into a MySQL database for further analysis.
- The package experiments with integrating the OpenAI GPT framework, aiming to provide an ad-hoc GPT economist expert to support data interpretation and analysis.
- By leveraging libraries like `pandas`, `datetime`, `requests`, `MySQL Connector`, `concurrent.futures`, `functools`, and `openai`, FredBrain transforms JSON responses into intuitive DataFrame objects, streamlining the data preparation phase of your projects.

As FredBrain continues to develop, it seeks to maintain a balance between expanding its functionality and ensuring reliability. It strives to be a helpful resource for users who need to integrate economic data into their work, without being overwhelming or overly complex.

FredBrain invites you to streamline the way you interact with economic data, opening up possibilities for more focused research and insightful analyses by providing the functionality to retrieve FRED data at scale by leveraging concurrent futures, MySQL insertion and OpenAI integration.
## Key Features of FredBrain

FredBrain stands out with its robust features designed to enhance your experience in economic data analysis:

- **Advanced Filtering and Navigation:** Effortlessly sift through FRED's vast array of series data with sophisticated filters, allowing for precise selection of datasets that matter most to your research.
  
- **Streamlined Data Discovery:** Simplify the process of identifying vital economic indicators by accessing broad categories of FRED data, ensuring you capture all relevant series effortlessly.
  
- **Rapid Data Conversion:** Transform FRED Series IDs into extensive, actionable datasets. Utilize the power of concurrent futures for fast, efficient processing of time-series data, whether original or revised.
  
- **Comprehensive Metadata Extraction:** Never lose sight of the context. FredBrain ensures you retain essential metadata, offering a deeper understanding of the time-series data for nuanced analysis.
  
- **Designed for Scale:** Built with the Federal Reserve's API limitations in mind, FredBrain optimizes data retrieval operations to stay within the 120 requests per minute cap, ensuring your research continues uninterrupted and efficiently.
  
- **Flexible Data Storage:** Whether you prefer local or cloud-based solutions, FredBrain facilitates seamless integration with MySQL databases for reliable, persistent storage of your economic data.
  
- **Innovative OpenAI Integration (Experimental):** Embark on a journey with FredBrain's AI feature - an Economist GPT powered by OpenAI. This cutting-edge integration aims to enrich your analysis with profound insights, transforming data into knowledge together with GPT.*

*Note: The integration of OpenAI to generate an Economist GPT is experimental. The results may vary and should be used with caution. FredBrain is not responsible for the accuracy of the generated insights and does not guarantee the suitability of the results for any specific use case. The OpenAI integration is intended to be a helpful tool for generating insights and should be used as a supplement to your analysis, not as a replacement for professional judgment and expertise.


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
- [Concurrent Futures](https://docs.python.org/3/library/concurrent.futures.html)
- [Functools](https://docs.python.org/3/library/functools.html)
- [hashlib](https://docs.python.org/3/library/hashlib.html)
- [time](https://docs.python.org/3/library/time.html)
- [OpenAI](https://platform.openai.com/docs/libraries)
## License
[MIT License](https://github.com/AlexanderRicht/InvestmentResearch/blob/main/LICENSE.md)
## Contributing
All contributions and ideas are welcome
# A walk-through - From Search to Time-Series Data
## Step 1: Importing and Initiating Preliminary Search for FRED Series IDs
Before diving into the vast sea of economic data, let's start by setting up our environment and performing an initial search to identify the FRED series of interest. This involves importing the `FredBrain` package, configuring API keys, and leveraging `FredBrain`'s functionalities to find the relevant data series.

### Prerequisites
To access the Federal Reserve Economic Data (FRED) and OpenAI services, you'll need to obtain API keys from their respective platforms:

- **FRED API Keys:** Sign up and request your key [here](https://fredaccount.stlouisfed.org/apikeys).
- **OpenAI API Keys:** Generate your API key by visiting [this link](https://platform.openai.com/api-keys).

### Setting Up
With your API keys at hand, proceed by importing necessary libraries and initializing the `FredBrain` object with your FRED API key. Here's how:

```python
from FredBrain import FredBrain
import os
import pandas as pd

# Load your API keys from environment variables
FRED_KEY = os.environ.get("fred_api_key")
OPENAI_KEY = os.environ.get("openai_api_key")

# Initialize FredBrain with your FRED API Key
fred = FredBrain(fred_api_key=FRED_KEY)
```
## Step 2: Search for Relevant Series IDs
After setting up your FredBrain instance, the next crucial step is to identify relevant data series that align with your research interests or queries. FredBrain simplifies this process, allowing you to specify both search criteria and filters to narrow down the vast data available in the FRED database. 

Here's how to conduct an effective search:

1. **Choose Your Search Texts:** Start with broad keywords that represent your area of interest. For this example, we'll use "Labor", "Employment", and "Wages".

2. **Define Search Attributes:** Decide on the attributes that will help refine your search. Options include "Popularity" and "Frequency", among others.

3. **Set Search Values:** For attributes like "Popularity", specify a threshold (e.g., 50, to return series with popularity equal to or greater than 50). For "Frequency", you might choose "Monthly" to filter for monthly data series.

4. **Execute Searches:** Perform searches for each of your chosen keywords, applying the specified attributes and values. 

Here’s a code snippet to guide you through searching for series on "Labor", "Employment", and "Wages" with specified popularity and frequency:
```sh
# Define your search parameters
search_attributes = ["popularity", "frequency"]
search_values = [50, "Monthly"]

# Conduct the searches
search_output_labor = fred.search_brain("Labor", search_attributes, search_values)
search_output_employment = fred.search_brain("Employment", search_attributes, search_values)
search_output_wages = fred.search_brain("Wages", search_attributes, search_values)

# Combine the search outputs into a single DataFrame
search_output_combined = pd.concat([search_output_labor, search_output_employment, search_output_wages], ignore_index=True)
```
| id          | notes                                                                     |
|:------------|:--------------------------------------------------------------------------|
| UNRATE      | The unemployment rate represents the number of...                         |
| UNRATENSA   | The unemployment rate represents the number of...                         |
| CIVPART     | The series comes from the 'Current Population...                          |
| U6RATE      | The series comes from the 'Current Population...                          |
| LNS11300060 | The series comes from the 'Current Population...                          |

## Step 3: Retrieve additional metadata related
After identifying the relevant series IDs for your analysis, the next step involves fetching detailed metadata for each series. This metadata provides valuable insights into the data's characteristics and can inform your analysis strategy. FredBrain makes it straightforward to retrieve this information through its `fetch_series_info` method which automates looping through your Series Id list.

### Retrieving Metadata:

1. **Prepare the Series IDs:** First, compile the series IDs from your DataFrame into a list. These IDs are essential for querying the FRED database for metadata.

2. **Select Relevant Metadata Fields:** Decide which metadata fields are crucial for your analysis. Useful fields include 'id', 'title', 'frequency', 'units', and 'notes', among others. A comprehensive list of available fields can be found in the [FRED Series Documentation](https://fred.stlouisfed.org/docs/api/fred/series.html).

3. **Fetch the Metadata:** Use FredBrain's `fetch_series_info` method to retrieve metadata for your list of series IDs. Specify the fields of interest to tailor the information to your needs.

4. **Convert to DataFrame and Save:** Organize the fetched metadata into a pandas DataFrame for easy analysis and manipulation. Optionally, you can save this DataFrame to an Excel file for offline access or further processing.

Here's an example code snippet that demonstrates these steps:

```python
# Define the metadata fields of interest
relevant_info = [
    'id', "realtime_start", "realtime_end", 'title', 'frequency', 'units',
    "seasonal_adjustment", "last_updated", 'popularity', 'notes'
]

# Fetch the series metadata
series_info_data = fred.fetch_series_info(series_ids=series_list, relevant_info=relevant_info)

# Convert the metadata into a DataFrame
series_information = pd.DataFrame(series_info_data)

# Save the DataFrame to an Excel file for further analysis
series_information.to_excel("series_information.xlsx")
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

## Step 4: Extract Unrevised, Revised and All Data Releases for Each Series
Having pinpointed the relevant series IDs, we now advance to the critical task of gathering the data in its various states: initial unrevised, latest revised, and all releases respectively while leveraging concurrent futures to optimize the retrieval process and cut down on the time required to fetch the data. This step is pivotal for conducting thorough analyses, particularly in areas requiring precise historical accuracy such as economic modeling or predictive analytics.

### Understanding the Importance of Data Variants

- **Unrevised Data:** Essential for analyses that aim to replicate the conditions and knowledge available at the time the data was first released. This approach helps prevent look-ahead bias, ensuring the predictions or models don't inadvertently incorporate future information not available at the original time of forecasting.
  
- **Revised Data:** Offers the most up-to-date version of the data, incorporating any corrections or updates made after the initial release. Vital for analyses that require the most accurate and current data.

- **All Releases:** Provides a comprehensive view by including every version of the data released, allowing for an in-depth study of how data estimates have evolved over time.

### Why Differentiate Unrevised from Revised Data?
In applications such as economic modeling or predictive analysis, it is important to mitigate any potential look-ahead bias. Look-ahead bias occurs when a model inadvertently uses information that was not available at the time of prediction, leading to overfitting and unrealistic performance estimates. By utilizing unrevised data, we ensure our analyses reflect the state of knowledge available at each observation's original reporting time, maintaining the integrity of our predictive efforts. Therefore, we can extract a `DataFrame` of unrevised, revised, and all releases for each series.
## Implementation
Between executing each method, we need to let the system rest for 60 seconds to ensure the rate limit of 120 requests per minute is not exceeded. These methods are wrapped by a RateLimitDecorator to ensure that the rate limit is not exceeded while looping through the Series IDs.
Additionally, a unique Hash Key is generated automatically for each row to be used later for database insertion and to ensure data integrity and no insertion of duplicate data.
```sh
print("Sleeping for 60 seconds before continuing to ensure rate limit is not exceeded as method was previously called.")
time.sleep(60)
collected_first_releases = fred.retrieve_series_first_release(series_ids=series_list)
collected_first_releases.to_excel("first_releases.xlsx")

print("Sleeping for 60 seconds before continuing to ensure rate limit is not exceeded as method was previously called.")
time.sleep(60)
collected_latest_releases = fred.retrieve_series_latest_release(series_ids=series_list)
collected_latest_releases.to_excel("latest_releases.xlsx")

print("Sleeping for 60 seconds before continuing to ensure rate limit is not exceeded as method was previously called.")
time.sleep(60)
collected_all_releases = fred.retrieve_series_all_releases(series_ids=series_list)
collected_all_releases.to_excel("all_releases.xlsx")
```
## Step 5: Insert the DataFrame into a MySQL Database for seamless storage
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

Additionally, for a cloud MySQL database, you can use services such as Amazon RDS, Google Cloud SQL, or Azure Database for MySQL. I currently use Goggle Cloud SQL for my MySQL database. 
```sh
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

# Initialize the database manager and connect to MySQL
db_manager = MySQLBrain(host, user, passwd, db_name=db)
db_manager.list_databases()  # Optional: List all existing databases to verify the connection
db_manager.check_create_database(db_name)  # Create the database if it doesn't exist
```
### Inserting DataFrame into the Database
With your data now structured in DataFrames and your database connection established, the next step is to insert this data into your database. This process involves specifying the destination table within your database and handling the DataFrame structure to ensure data is stored correctly.

Preparing for Insertion
1. Table Specification: Identify or define the table name where the data will be stored. If the specified table doesn't exist in your database, it will be automatically created to match the structure of your DataFrame.

2. Chunked Insertion: To prevent SQL timeout errors and enhance the efficiency of the data insertion process, data rows are inserted in chunks of 10,000. This approach ensures a smooth and efficient transfer of data into your database.

3. Automated Table Creation: The fred_create_table_sql method is designed to automatically generate a SQL table that mirrors the structure of your DataFrame, facilitating a seamless integration of FRED data into your database.

Executing the Insertion
```sh
# Insert the DataFrames into the MySQL database
db_manager.fred_create_table_sql(df=collected_first_releases, table_name="FirstReleases")
db_manager.fred_create_table_sql(df=collected_latest_releases, table_name="LatestReleases")
db_manager.fred_create_table_sql(df=collected_all_releases, table_name="AllReleases")
```
Congratulations! Your DataFrame is now stored in the specified MySQL database, making it accessible for future queries and analysis directly from SQL Workbench or any MySQL client.
## Step 6: Inserting new data into the existing MySQL Table
If you have new data that you want to append to an existing MySQL table, you can use the `fred_insert_data_sql` method to insert the new data into the table. This method will automatically only insert unique rows based on the hash key, ensuring that no duplicate data is added to the existing table. This allows you to seamlessly add new rows from a new FRED series or updated data from an existing series to your MySQL table.
```sh
db_manager.insert_new_rows( df=collected_first_releases, table_name="First Releases")
```
## Step 7: Input the DataFrame into OpenAI (GPT-4) for insights
The `DataFrame` from before can be inputted into the chatgpt method and a prompt of your choosing can be tailored. This will result in an output given by chatgpt based on the prompt and data provided
```sh
# Assuming this method returns a DataFrame
analysis = fred.analyze_with_chatgpt(all_data_observations, "Provide a summary of the key trends in this economic data.")
print(analysis)
```

Congratulations! You now have Federal Reserve Economic data stored in a Database and an LLM Powered Economist at your fingertips! Who knows what the world will have in store for you two!
![img.png](img.png)
![img_1.png](img_1.png)