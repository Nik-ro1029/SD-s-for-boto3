import boto3
from botocore.exceptions import ClientError


def start_ec2_instance():
    # 1. Prompt the user to enter the VM (EC2 Instance) ID
    instance_id = input("Please enter the EC2 VM Instance ID to start: ").strip()

    # 2. Prompt the user to enter the AWS Region right after the instance ID
    region = input("Please enter the AWS Region (e.g., us-east-1, us-west-2): ").strip()

    if not instance_id or not region:
        print("Error: Both Instance ID and Region are required.")
        return

    # 3. Initialize the Boto3 EC2 client targeting the specific region
    ec2_client = boto3.client("ec2", region_name=region)

    print(f"Attempting to start VM: {instance_id} in region: {region}...")

    try:
        # 4. Call start_instances to spin up the VM
        response = ec2_client.start_instances(
            InstanceIds=[instance_id], DryRun=False
        )

        # 5. Extract and display the status change information
        # Fixed index access [0] since StartingInstances is a list
        current_state = response["StartingInstances"][0]["CurrentState"]["Name"]
        previous_state = response["StartingInstances"][0]["PreviousState"][
            "Name"
        ]

        print(
            f"Success! VM status changed from '{previous_state}' to '{current_state}'."
        )

    except ClientError as e:
        print(f"An error occurred while starting the VM: {e}")


if __name__ == "__main__":
    start_ec2_instance()
