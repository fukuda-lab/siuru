#!/bin/bash
set -e

# Start influxDB container
docker-compose up -d influxdb

# Install jq
docker exec influxdb bash -c "apt-get update && apt-get install -y jq"

# vars from .env
INFLUXDB_USERNAME=${INFLUXDB_USERNAME}
INFLUXDB_ORG=${INFLUXDB_ORG}

# New token generation
INFLUXDB_TOKEN=$(docker exec influxdb bash -c "influx auth create --user '$INFLUXDB_USERNAME' --org '$INFLUXDB_ORG' --all-access --json | jq -r '.token'")

echo "Token generated: $INFLUXDB_TOKEN"

# Token verification
if [ -z "$INFLUXDB_TOKEN" ]; then
    echo "Unable to obtain InfluxDB token"
    exit 1
fi

# Check if the token entry already exists in .env
if grep -q "INFLUXDB_TOKEN=" ./.env; then
    echo "Updating the existing token in .env"
    sed -i "s/^INFLUXDB_TOKEN=.*/INFLUXDB_TOKEN=$INFLUXDB_TOKEN/" .env
else
    echo "Adding new token to .env"
    echo "INFLUXDB_TOKEN=$INFLUXDB_TOKEN" >> .env
fi

# Start grafana container using the token generated
docker-compose up -d grafana

