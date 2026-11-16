# Remote Keypad: Installer's Guide

For whoever sets up a Remote Keypad at a Locality. There are two parts:

- **Basic Installation:** no passwords or router access needed. Most Localities only need this.
- **Advanced Installation:** for whoever manages the church's router. It adds a fixed fallback address for phones that can't open `hymn.local`. Hand that section to them.

Your Remote Keypad arrives ready to use. The label shows its **MAC address** and has a blank line for a **fallback IP**.

---

## Basic Installation checklist

- [ ] **Remote Access Switch OFF.**
- [ ] Plug a network cable from a **staff network** port (wall jack or network switch, not a guest port) into the Remote Keypad.
- [ ] Turn the **Remote Access Switch ON** and wait about 30 seconds.
      *The cable must be plugged in **before** you turn it on. If you plug it in afterwards, turn the switch off and on again.*
- [ ] Connect a phone to the **staff Wi-Fi** and open **`http://hymn.local`**. The keypad page should appear.
- [ ] Type **1 2 3** and tap **On**. The board facing the congregation shows **123**.
- [ ] Tap **Off**. The board blanks.
- [ ] Try it from a second phone, ideally one Android and one iPhone. If one can't open `hymn.local`, see Troubleshooting.
- [ ] Turn the **switch OFF** and enter a number on the **Song Leaders' Bench keypad**. Check that it shows on the board. Then turn the switch **ON** and check again. *If the bench keypad stops working in either position, stop and contact support.*
- [ ] Turn the **switch OFF**. Leave the [song leader guide](song-leader-guide.md) with the box.

---

## Advanced Installation

*For whoever manages the church's network. Needs admin access to the router.*

The Remote Keypad is a small wired device that gets its address by DHCP and calls itself **`hymn`**. Phones normally reach it at `http://hymn.local` (mDNS). Some phones and networks can't resolve `.local` names, so we'd like a fixed fallback address.

1. **Reserve an IP address** for the MAC address on the label. Your router may call this "DHCP reservation", "static lease", "address reservation" or "fixed IP". Your router maker's help pages will show where it is.
2. **Write that IP on the label**, as `http://<ip>`.
3. **Same network:** the Remote Keypad's wired port and the **staff Wi-Fi** must be on the same network (same subnet/VLAN). Phones on the guest network must **not** be able to reach it.
4. **Allow mDNS** (multicast on UDP port 5353) between wired and wireless devices on the staff network. Some mesh and business Wi-Fi systems block it, or have a "multicast/mDNS" or "client isolation" setting.
5. **Never expose it to the internet.** No port forwarding. The Remote Keypad has no password: anyone who can reach it can change the board.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `hymn.local` doesn't open on any phone | Phone is on the guest Wi-Fi | Join the staff Wi-Fi. |
| | Cable plugged in after switching on | Turn the switch off and on again. |
| | Dead wall jack or wrong network port | Check the link light on the Remote Keypad's network jack, or try another port. |
| Works on iPhones, not on some Android phones | Older Android versions can't open `.local` addresses | Use the fallback IP (Advanced Installation). |
| Works from a wired computer, not from phones | Wi-Fi is blocking mDNS between wireless and wired devices | Use the fallback IP, or ask the network manager to allow mDNS (step 4). |
| Fallback IP worked before, not now | No reservation was made, so the address changed | Do Advanced Installation step 1. |
| The page opens but the board doesn't change | Remote Keypad needs a restart | Turn the switch off, wait 10 seconds, turn it on. |
| **The Song Leaders' Bench keypad stops working** | The Remote Keypad may be in the line to the board | Turn the Remote Access Switch off and contact support right away. |

## Support

Contact: **TBD**
