[ec2-user@ip-172-31-38-240 ~]$ cat monitor.py
import time
from datetime import datetime
from ping3 import ping
import boto3

ENDPOINTS = ["google.com", "cloudflare.com", "1.1.1.1"]
CHECKS_PER_ENDPOINT = 3
CHECK_INTERVAL_SECONDS = 60
LATENCY_THRESHOLD_MS = 50

cloudwatch = boto3.client("cloudwatch", region_name="eu-north-1")
dynamodb = boto3.resource("dynamodb", region_name="eu-north-1")
sns = boto3.client("sns", region_name="eu-north-1")
table = dynamodb.Table("network-monitor-logs")

SNS_TOPIC_ARN = "arn:aws:sns:eu-north-1:508716860525:network-monitor-alerts"

def check_endpoint(host):
    latencies = []
    failures = 0
    for _ in range(CHECKS_PER_ENDPOINT):
        result = ping(host, timeout=2)
        if result is None:
            failures += 1
        else:
            latencies.append(result * 1000)
    packet_loss_pct = round((failures / CHECKS_PER_ENDPOINT) * 100, 1)
    avg_latency_ms = round(sum(latencies) / len(latencies), 2) if latencies else None
    status = "DOWN" if avg_latency_ms is None else "UP"
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "endpoint": host,
        "status": status,
        "avg_latency_ms": avg_latency_ms,
        "packet_loss_pct": packet_loss_pct,
    }

def send_to_cloudwatch(result):
    cloudwatch.put_metric_data(
        Namespace="NetworkMonitor",
        MetricData=[
            {
                "MetricName": "Latency",
                "Dimensions": [{"Name": "Endpoint", "Value": result["endpoint"]}],
                "Value": result["avg_latency_ms"] if result["avg_latency_ms"] is not None else 0,
                "Unit": "Milliseconds",
            },
            {
                "MetricName": "PacketLoss",
                "Dimensions": [{"Name": "Endpoint", "Value": result["endpoint"]}],
                "Value": result["packet_loss_pct"],
                "Unit": "Percent",
            },
            {
                "MetricName": "Up",
                "Dimensions": [{"Name": "Endpoint", "Value": result["endpoint"]}],
                "Value": 1 if result["status"] == "UP" else 0,
                "Unit": "Count",
            },
        ],
    )

def save_to_dynamodb(result):
    table.put_item(Item={
        "endpoint": result["endpoint"],
        "timestamp": result["timestamp"],
        "status": result["status"],
        "avg_latency_ms": str(result["avg_latency_ms"]),
        "packet_loss_pct": str(result["packet_loss_pct"]),
    })

def send_alert(result, reason):
    message = f"""
NETWORK MONITOR ALERT
---------------------
Endpoint : {result['endpoint']}
Status   : {result['status']}
Latency  : {result['avg_latency_ms']}ms
Loss     : {result['packet_loss_pct']}%
Reason   : {reason}
Time     : {result['timestamp']}
"""
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=f"[ALERT] {result['endpoint']} - {reason}",
        Message=message,
    )
    print(f"  -> ALERT SENT: {reason}")

def run_monitoring_round():
    print(f"\n--- Check round: {datetime.utcnow().isoformat()} ---")
    for host in ENDPOINTS:
        result = check_endpoint(host)
        print(result)
        send_to_cloudwatch(result)
        save_to_dynamodb(result)
        print(f"  -> Saved to DynamoDB")
        if result["status"] == "DOWN":
            send_alert(result, "Endpoint is DOWN")
        elif result["avg_latency_ms"] and result["avg_latency_ms"] > LATENCY_THRESHOLD_MS:
            send_alert(result, f"High latency: {result['avg_latency_ms']}ms")

if __name__ == "__main__":
    print("Starting network monitor. Press Ctrl+C to stop.")
    while True:
        run_monitoring_round()
        time.sleep(CHECK_INTERVAL_SECONDS)