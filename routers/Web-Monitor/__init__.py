from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import uuid
from pydantic import BaseModel
from routers.Web-Monitor.models import Monitor
from routers.Web-Monitor.manager import get_global_manager, MonitorManager

router = APIRouter(prefix="/monitors", tags=["monitors"])

def get_manager() -> MonitorManager:
    return get_global_manager()

class MonitorCreate(BaseModel):
    method: str
    url: str
    data: Optional[str] = None
    frequency: int = 30

class MonitorUpdate(BaseModel):
    method: Optional[str] = None
    url: Optional[str] = None
    data: Optional[str] = None
    frequency: Optional[int] = None
    enabled: Optional[bool] = None

class MonitorOut(BaseModel):
    id: str
    method: str
    url: str
    data: Optional[str]
    frequency: int
    enabled: bool
    latest_result: Optional[dict]
    history: List[dict]

@router.get("/", response_model=List[MonitorOut])
async def list_monitors(manager: MonitorManager = Depends(get_manager)):
    return manager.get_monitors()

@router.post("/", response_model=MonitorOut)
async def create_monitor(mon: MonitorCreate, manager: MonitorManager = Depends(get_manager)):
    mid = uuid.uuid4().hex
    new_mon = Monitor(mid, mon.method, mon.url, mon.data, mon.frequency)
    manager.add_monitor(new_mon)
    return new_mon

@router.delete("/{monitor_id}")
async def delete_monitor(monitor_id: str, manager: MonitorManager = Depends(get_manager)):
    manager.remove_monitor(monitor_id)
    return {"status": "deleted"}

@router.patch("/{monitor_id}")
async def update_monitor(monitor_id: str, update: MonitorUpdate, manager: MonitorManager = Depends(get_manager)):
    manager.update_monitor(
        monitor_id,
        update.method,
        update.url,
        update.data,
        update.frequency,
        update.enabled
    )
    return {"status": "updated"}

@router.post("/{monitor_id}/toggle")
async def toggle_monitor(monitor_id: str, manager: MonitorManager = Depends(get_manager)):
    manager.toggle_enabled(monitor_id)
    return {"status": "toggled"}

@router.get("/{monitor_id}/status")
async def get_status(monitor_id: str, manager: MonitorManager = Depends(get_manager)):
    mon = manager.monitors.get(monitor_id)
    if not mon:
        raise HTTPException(404, "Monitor not found")
    return mon.latest_result or {}
