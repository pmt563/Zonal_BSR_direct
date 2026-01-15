#!/bin/bash

# Usage: sudo ./run.sh <image-name> <loopback-value> [brokerip:port]
# Example: sudo ./run.sh zonal_app 0 192.168.0.3:55556

VID="04d8"
PID="0053"

if [ $# -lt 2 ] || [ $# -gt 3 ]; then
  echo "Usage: sudo $0 <image-name> <loopback-value> [brokerip:port]"
  echo "loopback-value must be 0 or 1"
  exit 1
fi

loopback_value=$2
if [[ "$loopback_value" != "0" && "$loopback_value" != "1" ]]; then
    echo "Invalid loopback value. Please use 0 or 1."
    exit 1
fi

# Find the line in lsusb that matches the device
line=$(lsusb | grep "${VID}:${PID}")

if [ -n "$line" ]; then
    BUS=$(echo "$line" | awk '{print $2}')
    DEV=$(echo "$line" | awk '{print $4}' | sed 's/://')

    # Format the full path
    USB_DEV="/dev/bus/usb/${BUS}/${DEV}"

    echo "✅ Found USB device at $USB_DEV"
else
    echo "❌ USB device ${VID}:${PID} not found."
    exit 1
fi

IMAGE_NAME=$1
BROKER_ARG=${3:-192.168.1.1:55555}

podman run --rm -it --device=$USB_DEV "$IMAGE_NAME" -loopback="$loopback_value" "$BROKER_ARG" 