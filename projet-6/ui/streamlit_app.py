import httpx
import streamlit as st

API_BASE = "http://app:8000/api/v1"

st.set_page_config(page_title="Research Agent", page_icon="🔬", layout="wide")
st.title("Autonomous Research Agent")
st.caption("Searches the web, verifies sources, writes structured reports — then distributes via Slack & Notion.")

with st.sidebar:
    st.header("Tool Status")
    r = httpx.get(f"{API_BASE}/tools/status", timeout=5.0)
    if r.status_code == 200:
        for tool in r.json():
            icon = "✅" if tool["configured"] else "❌"
            st.write(f"{icon} {tool['name']}")

    st.divider()
    st.header("Distribution")
    post_slack = st.checkbox("Post to Slack")
    save_notion = st.checkbox("Save to Notion")
    notion_page_id = ""
    if save_notion:
        notion_page_id = st.text_input("Notion parent page ID")

col_input, col_output = st.columns([1, 2])

with col_input:
    topic = st.text_area("Research topic", height=120, placeholder="e.g. Impact of AI agents on software engineering productivity in 2025")
    submitted = st.button("Research", type="primary", use_container_width=True)

if submitted and topic:
    with st.spinner("Planning queries… searching… verifying… writing…"):
        try:
            response = httpx.post(
                f"{API_BASE}/research",
                json={
                    "topic": topic,
                    "post_to_slack": post_slack,
                    "save_to_notion": save_notion,
                    "notion_parent_page_id": notion_page_id,
                },
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            st.error(f"Error: {e.response.json().get('detail', str(e))}")
            st.stop()

    with col_output:
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Sources found", data["total_sources_found"])
        col_b.metric("Sources verified", data["total_sources_verified"])
        col_c.metric("Queries used", data["search_queries_used"])

        st.markdown("---")
        st.markdown(data["report"])

        with st.expander(f"Verified sources ({len(data['verified_sources'])})"):
            for s in data["verified_sources"]:
                st.markdown(f"**[{s['title']}]({s['url']})** — confidence: `{s['confidence']:.2f}`")
                if s["excerpt"]:
                    st.caption(f"> {s['excerpt']}")
