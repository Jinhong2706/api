import os
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from routers import ip, qrcode, bilibili, youdaolittlep
from routers.text2img import router as text2img_router

OPENAPI_TOKEN = os.environ.get("OPENAPI_TOKEN", "")


class TokenAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ("/openapi.json", "/docs", "/redoc"):
            token = request.query_params.get("token")
            if not OPENAPI_TOKEN or token != OPENAPI_TOKEN:
                return Response(content="Unauthorized", status_code=401, media_type="text/plain")
        response = await call_next(request)
        return response


app = FastAPI(
    openapi_url=f"/openapi.json?token={OPENAPI_TOKEN}" if OPENAPI_TOKEN else "/openapi.json"
)
app.add_middleware(TokenAuthMiddleware)

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
