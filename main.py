"""FastAPI application entrypoint."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import router as recipes_router
from app.chat_api import router as chat_router
from app.config import get_settings
from app.dependencies import shutdown_resources


# build and config the app instance
def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.include_router(recipes_router)
    app.include_router(chat_router)

    frontend_dir = Path(__file__).parent / "frontend"
    if frontend_dir.exists():
        app.mount(
            "/app", StaticFiles(directory=frontend_dir, html=True), name="frontend"
        )

        @app.get("/", include_in_schema=False)
        def read_index() -> FileResponse:
            return FileResponse(frontend_dir / "index.html")

    @app.on_event("shutdown")
    def _shutdown() -> None:
        shutdown_resources()

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.debug)
