import argparse

flags = argparse.ArgumentParser(description='Take control of your Palette.')

flags.add_argument('--device', default='16D0:09F8',
                   help='usb device vendor:product id')

flags.add_argument('--device_index', default=0,
                   help='index of device to control if multiple connected')

flags.add_argument('--debug', default=False, action='store_true',
                   help='include low level protocol messages')

flags.add_argument('--verbose', default=False, action='store_true',
                   help='include more detailed status output')

flags.add_argument('--layouts', default=[], type=str, nargs='*',
                   help='launch with the specified layouts')

flags.add_argument('--map_midi', default=True, action='store_true',
                   help='map midi controller inputs')

flags.add_argument('config_paths', type=str, metavar='CONFIG', nargs='*',
                   help='configuration files to load')

FLAGS = flags.parse_args()
