import os
import asyncio

from fastapi import APIRouter
from fastapi.responses import JSONResponse, FileResponse
from jinja2.exceptions import SecurityError
from loguru import logger
from pydantic import BaseModel

from .render import ScreenshotOptions, Text2ImgRender
from .util import cleanup_expired_files

router = APIRouter()

render = Text2ImgRender()

class GenerateRequest(BaseModel):
    html: str | None = None
    tmpl: str | None = None
    tmplname: str | None = None
    tmpldata: dict | None = None
    options: ScreenshotOptions | None = None
    return_json: bool = False

async def periodic_cleanup():
    while True:
        try:
            cleanup_expired_files()
        except Exception as e:
            logger.error(f"Error during periodic cleanup: {e}")
        await asyncio.sleep(3600)

@router.get("/text2img/data/{id}")
async def text2img_image(id: str):
    pic = os.path.join("data", id)
    if os.path.exists(pic):
        return FileResponse(pic, media_type="image/jpeg")
    else:
        return JSONResponse(
            status_code=404,
            content={"code": 1, "message": "file not found", "data": {}},
        )

@router.post("/text2img/generate")
async def text2img(request: GenerateRequest):
    is_json_return = request.return_json or False
    if request.tmpl or request.tmplname:
        if request.tmpl:
            tmpl = request.tmpl
        else:
            with open(f"tmpl/{request.tmplname}.html", "r", encoding="utf-8") as f:
                tmpl = f.read()
        try:
            _, abs_path = await render.from_jinja_template(tmpl, request.tmpldata or {})
        except SecurityError as e:
            return JSONResponse(
                status_code=400,
                content={"code": 1, "message": f"security error: {str(e)}", "data": {}},
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "code": 1,
                    "message": f"template render error: {str(e)}",
                    "data": {},
                },
            )
    elif request.html:
        html = request.html
        _, abs_path = await render.from_html(html)
    else:
        return JSONResponse(
            status_code=400,
            content={"code": 1, "message": "html or tmpl not found", "data": {}},
        )

    options = (
        request.options
        if request.options
        else ScreenshotOptions(
            timeout=None,
            type="png",
            quality=None,
            omit_background=None,
            full_page=True,
            clip=None,
            animations=None,
            caret=None,
            scale="device",
        )
    )

    pic = await render.html2pic(abs_path, options)
    media_type = "image/png" if pic.endswith(".png") else "image/jpeg"

    if is_json_return:
        return JSONResponse(
            content={
                "code": 0,
                "message": "success",
                "data": {"id": pic.replace("\\", "/")},
            },
        )
    else:
        return FileResponse(pic, media_type=media_type)
