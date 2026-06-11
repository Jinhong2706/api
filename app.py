import os
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.security import APIKeyQuery
from routers import ip, qrcode, bilibili, youdaolittlep
from routers.text2img import router as text2img_router

EXPECTED_TOKEN = os.environ.get("OPENAPI_TOKEN", "")
if not EXPECTED_TOKEN:
    raise RuntimeError("Environment variable OPENAPI_TOKEN is not set. Startup aborted.")

api_key_query = APIKeyQuery(name="token", auto_error=False)

async def verify_api_token(token: str = Depends(api_key_query)):
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if token != EXPECTED_TOKEN:
        raise HTTPException(status_code=403, detail=f"Authentication Fails, Your token: {token} is invalid")

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

@app.get("/openapi.json", include_in_schema=False)
async def openapi_json(valid: bool = Depends(verify_api_token)):
    return get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )

@app.get("/docs", include_in_schema=False)
async def swagger_ui(
    token: str = Depends(api_key_query),
    valid: bool = Depends(verify_api_token)
):
    return get_swagger_ui_html(
        openapi_url=f"/openapi.json?token={token}",
        title=app.title + " - Swagger UI"
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_ui(
    token: str = Depends(api_key_query),
    valid: bool = Depends(verify_api_token)
):
    return get_redoc_html(
        openapi_url=f"/openapi.json?token={token}",
        title=app.title + " - ReDoc"
    )

app.include_router(ip.router)
app.include_router(qrcode.router)
app.include_router(bilibili.router)
app.include_router(youdaolittlep.router)
app.include_router(text2img_router.router)

HELLO_TEXT = "Hello World\nPowered by Jinhong270\nRunning on Hugging Face\n"

@app.get("/", response_class=PlainTextResponse)
async def root():
    return HELLO_TEXT

@app.get("/status", response_class=PlainTextResponse)
async def status():
    return HELLO_TEXT

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
