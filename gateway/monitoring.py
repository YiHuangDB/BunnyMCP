from prometheus_client import Counter, Histogram

API_REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds", "Latency of API requests", ["endpoint"]
)
API_REQUEST_COUNT = Counter(
    "api_request_count", "Total number of API requests", ["endpoint", "method", "status"]
)
VAULT_ACCESS_COUNT = Counter(
    "vault_access_count", "Total number of vault accesses", ["path", "status"]
)
SYSTEM_RESOURCE_USAGE = Histogram(
    "system_resource_usage", "System resource usage", ["resource"]
)
