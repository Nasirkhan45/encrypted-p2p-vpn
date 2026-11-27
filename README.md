# Encrypted P2P VPN Tunnel: TUN setup and routing

Part of the team project: an encrypted peer-to-peer VPN over UDP using Linux TUN interfaces.

This folder is the **TUN setup and routing** part (Abdul Nasir). It gives the rest of the
team a working virtual interface on both nodes and a tiny API to read and write raw IP packets.

## What is here

| File | Purpose |
|---|---|
| `setup_tun.sh` | Creates `tun0`, assigns the VPN IP, sets MTU, enables IP forwarding, optional NAT |
| `tun_device.py` | `open_tun()`, `read_packet()`, `write_packet()` for the UDP tunnel and crypto modules |
| `tun_sniff.py` | Demo that prints every packet the kernel routes into `tun0` |

## Addressing

| Node | VPN IP |
|---|---|
| A | 10.8.0.1/24 |
| B | 10.8.0.2/24 |

MTU is 1400 to leave room for the outer IP (20) + UDP (8) + AES-GCM nonce and tag (about 28).

## Quick start

```bash
# Node A
sudo ./setup_tun.sh up A
python3 tun_sniff.py

# Node B
sudo ./setup_tun.sh up B

# From Node A, in another terminal
ping 10.8.0.2
```

You should see ICMP packets printed by `tun_sniff.py`. Nothing is encrypted yet; that is
the next layer.

Optional exit node with NAT (replace `eth0` with your internet interface):

```bash
sudo ./setup_tun.sh up A eth0
```

Clean up:

```bash
sudo ./setup_tun.sh down A
```

## How the others use this

```python
from tun_device import open_tun, read_packet, write_packet

fd = open_tun("tun0")
pkt = read_packet(fd)        # plaintext IP packet -> encrypt -> send over UDP
write_packet(fd, decrypted)  # packet received from the peer -> inject back
```

## Design notes

- **TUN, not TAP:** we only need Layer 3 (IP packets), not Ethernet frames.
- **`IFF_NO_PI`:** removes the 4-byte packet info header so reads are plain IP packets.
- **UDP transport:** avoids TCP-over-TCP retransmission conflicts.
- **Routing:** assigning `10.8.0.x/24` to `tun0` makes the kernel add `10.8.0.0/24 dev tun0`,
  so traffic for the VPN subnet goes into our program.
