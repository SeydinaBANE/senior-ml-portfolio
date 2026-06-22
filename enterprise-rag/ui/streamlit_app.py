import asyncio

import plotly.graph_objects as go
import streamlit as st

from app.rag.pipeline import run_rag
from app.evaluation.ragas_eval import EvalSample, run_ragas

st.set_page_config(page_title="Enterprise RAG", page_icon="🔍", layout="wide")
st.title("Enterprise RAG — Self-Correcting Knowledge Assistant")

with st.sidebar:
    st.header("Ingest Documents")
    uploaded = st.file_uploader("Upload PDF", type=["pdf"])
    url_input = st.text_input("Or ingest a URL")
    if st.button("Ingest"):
        st.info("Trigger ingestion via API: POST /api/v1/ingest/pdf or /ingest/web")

    st.divider()
    st.header("Evaluation")
    ground_truth = st.text_area("Ground truth (optional)", height=80)
    run_eval = st.checkbox("Run Ragas evaluation")

col_query, col_result = st.columns([1, 2])

with col_query:
    question = st.text_area("Your question", height=120, placeholder="Ask anything about your documents…")
    submitted = st.button("Ask", type="primary", use_container_width=True)

if submitted and question:
    with st.spinner("Retrieving and generating…"):
        answer, chunks, iterations = asyncio.run(run_rag(question))

    with col_result:
        st.subheader("Answer")
        st.markdown(answer)

        st.caption(f"Retrieval iterations: **{iterations}**")

        with st.expander(f"Context chunks ({len(chunks)})"):
            for i, chunk in enumerate(chunks, 1):
                st.markdown(f"**[{i}] {chunk.source}** (score: {chunk.score:.3f})")
                st.text(chunk.content[:300] + "…" if len(chunk.content) > 300 else chunk.content)

        if run_eval and chunks:
            with st.spinner("Running Ragas evaluation…"):
                sample = EvalSample(
                    question=question,
                    answer=answer,
                    contexts=[c.content for c in chunks],
                    ground_truth=ground_truth,
                )
                scores = run_ragas([sample])

            if scores:
                s = scores[0]
                st.subheader("Evaluation Scores")
                fig = go.Figure(go.Bar(
                    x=["Faithfulness", "Answer Relevancy", "Context Precision"],
                    y=[s.faithfulness, s.answer_relevancy, s.context_precision],
                    marker_color=["#2ecc71", "#3498db", "#9b59b6"],
                ))
                fig.update_layout(yaxis_range=[0, 1], height=300)
                st.plotly_chart(fig, use_container_width=True)
