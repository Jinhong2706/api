from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse, Response
from pydantic import BaseModel
import qrcode
import base64
from io import BytesIO

router = APIRouter(prefix="/qrcode", tags=["QR Code"])

class QRCodeRequest(BaseModel):
    text: str

def _generate_qrcode_image(text: str) -> BytesIO:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

@router.get("/", response_class=Response)
async def get_qrcode_image(text: str = Query(...)):
    try:
        buf = _generate_qrcode_image(text)
        return Response(content=buf.getvalue(), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/base64", response_class=PlainTextResponse)
async def get_qrcode_base64(text: str = Query(...)):
    try:
        buf = _generate_qrcode_image(text)
        img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_class=Response)
async def post_qrcode_image(request: QRCodeRequest):
    try:
        buf = _generate_qrcode_image(request.text)
        return Response(content=buf.getvalue(), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/base64", response_class=PlainTextResponse)
async def post_qrcode_base64(request: QRCodeRequest):
    try:
        buf = _generate_qrcode_image(request.text)
        img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
