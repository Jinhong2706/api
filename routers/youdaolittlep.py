import os
import hashlib
import time
import json
import uuid
import re
from typing import Optional, List, Union, Any, AsyncGenerator
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
import httpx

router = APIRouter(prefix="/youdaolittlep/v1", tags=["有道小P"])

FIXED_KEY = os.getenv("DICTPEN_FIXED_KEY")
KEY_ID = os.getenv("DICTPEN_KEY_ID")
DEVICE_SN = os.getenv("DICTPEN_SN")
BASE_URL = "https://dictpen-server.youdao.com"
AI_TOKEN = os.getenv("AI_TOKEN")
TIMEOUT = 120
TTS_TIMEOUT = 30
MAX_TEXT_LEN = 100

MODEL_TO_VOICE = {
    "youxiaoshi-tts": "youxiaoshi",
    "youxiaojin-tts": "youxiaojin",
}

class ChatMessage(BaseModel):
    role: str
    content: Union[str, List[Any]]

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "doubao-1.5-pro-32k"
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    max_tokens: Optional[int] = None

class ChatCompletionChoiceMessage(BaseModel):
    role: str = "assistant"
    content: str

class ChatCompletionChoice(BaseModel):
    index: int = 0
    message: ChatCompletionChoiceMessage
    finish_reason: str = "stop"

class ChatCompletionUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str = "doubao-1.5-pro-32k"
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage = ChatCompletionUsage()
    system_fingerprint: Optional[str] = "fp_dictpen"

class ModelObject(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "youdao"

class ModelsResponse(BaseModel):
    object: str = "list"
    data: List[ModelObject]

class BalanceInfo(BaseModel):
    currency: str = "CNY"
    total_balance: str = "27065590.06"
    granted_balance: str = "0.00"
    topped_up_balance: str = "27065590.06"

class BalanceResponse(BaseModel):
    is_available: bool = True
    balance_infos: List[BalanceInfo] = [BalanceInfo()]

class SpeechRequest(BaseModel):
    model: str
    input: str
    voice: Optional[str] = None

def verify_ai_token(authorization: Optional[str] = Header(None)):
    if not AI_TOKEN:
        raise HTTPException(status_code=401, detail="Authentication Fails")
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication Fails")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or token != AI_TOKEN:
        raise HTTPException(status_code=401, detail="Authentication Fails")

def _generate_sign(device_sn: str, key_id: str, mystic_time: str) -> str:
    return hashlib.md5(
        f"deviceSn={device_sn}&keyid={key_id}&mysticTime={mystic_time}&key={FIXED_KEY}"
        .encode('utf-8')
    ).hexdigest()

def _extract_text_from_content(content: Union[str, List[Any]]) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
        return " ".join(parts)
    return ""

def _estimate_tokens(text: str) -> int:
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    other_chars = len(text) - chinese_chars - sum(len(w) for w in re.findall(r'[a-zA-Z]+', text))
    return int(chinese_chars + english_words * 1.3 + other_chars * 0.5)

def _build_message_contents(question: str) -> str:
    content_obj = [{"text": {"content": question}, "type": "text"}]
    return json.dumps(content_obj, ensure_ascii=False)

def _build_conversation_prompt(messages: List[ChatMessage]) -> str:
    lines = []
    for msg in messages:
        role = msg.role
        content = _extract_text_from_content(msg.content)
        lines.append(f"{role.capitalize()}: {content}")
    return "\n".join(lines)

async def _yield_youdao_events(question: str) -> AsyncGenerator[tuple[Optional[str], Optional[str]], None]:
    mystic_time = str(int(time.time() * 1000))
    sign = _generate_sign(DEVICE_SN, KEY_ID, mystic_time)
    data = {
        "osAppVersion": "2.13.0",
        "product": "dictpen",
        "appVersion": "4.13.1",
        "client": "y09",
        "deviceSn": DEVICE_SN,
        "mid": "Linux5.10.160",
        "screen": "640x172",
        "model": "YDPA7-1",
        "imei": DEVICE_SN,
        "deviceSku": "OVERHEAD_Y09_SKU_CHN_PRO",
        "keyid": KEY_ID,
        "mysticTime": mystic_time,
        "sign": sign,
        "pointParam": "deviceSn,keyid,mysticTime",
        "deviceId": DEVICE_SN,
        "messageContents": _build_message_contents(question),
        "messageInfo": '{"subscribe":"strategy","sensitiveScope":"message","responseStyle":"offical"}',
        "messageScene": "dayiPracticeAsk",
        "messageSource": "yd_gpt_dictpen"
    }
    url = f"{BASE_URL}/teacherp/chat/ask/sse"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        async with client.stream("POST", url, data=data, headers=headers) as resp:
            if resp.status_code != 200:
                raise HTTPException(status_code=500, detail="服务器内部错误")
            async for line in resp.aiter_lines():
                if not line or line.startswith(("event:", "id:", "retry:")):
                    continue
                if not line.startswith("data:"):
                    continue
                data_line = line[len("data:"):].strip()
                if data_line == "[DONE]":
                    break
                try:
                    obj = json.loads(data_line)
                except json.JSONDecodeError:
                    continue
                if obj.get("code") != 0:
                    continue
                data_block = obj.get("data", {})
                for item in data_block.get("list", []):
                    if chat_info := item.get("chat"):
                        if cid := chat_info.get("chatId"):
                            yield (None, cid)
                    if text_info := item.get("text"):
                        if text_info.get("type") == "text":
                            if content := text_info.get("content", ""):
                                yield (content, None)

async def _fetch_youdao_answer_non_stream(question: str) -> tuple[str, Optional[str]]:
    answer = ""
    chat_id = None
    try:
        async for content_part, cid in _yield_youdao_events(question):
            if cid and not chat_id:
                chat_id = cid
            if content_part:
                answer += content_part
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="上游服务超时")
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="上游服务错误")
    except Exception:
        raise HTTPException(status_code=500, detail="服务器内部错误")
    if not answer:
        raise HTTPException(status_code=500, detail="服务器内部错误")
    return answer, chat_id

