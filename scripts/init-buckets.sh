#!/bin/bash
set -e

influx bucket create --name "${INFLUXDB_BUCKET_RAW}" --org "${INFLUXDB_ORG}" --token "${INFLUXDB_TOKEN}" --retention 30d
