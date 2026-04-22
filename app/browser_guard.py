import asyncio
import re
import sys
import time
import json
import subprocess
import requests
import websockets
from typing import Dict, Optional, List
from loguru import logger
from playwright.async_api import async_playwright, Page, BrowserContext
import os
from utils import get_screensize
from shutil import which


def _get_chromium_version(executable_path: str = "/usr/bin/chromium") -> Optional[str]:
    try:
        exe = executable_path if os.path.exists(executable_path) else (which("chromium") or which("chromium-browser") or executable_path)
        result = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=3)
        text = (result.stdout or result.stderr or "").strip()
        # e.g. Chromium 120.0.6099.109
        m = re.search(r"(Chromium|Google Chrome)\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", text)
        return m.group(2) if m else None
    except Exception:
        return None


def _chrome_major(version: Optional[str]) -> str:
    if not version:
        return "120"
    return version.split(".")[0]


def _build_user_agent(version: Optional[str], locale: str) -> str:
    # Example: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.109 Safari/537.36
    chrome_ver = version or "120.0.6099.109"
    return (
        f"Mozilla/5.0 (X11; Linux x86_64; {locale}) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/{chrome_ver} Safari/537.36"
    )


def _build_ua_ch_headers(version: Optional[str]) -> Dict[str, str]:
    major = _chrome_major(version)
    return {
        "Sec-CH-UA": f'"Not A(Brand)";v="99", "Chromium";v="{major}", "Google Chrome";v="{major}"',
        "Sec-CH-UA-Platform": '"Linux"',
        "Sec-CH-UA-Mobile": "?0",
    }
logger.remove()
logger.add(sys.stderr, level="INFO")

init_url = os.getenv("CHROME_INIT_URL", "chrome://newtab/")
resolution_pattern = re.compile(r"^(\d+)x(\d+)$")
SCREEN_RESOLUTION = os.getenv("SCREEN_RESOLUTION", "1920x1080")
match = resolution_pattern.match(SCREEN_RESOLUTION)
if not match:
    logger.warning(
        f"Invalid screen resolution: {SCREEN_RESOLUTION}, using default 1920x1080"
    )
    SCREEN_RESOLUTION = "1920x1080"

SCREEN_WIDTH = int(match.group(1) if match else "1920")
SCREEN_HEIGHT = int(match.group(2) if match else "1080")


