# ZenX Mini-Framework

## CLI Commands

### `zenx startproject`
Create a new ZenX project:
```bash
zenx startproject PROJECT_NAME
```


### `zenx list`
Display all available spiders, listeners, and pipelines:
```bash
zenx list
```

### `zenx crawl`
Run one or more spiders:

```bash
# Run a single spider
zenx crawl spider1

# Run multiple spiders
zenx crawl spider1 spider2 spider3

# Run all spiders
zenx crawl all

# Run continuously (scheduled execution)
zenx crawl spider1 --forever
```

## Configuration

### Default Settings

```bash
# Application Settings
APP_ENV=dev
LOG_LEVEL=DEBUG

# Performance Settings
SESSION_POOL_SIZE=1
# seconds (default 30 min)
MAX_SCRAPE_DELAY=1800.0
CONCURRENCY=1
TASK_INTERVAL_SECONDS=1.0
START_OFFSET_SECONDS=5.0

# Database Settings
DB_TYPE=memory
DQ_MAX_SIZE=1000

#DB_TYPE=redis
DB_NAME=
DB_USER=
DB_PASS=
DB_HOST=localhost
DB_PORT=6379
#-- 40 days (40*24*60*60)
REDIS_RECORD_EXPIRY_SECONDS=3456000

# Network Settings
PROXY=

# Synoptic Integration Settings
SYNOPTIC_GRPC_SERVER_URI=ingress.opticfeeds.com
SYNOPTIC_GRPC_TOKEN=
SYNOPTIC_GRPC_ID=

SYNOPTIC_DISCORD_WEBHOOK=

SYNOPTIC_WS_API_KEY=
SYNOPTIC_WS_STREAM_ID=
SYNOPTIC_FREE_WS_API_KEY=
SYNOPTIC_FREE_WS_STREAM_ID=

# Enterprise gRPC Settings
SYNOPTIC_ENTERPRISE_USEAST1_GRPC_SERVER_URI=us-east-1.enterprise.synoptic.com:50051
SYNOPTIC_ENTERPRISE_EUCENTRAL1_GRPC_SERVER_URI=eu-central-1.enterprise.synoptic.com:50051
SYNOPTIC_ENTERPRISE_EUWEST2_GRPC_SERVER_URI=eu-west-2.enterprise.synoptic.com:50051
SYNOPTIC_ENTERPRISE_USEAST1CHI2A_GRPC_SERVER_URI=us-east-1-chi-2a.enterprise.synoptic.com:50051
SYNOPTIC_ENTERPRISE_USEAST1NYC2A_GRPC_SERVER_URI=us-east-1-nyc-2a.enterprise.synoptic.com:50051
SYNOPTIC_ENTERPRISE_APNORTHEAST1_GRPC_SERVER_URI=ap-northeast-1.enterprise.synoptic.com:50051
SYNOPTIC_ENTERPRISE_GRPC_TOKEN=
SYNOPTIC_ENTERPRISE_GRPC_ID=

# Monitoring Settings
MONITOR_ITXP_TOKEN=
MONITOR_ITXP_URI=
```


#### Application Settings
- `APP_ENV`: Environment mode (`"dev"`) - In dev mode, only preprocess pipeline runs
- `LOG_LEVEL`: Logging level (`"DEBUG"`)

#### Performance Settings
- `SESSION_POOL_SIZE`: HTTP session pool size (`1`)
- `MAX_SCRAPE_DELAY`: Maximum allowed scrape delay in seconds (`3600.0`)
- `CONCURRENCY`: Number of concurrent tasks (`1`)
- `TASK_INTERVAL_SECONDS`: Interval between scheduled tasks (`1.0`)
- `START_OFFSET_SECONDS`: Start offset for scheduled tasks (`5.0`)

#### Database Settings
- `DB_TYPE`: Database type (`"memory"` or `"redis"`)
- `DB_NAME`: Database name (`None`)
- `DB_USER`: Database username (`None`)
- `DB_PASS`: Database password (`None`)
- `DB_HOST`: Database host (`localhost`)
- `DB_PORT`: Database port (`6379`)
- `DQ_MAX_SIZE`: Memory database max size (`1000`)
- `REDIS_RECORD_EXPIRY_SECONDS`: Redis record expiry (`3456000` - 40 days)

#### Network Settings
- `PROXY`: HTTP proxy URL (`None`)

#### Synoptic Integration Settings
- `SYNOPTIC_GRPC_SERVER_URI`: gRPC server URI (`"ingress.opticfeeds.com"`)
- `SYNOPTIC_GRPC_TOKEN`: gRPC authentication token (`None`)
- `SYNOPTIC_GRPC_ID`: gRPC client ID (`None`)
- `SYNOPTIC_DISCORD_WEBHOOK`: Discord webhook URL (`None`)
- `SYNOPTIC_WS_API_KEY`: WebSocket API key (`None`)
- `SYNOPTIC_WS_STREAM_ID`: WebSocket stream ID (`None`)

#### Enterprise Settings
Multiple enterprise gRPC endpoints are supported:
- `SYNOPTIC_ENTERPRISE_USEAST1_GRPC_SERVER_URI`
- `SYNOPTIC_ENTERPRISE_EUCENTRAL1_GRPC_SERVER_URI`
- `SYNOPTIC_ENTERPRISE_EUWEST2_GRPC_SERVER_URI`
- `SYNOPTIC_ENTERPRISE_USEAST1CHI2A_GRPC_SERVER_URI`
- `SYNOPTIC_ENTERPRISE_USEAST1NYC2A_GRPC_SERVER_URI`
- `SYNOPTIC_ENTERPRISE_APNORTHEAST1_GRPC_SERVER_URI`

#### Monitoring Settings
- `MONITOR_ITXP_TOKEN`: ITXP monitoring token (`None`)
- `MONITOR_ITXP_URI`: ITXP monitoring URI (`None`)

#### Quickstart:
```bash
docker run -d --name redis -p 127.0.0.1:6379:6379 -v redis-data:/data redis
```
