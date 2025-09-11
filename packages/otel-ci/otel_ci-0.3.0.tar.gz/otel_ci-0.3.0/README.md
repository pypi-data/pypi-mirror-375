# Opentelemetry CI

A python utility library (similar to [otel-cli](https://github.com/equinix-labs/otel-cli)) for recording and
generating spans in the CLI.

Similar to `otel-cli`; spans are propagated via environment variables.

Unlike `otel-cli`; spans can be exported to a directory and then replayed in bulk to an otel receiver. This is useful
when you do not want the overhead/delay of exporting spans live.

## Usage

Generating spans via `otel-cli`

```bash
uv tool install otel-cli

# Record a single span
otel-ci exec ls

# Nested span recording
otel-ci exec otel-ci exec ls

# Exporting to disk and replaying results
export OTEL_EXPORTER_FILE_DIRECTORY="/tmp/out"
export OTEL_TRACES_EXPORTER="file"
otel-ci --service test exec ls
# or
otel-ci --service=test -d /tmp/out -e file exec ls

export OTEL_TRACES_EXPORTER="otlp"
export OTEL_EXPORTER_OTLP_PROTOCOL="grpc"
export OTEL_EXPORTER_OTLP_ENDPOINT="localhost:4317"
otel-ci replay -d "/tmp/out"
```