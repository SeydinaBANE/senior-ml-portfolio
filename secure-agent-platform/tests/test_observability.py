from app.observability import METRICS, record_span


def test_record_span_collects_duration_and_attributes() -> None:
    METRICS.reset()
    with record_span("op.test", key="val"):
        pass
    assert len(METRICS.spans) == 1
    span = METRICS.spans[0]
    assert span.name == "op.test"
    assert span.attributes == {"key": "val"}
    assert span.duration_ms >= 0.0


def test_metrics_incr_and_reset() -> None:
    METRICS.reset()
    METRICS.incr("counter.a")
    METRICS.incr("counter.a")
    METRICS.incr("counter.b", 3)
    assert METRICS.counters["counter.a"] == 2
    assert METRICS.counters["counter.b"] == 3
    METRICS.reset()
    assert dict(METRICS.counters) == {}
    assert METRICS.spans == []
