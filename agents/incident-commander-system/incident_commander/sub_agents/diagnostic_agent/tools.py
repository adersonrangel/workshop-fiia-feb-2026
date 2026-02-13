"""Tools for the Diagnostic Agent."""


def check_service_status(service_name: str) -> dict:
    """Check the current health status of a service in the production platform.

    Args:
        service_name: Name of the service to check.
            Valid values: auth-service, api-gateway, payments-api
    Returns:
        dict with status, version, replicas, dependencies, error_message, etc.
        The 'dependencies' field lists external infrastructure components
        (postgres-primary, stripe-api) that are NOT queryable with tools.
        If the service does not exist, returns {"error": "...", "available_services": [...]}.
    """
    services = {
        "auth-service": {
            "service_name": "auth-service",
            "status": "DOWN",
            "last_healthy": "2025-06-15T14:58:00",
            "uptime_before_incident": "45 days",
            "host": "prod-auth-01.internal:8080",
            "version": "2.4.1",
            "replicas": "3/3 unhealthy",
            "dependencies": ["postgres-primary"],
            "last_deploy": "2025-06-15T14:25:00",
            "error_message": "Connection refused — all database connections exhausted",
        },
        "api-gateway": {
            "service_name": "api-gateway",
            "status": "DEGRADED",
            "last_healthy": "2025-06-15T14:59:30",
            "uptime_before_incident": "90 days",
            "host": "prod-gateway-01.internal:443",
            "version": "5.2.1",
            "replicas": "3/3 healthy (routing errors)",
            "dependencies": ["auth-service", "payments-api"],
            "last_deploy": "2025-04-15T08:00:00",
            "error_message": "Elevated 5xx error rate — upstream auth-service returning 503",
        },
        "payments-api": {
            "service_name": "payments-api",
            "status": "HEALTHY",
            "last_healthy": "2025-06-15T15:05:00",
            "uptime_before_incident": "12 days",
            "host": "prod-payments-01.internal:8081",
            "version": "3.1.0",
            "replicas": "2/2 healthy",
            "dependencies": ["postgres-primary", "stripe-api"],
            "last_deploy": "2025-06-12T09:15:00",
            "error_message": None,
        },
    }

    if service_name not in services:
        return {
            "error": f"Service '{service_name}' not found",
            "available_services": list(services.keys()),
        }

    return services[service_name]


def check_metrics(service_name: str) -> dict:
    """Retrieve current infrastructure metrics for a service including CPU,
    memory, database connections, request rates, latency, and error rates.

    Args:
        service_name: Name of the service.
            Valid values: auth-service, api-gateway, payments-api
    Returns:
        dict with cpu_percent, memory_percent, error_rate_percent, latency, etc.
        If the service does not exist, returns {"error": "...", "available_services": [...]}.
    """
    metrics = {
        "auth-service": {
            "service_name": "auth-service",
            "cpu_percent": 92.4,
            "memory_percent": 78.1,
            "active_db_connections": 100,
            "max_db_connections": 100,
            "idle_db_connections": 0,
            "waiting_for_connection": 47,
            "requests_per_second": 0,
            "failed_requests_per_second": 250,
            "error_rate_percent": 100.0,
            "avg_latency_ms": "timeout",
            "p99_latency_ms": "timeout",
            "active_threads": 200,
            "max_threads": 200,
        },
        "api-gateway": {
            "service_name": "api-gateway",
            "cpu_percent": 58.3,
            "memory_percent": 45.2,
            "requests_per_second": 800,
            "failed_requests_per_second": 336,
            "error_rate_percent": 42.0,
            "avg_latency_ms": 950,
            "p99_latency_ms": 10000,
        },
        "payments-api": {
            "service_name": "payments-api",
            "cpu_percent": 34.2,
            "memory_percent": 52.0,
            "active_db_connections": 25,
            "max_db_connections": 50,
            "requests_per_second": 45,
            "failed_requests_per_second": 0,
            "error_rate_percent": 0.1,
            "avg_latency_ms": 85,
            "p99_latency_ms": 210,
        },
    }

    if service_name not in metrics:
        return {
            "error": f"Service '{service_name}' not found",
            "available_services": list(metrics.keys()),
        }

    return metrics[service_name]
