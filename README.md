# Postgres collector
Collects database metrics using postgres exporter and forward the data to logz.io, based on opentelemetry collector

#### Before you begin
<details open>
<summary>Set up your IAM user</summary>

You'll need an [IAM user](https://console.aws.amazon.com/iam/home)
with the following permissions:

* `cloudwatch:ListMetrics`
* `cloudwatch:GetMetricStatistics`
* `tag:GetResources`

If you don't have one, set that up now.

Create an **Access key ID** and **Secret access key** for the IAM user,
and paste them in your text editor.

##### Get your metrics region

You'll need to specify the AWS region you're collecting metrics from.

![AWS region menu](https://dytvr9ot2sszz.cloudfront.net/logz-docs/aws/region-menu.png)

Find your region's slug in the region menu
(in the top menu, on the right side).

For example:
The slug for US East (N. Virginia)
is "us-east-1", and the slug for Canada (Central) is "ca-central-1".
</details>


#### Full list of configurable environment variables

| Environment variable | Description |
|---|---|
| LOGZIO_REGION (Required)| Your Logz.io region code. For example if your region is US, then your region code is `us`. You can find your region code here: https://docs.logz.io/user-guide/accounts/account-region.html#regions-and-urls. |
| TOKEN (Required)| Token for shipping metrics to your Logz.io account. Find it under Settings > Manage accounts. [_How do I look up my Metrics account token?_](/user-guide/accounts/finding-your-metrics-account-token/) |
| P8S_LOGZIO_NAME | The value of the `p8s_logzio_name` external label. This variable identifies which Prometheus environment the metrics arriving at Logz.io came from. Default = `postgres-observability`.  |
| CUSTOM_LISTENER | Set a custom URL to ship metrics to (for example, http://localhost:9200). This overrides the `LOGZIO_REGION` Environment variable. |
| REMOTE_TIMEOUT | the time to wait before throttling remote write post request to logz.io, Default = `120`|
| LOG_LEVEL | Opentelemetry log level, Default = `debug` |
| LOGZIO_LOG_LEVEL | `builder.py` Python script log level. Default = `debug` |

### Run with configuration file
Create `config.yml` file:
```yaml
otel:
  # your logz.io region
  logzio_region: "us"
  # custom listener address
  custom_listener: ""
  # environment tag that will be attached to all samples
  p8s_logzio_name: "postgres-observability"
  # your logz.io metrics token
  token: ""
  # the time to wait before throttling remote write post request to logz.io
  remote_timeout: 120
  # opentelemetry log level
  log_level: "debug"
  # python script log level
  logzio_log_level: "debug"
pg:
  # pg scrape interval
  pg_scrape_interval: 60
  # pg scrape timeout
  pg_scrape_timeout: 120
  # list of instances to monitor
  instances:
    - pg_host: host.com
      pg_port: 5432
      pg_db: postgres
      pg_user: postgres
      pg_password: pass
      # key value pairs of custom labels to attach
      pg_labels:
        - alias: rds-1

    - pg_host: host-2.com
      pg_port: 5432
      pg_db: postgres
      pg_user: postgres
      pg_password: pass
      pg_labels:
        - alias: rds-2
```
Mount the configuration file to your container:
```shell
docker run --rm --name logzio/postgres-rds-collector \
-v <<path_to_config_file>>:/config_files/config.yml \
logzio/postgres-collector
```

### Run with custom queries for postgres exporter:
Postgres exporter queries the database internal tables and converts the results to metrics you can generate custom queries file and mount it to the container. to do so follow these steps:
* Create `custom-queries.yml` file, for example:
```yaml
pg_postmaster:
  query: "SELECT pg_postmaster_start_time as start_time_seconds from pg_postmaster_start_time()"
  master: true
  metrics:
    - start_time_seconds:
        usage: "GAUGE"
        description: "Time at which postmaster started"
```
this file will generate a metric called `pg_postmaster_start_time_seconds`. for more examples you can see [queries.yml](./queries/queries.yml) file
* Run the container and mount your file to `queries` directory:
```shell
docker run --name logzio/postgres-rds-collector \
-v <<path_to_config_file>>:/config_files/config.yml \
-v <<path_to_custom_queries_file>>:/queries/custom-queries.yml \
logzio/postgres-collector
```
### Publish ports
You can monitor the container using opentelemetry extensions in the following ports:
* 8888 - `opentelemetry metrics`
* 55679 - `Zpages`
* 13133 - `Health check`
* 1777 - `Pprof`
You can also publish the ports to your host network by using the `-p` flag
  
```shell
docker run --rm --name logzio/postgres-rds-collector \
-v <<path_to_config_file>>:config_files/config.yml \
-p 8888:8888 \
-p 55679:55679 \
-p 13133:13133 \
-p 1777:1777 \
logzio/postgres-collector
```
