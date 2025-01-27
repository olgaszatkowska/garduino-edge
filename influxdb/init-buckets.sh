#!/bin/bash
set -e

influx bucket create --name "${DOCKER_INFLUXDB_INIT_BUCKET_RAW}" --org "${DOCKER_INFLUXDB_INIT_ORG}" --token "${DOCKER_INFLUXDB_INIT_ADMIN_TOKEN}" --retention 30d
