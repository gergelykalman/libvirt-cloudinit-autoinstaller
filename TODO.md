# TODO after install
- change node cpu to "host"
- add the machine to the default network, and add the interface
  to dhcp with `virsh net-edit --network default`
- set resolv.conf properly
- set up iptables reverse rules so that the instance is accessible
  - in /etc/libvirt/hooks/qemu

