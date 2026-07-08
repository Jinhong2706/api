import re
from .util import generate_data_path
from playwright.async_api import async_playwright
from jinja2.sandbox import SandboxedEnvironment
from pydantic import BaseModel
from typing_extensions import TypedDict
from typing import Literal
from loguru import logger
from playwright.async_api import BrowserContext, Browser, Playwright
from playwright._impl._errors import TargetClosedError

class FloatRect(TypedDict):
    x: float
    y: float
    width: float
    height: float

class ScreenshotOptions(BaseModel):
    timeout: float | None = None
    type: Literal["jpeg", "png", None] = None
    quality: int | None = None
    omit_background: bool | None = None
    full_page: bool | None = True
    clip: FloatRect | None = None
    animations: Literal["allow", "disabled", None] = None
    caret: Literal["hide", "initial", None] = None
    scale: Literal["css", "device", None] = None
    viewport_width: int | None = None
    viewport_height: int | None = None
    device_scale_factor_level: Literal["normal", "high", "ultra", None] = None

class Text2ImgRender:
    SCALE_FACTOR_MAP = {
        "normal": 1.0,
        "high": 1.3,
        "ultra": 1.8,
    }

    def __init__(self):
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.contexts: dict[str, BrowserContext] = {}

    async def _ensure_context(self, level: str = "normal") -> BrowserContext:
        if self.playwright is None:
            self.playwright = await async_playwright().start()
        if self.browser is None or not self.browser.is_connected():
            if self.browser is not None:
                try:
                    await self.browser.close()
                except Exception:
                    pass
            self.browser = await self.playwright.chromium.launch(headless=True)
        if level not in self.contexts:
            scale_factor = self.SCALE_FACTOR_MAP.get(level, 1.0)
            self.contexts[level] = await self.browser.new_context(device_scale_factor=scale_factor)
        return self.contexts[level]

    async def from_jinja_template(self, template: str, data: dict) -> tuple[str, str]:
        env = SandboxedEnvironment()
        html = env.from_string(template).render(data)
        return await self.from_html(html)

    async def from_html(self, html: str) -> tuple[str, str]:
        html_file_path, abs_path = generate_data_path(suffix="html", namespace="rendered")
        with open(html_file_path, "w", encoding="utf-8") as f:
            f.write(html)
        return html_file_path, abs_path

    def _resolve_viewport_size(self, html_file_path: str, screenshot_options: ScreenshotOptions) -> tuple[int | None, int | None]:
        viewport_width = screenshot_options.viewport_width
        viewport_height = screenshot_options.viewport_height
        if viewport_width is not None and viewport_height is not None:
            return viewport_width, viewport_height
        try:
            with open(html_file_path, "r", encoding="utf-8") as f:
                head_snippet = f.read(4096)
            if viewport_width is None:
                pattern = r'<meta\s+[^>]*name=["\']viewport["\'][^>]*content=["\'][^"\']*width\s*=\s*(\d+)[^"\']*["\'][^>]*>'
                if m := re.search(pattern, head_snippet, re.IGNORECASE):
                    viewport_width = int(m[1])
            if viewport_height is None:
                pattern = r'<meta\s+[^>]*name=["\']viewport["\'][^>]*content=["\'][^"\']*height\s*=\s*(\d+)[^"\']*["\'][^>]*>'
                if m := re.search(pattern, head_snippet, re.IGNORECASE):
                    viewport_height = int(m[1])
        except Exception:
            pass
        return viewport_width, viewport_height

    async def terminate(self) -> None:
        for level, context in list(self.contexts.items()):
            try:
                await context.close()
            except Exception:
                pass
        self.contexts.clear()
        if self.browser is not None:
            try:
                await self.browser.close()
            except Exception:
                pass
            self.browser = None
        if self.playwright is not None:
            try:
                await self.playwright.stop()
            except Exception:
                pass
            self.playwright = None

    async def html2pic(self, html_file_path: str, screenshot_options: ScreenshotOptions) -> str:
        level = screenshot_options.device_scale_factor_level or "normal"
        context = await self._ensure_context(level)
        suffix = screenshot_options.type if screenshot_options.type else "png"
        result_path, _ = generate_data_path(suffix=suffix, namespace="rendered")
        try:
            page = await context.new_page()
        except TargetClosedError:
            if level in self.contexts:
                try:
                    await self.contexts[level].close()
                except Exception:
                    pass
                del self.contexts[level]
            context = await self._ensure_context(level)
            page = await context.new_page()
        viewport_width, viewport_height = self._resolve_viewport_size(html_file_path, screenshot_options)
        width = viewport_width if viewport_width is not None else 800
        height = viewport_height if viewport_height is not None else 720
        if viewport_width is not None and viewport_height is not None:
            await page.set_viewport_size({"width": width, "height": height})
        try:
            await page.goto(f"file://{html_file_path}", timeout=screenshot_options.timeout)
            screenshot_kwargs = screenshot_options.model_dump(exclude_none=True)
            screenshot_kwargs.pop("viewport_width", None)
            screenshot_kwargs.pop("viewport_height", None)
            screenshot_kwargs.pop("device_scale_factor_level", None)
            if screenshot_options.type == "png":
                screenshot_kwargs.pop("quality", None)
            await page.screenshot(path=result_path, **screenshot_kwargs)
        finally:
            await page.close()
        return result_path
