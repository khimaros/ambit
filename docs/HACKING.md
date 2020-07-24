# HACKING

This document covers the reverse engineering process.

## Protocol reversing

### Prepare the Linux host

Enable virtualization in your BIOS.

Ensure KVM is enabled on your kernel, load the module.

Install virt-manager / QEMU / KVM

Ensure your user account is in the right groups for qemu.

```
# modprobe usbmon
```

Install wireshark and ensure that it is setuid so your user
account has privileges to capture.

### Create the Win10 VM

Download Win10 VirtualBox image:

https://developer.microsoft.com/en-us/microsoft-edge/tools/vms/

Convert the OVA to a qcow image for use by KVM/QEMU:

```
$ tar xvf MSEdge*.ova
$ qemu-img convert -O qcow2 MSEdge\ -\ Win10-disk001.vmdk MSEdge.qcow
```

Cleanup the intermediate images. You only need to keep MSEdge.qcow

Connect the Palette via USB

Create a virt-manager config from MSEdge.qcow

Configure VM: "Add Hardware" => "USB Host Device" => "MCS Palette"

Boot the VM, login with password "Passw0rd!"

Install PaletteApp in the VM.

At this point, you may want to take a snapshot of your Win10 VM
to restore from when the license expires.

### Capture USB traffic

Linux host: use wireshark to begin capture from usbmonX

Win10 VM: open PaletteApp, perform some action (eg. load config, press button)

Linux host: stop the capture, save to docs/capture/

## Screen image capture

Start a Wireshark capture.

Begin a screen image update in the Win10 VM.

Save the capture to `docs/captures/core-update-images.pcapng`

Run `make extract_reference_assets`

## Firmware capture

The simplest way to retrieve firmware images is to install the
PaletteApp and retrieve the `firmware.hex` file from the
Program Files directory.

You can also capture the firmware with Wireshark.

Start a Wireshark capture.

Begin a firmware flash in the Win10 VM.

Save the capture to `docs/captures/firmware-update-push.pcapng`.

Run `make out/firmware/palette-firmware.hex`

## Firmware reversing

Practical firmware reversing: https://beta.rada.re/en/latest/\_downloads/avrworkshops2016.pdf

### Capturing firmware updates

This is how wireshark parses the DFU dataframes: https://code.wireshark.org/review/gitweb?p=wireshark.git;a=blob;f=epan/dissectors/packet-usb-dfu.c;hb=35cdb63ecb4f97dd8bec3e45602104c45d28eaa9#l244

Here is how dfu-programmer writes them: https://github.com/dfu-programmer/dfu-programmer/blob/master/src/atmel.c#L53

https://osqa-ask.wireshark.org/questions/43330/dump-packet-leftover-data-capture-field-only

```
$ tshark -r docs/captures/firmware-update-push.pcapng -2 -T fields \
        -e usb.data_fragment -Y usb.data_fragment \
        -R 'usb.dst == "1.55.0" or usb.src == "1.55.0" and usb.bmRequestType == 0x21 and usb.urb_len > 70' \
        | sed 's/^.\{64\}//' | sed 's/.\{32\}$//' | tr -d '\n' \
        | xxd -r -ps > out/firmware/palette-firmware.bin

$ tools/bin_to_intel_hex.py out/firmware/palette-firmware.bin out/firmware/palette-firmware.hex

$ dfu-programmer at90usb1286 flash palette-firmware.hex
```

Wireshark USB DFU disection doesn't seem to be working:

https://bugs.wireshark.org/bugzilla/show\_bug.cgi?id=16616#c0

```
tshark -r firmware-update-push.pcapng -e usbdfu.data -T fields | tr -d '\n'
```

### Firmware extraction/analysis

https://github.com/ReFirmLabs/binwalk
https://nvisium.com/blog/2019/08/07/extracting-firmware-from-iot-devices.html
https://thanat0s.trollprod.org/2014/01/loader-un-binaire-arduino-dans-ida/

