from prometheus_client import Counter, Gauge, Histogram

agent_runs_total = Counter(
    "agent_platform_runs_total",
    "Total number of agent runs",
    ["tenant_id", "agent_name", "status"],
)

agent_run_latency = Histogram(
    "agent_platform_run_latency_seconds",
    "Agent run latency in seconds",
    ["agent_name"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

active_agents_gauge = Gauge(
    "agent_platform_active_agents",
    "Number of active agent definitions per tenant",
    ["tenant_id"],
)

token_usage_total = Counter(
    "agent_platform_token_usage_total",
    "Total tokens consumed",
    ["tenant_id", "direction"],
)
