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
    "BU": "Burgos",
    "CC": "Cáceres",
    "CA": "Cádiz",
    "S": "Cantabria",
    "CS": "Castellón/Castelló",
    "CE": "Ceuta",
    "CR": "Ciudad Real",
    "CO": "Córdoba",
    "CU": "Cuenca",
    "GI": "Girona",
    "SS": "Gipuzkoa",
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
    "ME": "Melilla",
    "MU": "Murcia",
    "NA": "Navarra",
    "NC": "Navarra",
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
    "BI": "Bizkaia",
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
