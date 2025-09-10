# obsv-tools

Observability tools for Python applications with OpenTelemetry integration.

## Features

- Easy-to-use instrumentator for metrics collection
- OpenTelemetry integration
- Prometheus metrics export
- Simple counter and histogram support

## Installation

```bash
pip install obsv-tools
```

## Quick Start

```python
import obsv_tools.metrics.instrumentator

# Create an instrumentator instance
instrumentator = obsv_tools.metrics.instrumentator.Instrumentator(
    server_port=8000,
    meter_name='my_app_metrics',
)

# Add metrics
instrumentator.add_counter(
    name='my_counter',
    description='A simple counter',
).add_histogram(
    name='my_histogram',
    description='A simple histogram',
)

# Start the metrics server
instrumentator.start()

# Use the metrics
instrumentator.increment_counter('my_counter', attributes={})
instrumentator.record_histogram('my_histogram', 1.0, attributes={})
```

## Requirements

- Python >= 3.12

## License

MIT License - see LICENSE file for details.
