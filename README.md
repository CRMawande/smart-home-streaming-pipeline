@"
# Smart Home IoT Stream Processing Pipeline

A real-time data engineering pipeline for processing and visualizing smart home sensor data using Apache Kafka, TimescaleDB, and Grafana.

## Project Overview

This project implements a scalable stream processing pipeline that ingests IoT sensor data, processes it through Apache Kafka, stores it in TimescaleDB (time-series database), and visualizes it in real-time using Grafana.

### Architecture Components

- **Kafka Producer**: Python-based producer that streams sensor measurements
- **Apache Kafka**: Distributed streaming platform for reliable message handling
- **Zookeeper**: Coordination service for Kafka
- **Kafka Connect**: JDBC Sink connector for database integration
- **TimescaleDB**: PostgreSQL-based time-series database
- **Grafana**: Real-time data visualization and monitoring

## Dataset

This project uses the **Open Smart Home IoT/IEQ/Energy Data** dataset from Kaggle.

**Dataset URL**: https://www.kaggle.com/datasets/gauravfof/open-smart-home-iotieqenergy-data

### Data Setup Instructions

1. Download the dataset from Kaggle (link above)
2. Extract the ZIP file
3. Create the measurements directory in your project:
   \`\`\`powershell
   New-Item -ItemType Directory -Force -Path "kafka/measurements"
   \`\`\`
4. Navigate to the extracted folder and locate the **Measurements** folder
5. Copy **all CSV files** from the Measurements folder to \`kafka/measurements/\`

## Prerequisites

- Docker Desktop installed and running
- PowerShell (Windows) or Bash (Linux/Mac)
- At least 4GB of available RAM
- 2GB of free disk space

## Installation and Setup

### 1. Clone the Repository

\`\`\`powershell
git clone https://github.com/CRMawande/smart-home-streaming-pipeline.git
cd streaming-pipeline
\`\`\`

### 2. Download and Prepare Dataset

Follow the **Data Setup Instructions** above to populate \`kafka/measurements/\` with CSV files.

### 3. Start the Pipeline

\`\`\`powershell
# Stop any existing containers
docker-compose down

# Build and start all services
docker-compose up --build -d

# Wait 40 seconds for services to initialize
Start-Sleep -Seconds 40

# Verify all containers are running
docker ps
\`\`\`

### 4. Deploy Kafka Connect Sink Connector

\`\`\`powershell
# Deploy the connector
curl.exe -X POST http://localhost:8083/connectors \`
  -H "Content-Type: application/json" \`
  -d "@connect/kafka-connect-config.json"

# Check connector status
curl.exe http://localhost:8083/connectors/timescaledb-sink/status | ConvertFrom-Json | ConvertTo-Json -Depth 10
\`\`\`

### 5. Verify Data Flow

\`\`\`powershell
# Get TimescaleDB container name
\`$timescaleContainer = docker ps --filter "name=timescaledb" --format "{{.Names}}"

# Check row count
docker exec -it \`$timescaleContainer psql -U sensor -d sensordb -c "SELECT COUNT(*) FROM measurements;"

# View latest data
docker exec -it \`$timescaleContainer psql -U sensor -d sensordb -c "SELECT * FROM measurements ORDER BY time DESC LIMIT 10;"
\`\`\`

### 6. Access Grafana

\`\`\`powershell
# Open Grafana in browser
Start-Process "http://localhost:3000"
\`\`\`

**Default Credentials**:
- Username: \`admin\`
- Password: \`admin\`

The TimescaleDB data source is pre-configured. You can start creating dashboards immediately.

## Service Endpoints

| Service | Port | URL |
|---------|------|-----|
| Grafana | 3000 | http://localhost:3000 |
| Kafka Connect | 8083 | http://localhost:8083 |
| TimescaleDB | 5432 | localhost:5432 |
| Kafka Broker | 9092 | localhost:9092 |
| Zookeeper | 2181 | localhost:2181 |

## Database Schema

\`\`\`sql
CREATE TABLE measurements (
    time        TIMESTAMPTZ       NOT NULL,
    location    TEXT              NOT NULL,
    metric      TEXT              NOT NULL,
    value       DOUBLE PRECISION  NOT NULL
);
\`\`\`

The table is converted to a TimescaleDB hypertable for optimized time-series queries.

## Sample Grafana Queries

### Temperature Over Time
\`\`\`sql
SELECT
  time AS "time",
  location,
  value as "temperature"
FROM measurements
WHERE
  metric = 'Temperature'
  AND \$__timeFilter(time)
ORDER BY time
\`\`\`

### Average Humidity by Location
\`\`\`sql
SELECT
  time_bucket('5 minutes', time) AS "time",
  location,
  AVG(value) as avg_humidity
FROM measurements
WHERE
  metric = 'Humidity'
  AND \$__timeFilter(time)
GROUP BY time_bucket('5 minutes', time), location
ORDER BY time
\`\`\`

### Latest Measurements by Metric
\`\`\`sql
SELECT
  metric,
  location,
  value,
  time
FROM measurements
WHERE time > NOW() - INTERVAL '1 minute'
ORDER BY time DESC
LIMIT 20
\`\`\`

## Monitoring and Debugging

### View Producer Logs
\`\`\`powershell
docker logs streaming-pipeline-producer-1 --tail 50
\`\`\`

### View Kafka Connect Logs
\`\`\`powershell
docker logs streaming-pipeline-kafka-connect-1 --tail 100
\`\`\`

### Check Kafka Topic Messages
\`\`\`powershell
docker exec -it streaming-pipeline-kafka-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic smart-home-measurements --from-beginning --max-messages 5
\`\`\`

### View All Available Metrics
\`\`\`powershell
docker exec -it \`$timescaleContainer psql -U sensor -d sensordb -c "SELECT DISTINCT metric FROM measurements ORDER BY metric;"
\`\`\`

### View All Locations
\`\`\`powershell
docker exec -it \`$timescaleContainer psql -U sensor -d sensordb -c "SELECT DISTINCT location FROM measurements ORDER BY location;"
\`\`\`

## Stopping the Pipeline

\`\`\`powershell
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
\`\`\`


## Architecture Diagram

\`\`\`
┌─────────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Kafka     │────▶│   Apache    │────▶│    Kafka     │────▶│ TimescaleDB │
│  Producer   │     │    Kafka    │     │   Connect    │     │   (PostgreSQL)│
│  (Python)   │     │   Broker    │     │ (JDBC Sink)  │     │             │
└─────────────┘     └─────────────┘     └──────────────┘     └─────────────┘
                           │                                          │
                           │                                          │
                    ┌──────▼──────┐                          ┌────────▼────────┐
                    │  Zookeeper  │                          │    Grafana      │
                    │             │                          │ (Visualization) │
                    └─────────────┘                          └─────────────────┘
\`\`\`

## Technologies Used

- **Apache Kafka 7.6.0**: Distributed streaming platform
- **TimescaleDB (PostgreSQL 15)**: Time-series database
- **Kafka Connect**: Data integration framework
- **Grafana**: Visualization and monitoring
- **Docker & Docker Compose**: Containerization
- **Python 3.11**: Producer implementation

## Project Structure

\`\`\`
streaming-pipeline/
├── kafka/
│   ├── Dockerfile              # Producer container configuration
│   ├── producer.py             # Kafka producer script
│   └── measurements/           # CSV data files (not in git)
├── connect/
│   └── kafka-connect-config.json  # JDBC sink connector config
├── timescaledb/
│   └── init.sql                # Database initialization
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── timescaledb.yml
│       └── dashboards/
│           └── dashboard.yml
├── docker-compose.yml          # Service orchestration
├── .gitignore
└── README.md
\`\`\`
  

## Performance Metrics

- **Ingestion Rate**: ~2-3 messages per second per sensor
- **Latency**: < 1 second end-to-end
- **Storage**: ~100K measurements = ~8MB in TimescaleDB
- **Retention**: Unlimited (configurable with TimescaleDB retention policies)

## Future Enhancements

- Add data aggregation and windowing with Kafka Streams
- Implement alerting based on threshold violations
- Add authentication and SSL/TLS encryption
- Deploy to cloud infrastructure (AWS/Azure/GCP)
- Add machine learning models for anomaly detection
- Implement data retention and compression policies


## References

- Apache Software Foundation. (2025). Apache Kafka Documentation. https://kafka.apache.org
- Confluent Inc. (2025). Kafka Connect JDBC Connector. https://docs.confluent.io/kafka-connectors/jdbc/
- Docker Inc. (2025). Docker Documentation. https://docs.docker.com/
- Grafana Labs. (2025). Grafana Documentation. https://grafana.com/docs/
- Schneider, G. F., & Rasmussen, M. H. (2018). Technical Building Systems/Open Smart Home Data
- Timescale Inc. (2025). TimescaleDB Documentation. https://docs.timescale.com/
"@ | Out-File -FilePath "README.md" -Encoding UTF8

