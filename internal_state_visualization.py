from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
from data_layer import load_from_json
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def create_app(internal_state_retriever):

    app = Dash(__name__)

    # Requires Dash 2.17.0 or later
    # Creates the general page that will display a graph and updates it every second
    app.layout = [
        html.H1(children='Internal State Visualizer', style={'textAlign':'center'}),
        dcc.Interval(id="refresh", interval=1000, n_intervals=0),
        dcc.Graph(id='graph-content')
    ]
    # Controls what the graph takes as input and what is outputted on the graph
    @app.callback(
        Output('graph-content', 'figure'),
        Input('refresh', 'n_intervals')
    )

    # Where the data populating the subplots comes from and what is called when the page gets updated every second
    # Pulls data from a json file that contains the internal state parameters over the number of turns the 
    # learner has interacted with the system
    def update_graph(n_intervals):
        df = internal_state_retriever()
        if df.empty:
            return go.Figure()
        
        plot_df = df.reset_index().rename(columns={"index": "turn"})

        fig = make_subplots(
            rows=2, 
            cols=2,
            subplot_titles=("Valence", "Arousal", "Momentum", "Intensity")
        )

        metrics = [
            ("Valence", 1, 1),
            ("Arousal", 1, 2),
            ("Momentum", 2, 1),
            ("Intensity", 2, 2)
        ]

        for metric, row, col in metrics:
            fig.add_trace(
                go.Scatter(x=plot_df["turn"], y=plot_df[metric], name=metric, mode="lines+markers"),
                row=row,
                col=col
            )

        fig.update_xaxes(title_text="Turn")
        fig.update_yaxes(title_text="Value")

        fig.update_yaxes(row=1, col=1, range=[-1.1, 1.1])
        fig.update_yaxes(row=1, col=2, range=[-1.1, 1.1])
        fig.update_yaxes(row=2, col=1, range=[-1.1, 1.1])
        fig.update_yaxes(row=2, col=2, range=[-0.1, 1.1])
        fig.update_layout(height=1000, title_font=dict(size=20), showlegend=True, legend=dict(font=dict(size=18)))

        return fig
    
    return app