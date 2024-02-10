from FredBrain import FredBrain
from config import FRED_API_KEY, OPENAI_API_KEY
import pandas as pd

fred = FredBrain(fred_api_key=FRED_API_KEY, openai_api_key=OPENAI_API_KEY)

search_attributes = ["popularity", "frequency"]
search_values = [50, "Monthly"]
# Perform searches for different terms
search_output_labor = fred.search_brain("Labor", search_attributes, search_values)
search_output_employment = fred.search_brain("Employment", search_attributes, search_values)
search_output_wages = fred.search_brain("Wages", search_attributes, search_values)
# Append the results into a single DataFrame
search_output_combined = pd.concat([search_output_labor, search_output_employment, search_output_wages],
                                   ignore_index=True)
print(search_output_combined)

series_list = list(search_output_combined['id'])
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

print(all_data_observations)

# Assuming this method returns a DataFrame
analysis = fred.analyze_with_chatgpt(all_data_observations, "Provide a summary of the key trends in this economic data.")
print(analysis)
