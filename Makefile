SHELL := /bin/bash

.DEFAULT_GOAL := help

.SHELLFLAGS := -eu -o pipefail -c

.ONESHELL:

.DELETE_ON_ERROR:

MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

AMBIT_FLAGS = --verbose
#AMBIT_FLAGS += --layouts=expertkit
#AMBIT_FLAGS += --config_paths=/path/to/*.plp
#AMBIT_FLAGS += --device=DEAD:BEEF
#AMBIT_FLAGS += --device_index=0
#AMBIT_FLAGS += --debug

SOURCES := ./ambit/ ./tools/ ./bin/ ./tests/


help:
	@echo -e "Available commands:\n"
	@sed -n '/^[a-zA-Z0-9_\-][a-zA-Z0-9_.\-]*:/s/:.*//p' < Makefile | sed 's/^/    /' | sort -u
	@echo
.PHONY: help


# VIRTUALENV

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


# EXTRACT

extract-assets: docs/captures/core-update-images.pcapng
	./tools/extract_reference_assets.sh docs/captures/core-update-images.pcapng ambit/resources/assets/reference/
.PHONY: extract-assets

ambit/resources/assets/%.raw: ambit/resources/assets/%.png out/make/virtual
	source ./venv/bin/activate && ./bin/ambit_image_convert $< $@

assets: ambit/resources/assets/23.raw ambit/resources/assets/24.raw ambit/resources/assets/25.raw
.PHONY: assets

extract-firmware: out/firmware/palette-firmware.hex
.PHONY: extract-firmware

out/firmware/palette-firmware.psh: docs/captures/firmware-update-push.pcapng
	mkdir -p $(@D)
	tshark -r $< -2 -T fields \
		-e usb.data_fragment -Y usb.data_fragment \
		-R 'usb.dst == "1.55.0" or usb.src == "1.55.0" and usb.bmRequestType == 0x21 and usb.data_fragment[0] == 0x01' \
		| sed 's/^.\{64\}//' | sed 's/.\{32\}$$//' | tr -d '\n' > $@

out/firmware/palette-firmware.bin: out/firmware/palette-firmware.psh
	xxd -r -ps < $< > $@

out/firmware/palette-firmware.hex: out/firmware/palette-firmware.bin
	./tools/bin_to_ihx.py $< $@

out/firmware/palette-firmware.asm: out/firmware/palette-firmware.hex
	avr-objdump -m avr:5 -s -j .sec1 -d $< > $@

out/firmware/palette-firmware.elf: out/firmware/palette-firmware.bin
	avr-objcopy -I binary -O elf32-avr $< $@


# SETUP

setup: virtual assets
.PHONY: setup

setup-dev: virtual assets deps-dev
.PHONY: setup-dev


# TEST

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

test-integration-slider_range: setup
	source ./venv/bin/activate && python3 tests/test_ambit.py AmbitIntegrationTest.test_slider_range_{broken,fixed}
.PHONY: test-integration-slider_range

test-integration-reference_meta: setup
	source ./venv/bin/activate && python3 tests/test_ambit.py AmbitIntegrationTest.test_reference_meta
.PHONY: test-integration-reference_meta

test-integration-multifunction_buttons: setup
	source ./venv/bin/activate && python3 tests/test_ambit.py AmbitIntegrationTest.test_multifunction_buttons
.PHONY: test-integration-multifunction_buttons

test-integration-behaviors: setup
	source ./venv/bin/activate && python3 tests/test_ambit.py AmbitIntegrationTest.test_behaviors
.PHONY: test-integration-behaviors

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


# PROFILE

benchmark: setup
	source ./venv/bin/activate && bin/ambit_benchmark $(AMBIT_FLAGS)
.PHONY: benchmark

profile-simulator: deps-dev setup
	mkdir -p ./out/mtprof/
	source ./venv/bin/activate && python3 -m mtprof -o ./out/mtprof/simulator.prof bin/ambit_simulator $(AMBIT_FLAGS)
	source ./venv/bin/activate && snakeviz ./out/mtprof/simulator.prof
.PHONY: profile-simulator

profile-test: deps-dev
	mkdir -p ./out/mtprof/
	source ./venv/bin/activate && python3 -m mtprof -o ./out/mtprof/test.prof tests/test_ambit.py
	source ./venv/bin/activate && snakeviz ./out/mtprof/test.prof
.PHONY: profile-test


# STATIC ANALYSIS

cloc:
	cloc --exclude-list-file=.gitignore .
.PHONY: cloc

lint: deps-dev
	source ./venv/bin/activate && mypy
.PHONY: lint


# GENERATE

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


# FLASHING

flash-reference-%: reference/firmware/firmware-%.hex
	dfu-programmer at90usb1286 erase
	dfu-programmer at90usb1286 flash $<
	dfu-programmer at90usb1286 launch
.PHONY: flash-reference-%

flash_teensy-reference-%: reference/firmware/firmware-%.hex
	teensy_loader_cli --mcu=at90usb1286 -v $<
.PHONY: flash_teensy-reference-%

flash: flash-reference-1.4.6136
.PHONY: flash

flash_teensy: flash_teensy-reference-1.4.6136
.PHONY: flash_teensy

flash-ledopt: flash-reference-1.3.1
.PHONY: flash-ledopt

flash_teensy-ledopt: flash_teensy-reference-1.3.1
.PHONY: flash_teensy-ledopt


