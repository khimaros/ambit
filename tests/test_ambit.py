import ambit
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

        device.components_connected()

        # run the simulation
        config = ambit.Configuration(['./reference/layouts/meta.plp'])
        ctrl = ambit.Controller(config, device)
        self.ctrl = ctrl
        ctrl.open()
        ctrl.connect()

        ctrl.wait_for_layout()

        self.assertEqual(8, len(ctrl.layout.connected()))

        # Button / Switch profile
        device.input_pressed(6)
        device.input_released(6)
        time.sleep(0.5)
        self.assertEqual("META", device.handle.screen_string)

        time.sleep(2)

        self.assertEqual(1, len(device.handle.messages['check']))
        self.assertEqual("META", device.handle.screen_string)

    def test_layout1(self):
        ambit.FLAGS.debug = True
        ambit.FLAGS.verbose = False

        # configure the device behavior
        device = ambit.fake.Device('DEAD:BEEF', 'XYZ')

        device.components_connected()

        # run the simulation
        config = ambit.Configuration(ambit.resources.layout_paths('layout1'))
        ctrl = ambit.Controller(config, device)
        self.ctrl = ctrl
        ctrl.open()
        ctrl.connect()

        ctrl.wait_for_layout()

        self.assertEqual(8, len(ctrl.layout.connected()))

        time.sleep(1)

        self.assertEqual(1, len(device.handle.messages['check']))
        self.assertEqual("META", device.handle.screen_string)
        self.assertEqual([0], device.handle.messages['screen_display'])

        time.sleep(2)

        # Dial / Change LED Colors
        device.input_rotation_left(2, 8)
        device.input_rotation_left(2, 8)
        device.input_rotation_left(2, 16)
        time.sleep(1)
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

        # Button / Switch profile
        device.input_pressed(6)
        device.input_released(6)
        time.sleep(0.5)
        self.assertEqual("HOME", device.handle.screen_string)

        # Button / Switch profile
        device.input_pressed(8)
        device.input_released(8)
        time.sleep(0.5)
        self.assertEqual("META", device.handle.screen_string)
        device.input_pressed(8)
        device.input_released(8)
        time.sleep(0.5)
        self.assertEqual("MUSIC", device.handle.screen_string)

        self.assertEqual(0, ctrl.failed_writes)
        self.assertEqual(0, ctrl.dropped_leds)
        self.assertEqual(0, ctrl.dropped_screen_strings)

    def test_layout2(self):
        ambit.FLAGS.debug = True
        ambit.FLAGS.verbose = False

        # configure the device behavior
        device = ambit.fake.Device('DEAD:BEEF', 'XYZ')

        device.components_connected()

        # run the simulation
        config = ambit.Configuration(ambit.resources.layout_paths('layout2'))
        ctrl = ambit.Controller(config, device)
        self.ctrl = ctrl
        ctrl.open()
        ctrl.connect()

        ctrl.wait_for_layout()

        self.assertEqual(8, len(ctrl.layout.connected()))

        time.sleep(1)

        self.assertEqual(1, len(device.handle.messages['check']))
        self.assertEqual("META", device.handle.screen_string)
        self.assertEqual([0], device.handle.messages['screen_display'])

        time.sleep(2)

        # Button / Select LED control
        device.input_pressed(8)
        time.sleep(0.5)
        device.input_released(8)
        time.sleep(0.5)
        self.assertEqual("Green", device.handle.screen_string)
        device.input_pressed(8)
        time.sleep(0.5)
        device.input_released(8)
        time.sleep(0.5)
        self.assertEqual("Blue", device.handle.screen_string)

        # Slider / Change LED colors
        device.input_slide_up(4, 4)
        device.input_slide_up(4, 16)
        device.input_slide_up(4, 128)
        time.sleep(1)
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
        time.sleep(0.5)
        self.assertEqual("HACK", device.handle.screen_string)

        # Button / Execute command (hello)
        device.input_pressed(5)
        device.input_released(5)
        time.sleep(0.5)
        self.assertEqual("UNIVERSE!", device.handle.screen_string)

        # Dial / Switch profile
        device.input_rotation_left(2, 16)
        device.input_rotation_left(2, 16)
        time.sleep(0.5)
        self.assertEqual("META", device.handle.screen_string)
        device.input_rotation_left(2, 16)
        device.input_rotation_left(2, 16)
        time.sleep(0.5)
        self.assertEqual("HOME", device.handle.screen_string)

        # Slider / Execute command (temperature)
        device.input_slide_up(7, 255)
        time.sleep(0.5)
        self.assertEqual("TEMP: 80F", device.handle.screen_string)
        device.input_slide_down(7, 20)
        time.sleep(0.5)
        self.assertEqual("TEMP: 77F", device.handle.screen_string)

        # Dial / Execute command (unlock)
        device.input_rotation_right(5, 16)
        device.input_rotation_right(5, 16)
        time.sleep(0.5)
        self.assertEqual("OPEN: 15m", device.handle.screen_string)

        self.assertEqual(0, ctrl.failed_writes)
        self.assertEqual(0, ctrl.dropped_leds)
        self.assertEqual(0, ctrl.dropped_screen_strings)

    def test_layout4(self):
        ambit.FLAGS.debug = True
        ambit.FLAGS.verbose = False

        # configure the device behavior
        device = ambit.fake.Device('DEAD:BEEF', 'XYZ')

        device.components_connected()

        # run the simulation
        config = ambit.Configuration(ambit.resources.layout_paths('layout4'))
        ctrl = ambit.Controller(config, device)
        self.ctrl = ctrl
        ctrl.open()
        ctrl.connect()

        ctrl.wait_for_layout()

        # the 00-test config sets the orientation to 180 degrees,
        # and we rotate another 90 degrees here to test 270 orientation.
        ctrl.rotate(90)
        time.sleep(2)
        self.assertEqual(270, ctrl.layout.find_component(1).orientation)
        self.assertEqual(270, ctrl.layout.find_component(2).orientation)
        self.assertEqual(180, ctrl.layout.find_component(3).orientation)
        self.assertEqual(180, ctrl.layout.find_component(4).orientation)
        self.assertEqual(0, ctrl.layout.find_component(5).orientation)
        self.assertEqual(90, ctrl.layout.find_component(6).orientation)
        self.assertEqual(0, ctrl.layout.find_component(7).orientation)
        self.assertEqual(90, ctrl.layout.find_component(8).orientation)

        self.assertEqual((0,0), ctrl.layout.find_component(1).slot)
        self.assertEqual((1,0), ctrl.layout.find_component(2).slot)
        self.assertEqual((1,1), ctrl.layout.find_component(3).slot)
        self.assertEqual((1,2), ctrl.layout.find_component(4).slot)
        self.assertEqual((1,-1), ctrl.layout.find_component(5).slot)
        self.assertEqual((0,-1), ctrl.layout.find_component(6).slot)
        self.assertEqual((0,-2), ctrl.layout.find_component(7).slot)
        self.assertEqual((0,1), ctrl.layout.find_component(8).slot)

        self.assertEqual(True, ctrl.layout.find_component(4).flip)
        self.assertEqual(False, ctrl.layout.find_component(7).flip)

        self.assertEqual(8, len(ctrl.layout.connected()))

        time.sleep(1)

        self.assertEqual(1, len(device.handle.messages['check']))
        self.assertEqual("TEST", device.handle.screen_string)
        self.assertEqual([0, 0], device.handle.messages['screen_display'])

        time.sleep(2)

        # Dial / ACCUMULATE
        device.input_rotation_left(5, 8)
        device.input_rotation_left(5, 8)
        time.sleep(0.5)
        self.assertEqual("A: -2", device.handle.screen_string)
        device.input_pressed(5)
        device.input_released(5)
        time.sleep(0.5)
        self.assertEqual("A: 998", device.handle.screen_string)
        device.input_rotation_right(5, 8)
        device.input_rotation_right(5, 8)
        time.sleep(0.5)
        self.assertEqual("A: 1000", device.handle.screen_string)

        # Slider / TRIGGER
        device.input_slide_up(7, 4)
        device.input_slide_up(7, 16)
        device.input_slide_up(7, 128)
        device.input_slide_up(7, 64)
        device.input_slide_up(7, 64)
        time.sleep(1)
        self.assertEqual("T: 255", device.handle.screen_string)

        # Slider / CYCLE
        device.input_slide_up(4, 255)
        time.sleep(0.5)
        self.assertEqual("C: SIX", device.handle.screen_string)
        device.input_slide_down(4, 40)
        time.sleep(0.5)
        self.assertEqual("C: FIVE", device.handle.screen_string)
        device.input_slide_down(4, 40)
        time.sleep(0.5)
        self.assertEqual("C: FOUR", device.handle.screen_string)
        device.input_slide_down(4, 40)
        time.sleep(0.5)
        self.assertEqual("C: THREE", device.handle.screen_string)
        device.input_slide_down(4, 40)
        time.sleep(0.5)
        self.assertEqual("C: TWO", device.handle.screen_string)
        device.input_slide_down(4, 55)
        time.sleep(0.5)
        self.assertEqual("C: ONE", device.handle.screen_string)

        # Button / TRIGGER
        device.input_pressed(8)
        time.sleep(0.5)
        self.assertEqual("T: 1", device.handle.screen_string)
        device.input_released(8)
        time.sleep(0.5)
        self.assertEqual("T: 0", device.handle.screen_string)

        # Button / CYCLE
        device.input_pressed(6)
        device.input_released(6)
        time.sleep(0.5)
        self.assertEqual("C: TWO", device.handle.screen_string)
        device.input_pressed(6)
        device.input_released(6)
        time.sleep(0.5)
        self.assertEqual("C: THREE", device.handle.screen_string)
        device.input_pressed(6)
        device.input_released(6)
        time.sleep(0.5)
        self.assertEqual("C: FOUR", device.handle.screen_string)
        device.input_pressed(6)
        device.input_released(6)
        time.sleep(0.5)
        self.assertEqual("C: FIVE", device.handle.screen_string)
        device.input_pressed(6)
        device.input_released(6)
        time.sleep(0.5)
        self.assertEqual("C: SIX", device.handle.screen_string)
        device.input_pressed(6)
        device.input_released(6)
        time.sleep(0.5)
        self.assertEqual("C: ONE", device.handle.screen_string)

        time.sleep(6)

        self.assertEqual("TEST", device.handle.screen_string)
        self.assertEqual(28, len(device.handle.messages['screen_string']))

        self.assertEqual(0, ctrl.failed_writes)
        self.assertEqual(0, ctrl.dropped_leds)
        self.assertEqual(0, ctrl.dropped_screen_strings)

    def test_layout_query(self):
        ambit.FLAGS.debug = True
        ambit.FLAGS.verbose = False

        # configure the device behavior
        device = ambit.fake.Device('DEAD:BEEF', 'XYZ')

        device.components_connected()

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

        # Start with several components connected.
        device.components_connected(ambit.fake.DEFAULT_COMPONENT_LAYOUT)

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

        device.layout_changed(ambit.fake.BASE_ONLY_LAYOUT)

        time.sleep(1)

        # When the base only is connected, check that the bytes match file data.
        ctrl.wait_for_layout()
        ctrl.configure_images()

        time.sleep(1)

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

        device.components_connected(ambit.fake.DEFAULT_COMPONENT_LAYOUT)

        # run the simulation
        config = ambit.Configuration()
        config.profile.icon = ambit.Configuration.ICON_PALETTE
        ctrl = ambit.Controller(config, device)
        self.ctrl = ctrl
        ctrl.open()
        ctrl.connect()

        ctrl.wait_for_layout()

        time.sleep(1)

        device.layout_changed(ambit.fake.RANDOM_COMPONENT_LAYOUT)

        ctrl.wait_for_layout()

        time.sleep(1)

        self.assertEqual(20, len(ctrl.layout.connected()))

        self.assertEqual(0, ctrl.failed_writes)
        self.assertEqual(0, ctrl.dropped_leds)
        self.assertEqual(0, ctrl.dropped_screen_strings)

    def test_default_input(self):
        ambit.FLAGS.debug = True
        ambit.FLAGS.verbose = True

        # configure the device behavior
        device = ambit.fake.Device('DEAD:BEEF', 'XYZ')

        device.components_connected(ambit.fake.DEFAULT_COMPONENT_LAYOUT)

        # run the simulation
        config = ambit.Configuration()
        config.profile.icon = ambit.Configuration.ICON_PALETTE
        ctrl = ambit.Controller(config, device)
        self.ctrl = ctrl
        ctrl.open()
        ctrl.connect()

        ctrl.wait_for_layout()

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

        time.sleep(1)

        self.assertEqual(1, len(device.handle.messages['check']))
        self.assertEqual("PALETTE", device.handle.screen_string)
        self.assertEqual([0], device.handle.messages['screen_display'])

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

        device.input_rotation_right(5, 1)
        device.input_rotation_right(5, 2)
        device.input_rotation_right(5, 2)
        device.input_rotation_left(5, 1)
        device.input_rotation_left(5, 1)
        device.input_pressed(5)
        device.input_released(5)
        device.input_slide_up(7, 4)

        time.sleep(2)

        self.assertEqual("Slider: 4", device.handle.screen_string)
        self.assertEqual([0,0,0,3,0,0,0,0], ctrl.layout.find_component(5).values)
        self.assertEqual([4,0,0,0,0,0,0,0], ctrl.layout.find_component(7).values)

        time.sleep(6)

        self.assertEqual("PALETTE", device.handle.screen_string)
        self.assertEqual(9, len(device.handle.messages['screen_string']))

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

    @unittest.mock.patch('pygame.display')
    @unittest.mock.patch('pygame.draw')
    @unittest.mock.patch('pygame.event.poll')
    def test_render_orientation(self, mock_poll, mock_draw, mock_display):
        # Default pygame event is no event.
        mock_poll.return_value = pygame.event.Event(pygame.NOEVENT)

        # Launch the simulator.
        config = ambit.Configuration()
        config.profile.icon = ambit.Configuration.ICON_PALETTE
        ctrl = ambit.simulator.Controller(config)
        ctrl.open()
        ctrl.connect()
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
