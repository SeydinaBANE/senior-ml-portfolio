import httpx
import streamlit as st

API_BASE = "http://app:8000/api/v1"

st.set_page_config(page_title="Agent Platform", page_icon="🤖", layout="wide")

PAGES = ["🏪 Marketplace", "🔧 Builder", "🚀 Run Agent", "💰 Billing", "🔑 Auth"]


def _headers() -> dict[str, str]:
    token = st.session_state.get("token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _api(method: str, path: str, **kwargs: object) -> httpx.Response:
    with httpx.Client(base_url=API_BASE, timeout=30.0) as client:
        return getattr(client, method)(path, **kwargs)


page = st.sidebar.selectbox("Navigation", PAGES)

if page == "🔑 Auth":
    st.title("Authentication")
    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            r = _api("post", "/auth/login", json={"email": email, "password": password})
            if r.status_code == 200:
                st.session_state["token"] = r.json()["access_token"]
                st.success("Logged in!")
            else:
                st.error(r.json().get("detail", "Login failed"))

elif page == "🏪 Marketplace":
    st.title("Agent Marketplace")
    r = _api("get", "/agents", headers=_headers())
    if r.status_code == 200:
        agents = r.json()
        if not agents:
            st.info("No agents available yet. Create one in the Builder.")
        for agent in agents:
            with st.expander(f"🤖 **{agent['name']}** — `{agent['category']}`"):
                st.write(agent["description"])
                st.caption(f"Model: {agent['model']} | Public: {agent['is_public']}")
                if agent.get("tags"):
                    st.write(" ".join(f"`{t}`" for t in agent["tags"]))
    else:
        st.error("Login required")

elif page == "🔧 Builder":
    st.title("Agent Builder (Low-Code)")
    with st.form("builder"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Agent name *")
            categories = ["support", "analytics", "coding", "research", "hr", "other"]
            category = st.selectbox("Category", categories)
            model = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"])
        with col2:
            description = st.text_area("Description *", height=80)
            tags = st.text_input("Tags (comma-separated)")
            is_public = st.checkbox("Publish to marketplace")

        system_prompt = st.text_area(
            "System prompt *", height=150, placeholder="You are an expert in..."
        )
        tools = st.multiselect(
            "Tools", ["web_search", "database_query", "calculator", "calendar"]
        )

        if st.form_submit_button("Create Agent", type="primary"):
            payload = {
                "name": name,
                "description": description,
                "category": category,
                "system_prompt": system_prompt,
                "model": model,
                "tags": [t.strip() for t in tags.split(",") if t.strip()],
                "tools": tools,
                "is_public": is_public,
            }
            r = _api("post", "/agents", json=payload, headers=_headers())
            if r.status_code == 201:
                st.success(f"Agent **{name}** created! ID: `{r.json()['id']}`")
            else:
                st.error(r.json().get("detail", "Creation failed"))

elif page == "🚀 Run Agent":
    st.title("Run — Smart Routing")
    message = st.text_area(
        "Your message", height=120,
        placeholder="The router will pick the best agent automatically…",
    )
    if st.button("Send", type="primary"):
        with st.spinner("Routing and generating…"):
            r = _api("post", "/run", json={"message": message}, headers=_headers())
        if r.status_code == 200:
            data = r.json()
            st.success(f"Routed to: **{data['agent_name']}**")
            tokens = f"{data['input_tokens']}↑ {data['output_tokens']}↓"
            st.caption(
                f"Reason: {data['routed_by']} | Latency: {data['latency_ms']}ms | Tokens: {tokens}"
            )
            st.markdown("### Response")
            st.markdown(data["output"])
        else:
            st.error(r.json().get("detail", "Routing failed"))

elif page == "💰 Billing":
    st.title("Usage & Billing")
    col1, col2 = st.columns(2)
    with col1:
        period_start = st.date_input("From")
    with col2:
        period_end = st.date_input("To")

    if st.button("Generate Report"):
        r = _api(
            "post",
            "/billing/report",
            json={
                "period_start": str(period_start) + "T00:00:00",
                "period_end": str(period_end) + "T23:59:59",
            },
            headers=_headers(),
        )
        if r.status_code == 200:
            d = r.json()
            cols = st.columns(4)
            cols[0].metric("Total Requests", d["total_requests"])
            cols[1].metric("Input Tokens", f"{d['total_input_tokens']:,}")
            cols[2].metric("Output Tokens", f"{d['total_output_tokens']:,}")
            cols[3].metric("Total Cost", f"${d['total_cost_usd']:.4f}")
            st.caption(f"Avg latency: {d['avg_latency_ms']:.0f}ms")
        else:
            st.error(r.json().get("detail", "Report failed"))
