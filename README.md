# Postgres rds collector
Collects rds host metrics from cloudwatch, database metrics using postgres exporter, query logs using fluentd and forward the data to logz.io, based on opentelemetry collector

### **Note:**
* Extra calls and charges on AWS API requests may be generated by this project.

* You can track the number of AWS API requests with the `cloudwatch_requests_total` metric, which provides labels with the API name and namespace specification. For example :
  `cloudwatch_requests_total{action="getMetricStatistics",namespace="AWS/EC2",} 876.0`.

* For more information about the prom/cloudwatch-exporter cost, refer to the relevant [Prometheus documentation](https://github.com/prometheus/cloudwatch_exporter#cost) and to the [AWS cloudwatch API pricing page](https://aws.amazon.com/cloudwatch/pricing/).

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



### Quick start with environment variables
```shell
docker run --name postgres-rds-collector \
-e TOKEN=<<TOKEN>> \
-e LOGZIO_REGION=<<LOGZIO_REGION>> \
-e AWS_REGION=<<AWS_REGION>> \
-e AWS_ACCESS_KEY_ID=<<AWS_ACCESS_KEY_ID>> \
-e AWS_SECRET_ACCESS_KEY=<<AWS_SECRET_ACCESS_KEY>> \
-e RDS_INSTANCES=<<AWS_NAMESPACES>> \
-e PG_HOST=<<PG_HOST>> \
-e PG_USER=<<PG_USER>> \
-e PG_PASSWORD=<<PG_PASSWORD>> \
-e LOGZIO_LOG_TOKEN=<<LOGZIO_LOG_TOKEN>> \
logzio/postgres-rds-collector
```

#### Full list of configurable environment variables

| Environment variable | Description |
|---|---|
| AWS_REGION (Required) | Your region's slug. You can find this in the AWS Console region menu (in the top menu, to the right).  **Note:** This is the region that you will collect metrics from. |
| LOGZIO_REGION (Required)| Your Logz.io region code. For example if your region is US, then your region code is `us`. You can find your region code here: https://docs.logz.io/user-guide/accounts/account-region.html#regions-and-urls. |
| TOKEN (Required)| Token for shipping metrics to your Logz.io account. Find it under Settings > Manage accounts. [_How do I look up my Metrics account token?_](/user-guide/accounts/finding-your-metrics-account-token/) |
| LOGZIO_LOG_TOKEN (Required) | . Your Logz.io logs account token. Replace `LOGZIO_LOG_TOKEN` with the [token](https://app.logz.io/#/dashboard/settings/general) of the logs account you want to ship to. |
| RDS_INSTANCES (Required) | Comma-separated list of namespaces of the metrics you want to collect. You can find a complete list of namespaces at [_AWS Services That Publish CloudWatch Metrics_](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/aws-services-cloudwatch-metrics.html).   **Note:** This Environment variable is required unless you define the `CUSTOM_CONFIG` Environment variable |
| PG_HOST (Required) | the host address of your postgresql database (ex: database.rds.amazonaws.com) |
| PG_PASSWORD (Required)| postgresql database password. |
| PG_USER | postgresql database username . Default = `postgres` |
| AWS_ROLE_ARN | Your IAM role to assume. |
| AWS_ACCESS_KEY_ID | Your IAM user's access key ID. |
| AWS_SECRET_ACCESS_KEY | Your IAM user's secret key. |
| SCRAPE_INTERVAL | The time interval (in seconds) during which the Cloudwatch exporter retrieves metrics from Cloudwatch, and the Opentelemtry collector scrapes and sends the metrics to Logz.io. Default = `300`.   **Note:** This value must be a multiple of 60.|
| P8S_LOGZIO_NAME | The value of the `p8s_logzio_name` external label. This variable identifies which Prometheus environment the metrics arriving at Logz.io came from. Default = `postgres-observability`.  |
| CUSTOM_CONFIG | Mount your cloudwatch exporter configuration file `-v pathToConfig/config.yml:config_files/cloudwatch.yml` and set to `true` if you want to use custom configuration for cloudwatch exporter, Default = `false` |
| CUSTOM_LISTENER | Set a custom URL to ship metrics to (for example, http://localhost:9200). This overrides the `LOGZIO_REGION` Environment variable. |
| SCRAPE_TIMEOUT | The time to wait before throttling a scrape request to cloudwatch exporter, Default = `120`|
| REMOTE_TIMEOUT | the time to wait before throttling remote write post request to logz.io, Default = `120`|
| LOG_LEVEL | Opentelemetry log level, Default = `debug` |
| LOGZIO_LOG_LEVEL | `builder.py` Python script log level. Default = `debug` |
| SET_TIMESTAMP | Boolean for whether to set the Prometheus metric timestamp as the original Cloudwatch timestamp. Default = `false` |
| PERIOD_SECONDS | period to request the metric for. Only the most recent data point is used. Default = `300` |
| RANGE_SECONDS | how far back to request data for. Useful for cases such as Billing metrics that are only set every few hours. Default = `300` |
| DELAY_SECONDS | The newest data to request. Used to avoid collecting data that has not fully converged. Default = `300` |
| PG_PORT | postgresql database port . Default = `5432` |
| PG_DB | postgresql database name . Default = `postgres` |
| PG_SCRAPE_INTERVAL | postgresql database scrape interval . Default = `60` |
| PG_SCRAPE_TIMEOUT | postgresql database scrape timeout . Default = `60` |
| LOGZIO_LOG_LISTENER | your region’s listener host . For more information on finding your account’s region, see Account region. Default= `https://listener.logz.io:8071`  |
| LOGZIO_TYPE | The log type you'll use with this Docker. This is shown in your logs under the `type` field in Kibana. <br> Logz.io applies parsing based on `type`. Default=`postgres-observability` |
| SLOW_FLUSH_LOG_THRESHOLD | The threshold for chunk flush performance check. Default=`20.0` |
| BUFFER_TYPE | Specifies which plugin to use as the backend. Default=`file` |
| BUFFER_PATH | Path of the buffer. Default=`/var/log/Fluentd-buffers/stackdriver.buffer` |
| OVERFLOW_ACTION | Controls the behavior when the queue becomes full. Refer to [fluentd docs](https://docs.fluentd.org/output#overflow_action) for more details about your options. Default=`block` |
| CHUNK_LIMIT_SIZE | Maximum size of a chunk allowed. Default=`2M`  |
| QUEUE_LIMIT_LENGTH | Maximum length of the output queue. Default=`6`  |
| FLUSH_INTERVAL | Interval, in seconds, to wait before invoking the next buffer flush. Default=`5s` |
| RETRY_MAX_INTERVAL | Maximum interval, in seconds, to wait between retries. Default=`30s` |
| FLUSH_THREAD_COUNT | Number of threads to flush the buffer. Default=`2` |

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
  # the time to wait between scrape requests
  scrape_interval: 300
  # the time to wait before throttling remote write post request to logz.io
  remote_timeout: 120
  # the time to wait before throttling a scrape request to cloudwatch exporter
  scrape_timeout: 120
  # opentelemetry log level
  log_level: "debug"
  # python script log level
  logzio_log_level: "debug"
  # aws credentials
  AWS_ACCESS_KEY_ID: ""
  AWS_SECRET_ACCESS_KEY: ""
cloudwatch:
  # set to true if you are loading a custom configuration file for cloudwatch exporter
  custom_config: "false"
  # your cloudwatch aws region
  region: "us-east-1"
  # role arn to assume
  role_arn: ""
  # list of rds instances to monitor
  rds_instances: ["instance-1","instance-2"]
  # The newest data to request. Used to avoid collecting data that has not fully converged
  delay_seconds: 300
  # how far back to request data for. Useful for cases such as Billing metrics that are only set every few hours
  range_seconds: 300
  # period to request the metric for. Only the most recent data point is used
  period_seconds: 300
  # boolean for whether to set the Prometheus metric timestamp as the original Cloudwatch timestamp
  set_timestamp: "false"
pg:
  # pg database host
  pg_host:
  # pg database port
  pg_port: 5432
  # pg database name
  pg_db: postgres
  # pg database username
  pg_user: postgres
  # pg database password
  pg_password:
  # pg scrape interval
  pg_scrape_interval: 60
  # pg scrape timeout
  pg_scrape_timeout: 60

fluentd:
  
  logzio_log_listener: "https://listener.logz.io:8071"

  logzio_log_token: ""

  logzio_type: "postgres-observability"

  buffer_type: "file"

  buffer_path: "/var/log/fluentd-buffers/stackdriver.buffer"

  overflow_action: "block"

  chunk_limit_size: "2M"

  queue_limit_length: "6"

  flush_interval: "5s"

  retry_max_interval: "30"

  retry_forever: "true"

  flush_thread_count: "2"

  slow_flush_log_threshold: "20.0"
```
Mount the configuration file to your container:
```shell
docker run --rm --name logzio/postgres-rds-collector \
-v <<path_to_config_file>>:/config_files/config.yml \
logzio/postgres-rds-collector
```

### Run with custom cloudwatch exporter configuration
Create `cloudwatch.yml` file (for details refer to [prom/cloudwatch_exporter](https://github.com/prometheus/cloudwatch_exporter#configuration) project),
and mount the configuration file to your container and set `CUSTOM_CONFIG` variable to `true`
```shell
docker run --name logzio/postgres-rds-collector \
-e TOKEN=<<TOKEN>> \
-e LOGZIO_REGION=<<LOGZIO_REGION>> \
-e AWS_REGION=<<AWS_REGION>> \
-e AWS_ACCESS_KEY_ID=<<AWS_ACCESS_KEY_ID>> \
-e AWS_SECRET_ACCESS_KEY=<<AWS_SECRET_ACCESS_KEY>> \
-e RDS_INSTANCES=<<AWS_NAMESPACES>> \
-e PG_HOST=<<PG_HOST>> \
-e PG_USER=<<PG_USER>> \
-e PG_PASSWORD=<<PG_PASSWORD>> \
-e LOGZIO_LOG_TOKEN=<<LOGZIO_LOG_TOKEN>> \
-e CUSTOM_CONFIG=true \
-v <<path_to_cloudwatch_config_file>>:/config_files/cloudwatch.yml \
logzio/postgres-rds-collector
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
-e TOKEN=<<TOKEN>> \
-e LOGZIO_REGION=<<LOGZIO_REGION>> \
-e AWS_REGION=<<AWS_REGION>> \
-e AWS_ACCESS_KEY_ID=<<AWS_ACCESS_KEY_ID>> \
-e AWS_SECRET_ACCESS_KEY=<<AWS_SECRET_ACCESS_KEY>> \
-e RDS_INSTANCES=<<AWS_NAMESPACES>> \
-e PG_HOST=<<PG_HOST>> \
-e PG_USER=<<PG_USER>> \
-e PG_PASSWORD=<<PG_PASSWORD>> \
-e LOGZIO_LOG_TOKEN=<<LOGZIO_LOG_TOKEN>> \
-e CUSTOM_CONFIG=true \
-v <<path_to_custom_queries_file>>:/queries/custom-queries.yml \
logzio/postgres-rds-collector
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
logzio/postgres-rds-collector
```