![Federal Reserve symbol](https://media.istockphoto.com/id/1308151210/photo/fed-federal-reserve-of-usa-sybol-and-sign.jpg?s=612x612&w=0&k=20&c=bO642TWIyj2hGte2WqW3CrWbd3DD3BA6TSRWzH6ocYg= "Federal Reserve")

# FredBrain: A Python Package for retrieving Federal Reserve Economic Data at Scale and feeding it to OpenAI
[FredBrain](https://pypi.org/project/FredBrain) is a Python package that offers a practical approach for accessing economic data from the Federal Reserve ([FRED API Documentation](https://fred.stlouisfed.org/docs/api/fred/)). It is built to assist those involved in economic research, financial analysis, and model development by providing a straightforward means of data retrieval. Additionally, it takes an experimental approach to integrating the OpenAI GPT framework into the class with the ultimate aim of creating an Ad-Hoc GPT economist expert to assist you in your analysis. Hence, why we refer to the class as `FredBrain`. The class itself will hopefully act as the Brain to power OpenAI Chat Completions. 

Utilizing familiar libraries such as `pandas`, `datetime`, `requests`, and  `openai` FredBrain facilitates the transformation of JSON responses into user-friendly `DataFrame` objects. This process is designed to be intuitive, allowing users to focus more on their analysis, less on data wrangling and to leverage OpenAI chat for analysis support and conclusions.

As FredBrain continues to develop, it seeks to maintain a balance between expanding its functionality and ensuring reliability. It strives to be a helpful resource for users who need to integrate economic data into their work, without being overwhelming or overly complex.

FredBrain invites you to streamline the way you interact with economic data, opening up possibilities for more focused research and insightful analyses.
## Things it does well
- Efficiently navigates through FRED's series data using single or multiple filters, enhancing the user's ability to pinpoint relevant datasets.
- Streamlines the discovery and selection of economic variables by fetching extensive subsets of FRED categories and their associated series.
- Equips users with tools to instantly convert series searches or category subsets into comprehensive datasets of original or revised time-series data.
- Offers the flexibility to fetch time-series data for pre-determined sets of series or categories without additional search requirements.
- Facilitates the extraction of metadata, preserving critical details about the time-series data for informed analysis.
- Optimized for scalability, complying with the Federal Reserve's API request limits, enabling extensive data retrieval within the threshold of 1000 requests per minute
- *Integrating OpenAI to create an economist GPT for providing additional insights on data extracted via the FredBrain
  
*This is experimental and not guaranteed to perform well. The ambition of myself and contributors would be to design a system that feeds data to a GPT to create an Economist GPT

## Installing FredBrain
Install the package using 
```sh
# or PyPI
pip install FredBrain
```
## Dependencies
- [Pandas](https://pypi.org/project/pandas/)
- [Datetime](https://docs.python.org/3/library/datetime.html)
- [Requests](https://pypi.org/project/requests/)
- [OpenAI](https://platform.openai.com/docs/libraries)
## License
[MIT License](https://github.com/AlexanderRicht/InvestmentResearch/blob/main/LICENSE.md)
## Contributing
All contributions and ideas are welcome
# A walk-through - From Search to Time-Series Data
## Step 1: Importing and getting our initial dataframe of FRED series IDs
The first thing we can do is import and then begin with a preliminary search to identify a series we want to extract. To do this, we need to import the FredBrain package and our api keys. API keys for FRED can be requested here [Fred API Keys](https://fredaccount.stlouisfed.org/apikeys). For OpenAI, keys can be created here [OpenAI API Keys](https://platform.openai.com/api-keys)
```sh
from FredBrain import FredBrain
from config import FRED_API_KEY, OPENAI_API_KEY
import pandas as pd

fred = FredBrain(fred_api_key=FRED_API_KEY, openai_api_key=OPENAI_API_KEY)
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

## Step 3: Extract the unrevised releases of data related to the series
Based on the series `DataFrame` we extracted before, we will loop through the given series ID, add the metadata extracted previously, and store the unrevised observation for each series in a `DataFrame`. Why unrevised? Well, if we intend to model or use the data for any predictive purposes, using revised data would incorporate look-ahead bias. Therefore, we want to retain the observations as they were reported based on the information that was known at that given time
```sh
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
```
## Step 4: Input the DataFrame into OpenAI (GPT-4) for insights
The `DataFrame` will be inputted into the chatgpt method and a prompt of your choosing can be tailored. This will result in an output given by chatgpt based on the prompt and data provided
```sh
# Assuming this method returns a DataFrame
analysis = fred.analyze_with_chatgpt(all_data_observations, "Provide a summary of the key trends in this economic data.")
print(analysis)
```

Congratulations! You now have a LLM Powered Economist at your finger-tips! Who knows what the world will have in store for you two!
![img.png](img.png)
![img_1.png](img_1.png)