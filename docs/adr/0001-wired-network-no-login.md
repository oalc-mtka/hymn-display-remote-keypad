# Remote Keypad joins the Locality's wired network at hymn.local, with no login

The first Remote Keypad ran its own open, hidden Wi-Fi hotspot ("Hymn"); a login page was tried and dropped, and WPA2 couldn't be enforced on the Pico W hotspot (micropython discussion #17059). The Remote Keypad now always uses Ethernet (WIZnet W6100-EVB-Pico2) on each Locality's own network, reachable at `http://hymn.local`, with no login of its own: securing that network is the Locality's job. Wi-Fi is deprecated; it survives only in git history and will be revisited if a Locality without a wired drop needs it.

## Considered Options

- **Own open hotspot (the original design):** no setup, but anyone in range who knows the SSID can change the Top Display, and WPA2 can't be enforced.
- **Join the Locality's Wi-Fi:** a Pico W has no keyboard, so credentials must be baked in at flash time (the Locality sends its Wi-Fi password to developers and re-flashes on every change) or entered through a setup hotspot (new code to build and support). Ethernet's DHCP needs neither.

## Consequences

- `hymn.local` only works on WIZnet's **LWIP** firmware build (v1.29.0-WIZnet-timeout or later); the TOE build has no mDNS and ignores the hostname. The firmware build is part of the deployment, not a detail.
- Anyone on the Locality's network can change the Top Display. The Remote Keypad is used only from inside the building, on the staff network, never from guest Wi-Fi and never exposed to the internet (no port forwarding).
- Older Android phones may not resolve `.local` names, so an Advanced Installation reserves a fallback IP on the router by MAC address. The MAC is fixed per board (the firmware derives it from the RP2350's unique ID), and developers print it on the label before shipping.
