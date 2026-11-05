import sys
import boto3
from botocore.exceptions import ClientError


def delete_ec2_instance():
    # Get user inputs manually
    instance_id = input("Enter the AWS VM (Instance) ID (e.g., i-0123456789abcdef0): ").strip()
    region = input("Enter the AWS Region (e.g., us-east-1): ").strip()

    if not instance_id or not region:
        print("Error: Both Instance ID and Region are required.")
        return

    # Initialize the boto3 client for EC2
    try:
        ec2 = boto3.client("ec2", region_name=region)

        print(f"\nAttempting to terminate instance {instance_id} in region {region}...")
        
        # Call the terminate_instances API
        response = ec2.terminate_instances(InstanceIds=[instance_id])

        # Parse the termination state changes
        for state in response["TerminatingInstances"]:
            print(f"Instance ID: {state['InstanceId']}")
            print(f"Previous State: {state['PreviousState']['Name']}")
            print(f"Current State: {state['CurrentState']['Name']}")

    except ClientError as e:
        print(f"\nAWS Error: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    delete_ec2_instance()
