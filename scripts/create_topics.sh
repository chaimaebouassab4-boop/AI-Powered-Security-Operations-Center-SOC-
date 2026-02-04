#!/bin/bash
# Utilisez le nom du service 'kafka' défini dans docker-compose
for topic in events_raw events_collected events_with_features events_with_anomaly decisions alerts metrics events_final; do
    docker exec soc-ia-unified_kafka_1 kafka-topics --create --bootstrap-server kafka:9092 --topic $topic --partitions 3 --replication-factor 1 --if-not-exists
done
