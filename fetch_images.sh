#!/bin/bash

set -e

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $BASE_DIR


DEBIAN_11_URL=https://cloud.debian.org/images/cloud/bullseye/latest/debian-11-generic-amd64.qcow2

cd images
echo "[+] Fetching debian cloud image"
wget --continue "$DEBIAN_11_URL"

echo "[+] All files fetched"

