import os
import json
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import List, Optional
import uuid
from pydantic import BaseModel
from routers.Monitor.models import Monitor
from routers.Monitor.manager import get_global_manager, MonitorManager

EXPECTED_TOKEN = os.environ.get("WEB_MONITORS_TOKEN", "")
if not EXPECTED_TOKEN:
    raise RuntimeError("WEB_MONITORS_TOKEN environment variable not set")

router = APIRouter(
    prefix="/monitors",
    tags=["Web Monitors"],
    redirect_slashes=False
)

def get_manager() -> MonitorManager:
    return get_global_manager()

async def get_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication Fails")
    token = authorization
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    if token != EXPECTED_TOKEN:
        raise HTTPException(status_code=403, detail=f"Authentication Fails, Your token: {token} is invalid")
    return token

class MonitorCreate(BaseModel):
    method: str
    url: str
    data: Optional[str] = None
    frequency: int = 30

class MonitorOut(BaseModel):
    id: str
    method: str
    url: str
    data: Optional[str]
    frequency: int
    enabled: bool
    latest_result: Optional[dict] = None

def _serialize_data(data):
    if data is None:
        return None
    if isinstance(data, dict):
        return json.dumps(data)
    return data

@router.get("", response_model=List[MonitorOut])
async def list_monitors(
    token: str = Depends(get_token),
    manager: MonitorManager = Depends(get_manager)
):
    monitors = manager.get_monitors()
    result = []
    for m in monitors:
        result.append(MonitorOut(
            id=m.id,
            method=m.method,
            url=m.url,
            data=_serialize_data(m.data),
            frequency=m.frequency,
            enabled=m.enabled,
            latest_result=m.latest_result
        ))
    return result

@router.post("", response_model=MonitorOut)
async def create_monitor(
    mon: MonitorCreate,
    token: str = Depends(get_token),
    manager: MonitorManager = Depends(get_manager)
):
    mid = uuid.uuid4().hex
    parsed_data = None
    if mon.data:
        try:
            parsed_data = json.loads(mon.data)
        except (json.JSONDecodeError, TypeError):
            parsed_data = mon.data
    new_mon = Monitor(mid, mon.method, mon.url, parsed_data, mon.frequency)
    manager.add_monitor(new_mon)
    return MonitorOut(
        id=new_mon.id,
        method=new_mon.method,
        url=new_mon.url,
        data=mon.data,
        frequency=new_mon.frequency,
        enabled=new_mon.enabled,
        latest_result=new_mon.latest_result
    )

@router.delete("/{monitor_id}")
async def delete_monitor(
    monitor_id: str,
    token: str = Depends(get_token),
    manager: MonitorManager = Depends(get_manager)
):
    if not manager.remove_monitor(monitor_id):
        raise HTTPException(status_code=404, detail="Monitor not found")
    return {"status": "deleted"}
