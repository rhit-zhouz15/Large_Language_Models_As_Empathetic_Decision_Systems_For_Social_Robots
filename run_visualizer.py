from data_layer import load_from_json, create_df
from internal_state_visualization import create_app

# Loads internal state values form json and turns it into a dataframe that plotly can use to create subplots
def get_latest_state():
    return create_df(load_from_json())

if __name__=="__main__":
    app = create_app(get_latest_state)
    app.run(debug=True)