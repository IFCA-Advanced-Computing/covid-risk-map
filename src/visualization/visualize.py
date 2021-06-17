import json
import pathlib

from dotenv import find_dotenv, load_dotenv
import pandas
import plotly


def main(data_dir):
    incidence = pandas.read_csv(
        data_dir / "processed" / "cantabria-incidence.csv"
    )

    with open(data_dir / "external" / "municipios-cantabria.geojson", "r") as f:
        municipalities = json.load(f)

    fig = plotly.graph_objects.Figure(
        plotly.graph_objects.Choroplethmapbox(
            geojson=municipalities,
            featureidkey="properties.COD_INE",
            locations=incidence["Codigo"],
            z=incidence["Casos"],
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
        mapbox_style="carto-positron",
        mapbox_zoom=9,
        mapbox_center={
            "lat": 43.16513048333179,
            "lon": -3.8942754858409394
        },
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.show()


if __name__ == '__main__':

    # not used in this stub but often useful for finding various files
    project_dir = pathlib.Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main(project_dir / "data")
