import os

os.environ['SDL_VIDEODRIVER'] = 'dummy'

import ambit
import ambit.controller
import ambit.coordinates
import ambit.fake
import ambit.image
import ambit.resources
import ambit.simulator

import glob
import io
import pygame
import time
import unittest
import unittest.mock

# Seconds to wait for input to register and settle.
TEST_INPUT_SETTLED_SECONDS = 0.25


class AmbitIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.ctrl = None

    def tearDown(self):
        if self.ctrl:
            self.ctrl.print_stats()
            self.ctrl.close()

    def test_reference_meta(self):
        ambit.FLAGS.debug = True
        ambit.FLAGS.verbose = False

        # configure the device behavior
        device = ambit.fake.Device('DEAD:BEEF', 'XYZ')

        # start with several components connected.
        device.components_connected(ambit.fake.LAYOUT_DEFAULT_EXPERTKIT)

        # run the simulation
        config = ambit.Configuration(['./reference/layouts/meta.plp'])
        ctrl = ambit.Controller(config, device)
        self.ctrl = ctrl
        ctrl.open()
        ctrl.connect()

        # initial state and layout
        ctrl.wait_for_layout()
        self.assertEqual(8, len(ctrl.layout.connected()))

        # Button / Switch profile
        device.input_pressed(6)
        device.input_released(6)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 2)
        self.assertEqual("META", device.handle.screen_string)

    def test_keepalive(self):
        ambit.FLAGS.debug = True
        ambit.FLAGS.verbose = False

        # configure the device behavior
        device = ambit.fake.Device('DEAD:BEEF', 'XYZ')

        # start with several components connected.
        device.components_connected(ambit.fake.LAYOUT_DEFAULT_EXPERTKIT)

        # run the simulation
        config = ambit.Configuration(['./reference/layouts/meta.plp'])
        ctrl = ambit.Controller(config, device)
        self.ctrl = ctrl
        ctrl.open()
        ctrl.connect()

        # initial state and layout
        ctrl.wait_for_layout()
        self.assertEqual(8, len(ctrl.layout.connected()))

        ctrl.wait()
        self.assertEqual(1, len(device.handle.messages['check']))

        # keepalive timeout reached when no user input
        time.sleep(ambit.controller.Controller.KEEPALIVE_TIMEOUT_SECONDS + 1)
        self.assertEqual(2, len(device.handle.messages['check']))

        # no keepalive when there is continuous user input
        for i in range(0, ambit.controller.Controller.KEEPALIVE_TIMEOUT_SECONDS + 1):
            ctrl.screen_string('CHECK: %d' % i)
            time.sleep(1)
        self.assertEqual(2, len(device.handle.messages['check']))

    def test_orientation_change(self):
        # TODO: need a test that loads a config with "orientation" defined as 180,
        # rotates another 90 for a final rotation of 270. the actionMap should
        # contain both uid based and query (incl. slot) based references and the
        # callbacks should still work correctly after rotation.
        pass

    def test_multifunction_buttons(self):
        ambit.FLAGS.debug = True
        ambit.FLAGS.verbose = False

        # configure the device behavior
        device = ambit.fake.Device('DEAD:BEEF', 'XYZ')

        # start with several components connected.
        device.components_connected(ambit.fake.LAYOUT_DEFAULT_EXPERTKIT)

        # run the simulation
        config = ambit.Configuration(ambit.resources.layout_paths('multifunction-buttons'))
        ctrl = ambit.Controller(config, device)
        self.ctrl = ctrl
        ctrl.open()
        ctrl.connect()

        # initial state and layout
        ctrl.wait_for_layout()
        self.assertEqual(8, len(ctrl.layout.connected()))
        self.assertEqual("META", device.handle.screen_string)
        self.assertEqual([0], device.handle.messages['screen_display'])

        # Dial / Change LED Colors
        device.input_rotation_left(2, 8)
        device.input_rotation_left(2, 8)
        device.input_rotation_left(2, 16)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 3)
        self.assertEqual("Green: 231", device.handle.screen_string)
        ctrl.wait()
        self.assertEqual({
            1: (255, 231, 255),
            2: (255, 231, 255),
            3: (255, 231, 255),
            4: (255, 231, 255),
            5: (255, 231, 255),
            6: (255, 231, 255),
            7: (255, 231, 255),
            8: (255, 231, 255),
        }, device.handle.leds)

        # Button / Switch profile (previous)
        device.input_pressed(6)
        device.input_released(6)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 2)
        self.assertEqual("HOME", device.handle.screen_string)

        # Button / Switch profile (next)
        device.input_pressed(8)
        device.input_released(8)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 2)
        self.assertEqual("META", device.handle.screen_string)
        device.input_pressed(8)
        device.input_released(8)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 2)
        self.assertEqual("HACK", device.handle.screen_string)

        # check for error conditions
        self.assertEqual(0, ctrl.failed_writes)
        self.assertEqual(0, ctrl.dropped_leds)
        self.assertEqual(0, ctrl.dropped_screen_strings)

    def test_multifunction_dial(self):
        ambit.FLAGS.debug = True
        ambit.FLAGS.verbose = False

        # configure the device behavior
        device = ambit.fake.Device('DEAD:BEEF', 'XYZ')

        # start with several components connected.
        device.components_connected(ambit.fake.LAYOUT_DEFAULT_EXPERTKIT)

        # run the simulation
        config = ambit.Configuration(ambit.resources.layout_paths('multifunction-dial'))
        ctrl = ambit.Controller(config, device)
        self.ctrl = ctrl
        ctrl.open()
        ctrl.connect()

        # initial state and layout
        ctrl.wait_for_layout()
        self.assertEqual(8, len(ctrl.layout.connected()))
        self.assertEqual("META", device.handle.screen_string)
        self.assertEqual([0], device.handle.messages['screen_display'])

        # Button / Select LED control
        device.input_pressed(8)
        device.input_released(8)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 2)
        self.assertEqual("Green", device.handle.screen_string)
        device.input_pressed(8)
        device.input_released(8)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 2)
        self.assertEqual("Blue", device.handle.screen_string)

        # Slider / Change LED colors
        device.input_slide_up(4, 4)
        device.input_slide_up(4, 16)
        device.input_slide_up(4, 128)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 3)
        self.assertEqual("Blue: 148", device.handle.screen_string)
        ctrl.wait()
        self.assertEqual({
            1: (255, 255, 148),
            2: (255, 255, 148),
            3: (255, 255, 148),
            4: (255, 255, 148),
            5: (255, 255, 148),
            6: (255, 255, 148),
            7: (255, 255, 148),
            8: (255, 255, 148),
        }, device.handle.leds)

        # Dial / Switch profile
        device.input_rotation_right(2, 8)
        device.input_rotation_right(2, 8)
        device.input_rotation_right(2, 16)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 3)
        self.assertEqual("HACK", device.handle.screen_string)

        # Button / Execute command (hello)
        device.input_pressed(5)
        device.input_released(5)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 2)
        self.assertEqual("UNIVERSE!", device.handle.screen_string)

        # Dial / Switch profile
        device.input_rotation_left(2, 16)
        device.input_rotation_left(2, 16)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 2)
        self.assertEqual("META", device.handle.screen_string)
        device.input_rotation_left(2, 16)
        device.input_rotation_left(2, 16)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 2)
        self.assertEqual("HOME", device.handle.screen_string)

        # Slider / Execute command (temperature)
        device.input_slide_up(7, 255)
        time.sleep(TEST_INPUT_SETTLED_SECONDS)
        self.assertEqual("TEMP: 80F", device.handle.screen_string)
        device.input_slide_down(7, 20)
        time.sleep(TEST_INPUT_SETTLED_SECONDS)
        self.assertEqual("TEMP: 77F", device.handle.screen_string)

        # Dial / Execute command (unlock)
        device.input_rotation_right(5, 16)
        device.input_rotation_right(5, 16)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 2)
        self.assertEqual("OPEN: 15m", device.handle.screen_string)

        # check for error conditions
        self.assertEqual(0, ctrl.failed_writes)
        self.assertEqual(0, ctrl.dropped_leds)
        self.assertEqual(0, ctrl.dropped_screen_strings)

    def test_behaviors(self):
        ambit.FLAGS.debug = True
        ambit.FLAGS.verbose = False

        # configure the device behavior
        device = ambit.fake.Device('DEAD:BEEF', 'XYZ')

        # start with several components connected.
        device.components_connected(ambit.fake.LAYOUT_DEFAULT_PROKIT)

        # run the simulation
        config = ambit.Configuration(ambit.resources.layout_paths('test-behaviors'))
        ctrl = ambit.Controller(config, device)
        self.ctrl = ctrl
        ctrl.open()
        ctrl.connect()

        # initial state and layout
        ctrl.wait_for_layout()
        # [0] Component attached: Base (1) 00000 (0, 0) - 0 - False ::
        # [0] Component attached: Dial (2) C4@ (0, -1) - 0 - False ::
        # [0] Component attached: Dial (3) D5o (1, -1) - 270 - False ::
        # [0] Component attached: Button (4) B$; (1, 0) - 180 - False ::
        # [0] Component attached: Button (5) 8S$ (1, 1) - 180 - False ::
        # [0] Component attached: Dial (6) 6pZ (0, -2) - 0 - False ::
        # [0] Component attached: Dial (7) 6RD (-1, -1) - 90 - False ::
        # [0] Component attached: Button (8) 8a4 (-1, 0) - 180 - False ::
        # [0] Component attached: Slider (9) 8W( (-2, 0) - 90 - True ::
        # [0] Component attached: Slider (10) 8V$ (-2, -2) - 0 - False ::
        # [0] Component attached: Slider (11) Ak~ (2, -1) - 270 - False ::
        # [0] Component attached: Dial (12) 6om (2, 1) - 180 - False ::
        # [0] Component attached: Slider (13) 8Uq (1, -2) - 0 - False ::
        # [0] Component attached: Button (14) 8R+ (-1, 1) - 180 - False ::
        # [0] Component attached: Dial (15) 6J@ (-2, 1) - 90 - False ::
        self.assertEqual(0, ctrl.layout.find_component(1).orientation)
        self.assertEqual(0, ctrl.layout.find_component(2).orientation)
        self.assertEqual(270, ctrl.layout.find_component(3).orientation)
        self.assertEqual(180, ctrl.layout.find_component(4).orientation)
        self.assertEqual(180, ctrl.layout.find_component(5).orientation)
        self.assertEqual(0, ctrl.layout.find_component(6).orientation)
        self.assertEqual(90, ctrl.layout.find_component(7).orientation)
        self.assertEqual(180, ctrl.layout.find_component(8).orientation)
        self.assertEqual(90, ctrl.layout.find_component(9).orientation)
        self.assertEqual(0, ctrl.layout.find_component(10).orientation)
        self.assertEqual(270, ctrl.layout.find_component(11).orientation)
        self.assertEqual(180, ctrl.layout.find_component(12).orientation)
        self.assertEqual(0, ctrl.layout.find_component(13).orientation)
        self.assertEqual(180, ctrl.layout.find_component(14).orientation)
        self.assertEqual(90, ctrl.layout.find_component(15).orientation)

        self.assertEqual((0,0), ctrl.layout.find_component(1).slot)
        self.assertEqual((0,-1), ctrl.layout.find_component(2).slot)
        self.assertEqual((1,-1), ctrl.layout.find_component(3).slot)
        self.assertEqual((1,0), ctrl.layout.find_component(4).slot)
        self.assertEqual((1,1), ctrl.layout.find_component(5).slot)
        self.assertEqual((0,-2), ctrl.layout.find_component(6).slot)
        self.assertEqual((-1,-1), ctrl.layout.find_component(7).slot)
        self.assertEqual((-1,0), ctrl.layout.find_component(8).slot)
        self.assertEqual((-2,0), ctrl.layout.find_component(9).slot)
        self.assertEqual((-2,-2), ctrl.layout.find_component(10).slot)
        self.assertEqual((2,-1), ctrl.layout.find_component(11).slot)
        self.assertEqual((2,1), ctrl.layout.find_component(12).slot)
        self.assertEqual((1,-2), ctrl.layout.find_component(13).slot)
        self.assertEqual((-1,1), ctrl.layout.find_component(14).slot)
        self.assertEqual((-2,1), ctrl.layout.find_component(15).slot)

        self.assertEqual(True, ctrl.layout.find_component(9).flip)
        self.assertEqual(False, ctrl.layout.find_component(10).flip)

        # [0] Bound callback pressed testAccumulate (ACCUMULATE) to component 6RD
        # [0] Bound callback rotation_left testAccumulate (ACCUMULATE) to component 6RD
        # [0] Bound callback rotation_right testAccumulate (ACCUMULATE) to component 6RD
        # [0] Bound callback released testCycle (CYCLE) to component 8a4
        # [0] Bound callback released testAccumulate (ACCUMULATE) to component 8R+
        # [0] Bound callback set testAccumulate (ACCUMULATE) to component 8V$
        # [0] Bound callback set testTrigger (TRIGGER) to component 8W(
        # [0] Bound callback rotation_left testCycle (CYCLE) to component 6J@
        # [0] Bound callback rotation_right testCycle (CYCLE) to component 6J@
        # [0] Bound callback rotation_left testDelta (DELTA) to component C4@
        # [0] Bound callback rotation_right testDelta (DELTA) to component C4@
        # [0] Bound callback pressed testTrigger (TRIGGER) to component 6pZ
        # [0] Bound callback rotation_left testAccumulate (ACCUMULATE) to component 6pZ
        # [0] Bound callback rotation_right testAccumulate (ACCUMULATE) to component 6pZ
        # [0] Bound callback pressed testTrigger (TRIGGER) to component D5o
        # [0] Bound callback set testTrigger (TRIGGER) to component D5o
        # [0] Bound callback set testDelta (DELTA) to component 8Uq
        # [0] Bound callback pressed testTrigger (TRIGGER) to component B$;
        # [0] Bound callback released testTrigger (TRIGGER) to component B$;
        # [0] Bound callback released testAccumulate (ACCUMULATE) to component 8S$
        # [0] Bound callback set testCycle (CYCLE) to component Ak~
        # [0] Bound callback set testAccumulate (ACCUMULATE) to component 6om

        # initial state and layout
        self.assertEqual(15, len(ctrl.layout.connected()))
        self.assertEqual("TEST", device.handle.screen_string)
        self.assertEqual([0], device.handle.messages['screen_display'])

        # Dial / ACCUMULATE
        device.input_rotation_left(7, 8)
        device.input_rotation_left(7, 8)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 2)
        self.assertEqual("A: -2", device.handle.screen_string)
        device.input_pressed(7)
        device.input_released(7)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 2)
        self.assertEqual("A: 998", device.handle.screen_string)
        device.input_rotation_right(7, 8)
        device.input_rotation_right(7, 8)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 2)
        self.assertEqual("A: 1000", device.handle.screen_string)

        # Slider / TRIGGER
        device.input_slide_up(9, 4)
        device.input_slide_up(9, 16)
        device.input_slide_up(9, 128)
        device.input_slide_up(9, 64)
        device.input_slide_up(9, 64)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 5)
        self.assertEqual("T: 255", device.handle.screen_string)

        # Slider / CYCLE
        device.input_slide_up(11, 255)
        time.sleep(TEST_INPUT_SETTLED_SECONDS)
        self.assertEqual("C: SIX", device.handle.screen_string)
        device.input_slide_down(11, 40)
        time.sleep(TEST_INPUT_SETTLED_SECONDS)
        self.assertEqual("C: FIVE", device.handle.screen_string)
        device.input_slide_down(11, 40)
        time.sleep(TEST_INPUT_SETTLED_SECONDS)
        self.assertEqual("C: FOUR", device.handle.screen_string)
        device.input_slide_down(11, 40)
        time.sleep(TEST_INPUT_SETTLED_SECONDS)
        self.assertEqual("C: THREE", device.handle.screen_string)
        device.input_slide_down(11, 40)
        time.sleep(TEST_INPUT_SETTLED_SECONDS)
        self.assertEqual("C: TWO", device.handle.screen_string)
        device.input_slide_down(11, 55)
        time.sleep(TEST_INPUT_SETTLED_SECONDS)
        self.assertEqual("C: ONE", device.handle.screen_string)

        # Button / TRIGGER
        device.input_pressed(4)
        time.sleep(TEST_INPUT_SETTLED_SECONDS)
        self.assertEqual("T: 1", device.handle.screen_string)
        device.input_released(4)
        time.sleep(TEST_INPUT_SETTLED_SECONDS)
        self.assertEqual("T: 0", device.handle.screen_string)

        # Button / CYCLE
        device.input_pressed(8)
        device.input_released(8)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 2)
        self.assertEqual("C: TWO", device.handle.screen_string)
        device.input_pressed(8)
        device.input_released(8)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 2)
        self.assertEqual("C: THREE", device.handle.screen_string)
        device.input_pressed(8)
        device.input_released(8)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 2)
        self.assertEqual("C: FOUR", device.handle.screen_string)
        device.input_pressed(8)
        device.input_released(8)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 2)
        self.assertEqual("C: FIVE", device.handle.screen_string)
        device.input_pressed(8)
        device.input_released(8)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 2)
        self.assertEqual("C: SIX", device.handle.screen_string)
        device.input_pressed(8)
        device.input_released(8)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 2)
        self.assertEqual("C: ONE", device.handle.screen_string)

        # screen reset timeout reached
        time.sleep(ambit.controller.Controller.SCREEN_RESET_SECONDS + 1)
        self.assertEqual("TEST", device.handle.screen_string)
        self.assertEqual(27, len(device.handle.messages['screen_string']))

        # check for error conditions
        self.assertEqual(0, ctrl.failed_writes)
        self.assertEqual(0, ctrl.dropped_leds)
        self.assertEqual(0, ctrl.dropped_screen_strings)

    def test_layout_query(self):
        ambit.FLAGS.debug = True
        ambit.FLAGS.verbose = False

        # configure the device behavior
        device = ambit.fake.Device('DEAD:BEEF', 'XYZ')

        # start with several components connected.
        device.components_connected(ambit.fake.LAYOUT_DEFAULT_EXPERTKIT)

        # run the simulation
        config = ambit.Configuration()
        ctrl = ambit.Controller(config, device)
        self.ctrl = ctrl
        ctrl.open()
        ctrl.connect()

        ctrl.wait_for_layout()

        self.assertEqual('49d', ctrl.layout.query('[kind=Dial | rowwise | select(2)]')[0].uid)
        self.assertEqual('49d', ctrl.layout.query('49d')[0].uid)
        self.assertEqual('4lf', ctrl.layout.query('[slot=(1,0)]')[0].uid)
        self.assertEqual('4}=', ctrl.layout.query('[kind=Slider orientation=270]')[0].uid)
        self.assertEqual('00000', ctrl.layout.query('[index=1]')[0].uid)
        self.assertEqual('4}=', ctrl.layout.query('[uid=4}=]')[0].uid)
        self.assertEqual(3, len(ctrl.layout.query('[kind=Dial]')))
        self.assertEqual(2, len(ctrl.layout.query('[orientation=90]')))

    def test_configure_images(self):
        ambit.FLAGS.debug = True
        ambit.FLAGS.verbose = True

        # configure the device behavior
        device = ambit.fake.Device('DEAD:BEEF', 'XYZ')

        # start with several components connected.
        device.components_connected(ambit.fake.LAYOUT_DEFAULT_EXPERTKIT)

        # run the simulation
        config = ambit.Configuration()
        config.profile.icon = ambit.Configuration.ICON_PALETTE
        ctrl = ambit.Controller(config, device)
        self.ctrl = ctrl
        ctrl.open()
        ctrl.connect()

        # Ensure that we don't write any screen images when components are connected.
        ctrl.wait_for_layout()
        ctrl.configure_images()
        self.assertEqual({}, device.handle.screen_images)

        device.layout_changed(ambit.fake.LAYOUT_BASE_ONLY)

        time.sleep(TEST_INPUT_SETTLED_SECONDS)

        # When the base only is connected, check that the bytes match file data.
        ctrl.wait_for_layout()
        ctrl.configure_images()

        time.sleep(TEST_INPUT_SETTLED_SECONDS)

        self.assertEqual(3, len(device.handle.screen_images))

        for index in (23, 24, 25):
            with ambit.resources.asset_file(index) as f:
                image_bytes = f.read()
            self.assertEqual(image_bytes, device.handle.screen_images[index])

    def test_layout_changed(self):
        ambit.FLAGS.debug = True
        ambit.FLAGS.verbose = True

        # configure the device behavior
        device = ambit.fake.Device('DEAD:BEEF', 'XYZ')

        device.components_connected(ambit.fake.LAYOUT_DEFAULT_EXPERTKIT)

        # run the simulation
        config = ambit.Configuration()
        config.profile.icon = ambit.Configuration.ICON_PALETTE
        ctrl = ambit.Controller(config, device)
        self.ctrl = ctrl
        ctrl.open()
        ctrl.connect()

        ctrl.wait_for_layout()

        time.sleep(TEST_INPUT_SETTLED_SECONDS)
        device.layout_changed(ambit.fake.LAYOUT_RANDOM)
        ctrl.wait_for_layout()
        time.sleep(TEST_INPUT_SETTLED_SECONDS)
        self.assertEqual(20, len(ctrl.layout.connected()))

        # check for error conditions
        self.assertEqual(0, ctrl.failed_writes)
        self.assertEqual(0, ctrl.dropped_leds)
        self.assertEqual(0, ctrl.dropped_screen_strings)

    # TODO: replace test_slider_range_{broken,fixed} with a parameterized
    # test suite which exercises the entire suite for both versions.
    def test_slider_range_broken(self):
        ambit.FLAGS.debug = True
        ambit.FLAGS.verbose = True

        # configure the device behavior
        device = ambit.fake.Device('DEAD:BEEF', 'XYZ')

        device.set_version_core('1.3.1')

        # start with several components connected.
        device.components_connected(ambit.fake.LAYOUT_DEFAULT_EXPERTKIT)

        # run the simulation
        config = ambit.Configuration()
        config.profile.icon = ambit.Configuration.ICON_PALETTE
        ctrl = ambit.Controller(config, device)

        self.ctrl = ctrl
        ctrl.open()
        ctrl.connect()

        ctrl.wait_for_layout()

        device.input_slide_up(7, 254)

        time.sleep(TEST_INPUT_SETTLED_SECONDS)

        self.assertEqual([255,0,0,0,0,0,0,0], ctrl.layout.find_component(7).values)

    def test_slider_range_fixed(self):
        ambit.FLAGS.debug = True
        ambit.FLAGS.verbose = True

        # configure the device behavior
        device = ambit.fake.Device('DEAD:BEEF', 'XYZ')

        device.set_version_core('1.4.6136')

        # start with several components connected.
        device.components_connected(ambit.fake.LAYOUT_DEFAULT_EXPERTKIT)

        # run the simulation
        config = ambit.Configuration()
        config.profile.icon = ambit.Configuration.ICON_PALETTE
        ctrl = ambit.Controller(config, device)

        self.ctrl = ctrl
        ctrl.open()
        ctrl.connect()

        ctrl.wait_for_layout()

        device.input_slide_up(7, 254)

        time.sleep(TEST_INPUT_SETTLED_SECONDS)

        self.assertEqual([254,0,0,0,0,0,0,0], ctrl.layout.find_component(7).values)

        device.input_slide_up(7, 1)

        time.sleep(TEST_INPUT_SETTLED_SECONDS)

        self.assertEqual([255,0,0,0,0,0,0,0], ctrl.layout.find_component(7).values)

    def test_default_input(self):
        ambit.FLAGS.debug = True
        ambit.FLAGS.verbose = True

        # configure the device behavior
        device = ambit.fake.Device('DEAD:BEEF', 'XYZ')

        # start with several components connected.
        device.components_connected(ambit.fake.LAYOUT_DEFAULT_EXPERTKIT)

        # run the simulation
        config = ambit.Configuration()
        config.profile.icon = ambit.Configuration.ICON_PALETTE
        ctrl = ambit.Controller(config, device)
        self.ctrl = ctrl
        ctrl.open()
        ctrl.connect()

        # initial state and layout
        ctrl.wait_for_layout()

        self.assertEqual("PALETTE", device.handle.screen_string)
        self.assertEqual([0], device.handle.messages['screen_display'])

        self.assertEqual(0, ctrl.layout.find_component(1).orientation)
        self.assertEqual(0, ctrl.layout.find_component(2).orientation)
        self.assertEqual(270, ctrl.layout.find_component(3).orientation)
        self.assertEqual(270, ctrl.layout.find_component(4).orientation)
        self.assertEqual(90, ctrl.layout.find_component(5).orientation)
        self.assertEqual(180, ctrl.layout.find_component(6).orientation)
        self.assertEqual(90, ctrl.layout.find_component(7).orientation)
        self.assertEqual(180, ctrl.layout.find_component(8).orientation)

        self.assertEqual((0,0), ctrl.layout.find_component(1).slot)
        self.assertEqual((0,-1), ctrl.layout.find_component(2).slot)
        self.assertEqual((1,-1), ctrl.layout.find_component(3).slot)
        self.assertEqual((-1,-1), ctrl.layout.find_component(5).slot)

        self.assertEqual(False, ctrl.layout.find_component(4).flip)
        self.assertEqual(True, ctrl.layout.find_component(7).flip)

        self.assertEqual(8, len(ctrl.layout.connected()))

        ctrl.wait()

        self.assertEqual({
            1: (255, 255, 255),
            2: (255, 255, 255),
            3: (255, 255, 255),
            4: (255, 255, 255),
            5: (255, 255, 255),
            6: (255, 255, 255),
            7: (255, 255, 255),
            8: (255, 255, 255),
        }, device.handle.leds)

        # device input
        device.input_rotation_right(5, 1)
        device.input_rotation_right(5, 2)
        device.input_rotation_right(5, 2)
        device.input_rotation_left(5, 1)
        device.input_rotation_left(5, 1)
        device.input_pressed(5)
        device.input_released(5)
        device.input_slide_up(7, 4)
        time.sleep(TEST_INPUT_SETTLED_SECONDS * 8)
        self.assertEqual("Slider: 4", device.handle.screen_string)
        self.assertEqual([0,0,0,3,0,0,0,0], ctrl.layout.find_component(5).values)
        self.assertEqual([4,0,0,0,0,0,0,0], ctrl.layout.find_component(7).values)

        # screen reset timeout reached
        time.sleep(ambit.controller.Controller.SCREEN_RESET_SECONDS + 1)
        self.assertEqual("PALETTE", device.handle.screen_string)
        self.assertEqual(9, len(device.handle.messages['screen_string']))

        # check for error conditions
        self.assertEqual(0, ctrl.failed_writes)
        self.assertEqual(0, ctrl.dropped_leds)
        self.assertEqual(6, ctrl.dropped_screen_strings)


