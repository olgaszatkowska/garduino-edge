# garduino-edge

First copy example.env to .env. Environment variables under AWS need to be set according to service on cloud provider. For variables under settings set `DRY_RUN_MODE` to skip sending data to cloud, in this case only local database will be used. Set `DATA_COLLECTION_INTERVAL_SECONDS` and `DATA_UPLOAD_INTERVAL_SECONDS` to wanted time, make sure that data is collected more often than it is uploaded. Depending on which sensors are connected set `DHT11_CONNECTED` and `SEN0193_CONNECTED` accordingly to 0 (not connected) or 1 (connected).

To run for the first time:

```
docker compose up --build
```

Once its build it can be run only with

```
docker compose up
```