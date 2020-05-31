# IMAGE

The images are essentially 4bpp BMP with bitmap headers stripped.

## Palette

The first 48 bytes of the image make up the color palette.

The color palette can hold up to 16 distinct 24 bit (3 byte) values.

If the image has fewer than 16 colors, the palette is padded with 0x00.

Each 24 bit value is in BGR order. There is no alpha channel.

```
[ BB BB BB BB , GG GG GG GG , RR RR RR RR ]
```

## Body

Image body is 128 x 128 pixels.

Each pixel in the body is 4 bits. Big Endian.

The pixel plane is packed.

```
  PX 0     PX 1     PX 3
[ DEAD ] [ BEEF ] [ FEED ] ...
```

Pixels are drawn starting from the bottom right.

The bottom 20% of the image is typically not visible
due to title text overlay.

## Compatibility

There are 68 bytes immediately following the body. From examining
the icons distributed with Palette, these bytes are always filled
with 0x00.

In the official app, the last 8192 bytes (oddly, sometimes 8191)
are padded with 0x00. This clever trick defeats the purpose of
using an 4bpp encoding as a space saving measure, so we omit these.
The display doesn't seem to mind the missing bytes.

