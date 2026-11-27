#!/usr/bin/env bash
# TUN setup and routing for one node.
#
# Usage:
#   sudo ./setup_tun.sh up A            # Node A -> 10.8.0.1
#   sudo ./setup_tun.sh up B            # Node B -> 10.8.0.2
#   sudo ./setup_tun.sh up A eth0       # also enable NAT out of eth0 (exit node)
#   sudo ./setup_tun.sh down A
#   ./setup_tun.sh status
set -euo pipefail

DEV="${TUN_DEV:-tun0}"
MTU="${TUN_MTU:-1400}"
SUBNET="10.8.0.0/24"
USER_NAME="${SUDO_USER:-$USER}"

ip_for() {
  case "$1" in
    A|a) echo "10.8.0.1" ;;
    B|b) echo "10.8.0.2" ;;
    *) echo "node must be A or B" >&2; exit 1 ;;
  esac
}

cmd="${1:-}"

case "$cmd" in
  up)
    node="${2:?node A or B required}"
    wan="${3:-}"
    addr="$(ip_for "$node")"

    ip tuntap add dev "$DEV" mode tun user "$USER_NAME"
    ip addr add "$addr/24" dev "$DEV"
    ip link set dev "$DEV" mtu "$MTU" up
    sysctl -w net.ipv4.ip_forward=1 >/dev/null

    if [ -n "$wan" ]; then
      iptables -t nat -A POSTROUTING -s "$SUBNET" -o "$wan" -j MASQUERADE
      echo "NAT enabled for $SUBNET out of $wan"
    fi
    echo "$DEV up with $addr/24, MTU $MTU"
    ;;

  down)
    node="${2:?node A or B required}"
    wan="${3:-}"
    if [ -n "$wan" ]; then
      iptables -t nat -D POSTROUTING -s "$SUBNET" -o "$wan" -j MASQUERADE || true
    fi
    ip link del "$DEV" || true
    echo "$DEV removed"
    ;;

  status)
    ip addr show "$DEV"
    ip route show dev "$DEV"
    ;;

  *)
    echo "usage: $0 {up|down} {A|B} [wan_iface]   |   $0 status" >&2
    exit 1
    ;;
esac
