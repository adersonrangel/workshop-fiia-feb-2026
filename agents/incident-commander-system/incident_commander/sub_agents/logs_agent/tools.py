"""Tools for the Logs Agent."""

from datetime import datetime, timedelta


def search_logs(service_name: str, severity: str = "ERROR", minutes: int = 30) -> dict:
    """Search log entries for a specific service, optionally filtered by minimum
    severity level and time window.

    Args:
        service_name: Name of the service.
            Valid values: auth-service, api-gateway, payments-api
        severity: Minimum severity level to include. Default: "ERROR".
            Hierarchy: INFO < WARN < ERROR < CRITICAL.
            Example: severity="WARN" returns WARN + ERROR + CRITICAL entries.
        minutes: Look back this many minutes from current time. Default: 30.
            The mock data simulates current time as 15:05 on 2025-06-15.
    Returns:
        dict with service_name, severity_filter, time_window, total_entries,
        and entries (list of dicts with timestamp, severity, message).
    """
    severity_levels = {"INFO": 0, "WARN": 1, "ERROR": 2, "CRITICAL": 3}

    logs = {
        "auth-service": [
            {
                "timestamp": "2025-06-15T14:25:30",
                "severity": "INFO",
                "message": "Deploy v2.4.1 completed successfully. Restarting pods.",
            },
            {
                "timestamp": "2025-06-15T14:26:00",
                "severity": "INFO",
                "message": "Service started. DB connection pool initialized: 0/100.",
            },
            {
                "timestamp": "2025-06-15T14:30:00",
                "severity": "INFO",
                "message": "Health check OK. Active DB connections: 45/100. Latency: 12ms.",
            },
            {
                "timestamp": "2025-06-15T14:40:00",
                "severity": "INFO",
                "message": "Health check OK. Active DB connections: 62/100. Latency: 18ms.",
            },
            {
                "timestamp": "2025-06-15T14:45:00",
                "severity": "INFO",
                "message": "Health check OK. Active DB connections: 78/100. Latency: 45ms.",
            },
            {
                "timestamp": "2025-06-15T14:48:00",
                "severity": "WARN",
                "message": "DB connection pool utilization above 80%: 82/100. Consider scaling.",
            },
            {
                "timestamp": "2025-06-15T14:50:00",
                "severity": "WARN",
                "message": "Slow query detected: `SELECT * FROM sessions WHERE expired=false` — 2.3s. Active connections: 87/100.",
            },
            {
                "timestamp": "2025-06-15T14:52:00",
                "severity": "WARN",
                "message": "Connection pool critical: 92/100. New connections taking >1s to acquire.",
            },
            {
                "timestamp": "2025-06-15T14:54:00",
                "severity": "ERROR",
                "message": "Failed to acquire DB connection after 5s timeout. Pool: 98/100. Rejecting: POST /api/auth/login.",
            },
            {
                "timestamp": "2025-06-15T14:55:00",
                "severity": "ERROR",
                "message": "Pool at capacity: 100/100. Query causing leak: `SELECT * FROM sessions WHERE expired=false` (not closing connections).",
            },
            {
                "timestamp": "2025-06-15T14:56:00",
                "severity": "ERROR",
                "message": "47 requests queued. Avg wait time: 8.2s.",
            },
            {
                "timestamp": "2025-06-15T14:57:00",
                "severity": "ERROR",
                "message": "Request timeout: POST /api/auth/login — DB connection unavailable after 10s.",
            },
            {
                "timestamp": "2025-06-15T14:58:00",
                "severity": "CRITICAL",
                "message": "Health check FAILED. 100/100 connections in use, 0 idle. Service UNHEALTHY.",
            },
            {
                "timestamp": "2025-06-15T14:58:30",
                "severity": "CRITICAL",
                "message": "All 3 replicas unhealthy. Load balancer removing auth-service from rotation.",
            },
            {
                "timestamp": "2025-06-15T14:59:00",
                "severity": "CRITICAL",
                "message": "Circuit breaker OPEN. All requests rejected with 503.",
            },
            {
                "timestamp": "2025-06-15T15:00:00",
                "severity": "CRITICAL",
                "message": "PagerDuty alert: P1 — auth-service DOWN. On-call notified.",
            },
        ],
        "api-gateway": [
            {
                "timestamp": "2025-06-15T14:30:00",
                "severity": "INFO",
                "message": "All routes healthy. Error rate: 0.02%.",
            },
            {
                "timestamp": "2025-06-15T14:58:00",
                "severity": "WARN",
                "message": "Upstream auth-service returning 503. Error rate: 12%.",
            },
            {
                "timestamp": "2025-06-15T14:59:00",
                "severity": "ERROR",
                "message": "Error rate spike: 35%. Routes affected: /auth/*, /users/*.",
            },
            {
                "timestamp": "2025-06-15T15:00:00",
                "severity": "ERROR",
                "message": "Error rate: 42%. Circuit breaker active for auth routes. Payments unaffected.",
            },
        ],
        "payments-api": [
            {
                "timestamp": "2025-06-15T14:30:00",
                "severity": "INFO",
                "message": "Health check OK. Processing 45 transactions/sec.",
            },
            {
                "timestamp": "2025-06-15T15:00:00",
                "severity": "INFO",
                "message": "Health check OK. No impact from auth-service outage.",
            },
        ],
    }

    if service_name not in logs:
        return {
            "error": f"Service '{service_name}' not found",
            "available_services": list(logs.keys()),
        }

    current_time = datetime(2025, 6, 15, 15, 5, 0)
    cutoff_time = current_time - timedelta(minutes=minutes)
    min_severity = severity_levels.get(severity.upper(), 2)

    filtered = [
        entry
        for entry in logs[service_name]
        if severity_levels.get(entry["severity"], 0) >= min_severity
        and datetime.fromisoformat(entry["timestamp"]) >= cutoff_time
    ]

    return {
        "service_name": service_name,
        "severity_filter": severity,
        "time_window": f"Last {minutes} minutes (from {cutoff_time.isoformat()} to {current_time.isoformat()})",
        "total_entries": len(filtered),
        "entries": filtered,
    }
