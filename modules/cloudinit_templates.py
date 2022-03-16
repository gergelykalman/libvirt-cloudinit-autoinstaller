from string import Template

meta_data_tpl = Template("""local-hostname: $HOSTNAME
network-interfaces: |
    iface $NET_IFACE inet dhcp
    address $NET_ADDR
    network $NET_NET
    netmask $NET_NETMASK
    broadcast $NET_BROADCAST
    gateway $NET_GATEWAY""")

user_data_tpl = Template("""cloud-config
hostname: $VM_NAME
packages:
  - qemu-guest-agent
users:
  - name: root
    lock_passwd: false
    hashed_passwd: $PASSWORDHASH
    ssh_authorized_keys: $SSH_AUTHORIZED_KEYS
ssh_pwauth: no
#package_update: true
runcmd:
  - systemctl enable qemu-guest-agent
  - systemctl start qemu-guest-agent
""")