class AmbitCoordinatesTest(unittest.TestCase):
    def test_narrow_male_port_slot_0deg(self):
        component_orientation = 0
        component_slot = (0,0)
        expected_male_slot = (0,1)
        male_slot = ambit.coordinates.calculate_male_slot(component_slot, component_orientation)
        self.assertEqual(expected_male_slot, male_slot)

    def test_narrow_male_port_slot_180deg(self):
        component_orientation = 180
        component_slot = (0,0)
        expected_male_slot = (0,-1)
        male_slot = ambit.coordinates.calculate_male_slot(component_slot, component_orientation)
        self.assertEqual(expected_male_slot, male_slot)

    def test_narrow_male_port_slot_90deg(self):
        component_orientation = 90
        component_slot = (0,0)
        expected_male_slot = (1,0)
        male_slot = ambit.coordinates.calculate_male_slot(component_slot, component_orientation)
        self.assertEqual(expected_male_slot, male_slot)

    def test_narrow_male_port_slot_270deg(self):
        component_orientation = 270
        component_slot = (0,0)
        expected_male_slot = (-1,0)
        male_slot = ambit.coordinates.calculate_male_slot(component_slot, component_orientation)
        self.assertEqual(expected_male_slot, male_slot)

    def test_narrow_female_port_slots_0deg(self):
        component_orientation = 0
        component_slot = (0,0)
        expected_female_slots = (1,0), (0,-1), (-1,0)
        female_slots = ambit.coordinates.calculate_female_slots(component_slot, component_orientation)
        self.assertEqual(expected_female_slots, female_slots)

    def test_narrow_female_port_slots_180deg(self):
        component_orientation = 180
        component_slot = (0,0)
        expected_female_slots = (-1,0), (0,1), (1,0)
        female_slots = ambit.coordinates.calculate_female_slots(component_slot, component_orientation)
        self.assertEqual(expected_female_slots, female_slots)

    def test_narrow_female_port_slots_90deg(self):
        component_orientation = 90
        component_slot = (0,0)
        expected_female_slots = (0,-1), (-1,0), (0,1)
        female_slots = ambit.coordinates.calculate_female_slots(component_slot, component_orientation)
        self.assertEqual(expected_female_slots, female_slots)

    def test_narrow_female_port_slots_270deg(self):
        component_orientation = 270
        component_slot = (0,0)
        expected_female_slots = (0,1), (1,0), (0,-1)
        female_slots = ambit.coordinates.calculate_female_slots(component_slot, component_orientation)
        self.assertEqual(expected_female_slots, female_slots)

    def test_wide_male_port_slot_0deg(self):
        component_orientation = 0
        component_slot = (0,0)
        expected_male_slot = (0,1)
        male_slot = ambit.coordinates.calculate_male_slot(component_slot, component_orientation)
        self.assertEqual(expected_male_slot, male_slot)

    def test_wide_male_port_slot_180deg(self):
        component_orientation = 180
        component_slot = (0,0)
        expected_male_slot = (0,-1)
        male_slot = ambit.coordinates.calculate_male_slot(component_slot, component_orientation)
        self.assertEqual(expected_male_slot, male_slot)

    def test_wide_male_port_slot_90deg(self):
        component_orientation = 90
        component_slot = (0,0)
        expected_male_slot = (1,0)
        male_slot = ambit.coordinates.calculate_male_slot(component_slot, component_orientation)
        self.assertEqual(expected_male_slot, male_slot)

    def test_wide_male_port_slot_270deg(self):
        component_orientation = 270
        component_slot = (0,0)
        expected_male_slot = (-1,0)
        male_slot = ambit.coordinates.calculate_male_slot(component_slot, component_orientation)
        self.assertEqual(expected_male_slot, male_slot)

    def test_wide_female_port_slots_0deg(self):
        component_orientation = 0
        component_slot = (0,0)
        expected_female_slots = (1,1), (2,0), (1,-1), (0,-1), (-1,0)
        female_slots = ambit.coordinates.calculate_female_slots_wide(component_slot, component_orientation)
        self.assertEqual(expected_female_slots, female_slots)

    def test_wide_female_port_slots_180deg(self):
        component_orientation = 180
        component_slot = (0,0)
        expected_female_slots = (-1,-1), (-2,0), (-1,1), (0,1), (1,0)
        female_slots = ambit.coordinates.calculate_female_slots_wide(component_slot, component_orientation)
        self.assertEqual(expected_female_slots, female_slots)

    def test_wide_female_port_slots_90deg(self):
        component_orientation = 90
        component_slot = (0,0)
        expected_female_slots = (1,-1), (0,-2), (-1,-1), (-1,0), (0,1)
        female_slots = ambit.coordinates.calculate_female_slots_wide(component_slot, component_orientation)
        self.assertEqual(expected_female_slots, female_slots)

    def test_wide_female_port_slots_270deg(self):
        component_orientation = 270
        component_slot = (0,0)
        expected_female_slots = (-1,1), (0,2), (1,1), (1,0), (0,-1)
        female_slots = ambit.coordinates.calculate_female_slots_wide(component_slot, component_orientation)
        self.assertEqual(expected_female_slots, female_slots)


