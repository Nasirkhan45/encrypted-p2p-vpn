"""TUN device helper (Abdul Nasir's part).

Other modules use this like:

    from tun_device import open_tun, read_packet, write_packet
    fd = open_tun("tun0")
    pkt = read_packet(fd)      # one raw IP packet leaving this machine
    write_packet(fd, pkt)      # inject a raw IP packet into this machine
"""
import fcntl
import os
import struct

TUNSETIFF = 0x400454CA
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000  # no 4-byte packet-info header, we get plain IP packets

MAX_PACKET = 2048  # larger than any packet at MTU 1400


def open_tun(name: str = "tun0") -> int:
    """Attach to an existing TUN interface and return its file descriptor.

    The interface must already be created and up (see setup_tun.sh).
    """
    fd = os.open("/dev/net/tun", os.O_RDWR)
    ifr = struct.pack("16sH", name.encode(), IFF_TUN | IFF_NO_PI)
    fcntl.ioctl(fd, TUNSETIFF, ifr)
    return fd


def read_packet(fd: int) -> bytes:
    """Block until the kernel hands us one raw IP packet."""
    return os.read(fd, MAX_PACKET)


def write_packet(fd: int, packet: bytes) -> int:
    """Inject one raw IP packet into the kernel's network stack."""
    return os.write(fd, packet)
