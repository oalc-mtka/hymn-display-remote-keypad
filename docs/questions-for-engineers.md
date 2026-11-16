# Questions for the Engineers

Questions about the Hymn Display Board hardware and firmware that the Remote Keypad code depends on. Answers go into the README (wiring, protocol) or an ADR, and resolve the matching [`needs-info` issues](https://github.com/oalc-mtka/hymn-display-remote-keypad/issues?q=is%3Aopen+label%3Aneeds-info).

1. **Wiring.** What is connected to the Remote Keypad's UART0 RX (GP1) and UART1 TX (GP4)? Does the Remote Keypad sit **in the line** between the Bottom Display and the Top Display? The code copies every byte from UART0 to UART1, which suggests it does.
2. **Remote Access Switch.** What exactly does it cut? With it off, does the Song Leaders' Bench keypad still reach the Top Display, or does the switch also route the line around the Remote Keypad?
3. **Bench Display Timeout.** Does the bench firmware run its own 7-minute Display Timeout? (See [ADR 0002](adr/0002-remote-keypad-keeps-its-own-timeout.md).)
4. **Send key.** The Remote Keypad sends a keypad code for each digit but never sends the Send code (`0x5D`). What does the Bottom Display show as a result, and should it send Send?
5. **Zero.** Does sending 0 (from the bench) blank the Top Display?
6. **Overlapping byte values.** Two Top Display segment bytes have the same values as keypad codes: the 7-segment "1" is `0x06`, the same as the Clear key, and "9" is `0x67`, the same as keypad "2". Does any device on the UART1 line read both kinds of byte? If so, how does it tell them apart?
7. **Sent twice.** Why is every Top Display frame and every blanking sequence sent twice? Is it for reliability, or does the receiver need it?
8. **Firmware source.** Where is the C firmware source for the Hymn Display Board? Can it go in the repo, or be linked from it?
