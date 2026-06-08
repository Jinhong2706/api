import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
import httpx

router = APIRouter(prefix="/web", tags=["Browser"])

WEB_BROWSE_TOKEN = os.getenv("WEB_BROWSE_TOKEN")
if not WEB_BROWSE_TOKEN:
    raise RuntimeError("WEB_BROWSE_TOKEN environment variable not set")

HOP_BY_HOP_HEADERS = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade", "content-length"
}


def _should_remove_header(header_name: str) -> bool:
    return header_name.lower() in HOP_BY_HOP_HEADERS


@router.api_route("/browse/{token}/{url:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def browse_all(token: str, url: str, req: Request):
    if token != WEB_BROWSE_TOKEN:
        raise HTTPException(status_code=401, detail="Authentication Fails")

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    query_string = req.url.query
    if query_string:
        url = f"{url}?{query_string}" if '?' not in url else f"{url}&{query_string}"

    headers = {key: value for key, value in req.headers.items() if key.lower() != "host"}

    if "baidu.com" in url.lower():
        headers["Host"] = "www.baidu.com"

    body = await req.body()

    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
        resp = await client.request(
            method=req.method,
            url=url,
            headers=headers,
            content=body,
            follow_redirects=True
        )

        response_headers = {
            key: value for key, value in resp.headers.items()
            if not _should_remove_header(key)
        }

        return StreamingResponse(
            resp.aiter_bytes(),
            status_code=resp.status_code,
            headers=response_headers,
            media_type="text/plain"
        )
