.PHONY: clean data lint requirements sync_data_to_s3 sync_data_from_s3

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BUCKET = [OPTIONAL] your-bucket-for-syncing-data (do not include 's3://')
PROFILE = default
PROJECT_NAME = covid_risk_map
PYTHON_INTERPRETER = python3
VENV = .virtualenv
ACTIVATE_VENV = . $(VENV)/bin/activate

ifeq (,$(shell which conda))
HAS_CONDA=False
else
HAS_CONDA=True
endif

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python Dependencies inside virtualenv. Use "make -B requirements" to
## update the environment
requirements: $(VENV) test_environment

$(VENV):
	@echo ">>> Creating virtualenv under $(VENV)"
	$(PYTHON_INTERPRETER) -m pip install -q virtualenv
	$(PYTHON_INTERPRETER) -m virtualenv --python $(PYTHON_INTERPRETER) .virtualenv
	$(ACTIVATE_VENV); $(PYTHON_INTERPRETER) -m pip install -U pip setuptools wheel
	$(ACTIVATE_VENV); $(PYTHON_INTERPRETER) -m pip install -r requirements.txt

update-requirements:


## Make Dataset
data: requirements
#	mkdir data/output
#	dacot em2
#	dacot em3
#	mv data/output/* data/processed
#	rmdir data/output
	curl -o data/raw/province-population.csv "https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/2852.csv?nocab=1"
	curl -o data/raw/casos_tecnica_provincias.csv https://cnecovid.isciii.es/covid19/resources/casos_tecnica_provincia.csv
	curl -o data/raw/COVID19_municipalizado.csv https://serviweb.scsalud.es:10443/ficheros/COVID19_municipalizado.csv
	$(ACTIVATE_VENV); $(PYTHON_INTERPRETER) src/data/make_dataset.py data

## Visualize map (requires to set the MAPBOX_TOKEN variable in the .env file)
visualize: requirements
	$(ACTIVATE_VENV); $(PYTHON_INTERPRETER) src/visualization/visualize.py

## Delete all compiled Python files and remove virtualenv
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	rm -Rf $(VENV)

## Lint using flake8
lint:
	flake8 src

## Upload Data to S3
sync_data_to_s3:
ifeq (default,$(PROFILE))
	aws s3 sync data/ s3://$(BUCKET)/data/
else
	aws s3 sync data/ s3://$(BUCKET)/data/ --profile $(PROFILE)
endif

## Download Data from S3
sync_data_from_s3:
ifeq (default,$(PROFILE))
	aws s3 sync s3://$(BUCKET)/data/ data/
else
	aws s3 sync s3://$(BUCKET)/data/ data/ --profile $(PROFILE)
endif

## Test python environment is setup correctly
test_environment:
	$(ACTIVATE_VENV); $(PYTHON_INTERPRETER) test_environment.py

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################



#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
