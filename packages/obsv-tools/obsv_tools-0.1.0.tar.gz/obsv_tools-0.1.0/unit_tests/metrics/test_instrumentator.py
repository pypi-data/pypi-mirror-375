import pytest
from unittest import mock

import obsv_tools.metrics.instrumentator


@pytest.fixture
def mock_start_http_server():
    with mock.patch('prometheus_client.start_http_server') as mock_server:
        yield mock_server


@pytest.fixture
def mock_meter_provider():
    with mock.patch('opentelemetry.metrics.set_meter_provider') as mock_provider:
        yield mock_provider


@pytest.fixture
def mock_meter():
    with mock.patch('opentelemetry.metrics.get_meter') as mock_get_meter:
        mock_meter_instance = mock.Mock()
        mock_get_meter.return_value = mock_meter_instance
        yield mock_meter_instance


@pytest.fixture
def mock_prometheus_metric_reader():
    with mock.patch('opentelemetry.exporter.prometheus.PrometheusMetricReader') as mock_reader:
        yield mock_reader


@pytest.fixture
def mock_meter_provider_class():
    with mock.patch('opentelemetry.sdk.metrics.MeterProvider') as mock_provider_class:
        yield mock_provider_class


def test_init_When_called_with_port_Then_starts_prometheus_server(
    mock_start_http_server,
    mock_meter_provider,
    mock_meter,
    mock_prometheus_metric_reader,
    mock_meter_provider_class,
):
    server_port = 8080
    
    instrumentator = obsv_tools.metrics.instrumentator.Instrumentator(
        server_port=server_port,
    )
    
    mock_start_http_server.assert_called_once_with(port=server_port)
    assert instrumentator.server_port == server_port


def test_init_When_called_with_custom_meter_name_Then_creates_meter_with_name(
    mock_start_http_server,
    mock_meter_provider,
    mock_meter,
    mock_prometheus_metric_reader,
    mock_meter_provider_class,
):
    server_port = 8080
    meter_name = 'custom_meter'
    
    with mock.patch('opentelemetry.metrics.get_meter') as mock_get_meter:
        obsv_tools.metrics.instrumentator.Instrumentator(
            server_port=server_port,
            meter_name=meter_name,
        )
        
        mock_get_meter.assert_called_once_with(name=meter_name)


def test_init_When_called_without_meter_name_Then_uses_default_name(
    mock_start_http_server,
    mock_meter_provider,
    mock_meter,
    mock_prometheus_metric_reader,
    mock_meter_provider_class,
):
    server_port = 8080
    
    with mock.patch('opentelemetry.metrics.get_meter') as mock_get_meter:
        obsv_tools.metrics.instrumentator.Instrumentator(
            server_port=server_port,
        )
        
        mock_get_meter.assert_called_once_with(name='my_metrics')


def test_init_When_called_Then_initializes_empty_metrics_collections(
    mock_start_http_server,
    mock_meter_provider,
    mock_meter,
    mock_prometheus_metric_reader,
    mock_meter_provider_class,
):
    server_port = 8080
    
    instrumentator = obsv_tools.metrics.instrumentator.Instrumentator(
        server_port=server_port,
    )
    
    assert instrumentator.counters == {}
    assert instrumentator.histograms == {}


def test_add_counter_When_called_with_new_name_Then_creates_counter(
    mock_start_http_server,
    mock_meter_provider,
    mock_meter,
    mock_prometheus_metric_reader,
    mock_meter_provider_class,
):
    instrumentator = obsv_tools.metrics.instrumentator.Instrumentator(
        server_port=8080,
    )
    counter_name = 'test_counter'
    counter_description = 'Test counter description'
    mock_counter = mock.Mock()
    mock_meter.create_counter.return_value = mock_counter
    
    result = instrumentator.add_counter(
        name=counter_name,
        description=counter_description,
    )
    
    mock_meter.create_counter.assert_called_once_with(
        name=counter_name,
        description=counter_description,
    )
    assert instrumentator.counters[counter_name] == mock_counter
    assert result == instrumentator


