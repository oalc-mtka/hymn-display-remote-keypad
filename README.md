# Hymn Display Remote Keypad

The Remote Keypad lets someone set the Song Number on a Locality's Hymn Display Board from a phone when nobody is on the Song Leaders' Bench (phone patches, viewings, gatherings). It's a small MicroPython board wired into the Hymn Display Board that serves a keypad web page at `http://hymn.local`.

This README is for the developers and engineers who work on it. Locality volunteers get pre-flashed devices and use the [installer's guide](docs/installers-guide.md) and [song leader guide](docs/song-leader-guide.md) instead.

- Domain language: [CONTEXT.md](CONTEXT.md). Use these terms in code, issues and docs.
- Decisions: [docs/adr/](docs/adr/)
- Flashing and shipping a device: [docs/engineers-setup.md](docs/engineers-setup.md)
- Open questions for the engineers: [docs/questions-for-engineers.md](docs/questions-for-engineers.md)
- Known problems: [GitHub issues](https://github.com/oalc-mtka/hymn-display-remote-keypad/issues)

## Status

`src/` is the **Ethernet** version, the product going forward. It was ported from [sarki012/hymn_control_ethernet](https://github.com/sarki012/hymn_control_ethernet).

The original Pico W version, which ran its own open, hidden Wi-Fi hotspot called "Hymn", is **deprecated** and lives only in git history ([ADR 0001](docs/adr/0001-wired-network-no-login.md)). Its last commit is `6346b40`.

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

Step-by-step flashing, with checks: [engineer's setup guide](docs/engineers-setup.md).

These firmware facts come from reading WIZnet's source and haven't been tested on a board yet.

## Development setup

1. Install VS Code and the recommended extensions (`.vscode/extensions.json`), in particular **MicroPico** (`paulober.pico-w-go`).
2. Flash the firmware (above).
3. Use MicroPico's upload-project command. It uploads everything in `src/` (set by `micropico.syncFolder`) to the board's root. `main.py` runs at boot.
4. Plug the board into a network with DHCP, then open `http://hymn.local` from a device on the same network.

### Repo layout

| Path | What it is |
| --- | --- |
| `src/` | Exactly what goes on the board. |
| `src/main.py` | Hardware, network, pass-through, web server and Display Timeout. Needs the board. |
| `src/protocol.py` | Song Number → UART1 bytes. Pure, so it runs and is tested on a laptop. |
| `src/index.html` | The phone keypad page. |
| `tests/` | Tests for `protocol.py`. |

### Tests

The byte protocol is tested on MicroPython's Unix port (the release the WIZnet firmware is built on) and on CPython. CI runs both on every push and pull request. Locally, from the repo root:

```bash
brew install micropython
```

```bash
micropython tests/test_protocol.py
```

`main.py` still can't run without the hardware: [#12](https://github.com/oalc-mtka/hymn-display-remote-keypad/issues/12).

## Preparing a device to ship

Follow the [engineer's setup guide](docs/engineers-setup.md): flash, upload, record the MAC address, bench test, ship. It also lists what's changed from the Pico W version.

## How it works

`main.py` runs three things on one `uasyncio` loop:

- **Network.** It brings up the W6100 with DHCP, using hostname `hymn` (answered as `hymn.local` over mDNS).
- **Pass-through.** Every byte from the Bottom Display on UART0 is copied unchanged to UART1.
- **Web server** on port 80:

| Request | What it does |
| --- | --- |
| `GET /` | Serves `index.html`, the phone keypad. |
| `GET /on?code=NNN` | Shows a Song Number (1–999; leading zeros are stripped, so `007` is sent as `7` to both displays). If a Display Timeout is running, it blanks the Top Display first. Then it sends one keypad code per digit (50 ms apart), the Top Display frame twice, and starts the 7-minute Display Timeout. |
| `GET /off` | If a Display Timeout is running, it cancels it and blanks the Top Display. Then it sends the keypad Clear code. |

### Byte protocol on UART1

The protocol mirrors the original C firmware (the C source isn't in this repo). It's all in `src/protocol.py`.

- **Keypad codes**, one byte per key: `0`=`0x17`, `1`=`0x33`, `2`=`0x67`, `3`=`0x19`, `4`=`0x32`, `5`=`0x65`, `6`=`0x0C`, `7`=`0x5F`, `8`=`0x63`, `9`=`0x5E`, Send=`0x5D` (defined but never sent), Clear=`0x06`.
- **Top Display frame** (`sendToTop()`): 6 bytes. These are the 7-segment patterns for the third, second and first digit with bit 7 cleared, then the same three bytes with bit 7 set. Leading positions are blank (`0x00`). It's always sent twice.
- **Blank the Top Display** (`clearTop()`): `00 00 00 80 80 80`, always sent twice.

The Remote Keypad keeps its own Display Timeout rather than leaving it to the bench firmware. See [ADR 0002](docs/adr/0002-remote-keypad-keeps-its-own-timeout.md) before changing that.

## License

MIT. Copyright Old Apostolic Lutheran Church of America. See [LICENSE](LICENSE).
