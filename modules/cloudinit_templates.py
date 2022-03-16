from string import Template

kvm_metadata_tpl = Template("""local-hostname: $HOSTNAME
network-interfaces: |
    iface $NET_IFACE inet dhcp
    address $NET_ADDR
    network $NET_NET
    netmask $NET_NETMASK
    broadcast $NET_BROADCAST
    gateway $NET_GATEWAY""")

kvm_userdata_tpl = Template("""cloud-config
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

ec2_userdata_tpl = Template("""#cloud-config
cloud_final_modules:
- [users-groups,always]
users:
  - name: vmmanager
    groups: [ wheel ]
    sudo: [ "ALL=(ALL) NOPASSWD:ALL" ]
    shell: /bin/bash
    ssh-authorized-keys: 
    - $SSH_KEY
""")
