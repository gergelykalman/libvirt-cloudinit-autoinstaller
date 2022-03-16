import tempfile
import subprocess

from modules.cloudinit_templates import user_data_tpl, meta_data_tpl


def generate_cloudinit_configs(hostname, net_iface, net_addr, net_net,
                               net_netmask, net_broadcast, net_gateway,
                               vm_name, passwordhash, ssh_authorized_keys):
    meta_data = meta_data_tpl.substitute({
        "HOSTNAME": hostname,
        "NET_IFACE": net_iface,
        "NET_ADDR": net_addr,
        "NET_NET": net_net,
        "NET_NETMASK": net_netmask,
        "NET_BROADCAST": net_broadcast,
        "NET_GATEWAY": net_gateway,
    })

    user_data = user_data_tpl.substitute({
        "VM_NAME": vm_name,
        "PASSWORDHASH": passwordhash,
        "SSH_AUTHORIZED_KEYS": ssh_authorized_keys,
    })
    return meta_data, user_data


def generate_cloudinit_iso(meta_data, user_data, iso_filename):
    with tempfile.NamedTemporaryFile(mode="wt") as m, \
         tempfile.NamedTemporaryFile(mode="wt") as u:
        m.write(meta_data)
        u.write(user_data)

        m.flush()
        u.flush()

        # TODO: do this without subshell
        subprocess.check_output(["cloud-localds", iso_filename,
                                 m.name, u.name])
