package platform.data_classification

import future.keywords.if
import future.keywords.in

default allow := false
default reason := "data classification denied"

sensitive_labels := {"PII", "CONFIDENTIAL", "SECRET"}

allow if {
    count({label | label := input.data_labels[_]; label in sensitive_labels}) == 0
}

allow if {
    data.agents[input.agent_id].clearance == "high"
}

reason := "agent lacks clearance for sensitive data" if {
    some label in input.data_labels
    label in sensitive_labels
    data.agents[input.agent_id].clearance != "high"
}
