import os
import json
import threading
import time
import logging
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import List, Optional
import uuid
from pydantic import BaseModel

logger = logging.getLogger(__name__)

DATA_FILE = os.environ.get("MONITORS_DATA_FILE", "/data/monitors.json")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}
MAX_WORKERS = 10

class Monitor:
    def __init__(self, mid, method, url, data, frequency, enabled=True):
        self.id = mid
        self.method = method
        self.url = url
        self.data = data
        self.frequency = frequency
        self.enabled = enabled
        self.last_run = 0
        self.latest_result = None

class MonitorManager:
    def __init__(self):
        self.monitors = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread = None
        self._executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Monitor manager started")

    def load_saved_monitors(self):
        if not os.path.exists(DATA_FILE):
            logger.info(f"Data file {DATA_FILE} not found, will create new")
            return
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            for item in data:
                mid = item.get("id")
                if mid is None:
                    continue
                mon = Monitor(
                    mid=mid,
                    method=item.get("method", "GET"),
                    url=item.get("url", ""),
                    data=item.get("data"),
                    frequency=item.get("frequency", 30),
                    enabled=item.get("enabled", True)
                )
                self.monitors[mid] = mon
            logger.info(f"Loaded {len(self.monitors)} monitors from {DATA_FILE}")
        except Exception as e:
            logger.error(f"Load failed: {e}")

    def save_monitors(self):
        try:
            with self._lock:
                data = []
                for mon in self.monitors.values():
                    data.append({
                        "id": mon.id,
                        "method": mon.method,
                        "url": mon.url,
                        "data": mon.data,
                        "frequency": mon.frequency,
                        "enabled": mon.enabled
                    })
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Save failed: {e}")

    def add_monitor(self, monitor):
        with self._lock:
            self.monitors[monitor.id] = monitor
        self.save_monitors()
        logger.info(f"Added monitor: {monitor.url}")

    def remove_monitor(self, mid):
        deleted = False
        with self._lock:
            if mid in self.monitors:
                del self.monitors[mid]
                deleted = True
        if deleted:
            self.save_monitors()
            logger.info(f"Removed monitor: {mid}")
        return deleted

    def update_monitor(self, mid, method, url, data, frequency, enabled=None):
        with self._lock:
            mon = self.monitors.get(mid)
            if mon:
                mon.method = method
                mon.url = url
                mon.data = data
                mon.frequency = frequency
                if enabled is not None:
                    mon.enabled = enabled
        self.save_monitors()
        logger.info(f"Updated monitor: {mid}")

    def toggle_enabled(self, mid):
        with self._lock:
            mon = self.monitors.get(mid)
            if mon:
                mon.enabled = not mon.enabled
        self.save_monitors()
        logger.info(f"Toggled monitor {mid} to {'enabled' if mon.enabled else 'disabled'}")

    def get_monitors(self):
        with self._lock:
            return list(self.monitors.values())

    def _execute(self, mon):
        start = time.time()
        try:
            if mon.method == "GET":
                resp = requests.get(mon.url, headers=HEADERS, timeout=10)
            else:
                if isinstance(mon.data, dict):
                    resp = requests.post(mon.url, json=mon.data, headers=HEADERS, timeout=10)
                else:
                    resp = requests.post(mon.url, data=mon.data, headers=HEADERS, timeout=10)
            elapsed = time.time() - start
            result = {
                "status_code": resp.status_code,
                "response_time": round(elapsed, 3),
                "error": None,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
        except Exception as e:
            elapsed = time.time() - start
            result = {
                "status_code": None,
                "response_time": round(elapsed, 3),
                "error": str(e),
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
        with self._lock:
            mon.latest_result = result

    def _run_loop(self):
        while self._running:
            now = time.time()
            with self._lock:
                monitors = list(self.monitors.values())
            for mon in monitors:
                if mon.enabled and (now - mon.last_run >= mon.frequency):
                    mon.last_run = now
                    self._executor.submit(self._execute, mon)
            time.sleep(1)

    def shutdown(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        self._executor.shutdown(wait=False)

_manager_instance = None

def get_global_manager():
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = MonitorManager()
        _manager_instance.load_saved_monitors()
        _manager_instance.start()
    return _manager_instance

def shutdown_global_manager():
    global _manager_instance
    if _manager_instance:
        _manager_instance.shutdown()
        _manager_instance = None

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
