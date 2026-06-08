import os
import socket
import ipaddress
from urllib.parse import urlparse, urlunparse
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import asyncio

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

def _is_unsafe_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return True
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ipv4_part = ip.ipv4_mapped
        if ipv4_part.is_loopback or ipv4_part.is_private:
            return True
    if ip.is_loopback or ip.is_private or ip.is_multicast or ip.is_link_local:
        return True
    return False

async def _check_url_safety_and_get_ip(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    if not host:
        raise HTTPException(status_code=400, detail="Invalid URL")
    try:
        loop = asyncio.get_running_loop()
        addrs = await loop.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except Exception:
        raise HTTPException(status_code=400, detail="Cannot resolve host")
    for addr in addrs:
        ip = addr[4][0]
        if not _is_unsafe_ip(ip):
            return ip
    raise HTTPException(status_code=403, detail="Access to internal/local addresses is forbidden")

def _replace_host_with_ip(url: str, ip: str) -> str:
    parsed = urlparse(url)
    original_host = parsed.hostname
    if not original_host:
        return url
    port = parsed.port
    netloc = ip
    if ':' in ip and not ip.startswith('['):
        netloc = f'[{ip}]'
    if port:
        netloc = f'{netloc}:{port}'
    new_parts = (parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment)
    return urlunparse(new_parts)

def _get_original_host_header(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.hostname
    if not host:
        return ''
    port = parsed.port
    if port and ((parsed.scheme == 'http' and port != 80) or (parsed.scheme == 'https' and port != 443)):
        return f'{host}:{port}'
    return host

async def _safe_request(client: httpx.AsyncClient, method: str, url: str, headers: dict, body: bytes, max_redirects: int = 20):
    current_url = url
    current_method = method
    current_headers = headers.copy()
    current_body = body
    redirect_count = 0

    while redirect_count <= max_redirects:
        safe_ip = await _check_url_safety_and_get_ip(current_url)
        new_url = _replace_host_with_ip(current_url, safe_ip)

        new_headers = current_headers.copy()
        new_headers['host'] = _get_original_host_header(current_url)

        resp = await client.request(
            method=current_method,
            url=new_url,
            headers=new_headers,
            content=current_body,
            follow_redirects=False
        )

        if 300 <= resp.status_code < 400 and 'location' in resp.headers:
            location = resp.headers['location']
            new_url = httpx.URL(current_url).join(location).__str__()
            await _check_url_safety_and_get_ip(new_url)

            if resp.status_code in (307, 308):
                current_method = current_method
                current_body = body
            else:
                current_method = 'GET'
                current_body = None

            current_url = new_url
            current_headers.pop('host', None)
            redirect_count += 1
            continue

        return resp

    raise HTTPException(status_code=500, detail="Too many redirects")

def _extract_raw_url_from_request(request: Request, token: str) -> str:
    full_path = request.url.path
    prefix = f"/web/browse/{token}/"
    if not full_path.startswith(prefix):
        raise HTTPException(status_code=400, detail="Invalid path")
    raw_url_part = full_path[len(prefix):]
    query_string = request.url.query
    if query_string:
        return f"{raw_url_part}?{query_string}"
    return raw_url_part

async def _browse(token: str, req: Request):
    if token != WEB_BROWSE_TOKEN:
        raise HTTPException(status_code=401, detail="Authentication failed")

    target_url = _extract_raw_url_from_request(req, token)
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url

    headers = {
        key: value for key, value in req.headers.items()
        if not _should_remove_header(key) and key.lower() not in ("host", "content-length", "transfer-encoding")
    }

    body = await req.body()

    async with httpx.AsyncClient(timeout=120.0, verify=False) as client:
        resp = await _safe_request(client, req.method, target_url, headers, body)

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

@router.api_route("/browse/{token}/{url:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def browse_all(token: str, url: str, req: Request):
    return await _browse(token, req)
