import time
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional

from . import globals
from .config import config
from .forkable import ForksafeLock, ForksafeMapping
from .format_utils import format_path_metric
from .logging import internal_logger
from .native import SketchData, get_time
from .schemas.events import EndpointMetric as EndpointMetricEvent
from .schemas.events import FlowMetric as FlowMetricEvent
from .schemas.events import KafkaMetric as KafkaMetricEvent
from .schemas.events import Sketch
from .utils import get_time_since_epoch_in_ns, timestamp_to_ns


class FlowMetric(ABC):
    def __init__(self, flow_id: Optional[str] = None) -> None:
        self.flow_id = flow_id
        self.duration = 0
        self.start_time = 0

    def start(self) -> None:
        self.start_time = get_time()

    def stop(self) -> None:
        if self.start_time > 0:
            self.duration = get_time() - self.start_time

    def save(self) -> None:
        if globals.metrics_aggregator is None:
            internal_logger.error("Metrics aggregator is not initialized")
            return
        globals.metrics_aggregator.add_metric(self)

    @abstractmethod
    def get_aggregation_key(self) -> str:
        pass

    def type_name(self) -> str:
        return type(self).__name__


class EndpointMetric(FlowMetric):
    def __init__(self, flow_id: Optional[str] = None) -> None:
        super().__init__(flow_id)
        self.status_code = None  # type: Optional[int]
        self.route = None  # type: Optional[str]
        self.method = None  # type: Optional[str]

    def set_request_attributes(self, route: str, method: str) -> None:
        self.route = format_path_metric(route)
        self.method = method.upper()

    def set_response_attributes(self, status_code: int) -> None:
        self.status_code = status_code

    def get_aggregation_key(self) -> str:
        if (
            self.flow_id is None
            or self.route is None
            or self.method is None
            or self.status_code is None
        ):
            internal_logger.warning(
                "Metric is missing required attributes",
                data=self.__dict__,
            )
            raise ValueError("Metric is missing required attributes")

        key = "{}|{}|{}|{}".format(
            self.flow_id, self.route, self.method, self.status_code
        )
        return key


class KafkaMetric(FlowMetric):
    def __init__(self, flow_id: Optional[str] = None) -> None:
        super().__init__(flow_id)
        self.partition = None  # type: Optional[int]
        self.error = None  # type: Optional[str]
        self.produced_timestamp = None  # type: Optional[int]
        self.total_consumed_duration = 0

    def set_partition(self, partition: int) -> None:
        self.partition = partition

    def set_error(self, error: str) -> None:
        self.error = error

    def set_produced_timestamp(self, produced_timestamp: Optional[int]) -> None:
        self.produced_timestamp = produced_timestamp

    def stop(self) -> None:
        super().stop()
        if self.produced_timestamp:
            self.total_consumed_duration = (
                get_time_since_epoch_in_ns() - timestamp_to_ns(self.produced_timestamp)
            )

    def get_aggregation_key(self) -> str:
        if self.flow_id is None or self.partition is None:
            internal_logger.warning(
                "Metric is missing required attributes",
                data=self.__dict__,
            )
            raise ValueError("Metric is missing required attributes")
        key = "{}|{}".format(self.flow_id, self.partition)
        return key


class AggregatedFlowMetric(ABC):
    def __init__(self, flow_id: str) -> None:
        self.flow_id = flow_id
        self.count = 0
        self.sum_duration = 0
        self.sum_squared_duration = 0.0
        self.sketch_data = SketchData(config.sketch_bin_width)

    def update(self, metric: FlowMetric) -> None:
        self.count += 1
        self.sum_duration += metric.duration
        self.sum_squared_duration += metric.duration**2
        if metric.duration != 0:
            self.sketch_data.add(metric.duration)

    @abstractmethod
    def to_event(self, timeslice: int) -> FlowMetricEvent:
        pass

    @classmethod
    @abstractmethod
    def create_from_metric(cls, metric: FlowMetric) -> "AggregatedFlowMetric":
        pass


class AggregatedEndpointMetric(AggregatedFlowMetric):
    def __init__(self, flow_id: str, route: str, method: str, status_code: int) -> None:
        super().__init__(flow_id)
        self.route = route
        self.method = method
        self.status_code = status_code

    def to_event(self, timeslice: int) -> EndpointMetricEvent:
        if self.count == 0:
            raise ValueError("No metrics to aggregate")

        sketch = Sketch(
            bin_width=self.sketch_data.bin_width,
            index_shift=self.sketch_data.index_shift,
            data=self.sketch_data.data.copy(),
        )

        return EndpointMetricEvent(
            flow_id=self.flow_id,
            count=self.count,
            sum_duration=self.sum_duration,
            sum_squared_duration=self.sum_squared_duration,
            timeslice=timeslice,
            timestamp=datetime.now(timezone.utc),
            sketch=sketch,
            status_code=self.status_code,
            method=self.method,
        )

    @classmethod
    def create_from_metric(cls, metric: FlowMetric) -> "AggregatedEndpointMetric":
        if not isinstance(metric, EndpointMetric):
            raise TypeError("metric must be an EndpointMetric")
        if (
            metric.flow_id is None
            or metric.route is None
            or metric.method is None
            or metric.status_code is None
        ):
            raise ValueError("Metric is missing required attributes")
        return cls(
            flow_id=metric.flow_id,
            route=metric.route,
            method=metric.method,
            status_code=metric.status_code,
        )