def test_add_counter_When_counter_already_exists_Then_logs_debug_and_returns_self(
    mock_start_http_server,
    mock_meter_provider,
    mock_meter,
    mock_prometheus_metric_reader,
    mock_meter_provider_class,
    caplog,
):
    instrumentator = obsv_tools.metrics.instrumentator.Instrumentator(
        server_port=8080,
    )
    counter_name = 'existing_counter'
    counter_description = 'Test counter description'
    mock_counter = mock.Mock()
    instrumentator.counters[counter_name] = mock_counter
    
    with caplog.at_level('DEBUG'):
        result = instrumentator.add_counter(
            name=counter_name,
            description=counter_description,
        )
    
    mock_meter.create_counter.assert_not_called()
    assert result == instrumentator
    assert 'Counter with this name already exists' in caplog.text


def test_add_histogram_When_called_with_new_name_Then_creates_histogram(
    mock_start_http_server,
    mock_meter_provider,
    mock_meter,
    mock_prometheus_metric_reader,
    mock_meter_provider_class,
):
    instrumentator = obsv_tools.metrics.instrumentator.Instrumentator(
        server_port=8080,
    )
    histogram_name = 'test_histogram'
    histogram_description = 'Test histogram description'
    mock_histogram = mock.Mock()
    mock_meter.create_histogram.return_value = mock_histogram
    
    result = instrumentator.add_histogram(
        name=histogram_name,
        description=histogram_description,
    )
    
    mock_meter.create_histogram.assert_called_once_with(
        name=histogram_name,
        description=histogram_description,
    )
    assert instrumentator.histograms[histogram_name] == mock_histogram
    assert result == instrumentator


def test_add_histogram_When_histogram_already_exists_Then_logs_debug_and_returns_self(
    mock_start_http_server,
    mock_meter_provider,
    mock_meter,
    mock_prometheus_metric_reader,
    mock_meter_provider_class,
    caplog,
):
    instrumentator = obsv_tools.metrics.instrumentator.Instrumentator(
        server_port=8080,
    )
    histogram_name = 'existing_histogram'
    histogram_description = 'Test histogram description'
    mock_histogram = mock.Mock()
    instrumentator.histograms[histogram_name] = mock_histogram
    
    with caplog.at_level('DEBUG'):
        result = instrumentator.add_histogram(
            name=histogram_name,
            description=histogram_description,
        )
    
    mock_meter.create_histogram.assert_not_called()
    assert result == instrumentator
    assert 'Histogram with this name already exists' in caplog.text


def test_increment_counter_When_counter_exists_Then_calls_add_with_default_amount(
    mock_start_http_server,
    mock_meter_provider,
    mock_meter,
    mock_prometheus_metric_reader,
    mock_meter_provider_class,
):
    instrumentator = obsv_tools.metrics.instrumentator.Instrumentator(
        server_port=8080,
    )
    counter_name = 'test_counter'
    mock_counter = mock.Mock()
    instrumentator.counters[counter_name] = mock_counter
    attributes = {'label1': 'value1', 'label2': 'value2'}
    
    instrumentator.increment_counter(
        name=counter_name,
        attributes=attributes,
    )
    
    mock_counter.add.assert_called_once_with(
        amount=1,
        attributes=attributes,
    )


def test_increment_counter_When_counter_exists_and_custom_amount_Then_calls_add_with_amount(
    mock_start_http_server,
    mock_meter_provider,
    mock_meter,
    mock_prometheus_metric_reader,
    mock_meter_provider_class,
):
    instrumentator = obsv_tools.metrics.instrumentator.Instrumentator(
        server_port=8080,
    )
    counter_name = 'test_counter'
    mock_counter = mock.Mock()
    instrumentator.counters[counter_name] = mock_counter
    attributes = {'label1': 'value1'}
    amount = 5
    
    instrumentator.increment_counter(
        name=counter_name,
        attributes=attributes,
        amount=amount,
    )
    
    mock_counter.add.assert_called_once_with(
        amount=amount,
        attributes=attributes,
    )