async def _stream_youdao_to_openai(question: str) -> AsyncGenerator[str, None]:
    request_id = uuid.uuid4().hex[:12]
    chat_id = None
    created = int(time.time())
    model_name = "doubao-1.5-pro-32k"
    system_fingerprint = "fp_dictpen"
    full_answer = ""

    role_chunk = {
        "id": f"chatcmpl-{request_id}",
        "object": "chat.completion.chunk",
        "created": created,
        "model": model_name,
        "system_fingerprint": system_fingerprint,
        "choices": [{"index": 0, "delta": {"role": "assistant", "content": ""}, "logprobs": None, "finish_reason": None}]
    }
    yield f"data: {json.dumps(role_chunk, ensure_ascii=False)}\n\n"

    try:
        async for content_part, cid in _yield_youdao_events(question):
            if cid and not chat_id:
                chat_id = cid
            if content_part:
                full_answer += content_part
                content_chunk = {
                    "id": f"chatcmpl-{request_id}",
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model_name,
                    "system_fingerprint": system_fingerprint,
                    "choices": [{"index": 0, "delta": {"content": content_part}, "logprobs": None, "finish_reason": None}]
                }
                yield f"data: {json.dumps(content_chunk, ensure_ascii=False)}\n\n"
    except Exception:
        error_chunk = {
            "id": f"chatcmpl-{request_id}",
            "object": "chat.completion.chunk",
            "created": created,
            "model": model_name,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "error"}],
            "error": {"message": "服务器内部错误"}
        }
        yield f"data: {json.dumps(error_chunk, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
        return

    prompt_tokens = _estimate_tokens(question)
    completion_tokens = _estimate_tokens(full_answer)
    total_tokens = prompt_tokens + completion_tokens
    final_chunk = {
        "id": f"chatcmpl-{request_id}",
        "object": "chat.completion.chunk",
        "created": created,
        "model": model_name,
        "system_fingerprint": system_fingerprint,
        "choices": [{"index": 0, "delta": {}, "logprobs": None, "finish_reason": "stop"}],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "prompt_tokens_details": {"cached_tokens": 0},
            "prompt_cache_hit_tokens": 0,
            "prompt_cache_miss_tokens": prompt_tokens
        }
    }
    yield f"data: {json.dumps(final_chunk, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"

