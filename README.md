COVID-19 Risk Map
=================

COVID-19 risk map based on mobility and socio-demographic data.

# Workflow

## Generate the data

1. Use the [mitma-covid](https://github.com/IFCA/mitma-covid) repository to generate the `province_flux.csv` file. Copy it to the `data/raw` folder in this package. You can also use the [dacot](https://github.com/IFCA/dacot) repo if you want to use INE mobility data (with are sparser).
2. Run `make data` to generate the additional data needed to plot everything (that is the covid cases that are updated weekly by the Health Ministry).

After running step 2, `data/processed` will have the following files:
* `cantabria-incidence.csv`: covid cases in Cantabria, by municipalities, for the most recent date
* `provinces-incidence.csv`: covid cases for all provinces, for all dates. Cases are divided in:
  - `cases new`: newly diagnosed cases
  - `cases acc`: cumsum of cases since the start of the pandemic
  - `cases inc`: increment of changes, porcentual changes in accumulated cases
  - `incidence X`: new cases per 100K persons, summed over last X days
* `provinces-mobility-incidence.csv`: We add mobility info to the previous file. Columns indicate the provinces where the trip starts (origin), the rows the province where the trips end (destination). 
 Each province column (origins) is divided in three, as a Pandas multiindex dataframe. For example `Zamora` has:
  - `Zamora.0`: flux coming from Zamora (in persons)
  - `Zamora.1`: incidence at 14 days in Zamora 
  - `Zamora.2`: incidence at 7 days in Zamora 
    
  The origin's (`flux`, `inc 14`, `inc 7`) values where `origin=destination` have been set to `NaN` as this information is already present in the destination's (`flux intra`, `incidence 7`, `incidence 14`).
 
## Generate the maps

3. Go to [Mapbox](https://www.mapbox.com/) and open a free account to get a mapbox token. Run:
`export MAPBOX_TOKEN="your_mapbox_token"` to set it as an environment variable.
4. Run `make visualize`. This will directly open the maps in your browser. Scroll down the webpage to the different plots.
