import json
import pandas as pd

# Writes internal state values into a json file
def write_to_json(data: dict):
    json_data = json.dumps(data)
    with open("internal_state.json", "w") as file:
        file.write(json_data)

# Loads the internal state values stored in a json file as a dictionary
def load_from_json():
    with open("internal_state.json", "r") as file:
        data = json.load(file)
    return data

# Create a dataframe using the dictionary loaded from the json file
def create_df(data: dict):
    df = pd.DataFrame(data)
    return df