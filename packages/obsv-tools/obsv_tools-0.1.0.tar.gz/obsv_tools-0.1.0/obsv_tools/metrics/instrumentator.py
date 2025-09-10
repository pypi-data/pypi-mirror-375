import logging

import opentelemetry.exporter.prometheus
import opentelemetry.metrics
import prometheus_client


logger = logging.getLogger(__name__)


class Instrumentator:
    def __init__(
        self,
        server_port: int,
        meter_name: str = 'my_metrics',
    ) -> None:
        self.server_port = server_port
        prometheus_client.start_http_server(
            port=server_port,
        )

        opentelemetry.metrics.set_meter_provider(
            opentelemetry.sdk.metrics.MeterProvider(
                metric_readers=[
                    opentelemetry.exporter.prometheus.PrometheusMetricReader(),
                ],
            ),
        )
        self.meter = opentelemetry.metrics.get_meter(
            name=meter_name,
        )

        self.counters: dict[str, opentelemetry.metrics.Counter] = {}
        self.histograms: dict[str, opentelemetry.metrics.Histogram] = {}

    def add_counter(
        self,
        name: str,
        description: str,
    ) -> 'Instrumentator':
        if name in self.counters:
            logger.debug(
                msg='Counter with this name already exists',
                extra={
                    'counter_name': name,
                },
            )

            return self

        self.counters[name] = self.meter.create_counter(
            name=name,
            description=description,
        )

        return self

    def add_histogram(
        self,
        name: str,
        description: str,
    ) -> 'Instrumentator':
        if name in self.histograms:
            logger.debug(
                msg='Histogram with this name already exists',
                extra={
                    'histogram_name': name,
                },
            )

            return self

        self.histograms[name] = self.meter.create_histogram(
            name=name,
            description=description,
        )

        return self

    def increment_counter(
        self,
        name: str,
        attributes: dict[str, str],
        amount: int | float = 1,
    ) -> None:
        if name not in self.counters:
            raise ValueError(f'Unknown counter name - {name}')

        self.counters[name].add(
            amount=amount,
            attributes=attributes,
        )

    def record_histogram(
        self,
        name: str,
        attributes: dict[str, str],
        amount: int | float,
    ) -> None:
        if name not in self.histograms:
            raise ValueError(f'Unknown histogram name - {name}')

        self.histograms[name].record(
            amount=amount,
            attributes=attributes,
        )