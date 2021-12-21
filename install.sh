#!/bin/bash

set -e

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $BASE_DIR

### Check dependencies
if [[ ! -f ssh_key ]]
then
    echo "Please put your SSH pubkey into $BASE_DIR/ssh_key file!"
    exit 1
fi
### END


### START PARAMETERS
# To get OSVARIANT: osinfo-query os
# NOTE: Only debian10 is supported right now for me, not debian 11

# To generate password: mkpasswd --method=SHA-512 --rounds=4096
# NOTE: Even though SSH password login is disabled, please change the password,
#       by default it's the empty string!

KVM_PARAM_OSVARIANT=debian10
BASE_IMG="$BASE_DIR/images/debian-11-generic-amd64.qcow2"

VM_NAME=test
HOSTNAME=test
KVM_PARAM_MEMORY=2048
KVM_PARAM_VCPU=2
PASSWORD='$6$rounds=4096$EUIV1CgxDGsMp3kb$eN79CWQDhUFdF2cEWqGoTeOB0r6sqs1JRNMbeWJm/U4/y9GpJZTMtIsNl1h8BTdJ7Lc6ASzlhgSTKwolZuFBk/'
SSH_AUTHORIZED_KEYS=$(cat ssh_key)
#NET_ADDR=192.168.1.10
#NET_NET=192.168.1.0
#NET_NETMASK=255.255.255.0
#NET_BROADCAST=192.168.1.255
#NET_GATEWAY=192.168.1.254
DISK_ENLARGEMENT=10G
### END PARAMETERS


VM_DISK_ROOT="$BASE_DIR/vms/$VM_NAME"
DISK_IMG="$VM_DISK_ROOT/root.qcow2"
CLOUDCONFIG_IMG="$VM_DISK_ROOT/cloud-init.iso"


### copying images
if [[ -d "$VM_DISK_ROOT" ]]
then
    echo "VM at $VM_DISK_ROOT already exists, aborting!"
    exit 1
fi

mkdir -p "$VM_DISK_ROOT"
cp "$BASE_IMG" "$DISK_IMG"
qemu-img resize $DISK_IMG "+$DISK_ENLARGEMENT"
echo $DISK_IMG
### END


### cloud-init
# to generate password:
# mkpasswd --method=SHA-512 --rounds=4096
echo "[+] Generating cloud init configuration"

echo "local-hostname: $HOSTNAME
network-interfaces: |
  iface eth0 inet dhcp
#  address $NET_ADDR
#  network $NET_NET
#  netmask $NET_NETMASK
#  broadcast $NET_BROADCAST
#  gateway $NET_GATEWAY
" > meta_data

echo "#cloud-config
hostname: $VM_NAME
packages:
  - qemu-guest-agent
users:
  - name: root
    lock_passwd: false
    hashed_passwd: $PASSWORD
    ssh_authorized_keys: $SSH_AUTHORIZED_KEYS
ssh_pwauth: no
#package_update: true
runcmd:
  - systemctl enable qemu-guest-agent
  - systemctl start qemu-guest-agent
" > user_data

cloud-localds $CLOUDCONFIG_IMG user_data meta_data && rm user_data meta_data
### END



### virt-install
# TODO: host-passthugh
echo "[+] Calling virt-install"
virt-install --name "$VM_NAME"\
    --virt-type kvm \
    --hvm \
    --os-variant="$KVM_PARAM_OSVARIANT"\
    --memory "$KVM_PARAM_MEMORY"\
    --vcpus "$KVM_PARAM_VCPU"\
    --network network=default,model=virtio\
    --graphics spice\
    --disk "$DISK_IMG",device=disk,bus=virtio\
    --disk "$CLOUDCONFIG_IMG",device=cdrom\
    --noautoconsole\
    --import

echo "[+] Domain successfully created: $VM_NAME"
#echo ""
#echo "[+] Spawning console in 3 seconds, press Ctrl-C to abort:"
#for i in $(seq 3)
#do
#    sleep 1
#    echo -n "."
#done
#
#echo
echo "[+] Launching console"
virsh console "$VM_NAME"
### END

