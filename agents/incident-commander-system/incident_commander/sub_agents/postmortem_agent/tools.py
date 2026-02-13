"""Tools for the Postmortem Agent."""


def get_runbook(issue_type: str) -> dict:
    """Look up the standard operating procedure (runbook) for a known incident type.
    Returns immediate actions, investigation steps, and prevention measures.

    Args:
        issue_type: Type of incident.
            Valid values: "database_connection_pool_exhaustion", "service_cascade_failure"
    Returns:
        dict with title, severity, symptoms, immediate_actions,
        root_cause_investigation, prevention.
        If the type does not exist, returns {"error": "...", "available_runbooks": [...]}.
    """
    runbooks = {
        "database_connection_pool_exhaustion": {
            "title": "Database Connection Pool Exhaustion",
            "severity": "P1 — Critical",
            "symptoms": [
                "Service returning 503 errors",
                "Health check failures",
                "DB connection count at maximum",
                "Request timeouts increasing",
            ],
            "immediate_actions": [
                "1. Verify pool status: check active vs max connections",
                "2. Identify leaked queries via pg_stat_activity",
                "3. TEMP FIX: Increase pool size — env var AUTH_DB_POOL_MAX (100 → 200)",
                "4. Restart pods: kubectl rollout restart deployment/auth-service -n production",
                "5. Monitor recovery: watch connections and error rate for 5 min",
            ],
            "root_cause_investigation": [
                "1. Check recent deploys — compare connection patterns before/after",
                "2. Review new queries in latest version for missing close()",
                "3. Verify ORM session lifecycle (SQLAlchemy scoping)",
                "4. Check connection timeout settings",
            ],
            "prevention": [
                "Alerts at 70% pool utilization",
                "PgBouncer for infra-level connection pooling",
                "Connection leak detection in CI/CD",
                "Code review checklist: verify DB sessions closed",
            ],
        },
        "service_cascade_failure": {
            "title": "Service Cascade Failure",
            "severity": "P1 — Critical",
            "immediate_actions": [
                "1. Identify the root failing service",
                "2. Check circuit breaker status across affected services",
                "3. Verify fallback/cache mechanisms are active",
                "4. Consider isolating the failing service",
            ],
            "prevention": [
                "Circuit breakers on all service-to-service calls",
                "Graceful degradation for critical dependencies",
                "Warm caches for frequently accessed data",
                "Regular chaos engineering exercises",
            ],
        },
    }

    if issue_type not in runbooks:
        return {
            "error": f"Runbook '{issue_type}' not found",
            "available_runbooks": list(runbooks.keys()),
        }

    return runbooks[issue_type]
