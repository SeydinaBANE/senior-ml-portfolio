package platform.agent_access

import future.keywords.if
import future.keywords.in

default allow := false
default reason := "access denied"

allow if {
    input.action == "invoke"
    input.agent_id in data.tenants[input.tenant_id].allowed_agents
}

reason := "agent not allowed for this tenant" if {
    not input.agent_id in data.tenants[input.tenant_id].allowed_agents
}