class AggregatedKafkaMetric(AggregatedFlowMetric):
    def __init__(self, flow_id: str, partition: int, error: Optional[str]) -> None:
        super().__init__(flow_id)
        self.partition = partition
        self.error = error
        self.sum_consumed_duration = 0
        self.sum_squared_consumed_duration = 0.0
        self.sketch_consumed_data = SketchData(config.sketch_bin_width)

    def update(self, metric: FlowMetric) -> None:
        super().update(metric)
        if not isinstance(metric, KafkaMetric):
            return
        if metric.total_consumed_duration != 0:
            self.sum_consumed_duration += metric.total_consumed_duration
            self.sum_squared_consumed_duration += metric.total_consumed_duration**2
            self.sketch_consumed_data.add(metric.total_consumed_duration)

    def to_event(self, timeslice: int) -> KafkaMetricEvent:
        if self.count == 0:
            raise ValueError("No metrics to aggregate")

        sketch = Sketch(
            bin_width=self.sketch_data.bin_width,
            index_shift=self.sketch_data.index_shift,
            data=self.sketch_data.data.copy(),
        )
        sketch_consumed = Sketch(
            bin_width=self.sketch_consumed_data.bin_width,
            index_shift=self.sketch_consumed_data.index_shift,
            data=self.sketch_consumed_data.data.copy(),
        )

        return KafkaMetricEvent(
            flow_id=self.flow_id,
            count=self.count,
            sum_duration=self.sum_duration,
            sum_squared_duration=self.sum_squared_duration,
            timeslice=timeslice,
            timestamp=datetime.now(timezone.utc),
            sketch=sketch,
            partition=self.partition,
            error=self.error,
            sum_consumed_duration=self.sum_consumed_duration,
            sum_squared_consumed_duration=self.sum_squared_consumed_duration,
            sketch_consume=sketch_consumed,
        )

    @classmethod
    def create_from_metric(cls, metric: FlowMetric) -> "AggregatedKafkaMetric":
        if not isinstance(metric, KafkaMetric):
            raise TypeError("metric must be a KafkaMetric")
        if metric.flow_id is None or metric.partition is None:
            raise ValueError("Metric is missing required attributes")
        return cls(
            flow_id=metric.flow_id, partition=metric.partition, error=metric.error
        )


class FlowMetricsAggregator:
    def __init__(self) -> None:
        self.aggregated_metrics_storage = ForksafeMapping(
            lambda: defaultdict(dict)
        )  # type: ForksafeMapping[str, Dict[str, AggregatedFlowMetric]]
        self.lock = ForksafeLock()
        self.last_dump = time.perf_counter()

    def add_metric(self, metric: FlowMetric) -> None:
        metric_type = metric.type_name()
        try:
            aggregation_key = metric.get_aggregation_key()
        except ValueError:
            internal_logger.warning(
                "Failed to get aggregation key for metric",
                data=metric.__dict__,
            )
            return

        with self.lock:
            if aggregation_key in self.aggregated_metrics_storage[metric_type]:
                try:
                    aggregated_metric = self.aggregated_metrics_storage[metric_type][
                        aggregation_key
                    ]
                    aggregated_metric.update(metric)
                except Exception:
                    internal_logger.warning(
                        "Failed to update aggregated metric",
                        data=metric.__dict__,
                        exc_info=True,
                    )
            else:
                try:
                    if isinstance(metric, EndpointMetric):
                        aggregated_metric = AggregatedEndpointMetric.create_from_metric(
                            metric
                        )
                    elif isinstance(metric, KafkaMetric):
                        aggregated_metric = AggregatedKafkaMetric.create_from_metric(
                            metric
                        )
                    else:
                        internal_logger.warning(
                            "Unsupported metric type",
                            data={"metric_type": metric_type},
                        )
                        return

                    aggregated_metric.update(metric)
                    self.aggregated_metrics_storage[metric_type][
                        aggregation_key
                    ] = aggregated_metric

                except Exception:
                    internal_logger.warning(
                        "Failed to create aggregated metric",
                        data=metric.__dict__,
                        exc_info=True,
                    )

    def get_and_clear_metrics(self) -> Dict[str, List[FlowMetricEvent]]:
        aggregated_metrics = self._get_and_clear_metrics()
        return self._create_events_from_aggregated(aggregated_metrics)

    def _get_and_clear_metrics(self) -> Dict[str, Dict[str, AggregatedFlowMetric]]:
        with self.lock:
            current_metrics = self.aggregated_metrics_storage.get_wrapped()
            self.aggregated_metrics_storage.reset_wrapped()
        return current_metrics

    def _create_events_from_aggregated(
        self, aggregated_metrics: Dict[str, Dict[str, AggregatedFlowMetric]]
    ) -> Dict[str, List[FlowMetricEvent]]:
        timeslice = self._calculate_timeslice()
        events = defaultdict(list)  # type: Dict[str, List[FlowMetricEvent]]

        for metric_type, metrics in aggregated_metrics.items():
            for aggregated_metric in metrics.values():
                try:
                    event = aggregated_metric.to_event(timeslice)
                    events[metric_type].append(event)
                except ValueError:
                    internal_logger.warning(
                        "Failed to create event from aggregated metric",
                        data=aggregated_metric.__dict__,
                        exc_info=True,
                    )
                    pass

        return events

    def _calculate_timeslice(self) -> int:
        current_time = time.perf_counter()
        timeslice = int(current_time - self.last_dump)
        self.last_dump = current_time
        return timeslice


globals.metrics_aggregator = FlowMetricsAggregator()
