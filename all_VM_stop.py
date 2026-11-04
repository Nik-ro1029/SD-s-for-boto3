import boto3
import sys
from botocore.exceptions import BotoCoreError, ClientError

ec2 = boto3.client("ec2", region_name="ap-southeast-2")

def stop_all_vms():
    print(
        f"{'Instance ID':<25} {'State':<15} {'Instance Type':<20} "
        f"{'Public IP':<20} {'Private IP':<20} {'Launch Time':<30}"
    )

    paginator = ec2.get_paginator("describe_instances")
    running_instance_ids = []
    found = False

    for page in paginator.paginate():
        for reservation in page["Reservations"]:
            for instance in reservation["Instances"]:
                found = True
                instance_id = instance["InstanceId"]
                state = instance["State"]["Name"]
                print(
                    f"{instance_id:<25} "
                    f"{state:<15} "
                    f"{instance['InstanceType']:<20} "
                    f"{instance.get('PublicIpAddress', 'N/A'):<20} "
                    f"{instance.get('PrivateIpAddress', 'N/A'):<20} "
                    f"{str(instance['LaunchTime']):<30}"
                )

                if state == "running":
                    running_instance_ids.append(instance_id)

    if not found:
        print("No instances found in ap-southeast-2.")
        return

    if not running_instance_ids:
        print("No running instances to stop.")
        return

    response = ec2.stop_instances(InstanceIds=running_instance_ids)
    for instance in response["StoppingInstances"]:
        print(
            f"Stop requested for {instance['InstanceId']}: "
            f"{instance['PreviousState']['Name']} -> {instance['CurrentState']['Name']}"
        )


def main() -> int:
    try:
        stop_all_vms()
        return 0
    except (BotoCoreError, ClientError) as error:
        print(f"AWS error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())