class BrowserGuard:
    """
    主要功能是在 Chromium 窗口被关闭后自动打开新标签页。
    """

    def __init__(self, check_interval: float = 1.0):
        self.running: bool = False
        self.check_interval: float = check_interval
        self.browser: Optional[BrowserContext] = None
        self.pages: List[Page] = []
        self.current_page_index: int = 0
        self.width: int = int(match.group(1) if match else "1920")
        self.height: int = int(match.group(2) if match else "1080")
        logger.info(
            f"BrowserGuard initialized with width: {self.width}, height: {self.height}"
        )

    async def start(self):
        try:
            # import this after x11 server is ready
            import pyautogui

            logger.info("Starting browser initialization...")
            playwright = await async_playwright().start()
            logger.info("Playwright started, launching browser...")

            # Build environment-aware identity
            locale = os.getenv("CHROME_LOCALE", "zh-CN")
            tz = os.getenv("TZ", "Asia/Shanghai")
            chromium_version = _get_chromium_version()
            user_agent = _build_user_agent(chromium_version, locale)
            ua_ch = _build_ua_ch_headers(chromium_version)

            extra_flags = os.getenv("CHROME_FLAGS", "")
            extra_args: List[str] = []
            if extra_flags:
                extra_args = extra_flags.split(" ")

            # Use non-headless mode for testing with slower timeouts
            launch_options = {
                "user_data_dir": "/app/data/chrome_data",
                "viewport": {"width": self.width, "height": self.height},
                "headless": False,
                "timeout": 60000.0,
                "user_agent": user_agent,
                "locale": locale,
                "timezone_id": tz,
                "extra_http_headers": {
                    "Accept-Language": f"{locale},en;q=0.8",
                    **ua_ch,
                },
                "args": [
                    "--window-position=0,0",
                    "--remote-debugging-port=9222",
                    "--single-process",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-background-networking",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-breakpad",
                    "--disable-component-extensions-with-background-pages",
                    "--disable-dev-shm-usage",
                    "--disable-features=TranslateUI",
                    "--disable-ipc-flooding-protection",
                    "--disable-renderer-backgrounding",
                    "--enable-features=NetworkServiceInProcess2",
                    "--force-color-profile=srgb",
                    "--metrics-recording-only",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--mute-audio",
                    "--enable-logging",
                    "--log-file=/app/logs/chromium.log",
                    "--no-sandbox",
                    "--disable-gpu",
                    # "--disable-extensions",
                    "--load-extension=/app/pdf-viewer",
                    '--js-flags="--max_old_space_size=1024"',
                    *extra_args,
                ],
                "ignore_default_args": [
                    "--disable-extensions",
                ],
            }

            count = 0
            while count < 3:
                try:
                    self.browser = await playwright.chromium.launch_persistent_context(
                        executable_path="/usr/bin/chromium", **launch_options
                    )

                    logger.info("Browser launched successfully")
                    x, y = pyautogui.position()
                    width, _ = get_screensize()
                    pyautogui.click(width - 25, 115)
                    pyautogui.moveTo(x, y)
                    # await self.browser.pages[0].reload()
                    await self.browser.pages[0].goto(init_url)
                    break
                except Exception as browser_error:
                    logger.info(f"Failed to launch browser: {browser_error}")
                    count += 1

            if count == 3:
                raise RuntimeError("Failed to launch browser, retried 3 times")

            logger.info("Browser initialization completed successfully")
        except Exception as e:
            logger.info(f"Browser startup error: {str(e)}")
            raise RuntimeError(f"Browser initialization failed: {str(e)}")

    async def shutdown(self):
        """Clean up browser instance on shutdown"""
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
                self.pages = []
                self.current_page_index = 0
        except Exception as e:
            logger.error(f"Shutdown error: {str(e)}")

    async def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                # 检查标签页
                logger.debug(f"浏览器状态: {self.browser}")
                if not self.browser:
                    logger.info("浏览器未启动，重新启动浏览器...")
                    await self.shutdown()
                    await self.start()
                    continue
                if not self.browser.pages:
                    logger.info("浏览器没有打开标签页，重新启动浏览器...")
                    await self.shutdown()
                    await self.start()

                logger.debug(f"浏览器标签页: {self.browser.pages}")

            except Exception as e:
                logger.error(f"监控循环出错: {e}")
                await self.shutdown()
                await self.start()

            await asyncio.sleep(self.check_interval)

    async def start_monitoring(self):
        """开始监控"""
        if self.running:
            return

        self.running = True

        try:
            # 运行监控循环
            await self._monitor_loop()
        except Exception as e:
            logger.error(f"监控循环出错: {e}")
        finally:
            await self.shutdown()

    async def stop_async(self):
        """异步停止监控和浏览器"""
        self.running = False

        logger.info("监控已停止")

    async def stop(self):
        """同步停止监控和浏览器"""
        self.running = False

        try:
            await self.stop_async()
        except Exception as e:
            logger.error(f"停止时出错: {e}")

    async def set_screen_resolution(self, width: int, height: int):
        """设置屏幕分辨率"""
        if self.browser:
            await self.browser.pages[0].set_viewport_size(
                {"width": width, "height": height}
            )


