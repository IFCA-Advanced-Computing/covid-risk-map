# Copyright (c) 2020 Spanish National Research Council
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import pathlib
import sys

import click
from dotenv import find_dotenv, load_dotenv
import numpy as np
import pandas as pd

from src.data import utils

log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fmt)
LOG = logging.getLogger(__name__)

FILES = [
    "raw/casos_tecnica_provincias.csv",
    "raw/province-population.csv",
    "external/provincias-ine.csv",
    "raw/province_flux.csv",
    # Mapping files
    "raw/municipios-cantabria.geojson",
    "raw/COVID19_municipalizado.csv",
    "raw/population-cantabria.csv",
]


def check_data(base_dir):
    LOG.info(f"Checking for needed data in '{base_dir}'")

    error = False
    for f in FILES:
        if not (path := pathlib.Path(base_dir / f)).exists():
            LOG.error(f"Cannot find '{path}'")
            error = True

    if error:
        sys.exit(1)


def read_population(base_dir):
    df = pd.read_csv(
        base_dir / "raw" / "province-population.csv",
        sep=";"
    )
    df = df.loc[
        (df["Sexo"] == "Total") &
        (df["Provincias"] != "Total") &
        (df["Periodo"] == 2019)
    ]
    df["province id"] = df["Provincias"].apply(lambda x: int(x.split()[0]))
    df["Total"] = df["Total"].apply(lambda x: int(x.replace(".", "")))
    df = df[["province id", "Total"]]

    return df


def calculate_incidence(df, base_dir):
    pop = read_population(base_dir)

    df = df.merge(
        pop,
        on="province id"
    )

    for w in (7, 14):
        df[f"incidence {w}"] = df.groupby("province")["cases new (pcr)"].apply(lambda x: x.rolling(window=w).sum())  # noqa
        df[f"incidence {w}"] = (df[f"incidence {w}"] / df["Total"] * 100000).round().fillna(value=0).astype("int")  # noqa

    df = df.drop(columns="Total")
    return df


