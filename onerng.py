#! /usr/bin/env python3

# OS-agnostic OneRNG-to-/dev/random entropy feeding daemon
#
# Copyright 2022 Chris Kobayashi

import os
import sys
import serial
import socket
import time
import argparse
import fcntl

feed_rate = 5
bs = 128
count = 200

def onerng_start(ser):
    ser.write(b'cmd0')
    ser.write(b'cmdO')

def onerng_stop(ser):
    ser.write(b'cmdo')
    ser.write(b'cmd4')
    ser.write(b'cmdw')

def onerng_initialize(ser):
    onerng_stop(ser)
    time.sleep(5)
    onerng_start(ser)
    byte = ser.read()
    time.sleep(2.5)

def main():
    parser = argparse.ArgumentParser(description='portable OneRNG daemon')
    parser.add_argument('-d', '--device', nargs=1, type=str, dest='device', help='OneRNG device (default /dev/ttyU0)', default='/dev/ttyU0')
    parser.add_argument('-D', '--debug', action='store_true', dest='debug', help='print debugging information (default false)', default=False)
    args = parser.parse_args()

    if args.debug is True:
        print(sys.argv[0]+': opening', args.device)
    ser = serial.Serial(args.device, 115200)
    if args.debug is True:
        print(sys.argv[0]+': initializing', args.device)
    onerng_initialize(ser)
    if args.debug is True:
        print(sys.argv[0]+': starting', args.device)
    onerng_start(ser)

    if args.debug is True:
        print(sys.argv[0]+': looping', args.device)
    while True:
        bytes = ser.read(bs * count)
        if args.debug is True:
            print (sys.argv[0]+': received', len(bytes), 'bytes (expected', (bs * count), ')')
        with open('/dev/random', 'wb') as dev_random:
            bytes_written = dev_random.write(bytes)
            if args.debug is True:
                print(sys.argv[0]+': wrote', bytes_written, 'bytes to /dev/random')
        dev_random.close()
        time.sleep(feed_rate)

if __name__ == '__main__':
    main()
