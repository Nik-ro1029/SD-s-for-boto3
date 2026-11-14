import boto3

ec2 = boto3.client("ec2", region_name="ap-southeast-2")


def check_all_vms():
    print(
        f"{'Instance ID':<25} {'VM Name':<25} {'State':<15} {'Instance Type':<20} "
        f"{'Public IP':<20} {'Private IP':<20} {'Launch Time':<30}"
    )

    paginator = ec2.get_paginator("describe_instances")
    found = False

    for page in paginator.paginate():
        for reservation in page["Reservations"]:
            for instance in reservation["Instances"]:
                found = True
                name = next(
                    (
                        tag.get("Value", "N/A")
                        for tag in instance.get("Tags", [])
                        if tag.get("Key") == "Name"
                    ),
                    "N/A",
                )
                print(
                    f"{instance['InstanceId']:<25} "
                    f"{name:<25} "
                    f"{instance['State']['Name']:<15} "
                    f"{instance['InstanceType']:<20} "
                    f"{instance.get('PublicIpAddress', 'N/A'):<20} "
                    f"{instance.get('PrivateIpAddress', 'N/A'):<20} "
                    f"{str(instance['LaunchTime']):<30}"
                )

    if not found:
        print("No instances found in ap-southeast-2.")

if __name__ == "__main__":
    check_all_vms()