class AmbitImageTest(unittest.TestCase):
    def setUp(self):
        self.fd = io.BytesIO()

    def test_surface(self):
        asset_raw_path = ambit.resources.asset_path(23)
        surface = ambit.image.surface(asset_raw_path)
        self.assertEqual(surface.get_size(), (128, 128))
        self.assertEqual(pygame.Color(30, 31, 29, 255), surface.get_at((64, 64)))
        self.assertEqual(pygame.Color(34, 36, 33, 255), surface.get_palette_at(12))

    def test_convert_image(self):
        asset_png_path = ambit.resources.asset_path(23, fmt='png')
        ambit.image.convert_image(asset_png_path, self.fd)
        with ambit.resources.asset_file(23) as f:
            self.assertEqual(f.read(), self.fd.getvalue())


class AmbitMessageTest(unittest.TestCase):
    def test_message_encode(self):
        data = ambit.message.message_encode([
            {'check': 1},
            {'screen_string': 'TEST'},
        ])
        expected = memoryview(bytes(b'{"check":1}{"screen_string":"TEST"}'))
        self.assertEqual(expected, data)

    def test_message_decode(self):
        data = memoryview(bytes(b'{"screen_write":23}EXTRA_DATA'))
        messages, extra_data = ambit.message.message_decode(data)
        self.assertEqual([
            {'screen_write': 23}
        ], messages) 
        self.assertEqual(b'EXTRA_DATA', extra_data)


