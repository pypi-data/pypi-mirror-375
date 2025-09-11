<div align="center">
    <img src="./static/CHIME_Logger_Logo.png" width="220", height="110">
</div>

<h1 align="center">CHIME Logger</h1>

Chime Logger is a Python logging extension that provides emitters for sending logs to [Grafana Loki](https://grafana.com/oss/loki/) and a file, and custom logging filters for pipeline and event tagging. It is designed for easy integration with Python applications and supports advanced log shipping and tagging use cases. It runs asynchronously, making it suitable for high-performance applications.

## Features

- **Loki Emitters**: Send logs to Loki using different API versions (v0, v1, v2), with support for custom tags and HTTP headers.
- **File Emitter**: Write logs to a local file for debugging and redundancy purposes.
- **Custom Filters**: Automatically add default `resource_name`, `resource_type`, `pipeline` and `site` attributes to log records for consistent tagging.

## Installation

Install the package using your favourite package manager:

**pip**

```bash
pip install chime_logger
```

**poetry**

```bash
poetry add chime_logger
```

**uv**

```bash
uv add chime_logger
```

## Usage

Once you have installed the package, you can use it in your Python application as follows:

```python
import chime_logger, logging
from chime_logger.context import LoggerContext, DynamicLoggerAdapter

chime_logger.setup_logging()

chime_log = logging.getLogger("CHIME")

context = LoggerContext(
    resource_name="a",
    resource_type="N2_Acquisition",
    pipeline="datatrail-registration",
    site="chime",
)

chime_log = DynamicLoggerAdapter(chime_log, context)

chime_log.info("Testing")

context.resource_name = "b"

chime_log.info("Testing take two")
```

Use of the `DynamicLoggerAdapter` adds context to your log messages. This allows you to dynamically change the context for different parts of your application without modifying the logger configuration.

The context fields are validated to ensure that they match the expected types and formats. If a field is set to an invalid value, a `ValidationError` is raised. Eg.

```python
In [10]: context.resource_type = "Fake type"
---------------------------------------------------------------------------
ValidationError                           Traceback (most recent call last)
Cell In[10], line 1
----> 1 context.resource_type = "Fake type"

File ~/Library/Caches/pypoetry/virtualenvs/chime-logger-5IKBwNMQ-py3.13/lib/python3.13/site-packages/pydantic/main.py:394, in BaseModel.__setattr__(self, name, value)
    392 value, error_ = known_field.validate(value, dict_without_original_value, loc=name, cls=self.__class__)
    393 if error_:
--> 394     raise ValidationError([error_], self.__class__)
    395 else:
    396     new_values[name] = value

ValidationError: 1 validation error for LoggerContext
resource_type
  unexpected value; permitted: 'event', 'n2_acquisition', 'raw_adc' (type=value_error.const; given=fake type; permitted=('event', 'n2_acquisition', 'raw_adc'))
```

### Configuration

If you want to send logs to a custom Loki instance or modify the default parameters, configure the logger using these environment variables:

- `CHIME_LOGGER_PIPELINE_NAME`: Name of the pipeline to attach to log records, by default it is set to "unknown_pipeline".
  ```bash
  export CHIME_LOGGER_PIPELINE_NAME="your-pipeline-name"
  ```
  _Default_: "unknown_pipeline"
- `CHIME_LOGGER_LOKI_URL`: URL of your Loki instance
  ```bash
  export CHIME_LOGGER_LOKI_URL="http://your-loki-instance:3100"
  ```
  _Default_: "https://frb.chimenet.ca/loki/loki/api/v1/push"
- `CHIME_LOGGER_LOKI_TENANT`: (Optional) Tenant ID for multi-tenancy
  ```bash
  export CHIME_LOGGER_LOKI_TENANT="your-tenant-id"
  ```
  _Default_: "CHIME". Note that this is ignored in Loki deployments that don't use multi-tenancy.
- `CHIME_LOGGER_LOKI_USER` and `CHIME_LOGGER_LOKI_PASSWORD`: (Optional) Credentials for authentication
  ```bash
  export CHIME_LOGGER_LOKI_USER="your-username"
  export CHIME_LOGGER_LOKI_PASSWORD="your-password"
  ```
  _Default_: None (no authentication)
- `CHIME_LOGGER_FILE_LOG_PATH`: (Optional) Path to a file where logs will be written. This is useful for local debugging.
  ```bash
  export CHIME_LOGGER_FILE_LOG_PATH="/path/to/your/logfile.log"
  ```
  _Default_: "logs/my_app.log"

## License

See [LICENSE](LICENSE) for details.
