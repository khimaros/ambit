# HACKING

This document mostly covers the reverse engineering process.

## Prepare the Linux host

Enable virtualization in your BIOS.

Ensure KVM is enabled on your kernel, load the module.

Install virt-manager / QEMU / KVM

Ensure your user account is in the right groups for qemu.

```
# modprobe usbmon
```

Install wireshark and ensure that it is installed setuid so
your user account has privileges to capture.

## Create the Win10 VM

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

## Capture USB traffic

Linux host: use wireshark to begin capture from usbmonX

Win10 VM: open PaletteApp, perform some action (eg. load config, press button)

Linux host: stop the capture, save to reference/capture/

