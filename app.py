import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.security import APIKeyQuery
from fastapi.staticfiles import StaticFiles
from routers import ip, qrcode, bilibili, youdaolittlep
from routers.text2img.router import router as text2img_router, periodic_cleanup
from routers.monitors import router as monitor_router, get_global_manager, shutdown_global_manager

EXPECTED_TOKEN = os.environ.get("FASTAPI_DOCS_TOKEN", "")
if not EXPECTED_TOKEN:
    raise RuntimeError("Environment variable FASTAPI_DOCS_TOKEN is not set. Startup aborted.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
api_key_query = APIKeyQuery(name="token", auto_error=False)

async def verify_api_token(token: str = Depends(api_key_query)):
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if token != EXPECTED_TOKEN:
        raise HTTPException(status_code=403, detail=f"Authentication Fails, Your token: {token} is invalid")

@asynccontextmanager
async def lifespan(app: FastAPI):
    get_global_manager()
    asyncio.create_task(periodic_cleanup())
    os.makedirs("data", exist_ok=True)
    os.makedirs("tmpl", exist_ok=True)
    yield
    shutdown_global_manager()

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
app.title = "Docs"

@app.get("/openapi.json", include_in_schema=False)
async def openapi_json(valid: bool = Depends(verify_api_token)):
    return get_openapi(title=app.title, version=app.version, openapi_version=app.openapi_version, description=app.description, routes=app.routes)

@app.get("/docs", include_in_schema=False)
async def swagger_ui(token: str = Depends(api_key_query), valid: bool = Depends(verify_api_token)):
    return get_swagger_ui_html(openapi_url=f"/openapi.json?token={token}", title="Docs")

@app.get("/redoc", include_in_schema=False)
async def redoc_ui(token: str = Depends(api_key_query), valid: bool = Depends(verify_api_token)):
    return get_redoc_html(openapi_url=f"/openapi.json?token={token}", title="Redoc")

app.include_router(ip.router)
app.include_router(qrcode.router)
app.include_router(bilibili.router)
app.include_router(youdaolittlep.router)
app.include_router(text2img_router)
app.include_router(monitor_router)

HELLO_TEXT = "Hello World\nPowered by Jinhong270\nRunning on Hugging Face\n"

@app.get("/", response_class=PlainTextResponse)
async def root():
    return HELLO_TEXT

@app.get("/status", response_class=PlainTextResponse)
async def status():
    return HELLO_TEXT

@app.get("/robots.txt", include_in_schema=False)
async def robots_txt():
    return FileResponse(os.path.join(BASE_DIR, "robots.txt"))

app.mount("/snake", StaticFiles(directory=os.path.join(BASE_DIR, "static/snake"), html=True), name="snake")
app.mount("/2048", StaticFiles(directory=os.path.join(BASE_DIR, "static/2048"), html=True), name="2048")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
