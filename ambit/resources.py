"""Embedded resource constants and helpers."""

import glob
import os


RESOURCES_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources'))

LAYOUTS_PATH = os.path.join(RESOURCES_PATH, 'layouts')

ASSETS_PATH = os.path.join(RESOURCES_PATH, 'assets')

TEMPLATE_SCREEN_IMAGE_PATHS = (
        os.path.join(ASSETS_PATH, '%d.%s'),
        os.path.join(ASSETS_PATH, 'reference', '%d.%s'),
)


def layout_paths(layout, recurse=True):
    path = os.path.join(LAYOUTS_PATH, layout)
    if recurse:
        path = os.path.join(path, '*.plp')
    return glob.glob(path)


def asset_path(index, fmt='raw'):
    for tmpl in TEMPLATE_SCREEN_IMAGE_PATHS:
        path = tmpl % (index, fmt)
        if os.path.exists(path):
            return path
    return None


def asset_file(index, fmt='raw'):
    return open(asset_path(index, fmt), 'rb')
