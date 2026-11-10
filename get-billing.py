from datetime import date, datetime, timedelta, timezone
import boto3
from botocore.exceptions import ClientError


def print_aws_bill_and_credits_details():
  # 1. Fetch Month-to-Date Bill Breakdown (Cost Explorer)
  ce_client = boto3.client("ce", region_name="us-east-1")

  today = date.today()
  start_date = today.replace(day=1).strftime("%Y-%m-%d")
  # End date is exclusive in Cost Explorer, so add 1 day to include today
  end_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")

  cost_response = ce_client.get_cost_and_usage(
      TimePeriod={"Start": start_date, "End": end_date},
      Granularity="MONTHLY",
      Metrics=["UnblendedCost"],
      GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
  )

  print(f"AWS BILL BREAKDOWN ({start_date} to {today})")
  print("-" * 60)

  total_bill = 0.0
  for result in cost_response.get("ResultsByTime", []):
    for group in result.get("Groups", []):
      service_name = group["Keys"][0] if group["Keys"] else "Unknown Service"
      amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
      unit = group["Metrics"]["UnblendedCost"]["Unit"]

      if amount > 0:
        print(f"{service_name:<42} {amount:>10.2f} {unit}")
        total_bill += amount

  print("-" * 60)
  print(f"{'Total Month-to-Date Cost (Before Credits):':<42} {total_bill:>10.2f} USD\n")

  # 2. Fetch Detailed Credits Remaining (AWS Billing Client)
  sts_client = boto3.client("sts")
  account_id = sts_client.get_caller_identity()["Account"]

  billing_client = boto3.client("billing", region_name="us-east-1")
  now = datetime.now(timezone.utc)
  # startDate is required and cannot be more than 1 year in the past
  credit_window_start = now - timedelta(days=364)

  try:
    print("AWS CREDITS REMAINING DETAILS")
    print("-" * 60)

    total_remaining_credits = 0.0
    found_credits = False
    next_token = None

    # Call get_credits directly and handle nextToken manually
    while True:
      request_kwargs = {
          "accountId": account_id,
          "startDate": credit_window_start,
          "endDate": now,
          "payerAccountFlag": True,
      }
      if next_token:
        request_kwargs["nextToken"] = next_token

      credit_response = billing_client.get_credits(**request_kwargs)

      for credit in credit_response.get("credits", []):
        found_credits = True
        name = credit.get("creditName", credit.get("creditId", "AWS Credit"))
        status = credit.get("status", "UNKNOWN")

        # Extract original, used, and remaining amounts
        orig_info = credit.get("originalAmount") or {}
        used_info = credit.get("usedAmount") or {}
        rem_info = credit.get("remainingAmount") or {}

        orig_amt = float(orig_info.get("currencyAmount", 0) or 0)
        used_amt = float(used_info.get("currencyAmount", 0) or 0)
        rem_amt = float(rem_info.get("currencyAmount", 0) or 0)
        currency = rem_info.get("currencyCode", "USD")

        # Extract expiration date and applicable products
        expiration = credit.get("expirationDate")
        exp_str = expiration.strftime("%Y-%m-%d") if expiration else "N/A"
        products = credit.get("applicableProducts") or ["All Eligible Services"]

        print(f"Credit Name:         {name}")
        print(f"Status:              {status}")
        print(f"Original Amount:     {orig_amt:.2f} {currency}")
        print(f"Used Amount:         {used_amt:.2f} {currency}")
        print(f"Credits Remaining:   {rem_amt:.2f} {currency}")
        print(f"Expiration Date:     {exp_str}")
        print(f"Applicable Services: {', '.join(products)}")
        print("-" * 60)

        if rem_amt > 0:
          total_remaining_credits += rem_amt

      next_token = credit_response.get("nextToken")
      if not next_token:
        break

    if not found_credits:
      print("No active credits found for this account.")
      print("-" * 60)

    print(f"TOTAL CREDITS REMAINING: {total_remaining_credits:.2f} USD")
    net_payable = max(0.0, total_bill - total_remaining_credits)
    print(f"ESTIMATED NET PAYABLE:   {net_payable:.2f} USD")

  except ClientError as e:
    print(f"Error fetching credits: {e.response['Error']['Message']}")


if __name__ == "__main__":
  print_aws_bill_and_credits_details()
