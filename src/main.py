import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from config import ENVIRONMENT, SHOW_DOCS_ENVIRONMENT
import core.service as core_service
from core.middlewares import ExceptionHandlingMiddleware
from auth import router as auth_router
from core.constants import MEDIA_ROOT
from guides import router as guides_router
from users import router as users_router

app_configs = {'title': 'Guidio'}

if ENVIRONMENT not in SHOW_DOCS_ENVIRONMENT:
    app_configs['openapi_url'] = None


def is_debug() -> bool:
    return False if ENVIRONMENT != 'dev' else True


app = FastAPI(**app_configs)
app.add_middleware(ExceptionHandlingMiddleware)
core_service.create_media_root()
app.mount("/media", StaticFiles(directory=MEDIA_ROOT), name="media")
app.include_router(auth_router.router,
                   prefix="/auth",
                   tags=["auth"])
app.include_router(users_router.router,
                   prefix="/users",
                   tags=["users"])
app.include_router(guides_router.router,
                   prefix="/guides",
                   tags=["guides"])


def main():
    if is_debug():
        uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
