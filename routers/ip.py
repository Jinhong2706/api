from fastapi import APIRouter, Request
import httpx

router = APIRouter(prefix="/ip", tags=["IP"])

@router.get("/")
async def get_client_ip(request: Request):
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"

    result = {"ip": client_ip}

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"http://ip-api.com/json/{client_ip}")
        data = resp.json()
        data.pop("query", None)
        data.pop("status", None)
        result.update(data)

    return result
