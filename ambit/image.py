#!/usr/bin/env python3

import ctypes
import math
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

import pygame

IMAGE_SIZE = (128, 128)

PALETTE_SIZE = 48


class ImageByte_bits(ctypes.BigEndianStructure):
    _fields_ = [
        ("a", ctypes.c_uint8, 4),
        ("b", ctypes.c_uint8, 4),
    ]


class ImageByte(ctypes.Union):
    _anonymous_ = ("bit",)
    _fields_ = [ ("bit", ImageByte_bits), ("asByte", ctypes.c_uint8) ]


def load_image(path, image_size=IMAGE_SIZE, palette_size=PALETTE_SIZE):
    with open(path, 'rb') as f:
        return parse_image(f, image_size, palette_size)


def parse_image(fd, image_size=IMAGE_SIZE, palette_size=PALETTE_SIZE):
    # Prepare a one-dimensional sequence of pixels
    pixels = []
    colors = []

    # read the palette
    for _ in range(int(palette_size / 3)):
        r = ord(fd.read(1))
        g = ord(fd.read(1))
        b = ord(fd.read(1))
        colors.append((b, g, r))

    # read the pixels
    body_size = int(image_size[0] / 2) * image_size[1]
    for _ in range(body_size):
        d = fd.read(1)

        k = ImageByte()
        k.asByte = ord(d)
        pixels.append(k.a)
        pixels.append(k.b)

    # not sure what this is?
    fd.read(4)
    fd.read(64)

    # extra bytes
    extra = fd.read()

    if len(extra):
        print('[!] WARNING: image input had extra bytes %d' % len(extra))

    return colors, pixels


def draw_pixels(surface, pixels, image_size=IMAGE_SIZE):
    # Draw the result to the surface
    i = 0
    for y in range(image_size[0], 0, -1):
        for x in range(image_size[1]):
            px = pixels[i]
            surface.set_at((x, y), px)
            i += 1


def surface(path, image_size=IMAGE_SIZE, palette_size=PALETTE_SIZE, surface_size=IMAGE_SIZE):
    surface = pygame.Surface(image_size, depth=8)
    colors, pixels = load_image(path, image_size, palette_size)
    surface.set_palette(colors)
    draw_pixels(surface, pixels, image_size)
    return pygame.transform.scale(surface, surface_size)


def load_standard_image(path, palette_size, image_size=IMAGE_SIZE):
    pygame.init()

    surface = pygame.image.load(path).convert(24)
    surface = pygame.transform.scale(surface, image_size)

    palette = []
    pixels = []
    seen_colors = {}
    palette_map = {}

    # first, grab all of the pixels in the image
    # and build a list of most common pixel colors
    for y in range(image_size[1]):
        for x in range(image_size[0] - 1, -1, -1):
            color = surface.get_at((x, y))
            c = surface.map_rgb(color)
            pixels.append(c)
            if not c in seen_colors: seen_colors[c] = 0
            seen_colors[c] += 1

    top_colors = [0] + sorted(seen_colors, key=seen_colors.get, reverse=True)
    num_colors = int(palette_size / 3)
    for i, c in enumerate(top_colors[:num_colors]):
        palette_map[c] = i
        color = pygame.Color(c)
        _, r, g, b = color
        palette.append(b)
        palette.append(g)
        palette.append(r)
    for i in range(16 - int(len(palette) / 3)):
        palette.extend((0, 0, 0))

    return palette, palette_map, pixels


def convert_image(src_path, dst_fd):
    palette, palette_map, pixels = load_standard_image(src_path, palette_size=PALETTE_SIZE)
    data = make_image_bytes(palette, palette_map, pixels)
    dst_fd.write(data)


def make_image_bytes(palette, palette_map, pixels):
    data = bytearray()
    mapped_pixels = []

    # add the palette mapped pixels to the body
    k = ImageByte()
    cur_nibble = 0
    for px in pixels:
        px_color = pygame.Color(px)
        color_diffs = []
        for c in palette_map:
            color = pygame.Color(c)
            diff = math.sqrt(abs(px_color.r - color.r)**2 + abs(px_color.g - color.g)**2 + abs(px_color.b - color.b)**2)
            color_diffs.append((diff, c))
        palette_index = palette_map[min(color_diffs)[1]]
        if cur_nibble == 0:
            k.b = palette_index
            cur_nibble = 1
            continue
        if cur_nibble == 1:
            k.a = palette_index
            mapped_pixels.append(k.asByte)
            cur_nibble = 0

    data.extend(palette)
    data.extend(reversed(mapped_pixels))

    if len(data) != 8240:
        print('[!] WARNING: image bytes output had %d extra bytes' % 8240 - len(data))

    return data
