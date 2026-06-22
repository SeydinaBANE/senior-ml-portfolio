from prometheus_client import Counter, Histogram

agent_latency_seconds = Histogram(
    "agent_latency_seconds",
    "Agent execution latency",
    labelnames=["agent_id", "tenant_id"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
)

llm_cost_tokens_total = Counter(
    "llm_cost_tokens_total",
    "Total LLM tokens consumed",
    labelnames=["agent_id", "tenant_id"],
)

guardrail_violations_total = Counter(
    "guardrail_violations_total",
    "Total guardrail violations detected",
    labelnames=["tenant_id", "direction"],
)

policy_denials_total = Counter(
    "policy_denials_total",
    "Total OPA policy denials",
    labelnames=["tenant_id", "agent_id"],
)
