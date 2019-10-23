

default:
# Actually download the code for all the git submodules.
	@git submodule update --init --recursive;
# Using the micropython-docker submodule, \
  Create a symbolic link to iome/filesystem called devicefs, \
  Erase the flash memory of the connected ESP32 device, \
  ... note that the micropython-docker Docker image will be built at this \
  this point if it doesn't already exist ... \
  Flash the connected ESP32 device with the micropython firmware, \
  Copy everything in devicefs to the connected device filesystem.
	@set -e; \
	cd micropython-docker; \
	ln --symbolic --no-dereference --force ../filesystem devicefs; \
	make erase-esp32-flash; \
	make flash-esp32-firmware; \
	make configure-device;
# Tell the user how to connect.
	@echo "Connect to the game-server-{uniqueId} WiFi Access Point and surf your web browser over to http://192.168.4.1"
