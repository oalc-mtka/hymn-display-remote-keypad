# Remote Keypad: Engineer's Setup Guide

For whoever flashes, tests and ships Remote Keypads. If you've set up the old Pico W version, read [What's changed](#whats-changed-from-the-pico-w-version) first. Locality volunteers don't need this: they get a ready device and the [installer's guide](installers-guide.md).

> **Not yet tried on a board.** These steps come from WIZnet's and MicroPico's docs and source. Fix this guide as soon as someone runs through it.

## What's changed from the Pico W version

| | Pico W version (deprecated) | Now |
| --- | --- | --- |
| Board | Raspberry Pi Pico W | WIZnet **W6100-EVB-Pico2** (RP2350, Ethernet jack, USB-C) |
| Firmware | MicroPython for Pico W, from micropython.org | **WIZnet's** MicroPython build, the **LWIP** file for **PICO2** (step 1) |
| Files on the board | `main.py`, `index.html` | `main.py`, **`protocol.py`**, `index.html`, all from the repo's `src/` folder |
| How phones connect | The board's own hidden Wi-Fi hotspot, "Hymn" | The Locality's wired network, at `http://hymn.local` |
| Bench wiring | UART0 RX on GP1, UART1 TX on GP4 (GP5 RX, unused) | **Unchanged.** WIZnet says the board has the same pinout as a Pico 2, so these are still physical pins 2, 6 and 7. |
| Pins you can't use | — | **GP16–GP21** belong to the Ethernet chip. Don't wire anything to them. |
| Per-board record | — | The **MAC address**, printed on the label (step 3) |

## You need

- A W6100-EVB-Pico2 and a USB-C **data** cable (some cables only charge).
- A computer with VS Code and the **MicroPico** extension. See [Development setup](../README.md#development-setup).
- This repo, checked out.
- A network cable into a network with DHCP (a home router is fine), and a phone on the same network.

## 1. Flash the firmware

1. From WIZnet's [v1.29.0-WIZnet-timeout release](https://github.com/WIZnet-ioNIC/WIZnet-EVB-Pico-micropython/releases/tag/v1.29.0-WIZnet-timeout) (or later), download **`LWIP-W6100_EVB_PICO2-v1.29.0-preview.uf2`**. Read the name carefully, because the release has several files that look almost the same:
   - `…W6100_EVB_PICO-…` without the **2** is for the older RP2040 board and won't run on this one.
   - The `TOE-…` file boots and serves the page, but `hymn.local` never works on it.
2. Hold **BOOTSEL**, plug the USB cable into the computer, then let go. A drive appears (on RP2350 boards it's normally called `RP2350`).
3. Copy the `.uf2` onto that drive. The board restarts by itself and the drive disappears.
4. In VS Code, connect with **MicroPico: Connect** and open the MicroPico terminal (the REPL). Check the firmware:

   ```python
   import os, network
   os.uname().machine   # expect 'W6100-EVB-Pico2 with RP2350'
   os.uname().release   # expect '1.29.0…' or later
   network.WIZNET6K     # must not raise AttributeError (stock MicroPython has no WIZNET6K)
   import lwip          # must not raise ImportError (the TOE build has no lwip)
   ```

## 2. Upload the app

1. In VS Code, open the **repo's root folder**, not `src/`. The setting that tells MicroPico to upload only `src/` is in the root's `.vscode/settings.json`.
2. On a board that has been used before, run **MicroPico: Delete All Files from Board** first so no old files are left behind.
3. Run **MicroPico: Upload Project to Board**. It copies everything in `src/` to the top level of the board.
4. Check that exactly these files are on the board:

   ```python
   import os
   os.listdir()   # ['index.html', 'main.py', 'protocol.py'], in any order
   ```

> **Don't upload files one at a time with "Upload File to Board", as you may have done for the Pico W.** If `protocol.py` is missing, `main.py` stops at its first line with `ImportError: no module named 'protocol'`. Then nothing runs, including the pass-through from the Song Leaders' Bench to the Top Display.

## 3. Record the MAC address

Print the MAC address on the label, with a blank line next to it for a fallback IP (see [Advanced Installation](installers-guide.md#advanced-installation)). It's there for phones that can't open `hymn.local`: the router admin reserves a fixed IP for this MAC address so those phones can use the IP instead ([ADR 0001](adr/0001-wired-network-no-login.md)). The firmware builds the MAC from the RP2350's unique ID, so it's fixed for each board and stays the same after re-flashing.

Until the app prints it at boot ([#5](https://github.com/oalc-mtka/hymn-display-remote-keypad/issues/5)), stop `main.py` with Ctrl-C in the REPL and run:

```python
import machine, network
spi = machine.SPI(0, baudrate=20_000_000, sck=machine.Pin(18), mosi=machine.Pin(19), miso=machine.Pin(16))
nic = network.WIZNET6K(spi, machine.Pin(17), machine.Pin(20))
nic.active(True)
print(':'.join('%02x' % b for b in nic.config('mac')))
```

## 4. Bench test

1. Plug in the network cable **first**, then run **MicroPico: Restart Board and Show Output**.
2. Within about 15 seconds the output should show `Connected! IP Address: …` and then `Web Server Active!`. Write down the IP address.
3. On a phone on the same network, open `http://hymn.local`. If it doesn't open, try `http://<the IP address>`. If the IP works and `hymn.local` doesn't, see Troubleshooting.
4. Enter **1 2 3** and tap Send. The output should show `Sending '123' to both displays...`. If the board is wired into a Hymn Display Board, the Top Display shows **123**.
5. Tap Clear. The output should show `Received OFF command…`, and the Top Display blanks.
6. If it's wired in, also do the bench-keypad check from the [installer's guide](installers-guide.md#basic-installation-checklist), with the Remote Access Switch both off and on.

## 5. Ship it

- The label shows the MAC address and has a blank line for the fallback IP.
- Include the [song leader guide](song-leader-guide.md) and the [installer's guide](installers-guide.md).

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| No drive appears in step 1 | Charge-only cable, or BOOTSEL let go too early | Use a data cable. Hold BOOTSEL until the drive appears. |
| `AttributeError: … WIZNET6K` | Stock MicroPython, not WIZnet's build | Flash again (step 1). |
| `ImportError: no module named 'protocol'` | Files uploaded one at a time | Do step 2 again. |
| The IP works but `hymn.local` doesn't | The TOE firmware, or the network blocks mDNS | Check `import lwip` (step 1). If the firmware is right, see [Advanced Installation](installers-guide.md#advanced-installation) step 4. |
| Stuck on `Connecting to network...`, or an `OSError` after about 10 seconds and the program stops | No cable, a dead port, or no DHCP. The program doesn't retry yet ([#1](https://github.com/oalc-mtka/hymn-display-remote-keypad/issues/1)). | Check the cable and network, then restart the board. |
