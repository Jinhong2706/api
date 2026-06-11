from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils import get_http_client
import httpx

router = APIRouter(prefix="/bilibili", tags=["Bilibili"])

BILIBILI_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/"
}

API_BASE = "https://api.bilibili.com"

class SearchRequest(BaseModel):
    keyword: str
    page: int = 1
    page_size: int = 20

async def _request(client: httpx.AsyncClient, url: str, params: dict = None, cookie: str = None) -> dict:
    headers = BILIBILI_HEADERS.copy()
    if cookie:
        headers["Cookie"] = cookie
    resp = await client.get(url, params=params, headers=headers)
    data = resp.json()
    if data.get("code") != 0:
        raise HTTPException(status_code=404, detail=data.get("message", "B站API返回错误"))
    return data["data"]

async def _get_video_info(client: httpx.AsyncClient, cookie: str = None, **params) -> dict:
    return await _request(client, f"{API_BASE}/x/web-interface/view", params=params, cookie=cookie)

async def _get_play_url(client: httpx.AsyncClient, params: dict, qn: int, fnval: int, cookie: str = None) -> dict:
    params.update({"qn": qn, "fnval": fnval})
    return await _request(client, f"{API_BASE}/x/player/playurl", params=params, cookie=cookie)

@router.get("/hot")
async def get_hot(ps: int = 50):
    ps = min(ps, 100)
    client = await get_http_client()
    return await _request(client, f"{API_BASE}/x/web-interface/popular", params={"ps": ps})

@router.get("/video/{bvid}")
async def get_video_by_bvid(bvid: str):
    client = await get_http_client()
    return await _get_video_info(client, bvid=bvid)

@router.post("/video")
async def post_video_by_bvid(bvid: str):
    client = await get_http_client()
    return await _get_video_info(client, bvid=bvid)

@router.get("/video/download/{bvid}")
async def get_video_download(bvid: str, cookie: str = None):
    client = await get_http_client()
    info = await _get_video_info(client, bvid=bvid, cookie=cookie)
    return await _get_play_url(client, {"bvid": bvid, "cid": info["cid"]}, qn=80, fnval=0, cookie=cookie)

@router.post("/video/download")
async def post_video_download(bvid: str, cookie: str = None):
    client = await get_http_client()
    info = await _get_video_info(client, bvid=bvid, cookie=cookie)
    return await _get_play_url(client, {"bvid": bvid, "cid": info["cid"]}, qn=80, fnval=0, cookie=cookie)

@router.get("/video/download/1080/{bvid}")
async def get_video_download_1080(bvid: str, cookie: str = None):
    client = await get_http_client()
    info = await _get_video_info(client, bvid=bvid, cookie=cookie)
    return await _get_play_url(client, {"bvid": bvid, "cid": info["cid"]}, qn=80, fnval=16, cookie=cookie)

@router.post("/video/download/1080")
async def post_video_download_1080(bvid: str, cookie: str = None):
    client = await get_http_client()
    info = await _get_video_info(client, bvid=bvid, cookie=cookie)
    return await _get_play_url(client, {"bvid": bvid, "cid": info["cid"]}, qn=80, fnval=16, cookie=cookie)

@router.get("/video/aid/{aid}")
async def get_video_by_aid(aid: int):
    client = await get_http_client()
    return await _get_video_info(client, aid=aid)

@router.post("/video/aid")
async def post_video_by_aid(aid: int):
    client = await get_http_client()
    return await _get_video_info(client, aid=aid)

@router.get("/video/download/aid/{aid}")
async def get_video_download_by_aid(aid: int, cookie: str = None):
    client = await get_http_client()
    info = await _get_video_info(client, aid=aid, cookie=cookie)
    return await _get_play_url(client, {"aid": aid, "cid": info["cid"]}, qn=80, fnval=0, cookie=cookie)

@router.post("/video/download/aid")
async def post_video_download_by_aid(aid: int, cookie: str = None):
    client = await get_http_client()
    info = await _get_video_info(client, aid=aid, cookie=cookie)
    return await _get_play_url(client, {"aid": aid, "cid": info["cid"]}, qn=80, fnval=0, cookie=cookie)

@router.get("/video/download/aid/1080/{aid}")
async def get_video_download_aid_1080(aid: int, cookie: str = None):
    client = await get_http_client()
    info = await _get_video_info(client, aid=aid, cookie=cookie)
    return await _get_play_url(client, {"aid": aid, "cid": info["cid"]}, qn=80, fnval=16, cookie=cookie)

@router.post("/video/download/aid/1080")
async def post_video_download_aid_1080(aid: int, cookie: str = None):
    client = await get_http_client()
    info = await _get_video_info(client, aid=aid, cookie=cookie)
    return await _get_play_url(client, {"aid": aid, "cid": info["cid"]}, qn=80, fnval=16, cookie=cookie)

@router.get("/search/{keyword}")
async def search_video(keyword: str, page: int = 1, page_size: int = 20):
    page_size = min(page_size, 50)
    client = await get_http_client()
    params = {
        "search_type": "video",
        "keyword": keyword,
        "page": page,
        "page_size": page_size
    }
    return await _request(client, f"{API_BASE}/x/web-interface/search/type", params=params)

@router.post("/search")
async def post_search_video(request: SearchRequest):
    page_size = min(request.page_size, 50)
    client = await get_http_client()
    params = {
        "search_type": "video",
        "keyword": request.keyword,
        "page": request.page,
        "page_size": page_size
    }
    return await _request(client, f"{API_BASE}/x/web-interface/search/type", params=params)
