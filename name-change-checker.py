import json
from datetime import datetime

import pandas as pd
import requests

# UUID of the open data set 'Official titles of Government of Canada departments and agencies'
# https://open.canada.ca/data/en/dataset/83320390-7715-43bc-a281-2049bf5d4232/resource/f0ca63e0-c15e-45b5-9656-77abe1564b1c
UUID_OFFICIAL_TITLES = "f0ca63e0-c15e-45b5-9656-77abe1564b1c"
CSV_PATH = 'data/official_titles.csv'  # Where is the resulting CSV saved

def get_opendata(uuid: str, limit: int = 9999) -> pd.DataFrame:
  
  """Get data from the Open Government Portal
    https://search.open.canada.ca/opendata/
    
    Args:
        uuid: unique identifier of dataset as per Open Government
    Returns:
        requested data set as a dataframe

  """ 
  
  # Get the dataset using the CKAN API
  api_url = f'https://open.canada.ca/data/en/api/3/action/datastore_search?resource_id={uuid}&limit={limit}'  
  response = requests.get(api_url)
  json_resp = json.loads(response.text)
    
  return pd.DataFrame.from_dict(json_resp['result']['records'])
  
def append_to_readme(
  df: pd.DataFrame, 
  template_path: str = 'README_template.md', 
  output_path: str = 'README.md'
  ) -> None:
  
  """Appends a dataframe to the end of the README.md file, formatted as Markdown
    
    Args:
        df: dataframe to print
        template_path: the first part of the readme, without the appended table
        output_path: path to write the readme to
    Returns:
        None

  """ 
  
  df.fillna({'Footnote':'', 'Note de bas de page':''}, inplace=True)  # Replace NA with empty string
  with open(output_path, 'w') as readme:
    with open(template_path) as template:
      for line in template:
        readme.write(line)
        
    readme.write('\n\n')
    readme.write('## Most Recent Changes\n')
    readme.write('Last changed:' + datetime.now().strftime("%b %d, %Y at %H:%M %z"\n))
    readme.write(df.to_markdown())
    
    return None
    


if __name__ == "__main__":
   
    old = pd.read_csv(CSV_PATH, encoding='Windows-1252')  # Open the dataset as it was the last time we saw it
    new = get_opendata(UUID_OFFICIAL_TITLES)              # Get the dataset from Open Government
    
    merged = pd.merge(old, new, how='outer', indicator=True)
    
    # Rows that aren't in both the old and the new
    changes = merged[merged['_merge'] != "both"].set_index('_id')

    if not changes.empty:
      print("Found some changes")
      # Add the latest changes to the README.md file
      append_to_readme(df=changes, template_path='README_template.md', output_path='README.md')
      
       # Write the new file to a CSV
      new.to_csv(CSV_PATH, encoding='Windows-1252', index=False) 
      
    print("All done!")
    