# UTILITY

reboot_bootloader: setup
	source ./venv/bin/activate && bin/ambit_reboot_bootloader $(AMBIT_FLAGS)
.PHONY: reboot_bootloader

push_assets: setup
	source ./venv/bin/activate && bin/ambit_push_assets $(AMBIT_FLAGS)
.PHONY: push_assets

bin/ambit_console: bin/ambit_console_simulator setup
	./tools/convert_simulator_bin.sh console

console: bin/ambit_console setup-dev
	source ./venv/bin/activate && bin/ambit_console $(AMBIT_FLAGS)
.PHONY: console

console_simulator: setup-dev
	source ./venv/bin/activate && bin/ambit_console_simulator $(AMBIT_FLAGS)
.PHONY: console_simulator


# DEMOSCENE

bin/ambit_lightshow: bin/ambit_lightshow_simulator setup
	./tools/convert_simulator_bin.sh lightshow

lightshow: bin/ambit_lightshow setup
	source ./venv/bin/activate && bin/ambit_lightshow $(AMBIT_FLAGS)
.PHONY: lightshow

lightshow_simulator: setup
	source ./venv/bin/activate && bin/ambit_lightshow_simulator $(AMBIT_FLAGS)
.PHONY: lightshow_simulator

bin/ambit_lavalamp: bin/ambit_lavalamp_simulator setup
	./tools/convert_simulator_bin.sh lavalamp

lavalamp: bin/ambit_lavalamp setup
	source ./venv/bin/activate && bin/ambit_lavalamp $(AMBIT_FLAGS)
.PHONY: lavalamp

lavalamp_simulator: setup
	source ./venv/bin/activate && bin/ambit_lavalamp_simulator $(AMBIT_FLAGS)
.PHONY: lavalamp_simulator

bin/ambit_demoscene: bin/ambit_demoscene_simulator setup
	./tools/convert_simulator_bin.sh demoscene

demoscene: bin/ambit_demoscene setup
	source ./venv/bin/activate && bin/ambit_demoscene $(AMBIT_FLAGS)
.PHONY: demoscene

demoscene_simulator: setup
	source ./venv/bin/activate && bin/ambit_demoscene_simulator $(AMBIT_FLAGS)
.PHONY: demoscene_simulator


# MAP

map_hid: setup
	source ./venv/bin/activate && bin/ambit_map_hid --debug ./ambit/resources/configs/hidmap.plp $(AMBIT_FLAGS)
.PHONY: map_hid

map_midi: setup
	source ./venv/bin/activate && bin/ambit_map_midi $(AMBIT_FLAGS)
.PHONY: map_midi


# SIMULATOR

simulator: setup
	source ./venv/bin/activate && bin/ambit_simulator $(AMBIT_FLAGS)
.PHONY: simulator

simulator-showcase: setup
	source ./venv/bin/activate && bin/ambit_simulator --layouts=showcase $(AMBIT_FLAGS)
.PHONY: simulator-showcase

simulator-test_behaviors: setup
	source ./venv/bin/activate && bin/ambit_simulator --layouts=test-behaviors $(AMBIT_FLAGS)
.PHONY: simulator-test_behaviors


# START

start: setup
	source ./venv/bin/activate && bin/ambit $(AMBIT_FLAGS)
.PHONY: start

start-showcase: setup
	source ./venv/bin/activate && bin/ambit --layouts=showcase $(AMBIT_FLAGS)
.PHONY: start-showcase

start-test_behaviors: setup
	source ./venv/bin/activate && bin/ambit --layouts=test-behaviors $(AMBIT_FLAGS)
.PHONY: start-test_behaviors


# GUI

gui: setup
	source ./venv/bin/activate && bin/ambit_gui $(AMBIT_FLAGS)
.PHONY: gui

gui-showcase: setup
	source ./venv/bin/activate && bin/ambit_gui --layouts=showcase $(AMBIT_FLAGS)
.PHONY: gui-showcase

gui-test_behaviors: setup
	source ./venv/bin/activate && bin/ambit_gui --layouts=test-behaviors $(AMBIT_FLAGS)
.PHONY: gui-test_behaviors


# DIST

install:
	python3 -m pip install .
.PHONY: install

uninstall:
	python3 -m pip uninstall -y ambit
.PHONY: uninstall

bdist_wheel: deps-dev
	python3 setup.py sdist bdist_wheel
.PHONY: bdist_wheel

zipapp-dist:
	mkdir -p ./out/zipapp-dist/
	rm -rf ./out/zipapp-dist/
	python3 -m pip install . -r ./requirements.txt --target ./out/zipapp-dist/
.PHONY: zipapp-dist

out/zipapp/%: zipapp-dist
	mkdir -p $(@D)
	shiv -p "/usr/bin/env python3" --site-packages ./out/zipapp-dist/ --compressed -o $@ -c $(notdir $@)

publish: deps-dev bdist_wheel
	source ./venv/bin/activate && python3 -m twine upload dist/*
.PHONY: publish

publish-testpypi: deps-dev bdist_wheel
	source ./venv/bin/activate && python3 -m twine upload --repository testpypi dist/*
.PHONY: publish-testpypi

clean:
	rm -rf ./venv/
	rm -rf ./out/
	rm -rf ./ambit.egg-info/
	rm -rf .mypy_cache/
	rm -f ./.coverage
	rm -rf dist/ build/
.PHONY: clean

