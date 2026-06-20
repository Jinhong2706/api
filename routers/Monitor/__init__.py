import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import APIKeyQuery
from typing import List, Optional
import uuid
from pydantic import BaseModel
from routers.Monitor.models import Monitor
from routers.Monitor.manager import get_global_manager, MonitorManager

EXPECTED_TOKEN = os.environ.get("WEB_MONITOR_TOKEN", "")
if not EXPECTED_TOKEN:
    raise RuntimeError("WEB_MONITOR_TOKEN environment variable not set")

api_key_query = APIKeyQuery(name="token", auto_error=False)

async def verify_monitor_token(token: str = Depends(api_key_query)):
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if token != EXPECTED_TOKEN:
        raise HTTPException(status_code=403, detail=f"Authentication Fails, Your token: {token} is invalid")

router = APIRouter(
    prefix="/monitors",
    tags=["Web Monitors"],
    dependencies=[Depends(verify_monitor_token)],
    redirect_slashes=False
)

def get_manager() -> MonitorManager:
    return get_global_manager()

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
    latest_result: Optional[dict]
    history: List[dict]

@router.get("")
async def list_monitors(manager: MonitorManager = Depends(get_manager)):
    return manager.get_monitors()

@router.post("")
async def create_monitor(mon: MonitorCreate, manager: MonitorManager = Depends(get_manager)):
    mid = uuid.uuid4().hex
    new_mon = Monitor(mid, mon.method, mon.url, mon.data, mon.frequency)
    manager.add_monitor(new_mon)
    return new_mon

@router.delete("/{monitor_id}")
async def delete_monitor(monitor_id: str, manager: MonitorManager = Depends(get_manager)):
    if not manager.remove_monitor(monitor_id):
        raise HTTPException(status_code=404, detail="Monitor not found")
    return {"status": "deleted"}
