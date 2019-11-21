# I/O <-> ME

iome is a platform for developing physical interfaces with a web application frontend using modern, off-the-shelf technologies.

The overall system looks like:

```
 ______________________          _____________________                      _________________________
| Buttons, Knobs, etc. |  --->  | Wifi-enabled micro- |  <-- WiFi ------>  | Device with a display   |
 ----------------------         | controller running  |           | \      | and a web browser, e.g. |
 ____________________           | an HTTP server and  |           |  OR    | phone, tablet, computer |
| LEDs, Motors, etc. |  <-----  | minimal web applic- |           |         --------------------------
 --------------------           | ation framework     |           |               /\   
                                 ---------------------        [ Router ] ---------'
```

## Applications

This was created specificially to serve as a wireless HTML5 game console:

[![vidthumbz](https://user-images.githubusercontent.com/585182/67110218-33585880-f1a0-11e9-9881-7b0d15b13a66.png)](https://youtu.be/Y_KrPvnUPak)

More generally, it enables wireless access to physical switch, knob, etc. data via a [Websocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API).

This means that you can:

1. Build/buy something like the [Dev Kit v1](https://github.com/derekenos/iome/tree/master/dev_kits/v1)
2. [Load it up with the `iome` software](https://github.com/derekenos/iome/tree/master/dev_kits/v1#loading-the-firmware-onto-the-esp32) (if necessary)
3. Power it up
4. Connect your computer to the `iome-{theUniqueId}` Wifi Access Point that it creates by default
5. Surf your browser over to `http://192.168.4.1`
6. Open the browser dev console and do:
```
const ws = new WebSocket(`ws://192.168.4.1/input`)
ws.onmessage = e => {
  const data = JSON.parse(e.data)
  console.log(data)
}
```
7. Watch the data change as you interact with the physical buttons, knob, etc.

From there, you can integrate that WebSocket hook into whatever web application code you want.

### Connect to an Existing Wifi Access Point

The default configuration [creates an Access Point on boot](https://github.com/derekenos/iome/blob/master/dev_kits/v1/filesystem/config.json#L7-L8), but you can edit the config to [specify that it connect to an existing Access Point instead](https://github.com/derekenos/iome/blob/master/dev_kits/v1/filesystem/config.json#L9-L11). You can use the editor [described here](https://github.com/derekenos/femtoweb/#in-browser-file-editor) to do this. Once connected, you should, providing your AP supports [mDNS](http://multicastdns.org/), be able to access it via `http://iome-{uniqueId}.local`, as opposed to having to discover and specify its IP address.

## [Dev Kit v1](https://github.com/derekenos/iome/tree/master/dev_kits/v1)

![all_in_one_20191010_bw](https://user-images.githubusercontent.com/585182/66948574-f74bb900-f022-11e9-9d6a-b5a0445ed567.png)

This first development kit features a familiar household rotary push-button dimmer knob as its primary physical input and three [living hinge](https://en.wikipedia.org/wiki/Living_hinge) tactile switch buttons (labelled 1, 2, 3). It employs the popular, low-cost ESP32 running Micropython as the brains of the operation.

## [Sketchy](https://github.com/derekenos/iome/tree/master/appliances/sketchy)

<a href="https://github.com/derekenos/iome/tree/master/appliances/sketchy">
  <img src="https://user-images.githubusercontent.com/585182/69062387-d80cc680-09e8-11ea-82ab-671f9070fd5e.png" alt="sketchy prototype" width="560" />
</a>

Sketchy is a motorized Etch A Sketch display appliance.

