import sys
import base64
import time
from pprint import pprint

import boto3

from modules.cloudinit_templates import ec2_userdata_tpl

TAGNAME = "Project"
TAGVALUE = "vmmanager"


class EC2Manager:
    def __init__(self):
        self.__ec2_client = boto3.client('ec2')
        self.__ec2_resource = boto3.resource('ec2')

    def printprices(self):
        price_history = self.__ec2_client.describe_spot_price_history(
            InstanceTypes=["c6g.medium"],
            ProductDescriptions=["Linux/UNIX"],
        )

        pprint(price_history["SpotPriceHistory"])

    # TODO: add spot instance support!

    def createinstances(self, key_name):
        # TODO: get these arguments properly:
        # - for every region these will be different, except maybe instance_type,
        #   but not every instance is available everywhere...

        # cmd: aws ec2 describe-images --filters='[{"Name":"architecture","Values":["arm64"]}]' --owners="903794441882"
        # ami-0245697ee3e07e755 (64-bit (x86)) / ami-0886e2450125a1f08 (64-bit (Arm))
        image_id = "ami-0886e2450125a1f08"

        # cmd: aws ec2 describe-instance-types
        instance_type = "c6g.medium"

        # cmd: aws ec2 describe-key-pairs
        # keyname comes from this ^^

        # cmd: aws ec2 describe-security-groups
        # NOTE: make sure tcp port 22 in is allowed in the group!
        securitygroup = "default"

        print("[+] Generating cloudinit script")
        sshkey_raw = open(".sshkey").read()
        userdata_raw = ec2_userdata_tpl.substitute({
            "SSH_KEY": sshkey_raw
        })
        user_data = base64.b64encode(userdata_raw.encode("utf-8")).decode("utf-8")

        instance_params = {
            "ImageId": image_id,
            "InstanceType": instance_type,
            "KeyName": key_name,
            "UserData": user_data,
            "SecurityGroups": [securitygroup],
            "TagSpecifications": [
                {
                    "ResourceType": "instance",
                    "Tags": [
                        {
                            "Key": TAGNAME,
                            "Value": TAGVALUE,
                        }
                    ]
                }
            ]
        }

        print("[+] Spawning instance {}".format(instance_type))
        instances = self.__ec2_resource.create_instances(
            **instance_params,
            MinCount=1,
            MaxCount=1
        )
        for instance in instances:
            print("Created instance: {}".format(instance))

    def __get_instances(self):
        reservations = self.__ec2_client.describe_instances(Filters=[
            {
                "Name": "tag:{}".format(TAGNAME),
                "Values": [TAGVALUE]
            },
        ])
        for reservation in reservations["Reservations"]:
            for instance in reservation["Instances"]:
                yield instance

    def describeinstances(self):
        for instance in self.__get_instances():
            state = instance["State"]["Name"]
            tags = instance.get("Tags", None)
            # if state not in ("terminated", "shutting-down"):
                # pprint(instance)
            print("{}: {}".format(instance["InstanceId"], state, tags))

    def destroyinstances(self):
        todelete = []
        for instance in self.__get_instances():
            iid = instance["InstanceId"]
            todelete.append(iid)

        resp = self.__ec2_client.terminate_instances(
            InstanceIds=todelete,
        )


if __name__ == "__main__":
    keyname = sys.argv[1]
    func = sys.argv[2]

    ec2mgr = EC2Manager()
    if func == "create":
        ec2mgr.createinstances(keyname)
    elif func == "list":
        ec2mgr.describeinstances()
    elif func == "destroy":
        ec2mgr.destroyinstances()
    else:
        print("Invalid func: {}".format(func))
