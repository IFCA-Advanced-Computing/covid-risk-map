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

iso_map = {
    "C": "Coruña, A",
    "VI": "Araba/Álava",
    "AB": "Albacete",
    "A": "Alicante/Alacant",
    "AL": "Almería",
    "O": "Asturias",
    "AV": "Ávila",
    "BA": "Badajoz",
    "PM": "Balears, Illes",
    "B": "Barcelona",
    "BI": "Bizkaia",
    "BU": "Burgos",
    "CC": "Cáceres",
    "CA": "Cádiz",
    "S": "Cantabria",
    "CS": "Castellón/Castelló",
    "CE": "Ceuta",
    "CR": "Ciudad Real",
    "CO": "Córdoba",
    "CU": "Cuenca",
    "SS": "Gipuzkoa",
    "GI": "Girona",
    "GR": "Granada",
    "GU": "Guadalajara",
    "H": "Huelva",
    "HU": "Huesca",
    "J": "Jaén",
    "LO": "Rioja, La",
    "GC": "Palmas, Las",
    "LE": "León",
    "L": "Lleida",
    "LU": "Lugo",
    "M": "Madrid",
    "MA": "Málaga",
    "ML": "Melilla",
    "MU": "Murcia",
    "NA": "Navarra",
    "NC": "Navarra",  # this is region's iso code, which appears by error in raw data of provinces
    "OR": "Ourense",
    "P": "Palencia",
    "PO": "Pontevedra",
    "SA": "Salamanca",
    "TF": "Santa Cruz de Tenerife",
    "SG": "Segovia",
    "SE": "Sevilla",
    "SO": "Soria",
    "T": "Tarragona",
    "TE": "Teruel",
    "TO": "Toledo",
    "V": "Valencia/València",
    "VA": "Valladolid",
    "ZA": "Zamora",
    "Z": "Zaragoza",
}


def add_province_info(df_orig, df_prov):
    df_orig.insert(1, "province id", 0)
    df_orig.insert(2, "province", 0)
    df_orig.insert(3, "region id", 0)
    df_orig.insert(4, "region", 0)

    # Homogenize codes, names, etc. using INE data
    df_orig["province"] = df_orig["province iso"].apply(iso_map.get)

    for p in df_orig["province"].unique():
        # print("-", p)
        df_orig.loc[
            df_orig["province"] == p,
            ("province id", "region", "region id")
        ] = (
            df_prov.loc[df_prov["provincia"] == p][
                ["id provincia", "autonomia", "id auto"]
            ].values[0]
        )

    del df_orig['province iso']
