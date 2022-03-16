import sys
import os
import shutil
import crypt
import os.path
import urllib.request

from modules.cloudinit import generate_cloudinit_iso, generate_cloudinit_configs
from modules.libvirt_installer import LibvirtWrapper
from modules.qemu_images import enlarge_image


class VMManager:
    def __init__(self, basedir):
        base_dir = basedir
        self.__image_dir = os.path.join(base_dir, "images")
        self.__vm_dir = os.path.join(base_dir, "vms")
        self.__lvw = LibvirtWrapper()

    def download_file(self, url, name, bufsize=1024*1024):
        outfilename = os.path.join(self.__image_dir, name)
        print("Downloading to {}".format(outfilename))

        if not os.path.exists(self.__image_dir):
            os.makedirs(self.__image_dir, exist_ok=True)

        with open(outfilename, "wb") as outfile:
            with urllib.request.urlopen(url) as f:
                total = 0
                while True:
                    buf = f.read(bufsize)
                    if len(buf) == 0:
                        break
                    outfile.write(buf)
                    total += len(buf)
                    print("Total: {:.2f} MB".format(total/1024/1024))
        print("Done")

    def install(self, sshkeyfile):
        sshkey = open(sshkeyfile, "rt").read()

        hostname = "test"
        osvariant = "debian11"
        base_image = os.path.join(self.__image_dir, "debian-11-generic-amd64.qcow2")
        kvm_param_memory = 2048
        kvm_param_vcpu = 2
        password = "test"
        passwordhash = crypt.crypt(password)
        disk_extrasize = 10*1024*1024*1024

        vm_disk_dir = os.path.join(self.__vm_dir, hostname)
        vm_root = os.path.join(vm_disk_dir, "root.qcow2")
        vm_cloudconfig = os.path.join(vm_disk_dir, "cloud-init.iso")

        if os.path.exists(vm_disk_dir):
            print("VM as {} already exists, aborting!".format(vm_disk_dir))
            exit(1)

        print("[+] Preparing images")
        os.makedirs(vm_disk_dir, exist_ok=True)
        shutil.copy(base_image, vm_root)
        enlarge_image(vm_root, disk_extrasize)

        print("[+] Generating cloud init configuration")
        meta_data, user_data = generate_cloudinit_configs(
            hostname=hostname,
            net_iface="eth0",
            net_addr="192.168.1.10",
            net_net="192.168.1.0",
            net_netmask="255.255.255.0",
            net_broadcast="192.168.1.255",
            net_gateway="192.168.1.254",
            vm_name=hostname,
            passwordhash=passwordhash,
            ssh_authorized_keys=sshkey)

        generate_cloudinit_iso(meta_data, user_data, vm_cloudconfig)

        print("[+] Installing VM")
        self.__lvw.install(
            name=hostname,
            osvariant=osvariant,
            memory=kvm_param_memory,
            cpucount=kvm_param_vcpu,
            diskimg=vm_root,
            cloudconfig_img=vm_cloudconfig,
        )

    def uninstall(self):
        name = "test"

        print("[+] Shutting down domain {}".format(name))
        self.__lvw.shutdown(name)

        print("[+] Undefining domain {}".format(name))
        self.__lvw.undefine(name)

        print("[+] Deleting data for {}".format(name))
        vm_disk_dir = os.path.join(self.__vm_dir, name)
        shutil.rmtree(vm_disk_dir)

    def status(self):
        name = "test"
        print("{} state: {}".format(name, self.__lvw.status(name)))


if __name__ == "__main__":
    basedir = sys.argv[1]
    func = sys.argv[2]

    vmm = VMManager(basedir)
    if func == "download":
        url = "https://cloud.debian.org/images/cloud/bullseye/latest/debian-11-generic-amd64.qcow2"
        outfilename = "debian-11-generic-amd64.qcow2"
        vmm.download_file(url, outfilename)
    elif func == "install":
        vmm.install(".sshkey")
    elif func == "uninstall":
        vmm.uninstall()
    elif func == "status":
        vmm.status()
    else:
        print("Invalid func: {}".format(func))
        exit(1)
