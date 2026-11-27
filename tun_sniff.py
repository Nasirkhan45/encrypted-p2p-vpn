"""Demo: show that traffic for the VPN subnet lands in our program.

1. sudo ./setup_tun.sh up A
2. python3 tun_sniff.py
3. In another terminal: ping 10.8.0.2
"""
import socket

from tun_device import open_tun, read_packet

PROTOS = {1: "ICMP", 6: "TCP", 17: "UDP"}


def main():
    fd = open_tun("tun0")
    print("Listening on tun0. Ping the other VPN address to see packets.")
    while True:
        pkt = read_packet(fd)
        version = pkt[0] >> 4
        if version != 4:
            print(f"{len(pkt)} bytes, IPv{version} (ignored)")
            continue
        proto = PROTOS.get(pkt[9], str(pkt[9]))
        src = socket.inet_ntoa(pkt[12:16])
        dst = socket.inet_ntoa(pkt[16:20])
        print(f"{len(pkt):4d} bytes  {src} -> {dst}  {proto}")


if __name__ == "__main__":
    main()