def test_increment_counter_When_counter_exists_and_float_amount_Then_calls_add_with_float(
    mock_start_http_server,
    mock_meter_provider,
    mock_meter,
    mock_prometheus_metric_reader,
    mock_meter_provider_class,
):
    instrumentator = obsv_tools.metrics.instrumentator.Instrumentator(
        server_port=8080,
    )
    counter_name = 'test_counter'
    mock_counter = mock.Mock()
    instrumentator.counters[counter_name] = mock_counter
    attributes = {'label1': 'value1'}
    amount = 2.5
    
    instrumentator.increment_counter(
        name=counter_name,
        attributes=attributes,
        amount=amount,
    )
    
    mock_counter.add.assert_called_once_with(
        amount=amount,
        attributes=attributes,
    )


def test_increment_counter_When_counter_does_not_exist_Then_raises_value_error(
    mock_start_http_server,
    mock_meter_provider,
    mock_meter,
    mock_prometheus_metric_reader,
    mock_meter_provider_class,
):
    instrumentator = obsv_tools.metrics.instrumentator.Instrumentator(
        server_port=8080,
    )
    counter_name = 'nonexistent_counter'
    attributes = {'label1': 'value1'}
    
    with pytest.raises(ValueError, match=f'Unknown counter name - {counter_name}'):
        instrumentator.increment_counter(
            name=counter_name,
            attributes=attributes,
        )


def test_record_histogram_When_histogram_exists_Then_calls_record(
    mock_start_http_server,
    mock_meter_provider,
    mock_meter,
    mock_prometheus_metric_reader,
    mock_meter_provider_class,
):
    instrumentator = obsv_tools.metrics.instrumentator.Instrumentator(
        server_port=8080,
    )
    histogram_name = 'test_histogram'
    mock_histogram = mock.Mock()
    instrumentator.histograms[histogram_name] = mock_histogram
    attributes = {'label1': 'value1', 'label2': 'value2'}
    amount = 10
    
    instrumentator.record_histogram(
        name=histogram_name,
        attributes=attributes,
        amount=amount,
    )
    
    mock_histogram.record.assert_called_once_with(
        amount=amount,
        attributes=attributes,
    )


def test_record_histogram_When_histogram_exists_and_float_amount_Then_calls_record_with_float(
    mock_start_http_server,
    mock_meter_provider,
    mock_meter,
    mock_prometheus_metric_reader,
    mock_meter_provider_class,
):
    instrumentator = obsv_tools.metrics.instrumentator.Instrumentator(
        server_port=8080,
    )
    histogram_name = 'test_histogram'
    mock_histogram = mock.Mock()
    instrumentator.histograms[histogram_name] = mock_histogram
    attributes = {'label1': 'value1'}
    amount = 15.7
    
    instrumentator.record_histogram(
        name=histogram_name,
        attributes=attributes,
        amount=amount,
    )
    
    mock_histogram.record.assert_called_once_with(
        amount=amount,
        attributes=attributes,
    )


def test_record_histogram_When_histogram_does_not_exist_Then_raises_value_error(
    mock_start_http_server,
    mock_meter_provider,
    mock_meter,
    mock_prometheus_metric_reader,
    mock_meter_provider_class,
):
    instrumentator = obsv_tools.metrics.instrumentator.Instrumentator(
        server_port=8080,
    )
    histogram_name = 'nonexistent_histogram'
    attributes = {'label1': 'value1'}
    amount = 10
    
    with pytest.raises(ValueError, match=f'Unknown histogram name - {histogram_name}'):
        instrumentator.record_histogram(
            name=histogram_name,
            attributes=attributes,
            amount=amount,
        )