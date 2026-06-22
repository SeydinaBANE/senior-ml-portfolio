from enum import StrEnum


class AuditEventType(StrEnum):
    AGENT_INVOKED = "agent_invoked"
    POLICY_DENIED = "policy_denied"
    GUARDRAIL_BLOCKED_INPUT = "guardrail_blocked_input"
    GUARDRAIL_BLOCKED_OUTPUT = "guardrail_blocked_output"
    AGENT_COMPLETED = "agent_completed"
    ATTACK_DETECTED = "attack_detected"
