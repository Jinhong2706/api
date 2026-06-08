import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import Response
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.security import APIKeyQuery
from fastapi.middleware.cors import CORSMiddleware
from starlette.status import HTTP_403_FORBIDDEN

from routers.bilibili import router as bilibili_router
from routers.qrcode import router as qrcode_router
from routers.ip import router as ip_router
from routers.web import router as web_router
from routers.youdaolittlep import router as youdaolittlep_router
from utils import close_http_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_http_client()


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)

EXPECTED_TOKEN = os.getenv("OPENAPI_TOKEN")
if not EXPECTED_TOKEN:
    raise RuntimeError("OPENAPI_TOKEN environment variable not set")

api_key_query = APIKeyQuery(name="token", auto_error=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def verify_token(token: str = Depends(api_key_query)):
    if token != EXPECTED_TOKEN:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid or missing token")
    return True


@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_json(valid: bool = Depends(verify_token)):
    return get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )


@app.get("/docs", include_in_schema=False)
async def get_documentation(
    token: str = Depends(api_key_query),
    valid: bool = Depends(verify_token)
):
    return get_swagger_ui_html(
        openapi_url=f"/openapi.json?token={token}",
        title=app.title + " - Swagger UI"
    )


@app.get("/redoc", include_in_schema=False)
async def get_redoc_documentation(
    token: str = Depends(api_key_query),
    valid: bool = Depends(verify_token)
):
    return get_redoc_html(
        openapi_url=f"/openapi.json?token={token}",
        title=app.title + " - ReDoc"
    )


app.include_router(bilibili_router)
app.include_router(qrcode_router)
app.include_router(ip_router)
app.include_router(web_router)
app.include_router(youdaolittlep_router)


@app.get("/")
async def root():
    return Response(
        content="Hello World\nPowered by Jinhong270\nRunning on YoudaoDictionaryPen",
        media_type="text/plain"
    )


@app.get("/status")
async def get_status():
    return Response(
        content="Hello World\nPowered by Jinhong270\nRunning on YoudaoDictionaryPen",
        media_type="text/plain"
    )





if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
