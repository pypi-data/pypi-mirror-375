
BUILD_DIR := ./dist

# tools
E := @echo
PYCODESTYLE := pycodestyle
PYCODESTYLE_FLAGS := --show-source --show-pep8 #--ignore=E501,E228,E722

AUTOPEP8 := autopep8
AUTOPEP8_FLAGS := --in-place

FLAKE8 := flake8
FLAKE8_FLAGS := --show-source  --ignore=E501,E228,E722

BANDIT := bandit
BANDIT_FLAGS := --format custom --msg-template \
    "{abspath}:{line}: {test_id}[bandit]: {severity}: {msg}"


HATCH := hatch



all: generate_parser




generate_parser:
	make -C ./cb_bsdl_parser/ generate_parser


test: generate_parser
	pytest -v -rP


build: generate_parser
	$(HATCH) build


install: build
	@pip install dist/cb_bsdl_parser*.whl --force-reinstall


deploy: build
	$(E) Uploading package to PyPI...
	twine upload dist/*

clean:
	make -C ./cb_bsdl_parser/ clean
	@rm -rf __pycache__
	@rm -rf */__pycache__

mr_proper: clean
	@rm -rf ./$(BUILD_DIR)