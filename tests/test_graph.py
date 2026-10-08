from backend.events import NodeName
from backend.graph import build_graph, get_topology


def _compiled_edges():
    return {(edge.source, edge.target) for edge in build_graph().get_graph().edges}


def test_topology_declares_every_node_and_edges_reference_them():
    topology = get_topology()
    ids = {node["id"] for node in topology["nodes"]}

    assert ids == {name.value for name in NodeName}
    for edge in topology["edges"]:
        assert edge["source"] in ids
        assert edge["target"] in ids


def test_compiled_graph_contains_every_topology_edge():
    declared = {(e["source"], e["target"]) for e in get_topology()["edges"]}

    assert declared <= _compiled_edges()


def test_compiled_graph_has_entry_and_exit():
    edges = _compiled_edges()

    assert ("__start__", "retrieve") in edges
    assert ("generate", "__end__") in edges
