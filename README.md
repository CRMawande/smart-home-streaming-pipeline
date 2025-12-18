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

This project uses the  [Open Smart Home IoT/IEQ/Energy Data](https://www.kaggle.com/datasets/claytonmiller/open-smart-home-iotieqenergy-data) dataset from Kaggle

## Prerequisites

- Docker Desktop installed and running
- Python 3.9+
- PowerShell 

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/CRMawande/smart-home-streaming-pipeline.git
cd smart-home-streaming-pipeline
```

### 2. Start the Pipeline

```bash
# Stop any existing containers
docker-compose down

# Build and start all services
docker-compose up --build -d

# Wait 40 seconds for services to initialize
Start-Sleep -Seconds 120

# Verify all containers are running
docker ps
```

### 3. Deploy Kafka Connect Sink Connector

```bash
# Deploy the connector
curl.exe -X POST http://localhost:8083/connectors `
  -H "Content-Type: application/json" `
  -d "@connect/kafka-connect-config.json"

# Check connector status
curl.exe http://localhost:8083/connectors/timescaledb-sink/status | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### 4. Verify Data Flow

```bash
# Get TimescaleDB container name
$timescaleContainer = docker ps --filter "name=timescaledb" --format "{{.Names}}"

# Check row count
docker exec -it $timescaleContainer psql -U sensor -d sensordb -c "SELECT COUNT(*) FROM measurements;"

# View latest data
docker exec -it $timescaleContainer psql -U sensor -d sensordb -c "SELECT * FROM measurements ORDER BY time DESC LIMIT 10;"
```

### 5. Access Grafana

```bash
# Open Grafana in browser
Start-Process "http://localhost:3000"
```

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

```bash
CREATE TABLE measurements (
    time        TIMESTAMPTZ       NOT NULL,
    location    TEXT              NOT NULL,
    metric      TEXT              NOT NULL,
    value       DOUBLE PRECISION  NOT NULL
);
```

The table is converted to a TimescaleDB hypertable for optimized time-series queries.

## Grafana Visuals

<img width="862" height="770" alt="image" src="https://github.com/user-attachments/assets/70c198ac-e4e6-42db-9ee9-aa120f1e5b20" />


## Stopping the Pipeline

```bash
# Stop all services
docker-compose down

# Stop and remove volumes 
docker-compose down -v
```


## Architecture Diagram

<img width="1038" height="355" alt="image" src="https://github.com/user-attachments/assets/97a00775-1695-4d1c-b0eb-c56c66fad4f8" />


## Technologies Used

- **Apache Kafka 7.6.0**: Distributed streaming platform
- **TimescaleDB (PostgreSQL 15)**: Time-series database
- **Kafka Connect**: Data integration framework
- **Grafana**: Visualization and monitoring
- **Docker & Docker Compose**: Containerization
- **Python 3.11**: Producer implementation

## Project Structure

<img width="349" height="518" alt="image" src="https://github.com/user-attachments/assets/f847e059-683f-4cd2-85d6-2ce162a8ea19" />


## Future Enhancements

- Add data aggregation and windowing with Kafka Streams
- Implement alerting based on threshold violations
- Add authentication and SSL/TLS encryption
- Deploy to cloud infrastructure (AWS/Azure/GCP)
- Add machine learning models for anomaly detection
- Implement data retention and compression policies


## References
Apache Software Foundation. (2010). Apache Zookeeper Documentation. https://zookeeper.apache.org/

Apache Software Foundation. (2025). Apache Kafka: A Distributed Streaming Platform. https://kafka.apache.org

Confluent Inc. (2025). Kafka Connect JDBC Connector. https://docs.confluent.io/kafka-connectors/jdbc/current/overview.html

Docker Inc. (2025). Docker Documentation. https://docs.docker.com/

Grafana Labs. (2025). Grafana Documentation. https://grafana.com/docs/

Schneider, G. F., & Rasmussen, M. H. (2018). Technical Building Systems/Open Smart Home Data: First release of Open Smart Home Data Set.

Timescale Inc. (2025). Tiger Data: PostgreSQL++ for Time Series, Analytics & AI. https://www.tigerdata.com/


