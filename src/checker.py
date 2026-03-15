import re

# OpenTelemetry metric name constraints
# https://opentelemetry.io/docs/specs/otel/metrics/api/#instrument-name-syntax
# "They MUST map to the regular expression ^[a-zA-Z][-a-zA-Z0-9_.]*$"
NAME_REGEX = re.compile(r"^[a-zA-Z][-a-zA-Z0-9_.]*$")

def validate_metric_name(name: str) -> bool:
    """
    Validates if the metric name conforms to OpenTelemetry specifications.
    MUST have a length less than or equal to 255.
    """
    if not isinstance(name, str):
        return False
    if not name or len(name) > 255:
        return False
    return bool(NAME_REGEX.match(name))

def validate_labels(labels: dict) -> bool:
    """
    Validates if the labels dictionary is valid.
    Keys must be strings.
    Values must be strings, booleans, ints, or floats.
    """
    if not isinstance(labels, dict):
        return False
    
    for key, value in labels.items():
        if not isinstance(key, str):
            return False
        # OTel Spec: The value of an Attribute MUST be one of the following types:
        # String, Boolean, Double, Int, Array of String, Array of Boolean, Array of Double, Array of Int
        # We will restrict to primitives for simplicity.
        if not isinstance(value, (str, bool, int, float)):
            return False
            
    return True
