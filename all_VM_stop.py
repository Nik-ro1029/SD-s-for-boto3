import boto3

ec2 = boto3.client('ec2',region_name='ap-southeast-2')

def stop_all_vms():
    print(f"{'Instance ID':<25} {'State':<15} {'Instance Type':<20} "
          f"{'Public IP':<20} {'Private IP':<20} {'Launch Time':<30}")

    paginator = ec2.get_paginator('describe_instances')
    found = False

    for page in paginator.paginate():
        for reservation in page['Reservations']:
            for instance in reservation['Instances']:
                found = True
                print(f"{instance['InstanceId']:<25} "
                      f"{instance['State']['Name']:<15} "
                      f"{instance['InstanceType']:<20} "
                      f"{instance.get('PublicIpAddress', 'N/A'):<20} "
                      f"{instance.get('PrivateIpAddress', 'N/A'):<20} "
                      f"{str(instance['LaunchTime']):<30}")

                if instance['State']['Name'] == 'running':
                    ec2.stop_instances(InstanceIds=[instance['InstanceId']])
                    print(f"Stopping instance {instance['InstanceId']}...")

    if not found:
        print("No instances found in ap-southeast-2.")