class AmbitSimulatorTest(unittest.TestCase):
    def setUp(self):
        self.ctrl = None

    def tearDown(self):
        if self.ctrl:
            self.ctrl.print_stats()
            self.ctrl.close()

    @unittest.mock.patch('pygame.key')
    @unittest.mock.patch('pygame.display')
    @unittest.mock.patch('pygame.draw')
    @unittest.mock.patch('pygame.event.poll')
    def test_render_orientation(self, mock_poll, mock_draw, mock_display, mock_key):
        # Default pygame event is no event.
        mock_poll.return_value = pygame.event.Event(pygame.NOEVENT)

        # Launch the simulator.
        config = ambit.Configuration()
        config.profile.icon = ambit.Configuration.ICON_PALETTE
        ctrl = ambit.simulator.Controller(config)
        ctrl.open()
        ctrl.connect()
        ctrl.device.components_connected(ambit.fake.LAYOUT_DEFAULT_EXPERTKIT)
        self.ctrl = ctrl
        self.ctrl.wait_for_layout()

        # Check the initial size of the screen surface.
        mock_display.set_mode.assert_called_with((1024, 576), pygame.RESIZABLE)
        self.assertEqual((1024, 576), self.ctrl.display.surface.get_size())

        # Rotate the screen
        mock_poll.side_effect = [
            pygame.event.Event(pygame.KEYUP, key=pygame.K_TAB),
        # Press the #2 button on the keyboard
        ] + [pygame.event.Event(pygame.NOEVENT) for i in range(50)] + [
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2),
        # Resize the screen to 2048 x 2048
        ] + [pygame.event.Event(pygame.NOEVENT) for i in range(50)] + [
            pygame.event.Event(pygame.VIDEORESIZE, size=(2048, 2048)),
        # Press the "q" key to quit.
        ] + [pygame.event.Event(pygame.NOEVENT) for i in range(50)] + [
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q),
        ] + [pygame.event.Event(pygame.NOEVENT) for i in range(20)]

        # Wait for the controller to catch up.
        self.ctrl.communicate()

        # Ensure that pygame.event.poll() was called.
        mock_poll.assert_called_with()

        # Ensure the screen surface was flipped at least once.
        mock_display.flip.assert_called_with()

        # Ensure the screen surface was resized.
        self.assertEqual((2048, 2048), self.ctrl.display.surface.get_size())

        # Ensure the correct rects were drawn at least once (90 degree rotation)
        mock_draw.rect.assert_has_calls([
            # LED strip rectangles
            unittest.mock.call(self.ctrl.display.screen, (255, 255, 255), pygame.Rect(629, 427, 379, 379), 12),
            unittest.mock.call(self.ctrl.display.screen, (255, 255, 255), pygame.Rect(1036, 427, 379, 379), 12),
            unittest.mock.call(self.ctrl.display.screen, (255, 255, 255), pygame.Rect(629, 20, 786, 379), 12),
            unittest.mock.call(self.ctrl.display.screen, (255, 255, 255), pygame.Rect(1036, 834, 379, 379), 12),
            unittest.mock.call(self.ctrl.display.screen, (255, 255, 255), pygame.Rect(629, 834, 379, 379), 12),
            unittest.mock.call(self.ctrl.display.screen, (255, 255, 255), pygame.Rect(629, 1241, 379, 379), 12),
            unittest.mock.call(self.ctrl.display.screen, (255, 255, 255), pygame.Rect(1036, 1241, 379, 379), 12),
            unittest.mock.call(self.ctrl.display.screen, (255, 255, 255), pygame.Rect(629, 1648, 786, 379), 12),

            # Component background (selected)
            unittest.mock.call(self.ctrl.display.screen, (164, 164, 255), pygame.Rect(617, 822, 403, 403)),

            # Component background
            unittest.mock.call(self.ctrl.display.screen, (164, 164, 164), pygame.Rect(1024, 822, 403, 403)),
            unittest.mock.call(self.ctrl.display.screen, (164, 164, 164), pygame.Rect(617, 1229, 403, 403)),
            unittest.mock.call(self.ctrl.display.screen, (164, 164, 164), pygame.Rect(1024, 1229, 403, 403)),
            unittest.mock.call(self.ctrl.display.screen, (164, 164, 164), pygame.Rect(617, 1636, 810, 403)),
            unittest.mock.call(self.ctrl.display.screen, (164, 164, 164), pygame.Rect(617, 415, 403, 403)),
            unittest.mock.call(self.ctrl.display.screen, (164, 164, 164), pygame.Rect(1024, 415, 403, 403)),
            unittest.mock.call(self.ctrl.display.screen, (164, 164, 164), pygame.Rect(617, 8, 810, 403)),
        ], any_order=True)

        # Ensure the correct circles were drawn at least once (90 degree rotation)
        mock_draw.circle.assert_has_calls([
            unittest.mock.call(self.ctrl.display.screen, (255, 0, 0, 128), (1427, 1023), 12),
            unittest.mock.call(self.ctrl.display.screen, (255, 0, 0, 128), (1020, 1023), 12),
            unittest.mock.call(self.ctrl.display.screen, (255, 0, 0, 128), (818, 1229), 12),
            unittest.mock.call(self.ctrl.display.screen, (255, 0, 0, 128), (1024, 1430), 12),
            unittest.mock.call(self.ctrl.display.screen, (255, 0, 0, 128), (819, 1636), 12),
            unittest.mock.call(self.ctrl.display.screen, (255, 0, 0, 128), (818, 818), 12),
            unittest.mock.call(self.ctrl.display.screen, (255, 0, 0, 128), (1024, 616), 12),
            unittest.mock.call(self.ctrl.display.screen, (255, 0, 0, 128), (1226, 411), 12),
        ], any_order=True)


if __name__ == '__main__':
    unittest.main(module='test_ambit')
