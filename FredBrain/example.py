from FredBrain import FredBrain
import os
import pandas as pd

FRED_KEY = os.environ.get("fred_api_key")
OPENAI_KEY = os.environ.get("openai_api_key")

fred = FredBrain(fred_api_key=FRED_KEY)

search_attributes = ["popularity", "frequency"]
search_values = [50, "Monthly"]
search_output_labor = fred.search_brain("Labor", search_attributes, search_values)
search_output_employment = fred.search_brain("Employment", search_attributes, search_values)
search_output_wages = fred.search_brain("Wages", search_attributes, search_values)
search_output_combined = pd.concat([search_output_labor, search_output_employment, search_output_wages],
                                   ignore_index=True)

series_list = list(search_output_combined['id'])
relevant_info = ['title', 'frequency', 'units', 'popularity', 'notes']
series_info_data = []
for item in series_list:
    series_info_data.append(fred.fetch_series_info(series_id=item, relevant_info=relevant_info))
series_information = pd.DataFrame(series_info_data)

# Initialize empty DataFrames to collect data
collected_first_releases = pd.DataFrame()

for i, item in enumerate(series_list):
    first_release = fred.retrieve_series_first_release(series_id=item)
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
        for df in [first_release]:
            for key, value in metadata.items():
                df[key] = value
        collected_first_releases = pd.concat([collected_first_releases, first_release], ignore_index=True)
    else:
        print(f"No data available for series {item}.")


print(collected_first_releases)

# Assuming this method returns a DataFrame
#analysis = fred.analyze_with_chatgpt(all_data_observations, "Provide a summary of the key trends in this economic data.")
#print(analysis)
