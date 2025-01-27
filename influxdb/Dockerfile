FROM influxdb:2.7.11

COPY ./init-buckets.sh /docker-entrypoint-initdb.d
RUN chmod +x /docker-entrypoint-initdb.d/init-buckets.sh