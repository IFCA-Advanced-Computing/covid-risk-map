COVID-19 Risk Map
==============================

COVID-19 risk map based on mobility and socio-demographic data.

# Workflow

## Generate the data

1. Use the [dacot](https://github.com/IFCA/dacot) package to generate the `province_flux_intra.csv` and `province_flux_inter.csv` files. Copy them to the `data/raw` folder in this package.
   Remove `data/interim/province_flux_by_destination.csv` (if present) so that the mobility dataset is generated afresh in the next step.
2. Run `make data` to generate the additional data needed to plot everything (that is the covid cases that are updated weekly by the Health Ministry).

After running step 2, `data/processed` will have the following files:
* `cantabria-incidence.csv`: covid cases in Cantabria, by municipalities, for the most recent date
* `provinces.csv`: covid cases for all provinces, for all dates. Cases are divided in:
  - `cases new`: newly diagnosed cases
  - `cases acc`: cumsum of cases since the start of the pandemic
  - `cases inc`: increment of changes, porcentual changes in accumulated cases
  - `incidence X`: new cases per 100K persons, summed over last X days
* `provinces-mobility.csv`: previous info + mobility between provinces, for all dates. Columns indicate the provinces where the trip starts, the rows the province where the trips end.
* `provinces-mobility-incidence.csv`: previous info + incidence in origin province, for all dates. Columns indicate the provinces where the trip starts (origin), the rows the province where the trips end (destination). 
 Each province column is divided in three, as a Pandas multiindex dataframe. For example `Zamora` has:
  - `Zamora`: flux coming from Zamora (in persons)
  - `Zamora.1`: incidence at 14 days in Zamora 
  - `Zamora.2`: incidence at 7 days in Zamora
 
## Generate the maps

3. Go to [Mapbox](https://www.mapbox.com/) and open a free account to get a mapbox token. Run:
`export MAPBOX_TOKEN="your_mapbox_token"` to set it as an environment variable.
4. Run `make visualize`. This will directly open the maps in your browser. Scroll down the webpage to the different plots.

# Project Organization

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
