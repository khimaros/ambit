SHELL := /bin/bash

.SHELLFLAGS := -eu -o pipefail -c

.ONESHELL:

.DELETE_ON_ERROR:

MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

SOURCES := ./ambit/ ./tools/ ./bin/ ./tests/

help:
	@echo -e "Available commands:\n"
	@sed -n '/^[a-zA-Z0-9_\-][a-zA-Z0-9_.\-]*:/s/:.*//p' < Makefile | sed 's/^/    /' | sort -u
	@echo

venv/bin/activate:
	python3 -m venv ./venv

out/make/deps: venv/bin/activate requirements.txt
	mkdir -p $(@D)
	source ./venv/bin/activate && python3 -m pip install -Ir ./requirements.txt
	touch $@

deps: out/make/deps
.PHONY: deps

out/make/deps-dev: requirements-dev.txt out/make/deps
	mkdir -p $(@D)
	source ./venv/bin/activate && python3 -m pip install -Ir $<
	touch $@

deps-dev: out/make/deps-dev
.PHONY: deps-dev

out/make/virtual: out/make/deps
	mkdir -p $(@D)
	source ./venv/bin/activate && python3 -m pip install -e .
	touch $@

virtual: out/make/virtual
.PHONY: virtual

example/assets/%.raw: example/assets/%.png out/make/virtual
	source ./venv/bin/activate && ./bin/ambit_image_convert $< $@

assets: example/assets/23.raw example/assets/24.raw example/assets/25.raw
.PHONY: assets

setup: virtual assets
.PHONY: setup

test: setup
	source ./venv/bin/activate && python3 tests/test_ambit.py
.PHONY: test

test-integration: setup
	source ./venv/bin/activate && python3 tests/test_ambit.py AmbitIntegrationTest
.PHONY: test-integration

test-integration-configure_images: setup
	source ./venv/bin/activate && python3 tests/test_ambit.py AmbitIntegrationTest.test_configure_images
.PHONY: test-integration-configure_images

test-integration-layout_query: setup
	source ./venv/bin/activate && python3 tests/test_ambit.py AmbitIntegrationTest.test_layout_query
.PHONY: test-integration-layout_query

test-integration-layout_changed: setup
	source ./venv/bin/activate && python3 tests/test_ambit.py AmbitIntegrationTest.test_layout_changed
.PHONY: test-integration-layout_changed

test-integration-reference_meta: setup
	source ./venv/bin/activate && python3 tests/test_ambit.py AmbitIntegrationTest.test_reference_meta
.PHONY: test-integration-reference_meta

test-integration-layout1: setup
	source ./venv/bin/activate && python3 tests/test_ambit.py AmbitIntegrationTest.test_layout1
.PHONY: test-integration-layout1

test-integration-layout2: setup
	source ./venv/bin/activate && python3 tests/test_ambit.py AmbitIntegrationTest.test_layout2
.PHONY: test-integration-layout2

test-integration-layout4: setup
	source ./venv/bin/activate && python3 tests/test_ambit.py AmbitIntegrationTest.test_layout4
.PHONY: test-integration-layout4

test-integration-layout5: setup
	source ./venv/bin/activate && python3 tests/test_ambit.py AmbitIntegrationTest.test_layout5
.PHONY: test-integration-layout5

test-message: setup
	source ./venv/bin/activate && python3 tests/test_ambit.py AmbitMessageTest
.PHONY: test-message

test-coordinates: setup
	source ./venv/bin/activate && python3 tests/test_ambit.py AmbitCoordinatesTest
.PHONY: test-coordinates

test-image: setup
	source ./venv/bin/activate && python3 tests/test_ambit.py AmbitImageTest
.PHONY: test-image

test-simulator: setup
	source ./venv/bin/activate && python3 tests/test_ambit.py AmbitSimulatorTest
.PHONY: test-simulator

test-prof: deps-dev
	mkdir -p ./out/mtprof/
	source ./venv/bin/activate && python3 -m mtprof -o ./out/mtprof/test.prof tests/test_ambit.py
	source ./venv/bin/activate && snakeviz ./out/mtprof/test.prof
.PHONY: test-prof

cloc:
	cloc --exclude-list-file=.gitignore .
.PHONY: cloc

lint: deps-dev
	source ./venv/bin/activate && mypy
.PHONY: lint

docs:
	mkdir -p ./out/docs/
	source ./venv/bin/activate && pyreverse3 -Amy ambit -p ambit
	mv classes_ambit.dot packages_ambit.dot ./out/docs/
	dot -Tsvg ./out/docs/classes_ambit.dot > ./out/docs/classes_ambit.svg
	dot -Tsvg ./out/docs/packages_ambit.dot > ./out/docs/packages_ambit.svg
.PHONY: docs

coverage-report: deps-dev setup
	mkdir -p ./out/coverage/
	coverage run --source=. --omit=./setup.py --branch -m unittest tests/test_ambit.py
	coverage html --show-contexts -d ./out/coverage/htmlcov/
	coverage report
	xdg-open ./out/coverage/htmlcov/index.html