def _split_text(text: str, max_len: int = MAX_TEXT_LEN) -> list[str]:
    sentences = re.split(r'(?<=[。！？\n])', text)
    chunks = []
    current = ""
    for sent in sentences:
        if len(current) + len(sent) <= max_len:
            current += sent
        else:
            if current:
                chunks.append(current)
            current = sent
    if current:
        chunks.append(current)
    final = []
    for chunk in chunks:
        if len(chunk) > max_len:
            for i in range(0, len(chunk), max_len):
                final.append(chunk[i:i+max_len])
        else:
            final.append(chunk)
    return final

async def _tts_request(text: str, voice: str) -> bytes:
    mystic_time = str(int(time.time() * 1000))
    sign = _generate_sign(DEVICE_SN, KEY_ID, mystic_time)
    data = {
        "osAppVersion": "2.13.0",
        "appVersion": "4.13.1",
        "client": "y09",
        "deviceSku": "OVERHEAD_Y09_SKU_CHN_PRO",
        "deviceSn": DEVICE_SN,
        "format": "mp3",
        "imei": DEVICE_SN,
        "keyid": KEY_ID,
        "mid": "Linux5.10.160",
        "model": "YDPA7-1",
        "product": "dictpen",
        "q": text,
        "screen": "640x172",
        "voiceName": voice,
        "volume": "1",
        "mysticTime": mystic_time,
        "sign": sign,
        "pointParam": "deviceSn,keyid,mysticTime",
    }
    url = f"{BASE_URL}/zhiyun/tts"
    async with httpx.AsyncClient(timeout=TTS_TIMEOUT) as client:
        resp = await client.post(url, data=data)
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail="服务器内部错误")
        if not resp.headers.get("Content-Type", "").startswith("audio/"):
            raise HTTPException(status_code=500, detail="服务器内部错误")
        return resp.content

async def _combine_audio_chunks(text: str, voice: str) -> bytes:
    chunks = _split_text(text)
    if not chunks:
        raise HTTPException(status_code=500, detail="服务器内部错误")
    audios = []
    for chunk in chunks:
        try:
            audio = await _tts_request(chunk, voice)
            audios.append(audio)
        except Exception:
            raise HTTPException(status_code=500, detail="服务器内部错误")
    return b"".join(audios)

@router.get("/user/balance", response_model=BalanceResponse)
async def get_user_balance(valid: bool = Depends(verify_ai_token)):
    return BalanceResponse()

@router.get("/models", response_model=ModelsResponse)
async def list_models(valid: bool = Depends(verify_ai_token)):
    return ModelsResponse(
        data=[
            ModelObject(id="doubao-1.5-pro-32k", created=int(time.time())),
            ModelObject(id="youxiaoshi-tts", created=int(time.time())),
            ModelObject(id="youxiaojin-tts", created=int(time.time())),
        ]
    )

@router.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest, valid: bool = Depends(verify_ai_token)):
    if not request.messages:
        raise HTTPException(status_code=500, detail="服务器内部错误")
    full_prompt = _build_conversation_prompt(request.messages)
    if not full_prompt.strip():
        raise HTTPException(status_code=500, detail="服务器内部错误")
    if request.stream:
        return StreamingResponse(
            _stream_youdao_to_openai(full_prompt),
            media_type="text/event-stream"
        )
    answer, chat_id = await _fetch_youdao_answer_non_stream(full_prompt)
    prompt_tokens = _estimate_tokens(full_prompt)
    completion_tokens = _estimate_tokens(answer)
    total_tokens = prompt_tokens + completion_tokens
    resp = ChatCompletionResponse(
        id=f"chatcmpl-{chat_id or 'unknown'}",
        created=int(time.time()),
        choices=[
            ChatCompletionChoice(
                message=ChatCompletionChoiceMessage(content=answer)
            )
        ],
        usage=ChatCompletionUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens
        )
    )
    return resp

@router.post("/audio/speech")
async def create_speech(request: SpeechRequest, valid: bool = Depends(verify_ai_token)):
    if not request.input.strip():
        raise HTTPException(status_code=500, detail="服务器内部错误")
    if request.model not in MODEL_TO_VOICE:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "message": "服务器内部错误",
                    "type": "invalid_request_error",
                    "param": "model",
                    "code": "model_not_found"
                }
            }
        )
    voice = MODEL_TO_VOICE[request.model]
    try:
        audio_bytes = await _combine_audio_chunks(request.input, voice)
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="服务器内部错误")
