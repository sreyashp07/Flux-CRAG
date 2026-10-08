from fastapi.testclient import TestClient

from backend import main as main_module


def test_root_explains_how_to_build_when_dashboard_is_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(main_module, "BASE_DIR", tmp_path)

    body = TestClient(main_module.create_app()).get("/").json()

    assert "npm run build" in body["detail"]


def test_root_serves_built_dashboard_and_keeps_api_routes(monkeypatch, tmp_path):
    dist = tmp_path / "frontend" / "dist"
    dist.mkdir(parents=True)
    (dist / "index.html").write_text("<html><title>Flux</title></html>", encoding="utf-8")
    monkeypatch.setattr(main_module, "BASE_DIR", tmp_path)

    client = TestClient(main_module.create_app())
    response = client.get("/")

    assert response.status_code == 200
    assert "Flux" in response.text
    assert client.get("/api/graph").status_code == 200
