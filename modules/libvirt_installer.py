import subprocess
import time

import libvirt


class LibvirtWrapper:
    def __init__(self):
        self.__conn = libvirt.open(None)

    def __waitstate(self, dom, needed_state, sleeptime=0.1):
        while True:
            state, _ = dom.state()
            # print("Current state: {}, required: {}".format(state, needed_state))
            if state == needed_state:
                break
            time.sleep(sleeptime)

    def install(self, name, osvariant, memory, cpucount, diskimg,
                cloudconfig_img):

        # TODO: do this without subshells and actually use libvirt!
        subprocess.check_output([
            "virt-install",
            "--name", name,
            "--virt-type", "kvm",
            "--hvm",
            "--os-variant={}".format(osvariant),
            "--memory", "{}".format(memory),
            "--vcpus", "{}".format(cpucount),
            "--network", "network=default,model=virtio",
            "--graphics", "spice",
            "--disk", "{},device=disk,bus=virtio".format(diskimg),
            "--disk", "{},device=cdrom".format(cloudconfig_img),
            "--noautoconsole",
            "--import"
        ])

    def shutdown(self, name):
        dom = self.__conn.lookupByName(name)

        # TODO: make sure shutdown is successful
        #self.__waitstate(dom, libvirt.VIR_DOMAIN_RUNNING)
        dom.shutdown()
        self.__waitstate(dom, libvirt.VIR_DOMAIN_SHUTOFF)

    def undefine(self, name):
        dom = self.__conn.lookupByName(name)
        dom.undefine()
