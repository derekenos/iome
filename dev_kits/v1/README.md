# Dev Kit v1

![all_in_one_20191010_bw](https://user-images.githubusercontent.com/585182/66948574-f74bb900-f022-11e9-9d6a-b5a0445ed567.png)

This first development kit features a familiar household rotary push-button dimmer knob as its primary physical input and three [living hinge](https://en.wikipedia.org/wiki/Living_hinge) tactile switch buttons (labelled 1, 2, 3). It employs the popular, low-cost ESP32 running Micropython as the brains of the operation.

## Bill of Materials

| Quantity | Description | Manufacturer | Part Number | Approx. Cost (USD) |
| --- | --- | --- | --- | --- |
| 1 | Wifi Dev Board | Espressif | [ESP32-PICO-KIT](https://octopart.com/esp32-pico-kit-espressif+systems-91893718) | $10 |
| 1 | Half-size breadboard | FICBOX | [B01NARN7SM](https://www.amazon.com/gp/product/B01NARN7SM) | $2 |
| 1 | Rotary dimmer knob | Lutron | [D-600PH-DK](https://www.lowes.com/pd/Lutron-Rotary-600-Watt-Single-Pole-White-Ivory-Dimmer/1059607) | $8 |
| 1 | 4xAA Battery Holder | Keystone | [2478](https://octopart.com/2478-keystone-3786) | $2 |
| 3 | Tactile switches | TE Connectivity | [FSM4JRT](https://octopart.com/fsm4jrt-te+connectivity+%2F+alcoswitch-40415111) | $1 |
| 16 | 8mm M4 bolts | McMASTER-CARR | [91292A108](https://www.mcmaster.com/catalog/125/3218) | $1 |
| 16 | M4 nuts | McMASTER-CARR | [90591A255](https://www.mcmaster.com/90591A255) | $1 |
| 1 | Laser-cut enclosure | ? | ? | ? |
| >0 | Wires | ? | ? | ? |

Approx. Total Cost: $25


## Professional Electrical Interconnection Diagram

![circuit_diagram](https://user-images.githubusercontent.com/585182/67024745-eb1f3480-f0d2-11e9-83d2-d62e8a006ba7.png)

_Note that there should probably be some resistors and capacitors in there for current limiting and switch debouncing._


## The Enclosure

[![enclosure](https://user-images.githubusercontent.com/585182/67147896-25b9d600-f267-11e9-82a1-92d8972328c8.png)](https://github.com/derekenos/iome/blob/master/dev_kits/v1/enclosure.svg)


## Loading the Firmware onto the ESP32

The [Makefile](https://github.com/derekenos/iome/blob/master/dev_kits/v1/Makefile) in this directory, when run using `make`, will execute a number of steps to prepare a connected ESP32-PICO-KIT to function as an iome device. When it's done, you will be prompted with:

> Connect to the game-server-{uniqueId} WiFi Access Point and surf your web browser over to http://192.168.4.1

Note that executing this `Makefile` requires that you have the `make` utility installed, as well as `docker` and `docker-compose`. Development happened using these versions:

```
$ make --version
GNU Make 4.1

$ docker --version
Docker version 19.03.4, build 9013bf583a

$ docker-compose --version
docker-compose version 1.19.0, build 9e633ef
```

The procedure is:

1. Connect the ESP32-PICO-KIT board to your computer with a USB cable
2. Run `make`
