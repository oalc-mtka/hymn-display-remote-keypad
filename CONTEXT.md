# Hymn Display Board

A custom-built system that shows the current song number to the congregation during services, used in about 15 localities. This repo adds a way to set the song number remotely when no song leader is sitting on the song leaders' bench.

## Language

### People and places

**Song Leader**:
The person who chooses and announces the songs (and verses) during a service.

**Song Leaders' Bench**:
The bench on one side of the altar where song leaders sit for most services, and where the Bottom Display is.
_Avoid_: Song bench

### The board

**Hymn Display Board**:
The whole installation in one locality: the Top Display, the Bottom Display, and the electronics behind them.
_Avoid_: Hymn board, the board, the display

**Top Display**:
The large display facing the sanctuary that shows the song number to the congregation.
_Avoid_: Main display, sanctuary display

**Bottom Display**:
The physical keypad unit on the Song Leaders' Bench, used to enter song numbers and show them on the Top Display. It is the owner of what is shown; the Remote Keypad is only for when nobody is on the bench.
_Avoid_: Bench display, physical keypad

**Song Number**:
The number of the song being sung: digits only, at most three, no leading zeros, never 0. The current hymnal's range is 1–300, but that is a hymnal fact, not a board rule.
_Avoid_: Hymn code, code, hymn number

**Send**:
The key that shows the entered Song Number on the Top Display. Pressing it again with no new digits shows the same Song Number again.
_Avoid_: On, Enter

**Clear**:
The key that blanks the Top Display.
_Avoid_: Off

### Remote access

**Remote Keypad**:
The add-on that lets someone set the Song Number from a phone or computer when nobody is on the Song Leaders' Bench (e.g. phone patches, viewings, gatherings).
_Avoid_: Pico, web app, phone app, remote control

**Remote Access Switch**:
The physical switch on the Hymn Display Board that turns the Remote Keypad off. It is off whenever a Song Leader is on the Song Leaders' Bench, so the Remote Keypad and the Bottom Display never compete.

**Basic Installation**:
Setting up a Remote Keypad at a Locality without access to the router's admin settings: cable in, switch on, confirm `hymn.local` works.

**Advanced Installation**:
The optional steps done by whoever manages the Locality's router: reserving a fallback IP for the Remote Keypad's MAC address and writing it on the label.
_Avoid_: Network setup

**Locality**:
One of the (about 15) places that has a Hymn Display Board. Each Locality is responsible for securing the network its Remote Keypad is on.
_Avoid_: Congregation, church, site, installation

**Display Timeout**:
The fixed 7-minute fallback after which the Top Display blanks itself in case a song leader forgets to turn it off. Only the Top Display blanks, so the same Song Number can be shown again after a pause (e.g. verses before and after a prayer).
_Avoid_: Seven-minute timer