.PHONY: coverage-report

benchmark: setup
	source ./venv/bin/activate && bin/ambit_benchmark
.PHONY: benchmark

bin/ambit_lightshow: bin/ambit_lightshow_simulator setup
	./tools/convert_simulator_bin.sh lightshow

lightshow: bin/ambit_lightshow setup
	source ./venv/bin/activate && bin/ambit_lightshow
.PHONY: lightshow

lightshow-gui: setup
	source ./venv/bin/activate && bin/ambit_lightshow_gui
.PHONY: lightshow-gui

lightshow_simulator: setup
	source ./venv/bin/activate && bin/ambit_lightshow_simulator
.PHONY: lightshow_simulator

bin/ambit_lavalamp: bin/ambit_lavalamp_simulator setup
	./tools/convert_simulator_bin.sh lavalamp

lavalamp: bin/ambit_lavalamp setup
	source ./venv/bin/activate && bin/ambit_lavalamp
.PHONY: lavalamp

lavalamp_simulator: setup
	source ./venv/bin/activate && bin/ambit_lavalamp_simulator
.PHONY: lavalamp_simulator

bin/ambit_demoscene: bin/ambit_demoscene_simulator setup
	./tools/convert_simulator_bin.sh demoscene

demoscene: bin/ambit_demoscene setup
	source ./venv/bin/activate && bin/ambit_demoscene
.PHONY: demoscene

demoscene_simulator: setup
	source ./venv/bin/activate && bin/ambit_demoscene_simulator
.PHONY: demoscene_simulator

map_hid: setup
	source ./venv/bin/activate && bin/ambit_map_hid --debug ./example/configs/hidmap.plp
.PHONY: map_hid

map_midi: setup
	source ./venv/bin/activate && bin/ambit_map_midi
.PHONY: map_midi

push_assets: setup
	source ./venv/bin/activate && bin/ambit_push_assets
.PHONY: push_assets

simulator: setup
	source ./venv/bin/activate && bin/ambit_simulator --verbose
.PHONY: simulator

simulator-prof: deps-dev setup
	mkdir -p ./out/mtprof/
	source ./venv/bin/activate && python3 -m mtprof -o ./out/mtprof/simulator.prof bin/ambit_simulator --verbose
	source ./venv/bin/activate && snakeviz ./out/mtprof/simulator.prof
.PHONY: simulator-prof

simulator-layout1: setup
	source ./venv/bin/activate && bin/ambit_simulator ./example/configs/layout1/*.plp
.PHONY: simulator-layout1

simulator-layout2: setup
	source ./venv/bin/activate && bin/ambit_simulator ./example/configs/layout2/*.plp
.PHONY: simulator-layout2

simulator-layout4: setup
	source ./venv/bin/activate && bin/ambit_simulator ./example/configs/layout4/*.plp
.PHONY: simulator-layout4

start: setup
	source ./venv/bin/activate && bin/ambit --verbose
.PHONY: start

start-gui: setup
	source ./venv/bin/activate && bin/ambit_gui --verbose
.PHONY: start-gui

start-debug: setup
	source ./venv/bin/activate && bin/ambit --verbose --debug
.PHONY: start-debug

start-layout1: setup
	source ./venv/bin/activate && bin/ambit ./example/configs/layout1/*.plp
.PHONY: start-layout1

start-layout2: setup
	source ./venv/bin/activate && bin/ambit ./example/configs/layout2/*.plp
.PHONY: start-layout2

start-layout2-gui: setup
	source ./venv/bin/activate && bin/ambit_gui ./example/configs/layout2/*.plp
.PHONY: start-layout2-gui

start-layout3: setup
	source ./venv/bin/activate && bin/ambit ./example/configs/layout3/*.plp
.PHONY: start-layout3

start-layout4: setup
	source ./venv/bin/activate && bin/ambit ./example/configs/layout4/*.plp
.PHONY: start-layout4

start-layout4-gui: setup
	source ./venv/bin/activate && bin/ambit_gui ./example/configs/layout4/*.plp
.PHONY: start-layout4-gui

start-layout5: setup
	source ./venv/bin/activate && bin/ambit ./example/configs/layout5/*.plp
.PHONY: start-layout5

start-layout5-gui: setup
	source ./venv/bin/activate && bin/ambit_gui ./example/configs/layout5/*.plp
.PHONY: start-layout5-gui

install:
	python3 -m pip install .
.PHONY: install

uninstall:
	python3 -m pip uninstall -y ambit
.PHONY: uninstall

publish: deps-dev
	source ./venv/bin/activate && python3 -m twine upload dist/*
.PHONY: publish

publish-testpypi: deps-dev
	source ./venv/bin/activate && python3 -m twine upload --repository testpypi dist/*
.PHONY: publish-testpypi

clean:
	rm -rf ./venv/
	rm -rf ./out/
	rm -rf ./ambit.egg-info/
	rm -rf .mypy_cache/
	rm -f ./.coverage
	rm -f example/assets/*.raw
.PHONY: clean

