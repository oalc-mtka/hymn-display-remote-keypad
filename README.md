# Hymn Display Remote Keypad

The Remote Keypad lets someone set the Song Number on a Locality's Hymn Display Board from a phone when nobody is on the Song Leaders' Bench (phone patches, viewings, gatherings). It's a small MicroPython board wired into the Hymn Display Board that serves a keypad web page at `http://hymn.local`.

This README is for the developers and engineers who work on it. Locality volunteers get pre-flashed devices and use the [installer's guide](docs/installers-guide.md) and [song leader guide](docs/song-leader-guide.md) instead.

- Domain language: [CONTEXT.md](CONTEXT.md). Use these terms in code, issues and docs.
- Decisions: [docs/adr/](docs/adr/)
- Open questions for the engineers: [docs/questions-for-engineers.md](docs/questions-for-engineers.md)
- Known problems, drafted as issues: [docs/review-findings.md](docs/review-findings.md)

## Status

The code is moving to `oalc-mtka/hymn-display-remote-keypad`.

- **This repo** holds the original Pico W version, which runs its own open, hidden Wi-Fi hotspot called "Hymn". That version is **deprecated** ([ADR 0001](docs/adr/0001-wired-network-no-login.md)).
- **The Ethernet version**, which is the product going forward, is in [sarki012/hymn_control_ethernet](https://github.com/sarki012/hymn_control_ethernet). It's the same app with the hotspot replaced by a wired connection. It will be brought into the new repo as one commit on top of this repo's history.

The rest of this README describes the Ethernet version.

## Hardware

| Part | Detail |
| --- | --- |
| Board | WIZnet **W6100-EVB-Pico2** (RP2350 + W6100 Ethernet) |
| Ethernet (SPI0) | MISO GP16, CS GP17, SCK GP18, MOSI GP19, RST GP20 |
| From the Bottom Display | UART0 RX on GP1, 9600 baud, **inverted** |
| To the Hymn Display Board | UART1 TX on GP4, 9600 baud, **inverted** (GP5 is configured as RX but unused) |
| Remote Access Switch | Turns the Remote Keypad off. It must be off whenever a Song Leader is on the bench. |

How the UARTs connect to the Hymn Display Board isn't documented yet, including whether the Remote Keypad sits in the line between the Bottom Display and the Top Display. See [questions for the engineers](docs/questions-for-engineers.md). Until that's answered, assume it does: if the Remote Keypad stops, the bench may stop working too.

## Firmware

`network.WIZNET6K` isn't in upstream MicroPython (the upstream PR is [micropython#18035](https://github.com/micropython/micropython/pull/18035)). Use WIZnet's build:

- Release: [v1.29.0-WIZnet-timeout](https://github.com/WIZnet-ioNIC/WIZnet-EVB-Pico-micropython/releases/tag/v1.29.0-WIZnet-timeout) or later. Older releases report the W6100 as never connected.
- File: **`LWIP-W6100_EVB_PICO2-v1.29.0-preview.uf2`**. It must be the **LWIP** build. The **TOE** build has no mDNS, so `hymn.local` won't work on it, and it ignores the hostname.

To flash it: hold BOOTSEL while plugging in USB, then copy the `.uf2` onto the drive that appears.

These firmware facts come from reading WIZnet's source and haven't been tested on a board yet.

## Development setup

1. Install VS Code and the recommended extensions (`.vscode/extensions.json`), in particular **MicroPico** (`paulober.pico-w-go`).
2. Flash the firmware (above).
3. Use MicroPico to upload `main.py` and `index.html` to the board. `main.py` runs at boot.
4. Plug the board into a network with DHCP, then open `http://hymn.local` from a device on the same network.

There's no way to run or test the code without the hardware yet. That's a known gap, drafted as an issue in [review findings](docs/review-findings.md).

## Preparing a device to ship

1. Flash the firmware and upload the app.
2. Record the board's MAC address and print it on the label, with a blank line beside it for the fallback IP. The firmware builds the MAC from the RP2350's unique ID, so it's fixed per board and survives re-flashing. Until the app prints it at boot (drafted as an issue), read it from the REPL after stopping `main.py` (untested):

   ```python
   import machine, network
   spi = machine.SPI(0, baudrate=20_000_000, sck=machine.Pin(18), mosi=machine.Pin(19), miso=machine.Pin(16))
   nic = network.WIZNET6K(spi, machine.Pin(17), machine.Pin(20))
   nic.active(True)
   print(':'.join('%02x' % b for b in nic.config('mac')))
   ```

3. Check it on a test network: `http://hymn.local` opens and the keypad sends.
4. Include the [song leader guide](docs/song-leader-guide.md) and the [installer's guide](docs/installers-guide.md) checklist.

## How it works

`main.py` runs three things on one `uasyncio` loop:

- **Network.** It brings up the W6100 with DHCP, using hostname `hymn` (answered as `hymn.local` over mDNS).
- **Pass-through.** Every byte from the Bottom Display on UART0 is copied unchanged to UART1.
- **Web server** on port 80:

| Request | What it does |
| --- | --- |
| `GET /` | Serves `index.html`, the phone keypad. |
| `GET /on?code=NNN` | Shows a Song Number. If a Display Timeout is running, it blanks the Top Display first. Then it sends one keypad code per digit (50 ms apart), the Top Display frame twice, and starts the 7-minute Display Timeout. |
| `GET /off` | If a Display Timeout is running, it cancels it and blanks the Top Display. Then it sends the keypad Clear code. |

### Byte protocol on UART1

The protocol mirrors the original C firmware (the C source isn't in this repo).

- **Keypad codes**, one byte per key: `0`=`0x17`, `1`=`0x33`, `2`=`0x67`, `3`=`0x19`, `4`=`0x32`, `5`=`0x65`, `6`=`0x0C`, `7`=`0x5F`, `8`=`0x63`, `9`=`0x5E`, Send=`0x5D` (defined but never sent), Clear=`0x06`.
- **Top Display frame** (`sendToTop()`): 6 bytes. These are the 7-segment patterns for the third, second and first digit with bit 7 cleared, then the same three bytes with bit 7 set. Leading positions are blank (`0x00`). It's always sent twice.
- **Blank the Top Display** (`clearTop()`): `00 00 00 80 80 80`, always sent twice.

The Remote Keypad keeps its own Display Timeout rather than leaving it to the bench firmware. See [ADR 0002](docs/adr/0002-remote-keypad-keeps-its-own-timeout.md) before changing that.

## License

MIT. Copyright Old Apostolic Lutheran Church of America. See [LICENSE](LICENSE).
