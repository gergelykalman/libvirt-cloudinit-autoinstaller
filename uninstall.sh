#!/bin/bash

set -e

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $BASE_DIR

if [[ $1 == "" ]]
then
    echo "VM_NAME not specified!"
    exit 1
fi

VM_NAME="$1"

echo "##################"
echo "###  WARNING!  ###"
echo "##################"
echo "You are about to remove VM: $VM_NAME"
echo "You will LOSE ALL FILES and VM configuration"
echo -n "Are you sure (yes/no)?: "

read answer
if [[ $answer != "yes" ]]
then
    exit 1
fi

### Uninstall
set +e

echo "[+] Shutting down VM"
virsh shutdown "$VM_NAME"
sleep 3

echo "[+] Undefining VM"
virsh undefine "$VM_NAME"

echo "[+] Removing files for VM"
rm -rfv "vms/$VM_NAME"

set -e
### END