class BrowserCDPGuard:
    """
    Chromium 监控器，使用 CDP (Chrome DevTools Protocol) 直接控制浏览器。

    主要功能是在 Chromium 窗口被关闭或被最小化后自动打开新标签页或最大化窗口。
    """

    def __init__(self, check_interval: int = 1, executable_path: Optional[str] = None):
        self.running = False
        self.check_interval = check_interval
        self.debugging_port = None
        self.browser_process = None
        self.cdp_url = "http://localhost:9222"
        self.ws_connections = {}  # 存储每个标签页的 WebSocket 连接
        self.executable_path = executable_path or "/usr/bin/chromium"

    async def _send_cdp_command(
        self,
        ws,
        command: str,
        params: Optional[Dict] = None,
        timeout: float = 5.0,
    ):
        """发送 CDP 命令"""
        if params is None:
            params = {}

        message = {"id": 1, "method": command, "params": params}

        try:
            data = json.dumps(message)
            await ws.send(data)

            # 使用 asyncio.wait_for 来实现超时
            async def wait_for_response():
                while True:
                    response = await ws.recv()
                    response_obj = json.loads(response)

                    # 如果是事件消息，跳过继续等待
                    if "method" in response_obj:
                        logger.debug(f"收到事件消息: {response_obj['method']}")
                        continue

                    # 检查是否是我们发送的命令的响应
                    if "id" in response_obj and response_obj["id"] == message["id"]:
                        if "error" in response_obj:
                            logger.error(f"CDP 命令错误: {response_obj['error']}")
                            return None
                        return response_obj.get("result", {})

                    # 如果不是我们的响应，继续等待
                    logger.info(f"收到未匹配的响应: {response_obj}")

            return await asyncio.wait_for(wait_for_response(), timeout)

        except asyncio.TimeoutError:
            logger.error(f"CDP 命令超时: {command}")
            return None
        except Exception as e:
            logger.error(f"CDP 命令执行失败: {e}")
            return None

    async def start(
        self,
        headless: bool = False,
        debugging_port: int = 9222,
        retry_count: int = 6,
    ):
        """启动 Chromium 浏览器进程"""
        try:
            import pyautogui

            self.debugging_port = debugging_port
            self.cdp_url = f"http://localhost:{debugging_port}"
            url = os.getenv("CHROME_INIT_URL", "chrome://newtab/")
            # 构建启动参数
            chrome_args = [
                self.executable_path,
                url,
                f"--remote-debugging-port={debugging_port}",
                "--remote-debugging-address=0.0.0.0",
                "--window-position=0,0",
                f"--window-size={SCREEN_WIDTH},{SCREEN_HEIGHT}",
                "--no-first-run",
                "--no-default-browser-check",
                "--start-maximized",
                "--no-sandbox",
                "--disable-dbus",
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--enable-logging=file",
                "--log-file=/tmp/chromium_detailed.log",
                "--disable-infobars",
                "--disable-blink-features=AutomationControlled",
                "--user-data-dir=/tmp/chromium_user_data",
                "--allow-file-access-from-files",  # This is a dangerous flag, use it at your own risk
                "--load-extension=/app/pdf-viewer",
                '--js-flags="--max_old_space_size=512"',
            ]
            chrome_flags = os.getenv("CHROME_FLAGS", "")
            extra_args: List[str] = []
            if chrome_flags:
                extra_args = chrome_flags.split(" ")

            chrome_args.extend(extra_args)

            if headless:
                chrome_args.append("--headless")

            count = 0
            while count < retry_count:
                # 启动浏览器进程
                self.browser_process = subprocess.Popen(
                    chrome_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                # 等待浏览器启动
                time.sleep(0.5 * ((1.2) ** (count + 1)))

                # 检查浏览器是否成功启动
                if not self._is_browser_running():
                    count += 1
                    self.browser_process.kill()
                    logger.error(f"浏览器启动失败，尝试第 {count} 次")
                    time.sleep(0.1 * (2**count))
                    continue
                break

            x, y = pyautogui.position()
            width, _ = get_screensize()
            pyautogui.click(width - 25, 115)
            pyautogui.moveTo(x, y)

            logger.info("Chromium 已启动并连接")
            return True

        except Exception as e:
            logger.error(f"启动 Chromium 失败: {e}")
            await self.stop_async()
            return False

    async def connect_to_cdp(self, url: str):
        """连接到 CDP"""
        self.cdp_url = url

    def _is_browser_running(self) -> bool:
        """检查浏览器是否在运行"""
        try:
            response = requests.get(self.cdp_url + "/json/version", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"检查浏览器是否在运行失败: {e}")
            return False

    async def get_cdp_tabs(self):
        """获取所有标签页"""
        try:
            response = requests.get(f"{self.cdp_url}/json/list", timeout=5)
            if response.status_code != 200:
                raise ValueError(f"获取标签页失败，状态码: {response.status_code}")

            tabs = response.json()
            # 过滤出 type 为 "page" 的标签页，这些是正常的网页标签页，而不是其他类型的标签页（如 DevTools 等）
            return [tab for tab in tabs if tab.get("type") == "page"]
        except Exception as e:
            raise ValueError(f"获取标签页失败: {e}")

    async def open_new_tab(self, url: str = "chrome://newtab/"):
        """打开新标签页"""
        try:
            # 使用 PUT 方法创建新标签页
            response = requests.put(
                f"{self.cdp_url}/json/new", json={"url": url}, timeout=5
            )
            if response.status_code != 200:
                print(response.text)
                raise Exception(f"打开新标签页失败，状态码: {response.status_code}")

            # 获取新标签页信息
            tab_info = response.json()
            logger.info(f"已打开新标签页: {tab_info.get('id')}")

            # 不在这里调用 maximize_window，让监控循环处理
            return True
        except Exception as e:
            logger.error(f"打开新标签页失败: {e}")
            return False

    async def _connect_to_tab(self, ws_url: str):
        """连接到标签页的 WebSocket"""
        try:
            # 如果已经存在连接，先关闭
            if ws_url in self.ws_connections:
                try:
                    await self.ws_connections[ws_url].close()
                except Exception as e:
                    logger.error(f"关闭 WebSocket 连接失败: {e}")
                del self.ws_connections[ws_url]

            # 创建新连接
            ws = await websockets.connect(
                ws_url,
                # ping_interval=None,  # 禁用自动ping
                close_timeout=5,
                max_size=None,
            )

            # 启用 Browser 域
            self.ws_connections[ws_url] = ws
            return ws
        except Exception as e:
            logger.error(f"连接到标签页 WebSocket 失败: {e}")
            return None

    async def maximize_window(self, tab_id: str):
        """最大化窗口"""
        ws_url = None
        try:
            # 获取标签页信息
            tabs = await self.get_cdp_tabs()
            tab_info = next((tab for tab in tabs if tab["id"] == tab_id), None)

            if not tab_info:
                logger.warning(f"找不到标签页: {tab_id}")
                return

            # 获取或创建 WebSocket 连接
            ws_url = tab_info["webSocketDebuggerUrl"]
            ws = self.ws_connections.get(ws_url)

            # 检查连接是否有效
            if not ws:
                logger.debug("WebSocket 连接已关闭，重新连接")
                ws = None
                if ws_url in self.ws_connections:
                    del self.ws_connections[ws_url]

            if not ws:
                logger.debug(f"创建新的 WebSocket 连接: {ws_url}")
                ws = await self._connect_to_tab(ws_url)
                if not ws:
                    logger.error("无法创建 WebSocket 连接")
                    return

            # 先获取当前窗口状态
            window_state = await self._send_cdp_command(
                ws,
                "Browser.getWindowForTarget",
                {"targetId": tab_id},  # 使用标签页ID而不是固定的windowId
                timeout=3.0,
            )

            if not window_state:
                logger.error("获取窗口状态失败")
                return

            window_id = window_state.get("windowId")
            if not window_id:
                logger.error("无法获取窗口ID")
                return

            bounds: Dict = window_state.get("bounds", {})
            current_state = bounds.get("windowState", "")

            # 获取当前窗口状态
            bounds_state = await self._send_cdp_command(
                ws, "Browser.getWindowBounds", {"windowId": window_id}, timeout=3.0
            )

            if not bounds_state:
                logger.error("获取窗口边界失败")
                return

            current_state = bounds_state.get("bounds", {}).get("windowState", "")
            logger.debug(f"当前窗口状态: {current_state}")

            # 如果窗口不是最大化状态，则进行最大化
            if current_state == "minimized":
                # 恢复窗口
                result = await self._send_cdp_command(
                    ws,
                    "Browser.setWindowBounds",
                    {"windowId": window_id, "bounds": {"windowState": "normal"}},
                    timeout=3.0,
                )
                logger.info("窗口已恢复")

            elif current_state != "maximized":
                # 最大化窗口
                result = await self._send_cdp_command(
                    ws,
                    "Browser.setWindowBounds",
                    {"windowId": window_id, "bounds": {"windowState": "maximized"}},
                    timeout=3.0,
                )

                if result is None:
                    logger.error("窗口最大化失败")

        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket 连接已关闭，将在下次循环重试")
            if ws_url in self.ws_connections:
                del self.ws_connections[ws_url]
        except Exception as e:
            logger.error(f"最大化窗口失败: {e}")
            if ws_url and ws_url in self.ws_connections:
                del self.ws_connections[ws_url]

    async def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                # 检查标签页
                tabs = await self.get_cdp_tabs()
                if not tabs:
                    logger.info("没有打开的标签页，创建新标签页...")
                    await self.open_new_tab()
                    await asyncio.sleep(1)  # 等待标签页创建完成
                    continue

                # 只对第一个标签页进行最大化检查
                await self.maximize_window(tabs[0]["id"])

            except Exception as e:
                logger.error(f"监控循环出错: {e}")
                # 清理所有连接
                for ws in self.ws_connections.values():
                    try:
                        await ws.close()
                    except Exception as e:
                        logger.error(f"关闭 WebSocket 连接失败: {e}")
                self.ws_connections.clear()
                try:
                    if self.browser_process:
                        self.browser_process.terminate()
                        self.browser_process.kill()
                except Exception as e:
                    logger.error(f"停止浏览器进程失败: {e}")
                await self.start()

            await asyncio.sleep(self.check_interval)

    async def start_monitoring(self):
        """开始监控"""
        if self.running:
            return

        self.running = True

        try:
            # 运行监控循环
            await self._monitor_loop()
        except Exception as e:
            logger.error(f"监控循环出错: {e}")
        finally:
            await self.stop_async()

    async def stop_async(self):
        """异步停止监控和浏览器"""
        self.running = False

        # 关闭所有 WebSocket 连接
        for ws in self.ws_connections.values():
            try:
                await ws.close()
            except Exception as e:
                logger.error(f"关闭 WebSocket 连接失败: {e}")
        self.ws_connections.clear()

        # 关闭浏览器进程
        if self.browser_process:
            try:
                self.browser_process.terminate()
                await asyncio.sleep(0.1)  # 给进程一些时间来终止
                if self.browser_process.poll() is None:
                    self.browser_process.kill()
            except Exception as e:
                logger.error(f"停止浏览器进程失败: {e}")
            self.browser_process = None

        logger.info("监控已停止")

    def stop(self):
        """同步停止监控和浏览器"""
        self.running = False

        try:
            # 获取当前事件循环
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果循环正在运行，使用 run_coroutine_threadsafe
                future = asyncio.run_coroutine_threadsafe(self.stop_async(), loop)
                future.result(timeout=5)  # 等待停止完成
            else:
                # 如果循环没有运行，直接运行
                loop.run_until_complete(self.stop_async())
        except Exception as e:
            logger.error(f"停止时出错: {e}")
            # 强制停止进程
            if self.browser_process:
                self.browser_process.kill()

    async def set_screen_resolution(self, width: int, height: int):
        """通过 CDP 协议设置浏览器视窗大小"""
        tabs = await self.get_cdp_tabs()
        tab_info = next((tab for tab in tabs if tab["type"] == "page"), None)
        if not tab_info:
            raise ValueError("没有找到标签页")
        ws_url = tab_info["webSocketDebuggerUrl"]
        ws = self.ws_connections.get(ws_url)
        if not ws:
            ws = await self._connect_to_tab(ws_url)
            if not ws:
                raise ValueError("无法连接到标签页的 WebSocket")

        # 先获取窗口ID
        window_state = await self._send_cdp_command(
            ws,
            "Browser.getWindowForTarget",
            {"targetId": tab_info["id"]},
            timeout=3.0,
        )

        if not window_state:
            raise ValueError("获取窗口状态失败")

        window_id = window_state.get("windowId")
        if not window_id:
            raise ValueError("无法获取窗口ID")

        # 设置窗口大小
        await self._send_cdp_command(
            ws,
            "Browser.setWindowBounds",
            {
                "windowId": window_id,
                "bounds": {"width": width, "height": height, "windowState": "normal"},
            },
        )


def wait_for_display(display=None, timeout=60):
    """等待 X11 显示服务器准备就绪"""
    if display is None:
        display = os.getenv("DISPLAY", ":99")

    logger.info(f"等待显示服务器 {display} 准备就绪...")

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # 尝试连接到 X11 显示服务器
            from Xlib import display as xlib_display

            d = xlib_display.Display(display)
            d.close()
            logger.info(f"显示服务器 {display} 已准备就绪")
            return True
        except Exception as e:
            logger.debug(f"显示服务器未就绪: {e}")
            time.sleep(0.5)

    logger.error(f"超时：显示服务器 {display} 在 {timeout} 秒内未准备就绪")
    return False


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Browser Guard - Monitor and manage browser instances"
    )
    parser.add_argument(
        "--wait-display",
        action="store_true",
        help="Wait for X11 display server to be ready",
    )
    parser.add_argument(
        "--monitor", action="store_true", help="Start browser monitoring"
    )
    parser.add_argument(
        "--display",
        type=str,
        default=None,
        help="X11 display to use (default: from DISPLAY env or :99)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Timeout in seconds for display wait (default: 60)",
    )

    args = parser.parse_args()

    if args.wait_display:
        success = wait_for_display(display=args.display, timeout=args.timeout)
        if not success:
            sys.exit(1)
        logger.info("Display server is ready")

    if args.monitor:

        async def run_monitor():
            if os.getenv("USE_CDP", "false").lower() == "true":
                browser_guard = BrowserCDPGuard()
            else:
                browser_guard = BrowserGuard()

            await browser_guard.start()
            await browser_guard.start_monitoring()

        import asyncio

        try:
            asyncio.run(run_monitor())
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            sys.exit(1)
