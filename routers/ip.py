from fastapi import APIRouter, Request
import httpx

router = APIRouter(prefix="/ip", tags=["IP"])


def _is_private_ip(ip: str) -> bool:
    if ip in ("unknown", "0.0.0.0", "127.0.0.1", "::1"):
        return True
    parts = ip.split(".")
    if len(parts) == 4:
        first = int(parts[0])
        second = int(parts[1]) if len(parts) > 1 else 0
        if first == 10:
            return True
        if first == 172 and 16 <= second <= 31:
            return True
        if first == 192 and second == 168:
            return True
    return False


@router.get("/")
async def get_client_ip(request: Request):
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"

    result = {"ip": client_ip}

    if client_ip != "unknown" and not _is_private_ip(client_ip):
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"http://ip-api.com/json/{client_ip}",
                params={"fields": "status,message,country,regionName,city,lat,lon"}
            )
            data = resp.json()
            if data.get("status") == "success":
                result["location"] = {
                    "country": data.get("country"),
                    "region": data.get("regionName"),
                    "city": data.get("city"),
                    "latitude": data.get("lat"),
                    "longitude": data.get("lon")
                }
    return result