def prepare_dataset(base_dir):
    df = pd.read_csv(
        base_dir / "raw" / "casos_tecnica_provincias.csv",
        keep_default_na=False
    )

    columns = ["province iso", "date",
               "cases new", "cases new (pcr)", "cases new (ac)",
               "cases new (ag)", "cases new (elisa)", "cases new (unk)"]
    df.columns = columns

    # Combine the 'NA' and 'NC' iso codes (both corresponding to Navarra)
    df = df.replace('NC', 'NA')
    df = df.groupby(['province iso', 'date']).sum().reset_index()

    # Only use the colums that we need
    columns = ["province iso", "date", "cases new (pcr)"]
    df = df[columns]
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")

    prov = pd.read_csv(
        base_dir / "external" / "provincias-ine.csv",
        sep=";"
    )

    utils.add_province_info(df, prov)

    cols = ["cases new (pcr)"]

    # Calculate cumulative cases
    new_cols = [i.replace("new", "acc") for i in cols]
    df[new_cols] = df.groupby('province id')[cols].cumsum()

    # Calculate cases increment in percentage
    cols = new_cols
    new_cols = [i.replace("acc", "inc") for i in cols]
    df[new_cols] = df.groupby(['province'])[cols].pct_change() * 100
    df[new_cols] = df[new_cols].fillna(value=0)

    # Now add incidence data
    df = calculate_incidence(df, base_dir)

    f = base_dir / "processed" / "provinces-incidence.csv"
    LOG.info(f"Writing province data to '{f}', {df.shape[0]} observations")
    df.to_csv(
        f,
        index=False,
    )

    # Now generate a dataset `aux_mob` that contains a column-based matrix of mobility
    # fluxes, with the rows the destination province, columns the origin.
    mob = pd.read_csv(
        base_dir / "raw" / "province_flux.csv",
        parse_dates=[0],
    )

    mob = mob.drop(columns=['province id destination', 'province id origin'])

    mob_inter = mob[mob['province origin'] != mob['province destination']]
    mob_intra = mob[mob['province origin'] == mob['province destination']]
    mob_intra = mob_intra.drop(columns=['province destination'])

    aux_mob = mob_inter.merge(
        df,
        left_on=["province origin", "date"],
        right_on=["province", "date"]
    )
    aux_mob = aux_mob.pivot(
        index=["date", "province destination"],
        columns="province origin",
        values=["incidence 7", "incidence 14", "flux"],
    ).reset_index()

    # Switch levels so that province is on top of flux and incidences
    aux_mob.columns = aux_mob.columns.swaplevel()

    # Add flux intra to incidence df
    df = df.merge(mob_intra,
                  left_on=["province", "date"],
                  right_on=["province origin", "date"]
                  )
    df = df.drop(columns='province origin')
    df = df.rename(columns={'flux': 'flux intra'})

    # Change df to multi index in order to join
    df.columns = pd.MultiIndex.from_product([df.columns, [""]])

    # Add incidence+flux intra info to province origin in `aux_mob`
    merged = df.merge(
        aux_mob,
        left_on=[("date", ""), ("province", "")],
        right_on=[("", "date"), ("", "province destination")]
    )

    merged = merged.drop(columns=[('', 'date'),
                                  ('', 'province destination')])
    merged = merged.sort_values(by=['province', 'date'])

    # Order columns
    cols = [
        ('date', ''),
        ('province', ''),
        ('province id', ''),
        ('region', ''),
        ('region id', ''),
        ('cases new (pcr)', ''),
        ('cases acc (pcr)', ''),
        ('cases inc (pcr)', ''),
        ('incidence 14', ''),
        ('incidence 7', ''),
        ('flux intra', ''),
    ]

    aux = list(set(merged) - set(cols))
    aux.sort()
    cols.extend(aux)
    merged = merged[cols]

    f = base_dir / "processed" / "provinces-incidence-mobility.csv"
    LOG.info("Writing province +  mobility data + incidence on origin to "
             f"'{f}', {merged.shape[0]} observations")
    merged.to_csv(
        f,
        index=False,
    )

    # View data summary
    u, c = np.unique(merged['province'], return_counts=True)
    med = np.median(c)
    print('Available data for each province:')
    print('#################################')
    for i, j in zip(u, c):
        print(f"{i}: {j} {'*' if j != med else ''}")


def calculate_incidence_cantabria(base_dir):
    pob = pd.read_csv(
        base_dir / "raw" / "population-cantabria.csv",
        sep=";",
        dtype={"Codigo": str},
    )

    df = pd.read_csv(
        base_dir / "raw" / "COVID19_municipalizado.csv",
        sep=";",
        dtype={"Codigo": str},
    )

    df = df.merge(pob, on=["Codigo"])
    df = df.drop(columns=['Ano', 'Municipio', 'Metrica'])  # remove useless columns
    # (Ano:census year, Municipio: duplicated with Municio, Metrica: Total census)
    df = df.rename(columns={'Municio': 'Municipio', 'Total': 'Poblacion'})

    df['incidence rel'] = df['Casos'] / df['Poblacion']
    df['incidence 100k'] = df['Casos'] * 100000 / df['Poblacion']

    # Add NaN data for the Macomunidad de Cabuerniga
    # We use zeros because Mapbox doesn't plot NaN/None data
    cabuer = pd.DataFrame(np.zeros_like(df[0:1]), columns=df.columns)
    k = ['Fecha', 'Codigo', 'Municipio']
    v = df.loc[0, 'Fecha'], 39000, 'Comunidad Campoo-Cabuerniga'
    cabuer.at[0, k] = v
    df = pd.concat([cabuer, df], axis=0, ignore_index=True)

    f = base_dir / "processed" / "cantabria-incidence.csv"
    df.to_csv(
        f,
        index=False)


@click.command()
@click.argument('base_dir', type=click.Path(exists=True))
def main(base_dir):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    LOG.info('making final data set from raw data')

    base_dir = pathlib.Path(base_dir)
    check_data(base_dir)

    prepare_dataset(base_dir)

    calculate_incidence_cantabria(base_dir)


if __name__ == '__main__':

    # not used in this stub but often useful for finding various files
    project_dir = pathlib.Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
