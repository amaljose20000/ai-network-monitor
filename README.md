# AI-Powered Network Monitoring System

A real-time network monitoring system built on AWS that uses machine learning to detect anomalies in network behavior — going beyond simple threshold alerts to identify subtle performance degradation before it becomes an outage.

## What It Does

- Monitors endpoint health (latency, packet loss, uptime) every 60 seconds
- Sends real-time metrics to AWS CloudWatch for live visualization
- Stores all historical data in DynamoDB for trend analysis
- Sends instant email alerts via SNS when endpoints go down or latency spikes
- Runs an AI anomaly detection model (Isolation Forest) hourly to flag unusual patterns that fixed thresholds would miss

## Architecture
EC2 Monitoring Agent (Python)

|

├── CloudWatch (live metrics dashboard)

├── DynamoDB (historical data store)

└── SNS (email alerts)

|

└── AI Anomaly Detection (scikit-learn Isolation Forest)

|

└── SNS (AI-powered alerts)

## Tech Stack

| Service | Purpose |
|---|---|
| AWS EC2 | Always-on monitoring agent |
| AWS CloudWatch | Real-time metrics and dashboard |
| AWS DynamoDB | Historical data storage |
| AWS SNS | Email alerting |
| AWS IAM | Least-privilege security |
| Python 3 | Core scripting |
| ping3 | Network latency measurement |
| boto3 | AWS SDK |
| scikit-learn | Isolation Forest anomaly detection |
| pandas | Data processing |

## Key Features

**Threshold-based alerting:** Instant SNS email when an endpoint goes DOWN or latency exceeds 50ms.

**AI anomaly detection:** Isolation Forest model trained on historical latency data flags statistically unusual patterns — catching slow latency creep and time-of-day anomalies that hard thresholds miss.

**Auto-recovery:** Script auto-starts on EC2 reboot via cron. Runs continuously in background via nohup.

**Least-privilege IAM:** EC2 instance role has only the exact permissions needed (CloudWatch, DynamoDB, SNS) — no admin access.

## Setup

```bash
# Install dependencies
pip3 install ping3 boto3 scikit-learn pandas

# Run monitoring agent
sudo python3 monitor.py

# Run AI anomaly detection
sudo python3 anomaly.py
```

## Screenshots

*CloudWatch Dashboard showing live latency metrics for monitored endpoints*

*<img width="1920" height="784" alt="Cloud-Watch" src="https://github.com/user-attachments/assets/0b758b00-b452-4dc0-a0f7-3c45a1e61f37" />
*

## Author

**Amal Jose** — Network & Cloud Engineer  
CCNA | AWS |  
📍 Dammam, Saudi Arabia  
🔗 [LinkedIn](https://linkedin.com/in/amaljose-network)  
📧 amalmj094@gmail.com
