import argparse
import sys
import logging
from otel_lib import MetricsRegistry
from checker import validate_metric_name, validate_labels

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def parse_labels(labels_list):
    """
    Parses a list of "key=value" strings into a dictionary.
    """
    # Action=append results in None if not provided
    if not labels_list:
        return {}

    parsed_labels = {}
    for item in labels_list:
        try:
            key, value = item.split("=", 1)
            # Basic type inference
            if value.lower() in ("true", "false"):
                value_parsed = value.lower() == "true"
            else:
                try:
                    value_parsed = int(value)
                except ValueError:
                    try:
                        value_parsed = float(value)
                    except ValueError:
                        value_parsed = value
                        
            parsed_labels[key] = value_parsed
        except ValueError:
            logger.warning(f"Invalid label format '{item}'. Expected 'key=value'. Ignoring.")
            
    return parsed_labels

def main():
    parser = argparse.ArgumentParser(description="Developer Telemetry Wrapper CLI")
    
    subparsers = parser.add_subparsers(dest="command", help="Metric type to emit")
    
    # Common arguments for all metrics
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--name", required=True, help="Name of the metric")
    parent_parser.add_argument("--value", type=float, required=True, help="Value to emit")
    parent_parser.add_argument("--label", action="append", help="Label in key=value format (can be specified multiple times)")
    parent_parser.add_argument("--desc", default="", help="Description of the metric")
    parent_parser.add_argument("--endpoint", default=None, help="OTLP gRPC endpoint (e.g., http://localhost:4317)")
    parent_parser.add_argument("--service", default="otel_cli_wrapper", help="Service name for resource")

    subparsers.add_parser("emit_counter", parents=[parent_parser], help="Emit a Counter metric")
    subparsers.add_parser("emit_up_down_counter", parents=[parent_parser], help="Emit an UpDownCounter metric")
    subparsers.add_parser("emit_histogram", parents=[parent_parser], help="Emit a Histogram metric")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    labels = parse_labels(args.label)
    
    # Validation phase
    if not validate_metric_name(args.name):
        logger.error(f"Invalid metric name: {args.name}")
        sys.exit(1)
        
    if not validate_labels(labels):
        logger.error(f"Invalid labels provided: {labels}")
        sys.exit(1)

    # Initialize registry and provider
    registry = MetricsRegistry()
    registry.init_provider(service_name=args.service, endpoint=args.endpoint)
    registry._initialized = True # Singleton state trigger

    logger.info(f"Emitting {args.command} '{args.name}' with value {args.value} and labels: {labels}")

    # Emit the metric based on command
    if args.command == "emit_counter":
        registry.emit_counter(args.name, args.value, labels=labels, description=args.desc)
    elif args.command == "emit_up_down_counter":
        registry.emit_up_down_counter(args.name, args.value, labels=labels, description=args.desc)
    elif args.command == "emit_histogram":
        registry.emit_histogram(args.name, args.value, labels=labels, description=args.desc)
        
    logger.info("Metric emitted successfully.")

if __name__ == "__main__":
    main()
