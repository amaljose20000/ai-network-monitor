[ec2-user@ip-172-31-38-240 ~]$ cat anomaly.py
import boto3
import pandas as pd
from sklearn.ensemble import IsolationForest
from datetime import datetime

dynamodb = boto3.resource("dynamodb", region_name="eu-north-1")
sns = boto3.client("sns", region_name="eu-north-1")
table = dynamodb.Table("network-monitor-logs")

SNS_TOPIC_ARN = "arn:aws:sns:eu-north-1:508716860525:network-monitor-alerts"
ENDPOINTS = ["google.com", "cloudflare.com", "1.1.1.1"]

def fetch_data(endpoint):
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("endpoint").eq(endpoint)
    )
    items = response["Items"]
    df = pd.DataFrame(items)
    df["avg_latency_ms"] = pd.to_numeric(df["avg_latency_ms"])
    df["packet_loss_pct"] = pd.to_numeric(df["packet_loss_pct"])
    return df

def detect_anomalies(endpoint):
    print(f"\nAnalyzing {endpoint}...")
    df = fetch_data(endpoint)

    if len(df) < 10:
        print(f"  Not enough data yet ({len(df)} records). Need at least 10.")
        return

    features = df[["avg_latency_ms", "packet_loss_pct"]]
    model = IsolationForest(contamination=0.05, random_state=42)
    df["anomaly"] = model.fit_predict(features)

    anomalies = df[df["anomaly"] == -1]
    print(f"  Total records: {len(df)}")
    print(f"  Anomalies found: {len(anomalies)}")

    if len(anomalies) > 0:
        print(f"  Latest anomaly: latency={anomalies.iloc[-1]['avg_latency_ms']}ms")
        message = f"""
AI ANOMALY DETECTION ALERT
--------------------------
Endpoint  : {endpoint}
Anomalies : {len(anomalies)} detected out of {len(df)} records
Latest    : latency={anomalies.iloc[-1]['avg_latency_ms']}ms  loss={anomalies.iloc[-1]['packet_loss_pct']}%
Time      : {datetime.utcnow().isoformat()}

These were flagged as unusual by the AI model based on historical patterns.
"""
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f"[AI ALERT] Anomaly detected on {endpoint}",
            Message=message,
        )
        print(f"  -> AI ALERT SENT")
    else:
        print(f"  All normal - no anomalies detected")

if __name__ == "__main__":
    print("=== AI Anomaly Detection ===")
    print(f"Running at {datetime.utcnow().isoformat()}")
    for endpoint in ENDPOINTS:
        detect_anomalies(endpoint)
    print("\nDone.")