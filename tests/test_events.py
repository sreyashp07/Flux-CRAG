from backend.events import NodeName, Status, build_event, emit


def test_build_event_has_expected_shape():
    event = build_event(NodeName.GRADE, Status.DECISION, "Relevance failed", {"relevant": 0})

    assert event["node"] == "grade_documents"
    assert event["status"] == "decision"
    assert event["message"] == "Relevance failed"
    assert event["data"] == {"relevant": 0}
    assert isinstance(event["timestamp"], float)


def test_build_event_defaults_to_empty_data():
    assert build_event(NodeName.RETRIEVE, Status.STARTED, "go")["data"] == {}


def test_emit_outside_graph_is_a_noop():
    emit(build_event(NodeName.GENERATE, Status.STARTED, "no graph running"))
