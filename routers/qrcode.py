from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import qrcode
import base64
from io import BytesIO

router = APIRouter(prefix="/qrcode", tags=["二维码"])


class QRCodeRequest(BaseModel):
    text: str


def _generate_qrcode_base64(text: str) -> str:
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成二维码失败: {str(e)}")


@router.get("/{text:path}", response_class=PlainTextResponse)
async def get_qrcode(text: str):
    return _generate_qrcode_base64(text)


@router.post("/", response_class=PlainTextResponse)
async def post_qrcode(request: QRCodeRequest):
    return _generate_qrcode_base64(request.text)
