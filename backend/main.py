"""FastAPI entry point: serves the API and the dashboard from a single local process.

Run from the repo root:
    python -m backend.main
"""
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api.routes import router
from backend.config import BASE_DIR, get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0")
    app.include_router(router)

    # Mounted last so /api/* routes win; serves the built dashboard at "/".
    dist_dir = BASE_DIR / "frontend" / "dist"
    if dist_dir.exists():
        app.mount("/", StaticFiles(directory=dist_dir, html=True), name="frontend")
    else:

        @app.get("/", include_in_schema=False)
        def dashboard_not_built() -> dict:
            return {"detail": "Dashboard not built. Run: cd frontend && npm install && npm run build"}
    return app


app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(app, host=settings.host, port=settings.port)
