import subprocess


def enlarge_image(imagename, extrasize_bytes):
    # TODO: do this without subprocess
    subprocess.check_call([
        "qemu-img", "resize", imagename, "+{}".format(extrasize_bytes)
    ])
