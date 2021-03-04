"""
Use Dash to easily switch between different metrics while staying in the same plot

Add external style sheet?
# external CSS stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/dZVMbK.css',
]
app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets)
"""


import json
import os
import pathlib

import plotly
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dotenv import find_dotenv, load_dotenv
import pandas as pd


def main(data_dir, mapbox_access_token):

    # Load data
    incidence = pd.read_csv(
        data_dir / "processed" / "cantabria-incidence.csv"
    )

    with open(data_dir / "raw" / "municipios-cantabria.geojson", "r") as f:
        municipalities = json.load(f)

    cantabria_metrics = ['Activos', 'Curados', 'Casos', 'Fallecidos', 'incidence rel', 'incidence 100k']

    provinces = pd.read_csv(
        data_dir / "processed" / "provinces.csv"
    )

    spain_metrics = ['cases new (pcr)', 'cases acc (pcr)', 'cases inc (pcr)', 'incidence 7', 'incidence 14']

    # Define Dash app
    app = dash.Dash(__name__)

    app.layout = html.Div(children=[
        html.Div([
            html.H1(children='Covid Cases in Cantabria (yesterday)'),
            html.P("Metric:"),
            dcc.RadioItems(
                id='cantabria_metric',
                options=[{'value': x, 'label': x}
                         for x in cantabria_metrics],
                value=cantabria_metrics[2],
                labelStyle={'display': 'inline-block'}
            ),
            dcc.Graph(id="choropleth_cantabria", style={"height": "100vh"}),
            ]),
        html.Div([
            html.H1(children='Daily Covid cases in Spain (averaged by week)'),
            html.P("Metric:"),
            dcc.RadioItems(
                id='spain_metric',
                options=[{'value': x, 'label': x}
                         for x in spain_metrics],
                value=spain_metrics[-1],
                labelStyle={'display': 'inline-block'}
            ),
            dcc.Graph(id="covid_spain", style={"height": "100vh"}),
        ]),
    ])

    # Plot cases in Cantabria map (for yesterday)
    ############################################

    @app.callback(
        Output("choropleth_cantabria", "figure"),
        [Input("cantabria_metric", "value")])
    def display_choropleth(map_metric):
        fig = plotly.graph_objects.Figure(
            plotly.graph_objects.Choroplethmapbox(
                geojson=municipalities,
                featureidkey="properties.COD_INE",
                locations=incidence["Codigo"],
                z=incidence[map_metric],
                text=incidence['Municipio'],
                colorscale="Cividis",
                reversescale=True,
                showlegend=False,
                showscale=False,
                marker={
                    "line": {
                        "width": 0.1
                    },
                    "opacity": 0.5
                },
            )
        )

        fig.update_layout(
            title='COVID-19 Data (Cantabria)',
            autosize=True,
            mapbox_style="carto-positron",
            mapbox_accesstoken=mapbox_access_token,
            mapbox_zoom=9,
            mapbox_center={
                "lat": 43.16513048333179,
                "lon": -3.8942754858409394
            },
            margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )

        return fig

    # Plot daily cases in Spain (averaged by week)
    #############################################

    provinces['date'] = pd.to_datetime(provinces['date'])
    reg_output = pd.DataFrame()

    for region_id in set(provinces['region id']):
        reg = provinces.loc[provinces['region id'] == region_id]

        region = reg['region'].values[0]
        reg = reg.drop(['region id', 'province id'], 'columns')

        s = reg.resample(rule='W', on='date').mean()
        s = s.reset_index()
        s.insert(0, 'region id', region_id)
        s.insert(1, 'region', region)
        reg_output = pd.concat([reg_output, s], ignore_index=True)

    @app.callback(
        Output("covid_spain", "figure"),
        [Input("spain_metric", "value")])
    def update_line_chart(spain_metric):
        fig = px.line(reg_output, x='date', y=spain_metric, color='region')
        for d in fig.data:
            d.update(mode='markers+lines')
        return fig

    app.run_server(debug=True)


if __name__ == '__main__':

    # not used in this stub but often useful for finding various files
    project_dir = pathlib.Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main(project_dir / "data", os.environ["MAPBOX_TOKEN"])
