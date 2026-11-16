# Review Findings (issue drafts)

These are drafted from a code review of this repo and [sarki012/hymn_control_ethernet](https://github.com/sarki012/hymn_control_ethernet), held here until the repo moves to `oalc-mtka/hymn-display-remote-keypad`. File each one as a GitHub issue there with its label, then delete this file.

Line numbers refer to the Ethernet `main.py`.

---

## 1. Start the bench pass-through before networking, and never stop it
**Label:** `ready-for-agent` · **Priority:** must-fix

The UART0→UART1 pass-through (`uart_relayer`) is only started after the network comes up. In the Ethernet version, with no cable or no DHCP server, `nic.ifconfig('dhcp')` raises `OSError` after about 10 s. Nothing catches it, so `main()` exits and the program stops. If the Remote Keypad is in the line (see [questions-for-engineers.md](questions-for-engineers.md) #1), the Song Leaders' Bench can't reach the Top Display until someone power-cycles the box with a cable plugged in.

**Done when:**
- The pass-through task starts first, before any networking.
- A network failure is caught and retried in the background, and never ends the program.
- Booting with no cable keeps the pass-through working, and plugging the cable in later brings the web page up without a restart.
- Any unexpected crash restarts the board (for example `machine.reset()`, or a watchdog).

## 2. Header loop spins forever when a client disconnects
**Label:** `ready-for-agent`

`main.py:185`: `while await reader.readline() != b"\r\n"` never ends if the client closes early, because `readline()` then returns `b""` forever. That connection is never closed.

**Done when:** the loop also stops on `b""`, and the connection is closed.

## 3. Malformed HTTP responses
**Label:** `ready-for-agent`

`main.py:192` always sends `200 OK` first. For an unknown path, including the `/favicon.ico` every browser requests, it then writes a second `404` status line into the body. Validation errors also come back as `200`.

**Done when:** each response has exactly one status line: `200` for success, `400` for a bad Song Number, `404` for an unknown path.

## 4. Validate Song Numbers properly
**Label:** `ready-for-agent`

Today `0`, `00` and `000` are accepted. Leading zeros are stripped for the Top Display but not for the Bottom Display: `007` sends keypad 0, 0, 7 but shows "  7" on top.

**Done when:** the server strips leading zeros and accepts only 1–999. The same normalised digits go to both displays. `0` is rejected with `400`. See the glossary for the definition of a Song Number.

## 5. Ethernet start-up clean-up
**Label:** `ready-for-agent`

- `nic.config(hostname="hymn")` always raises `ValueError` (the WIZNET6K driver only accepts `mac` and `trace`), and a bare `except: pass` hides it. Keep `network.hostname("hymn")`, which must run before `active(True)`, and remove the rest.
- It prints `http://hymn/`. Print `http://hymn.local`, the IP address and the **MAC address** instead. Developers need the MAC for the label (see README, "Preparing a device to ship").
- Replace the fixed `time.sleep(3)` "stabilising rails" delay with the retry from #1, unless the engineers say the delay is needed.

## 6. Phone page should match the bench keypad
**Label:** `needs-info` (waiting on a check of the bench behaviour)

The phone buttons say **On/Off**, but the bench says **Send/Clear**. Off also wipes the typed digits, so you can't show the same song again after blanking. Typing after a Send adds digits to the old number instead of starting a new one.

**Needs:** on the bench, (a) does Clear keep the number on the Bottom Display, and (b) do new digits after a Send replace the old number?
**Then:** rename the buttons to Send/Clear (and the `/on` and `/off` endpoints to match), and copy the bench's behaviour exactly.

## 7. The Remote Keypad never sends the Send key
**Label:** `needs-info` (engineers #4)

`KEYPAD_ENTER` (`0x5D`) is defined but never sent. The Bottom Display gets digits with no Send after them.

## 8. Byte values overlap between the two displays
**Label:** `needs-info` (engineers #6)

The 7-segment "1" is `0x06`, the same as `KEYPAD_CLEAR`, and "9" is `0x67`, the same as keypad "2". This only matters if one receiver reads both.

## 9. Phone page doesn't show what the board is actually showing
**Label:** `needs-triage`

The page keeps flashing the number after the Display Timeout has blanked the board, and shows nothing after a reload. Two phones each show their own local guess.

## 10. Use the glossary's terms in the code
**Label:** `ready-for-agent`

Rename to match [CONTEXT.md](../CONTEXT.md): `hymn_code_str`/`code_str` → `song_number`, `manage_seven_minute_timer`/`timer_*` → Display Timeout, "physical keypad" → Bottom Display. Remove the stale comment "The original values were incorrect…". Do this with or after #6 so the endpoint names change only once.

## 11. Remove dead code
**Label:** `ready-for-agent`

`perform_blink_cycle` and `led` (unused), `import socket`, `blink.py`, and `config.html` (only a license header).

## 12. No way to test without hardware
**Label:** `needs-triage`

Every change needs a board wired into a real Hymn Display Board. Separating the byte-building (keypad codes, Top Display frames) from the UART would allow plain tests of the byte sequences. A fake UART would let the web server run on a laptop.

## 13. Finish the move to `oalc-mtka/hymn-display-remote-keypad`
**Label:** `ready-for-human`

The history, the Ethernet `main.py` and the docs are in this repo. Still to do:

- sarki012 archives `sarki012/hymnal_display_raspberry_pi_webapp` and `sarki012/hymn_control_ethernet`, each with a README line pointing here.
- Choose the support contact and replace **TBD** in the song leader guide and the installer's guide.
