from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx

router = APIRouter(prefix="/bilibili", tags=["Bilibili"])

BILIBILI_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/"
}

API_BASE = "https://api.bilibili.com"

class BvRequest(BaseModel):
    bvid: str

class SearchRequest(BaseModel):
    keyword: str
    page: int = 1
    page_size: int = 20

class AvidRequest(BaseModel):
    avid: int

async def _get_info(client: httpx.AsyncClient, **params) -> dict:
    resp = await client.get(f"{API_BASE}/x/web-interface/view", params=params)
    data = resp.json()
    if data.get("code") != 0:
        raise HTTPException(404, "视频不存在")
    return data["data"]

async def _get_play_url(client: httpx.AsyncClient, params: dict, qn: int = 80, fnval: int = 4048) -> dict:
    params["qn"] = qn
    params["fnval"] = fnval
    resp = await client.get(f"{API_BASE}/x/player/playurl", params=params)
    return resp.json()

def _get_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(headers=BILIBILI_HEADERS, timeout=30)

@router.get("/hot")
async def get_hot(ps: int = 50):
    ps = min(ps, 100)
    async with _get_client() as client:
        resp = await client.get(f"{API_BASE}/x/web-interface/popular", params={"ps": ps})
        return resp.json()

@router.get("/video/{bvid}")
async def get_video(bvid: str):
    async with _get_client() as client:
        resp = await client.get(f"{API_BASE}/x/web-interface/view", params={"bvid": bvid})
        return resp.json()

@router.post("/video")
async def post_video(request: BvRequest):
    async with _get_client() as client:
        resp = await client.get(f"{API_BASE}/x/web-interface/view", params={"bvid": request.bvid})
        return resp.json()

@router.api_route("/video/download/{bvid}", methods=["GET", "POST"])
async def get_video_download(bvid: str, qn: int = 80, fnval: int = 0):
    async with _get_client() as client:
        info = await _get_info(client, bvid=bvid)
        return await _get_play_url(client, {"bvid": bvid, "cid": info["cid"]}, qn=qn, fnval=fnval)

@router.api_route("/video/download/1080/{bvid}", methods=["GET", "POST"])
async def get_video_download_1080(bvid: str, qn: int = 80, fnval: int = 4048):
    async with _get_client() as client:
        info = await _get_info(client, bvid=bvid)
        return await _get_play_url(client, {"bvid": bvid, "cid": info["cid"]}, qn=qn, fnval=fnval)

@router.get("/video/avid/{aid}")
async def get_video_by_aid(aid: int):
    async with _get_client() as client:
        resp = await client.get(f"{API_BASE}/x/web-interface/view", params={"aid": aid})
        return resp.json()

@router.post("/video/avid")
async def post_video_by_aid(request: AvidRequest):
    async with _get_client() as client:
        resp = await client.get(f"{API_BASE}/x/web-interface/view", params={"aid": request.avid})
        return resp.json()

@router.api_route("/video/download/avid/{aid}", methods=["GET", "POST"])
async def get_video_download_by_aid(aid: int, qn: int = 80, fnval: int = 4048):
    async with _get_client() as client:
        info = await _get_info(client, aid=aid)
        return await _get_play_url(client, {"aid": aid, "cid": info["cid"]}, qn=qn, fnval=fnval)

async def _search_bilibili(keyword: str, page: int, page_size: int):
    page_size = min(page_size, 50)
    params = {"search_type": "video", "keyword": keyword, "page": page, "page_size": page_size}
    async with _get_client() as client:
        resp = await client.get(f"{API_BASE}/x/web-interface/wbi/search/type", params=params)
        return resp.json()

@router.get("/search/{keyword}")
async def search_video(keyword: str, page: int = 1, page_size: int = 20):
    return await _search_bilibili(keyword, page, page_size)

@router.post("/search")
async def post_search_video(request: SearchRequest):
    return await _search_bilibili(request.keyword, request.page, request.page_size)
