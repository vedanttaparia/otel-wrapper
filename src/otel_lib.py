import threading
import weakref
import logging

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

logger = logging.getLogger(__name__)

class MetricsRegistry:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        with self._lock:
            if self._initialized:
                return
            
            self.meter = None
            
            # Using WeakValueDictionary to avoid memory leaks. 
            # If the caller drops the reference to the instrument, it will be garbage collected.
            self.counters = weakref.WeakValueDictionary()
            self.up_down_counters = weakref.WeakValueDictionary()
            self.histograms = weakref.WeakValueDictionary()
            self.gauges = weakref.WeakValueDictionary()
            
            self._initialized = True

    def init_provider(self, service_name: str = "otel_wrapper", endpoint: str = None):
        with self._lock:
            if self.meter is not None:
                return # Already initialized
                
            try:
                resource = Resource.create({"service.name": service_name})
                
                # Configure the OTLP Exporter (gRPC)
                exporter_kwargs = {}
                if endpoint:
                    exporter_kwargs["endpoint"] = endpoint
                    
                exporter = OTLPMetricExporter(**exporter_kwargs)
                
                # Periodic exporter
                reader = PeriodicExportingMetricReader(exporter)
                
                provider = MeterProvider(resource=resource, metric_readers=[reader])
                metrics.set_meter_provider(provider)
                
                self.meter = metrics.get_meter(service_name)
                logger.info("OpenTelemetry MeterProvider initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize OpenTelemetry provider: {e}")
                # We do not raise, ensuring we don't crash main processes on network/config issues.

    def _get_meter(self):
        if self.meter is None:
            # Fallback initializing with defaults if none was provided
            self.init_provider()
        return self.meter

    def emit_counter(self, name: str, value: int | float, labels: dict = None, description: str = ""):
        try:
            if name not in self.counters:
                instrument = self._get_meter().create_counter(name=name, description=description)
                self.counters[name] = instrument
            
            self.counters[name].add(value, attributes=labels)
        except Exception as e:
            logger.error(f"Failed to emit counter metric '{name}': {e}")
            
    def emit_up_down_counter(self, name: str, value: int | float, labels: dict = None, description: str = ""):
        try:
            if name not in self.up_down_counters:
                instrument = self._get_meter().create_up_down_counter(name=name, description=description)
                self.up_down_counters[name] = instrument
                
            self.up_down_counters[name].add(value, attributes=labels)
        except Exception as e:
            logger.error(f"Failed to emit up_down_counter metric '{name}': {e}")

    def emit_histogram(self, name: str, value: int | float, labels: dict = None, description: str = ""):
        try:
            if name not in self.histograms:
                instrument = self._get_meter().create_histogram(name=name, description=description)
                self.histograms[name] = instrument
                
            self.histograms[name].record(value, attributes=labels)
        except Exception as e:
            logger.error(f"Failed to emit histogram metric '{name}': {e}")


    def emit_gauge(self, name: str, value: int | float, labels: dict = None, description: str = ""):
        try:
            if name not in self.gauges:
                instrument = self._get_meter().create_gauge(name=name, description=description)
                self.gauges[name] = instrument
                
            self.gauges[name].set(value, attributes=labels)
        except Exception as e:
            logger.error(f"Failed to emit gauge metric '{name}': {e}")
