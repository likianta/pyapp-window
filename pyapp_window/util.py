import os
import re
import subprocess as sp
import sys
import typing as t
from time import sleep
from time import time

import lk_logger
import requests

_has_proxy_set_before = 'HTTP_PROXY' in os.environ
# if not _has_proxy_set_before:
#     os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
#     os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'


class T:
    Position0 = t.Union[t.Tuple[int, int], t.Literal['center']]
    Position1 = t.Tuple[int, int]
    Size0 = t.Union[
        t.Tuple[t.Union[int, float], t.Union[int, float]],
        t.Literal['fullscreen']
    ]
    Size1 = t.Tuple[int, int]


def get_screen_size() -> T.Size1:
    def via_tkinter() -> T.Size1:
        # notice: on windows, the size is taking account of the scale factor!
        # i.e. if your screen resolution is 3456x2160, and the scale factor is
        # 150%, the return value will be (2304, 1440) instead of (3456, 2160).
        # see also `normalize_size : if sys.platform == 'win32'`.
        import tkinter
        root = tkinter.Tk()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return width, height - 80  # -80: strip the height of the taskbar
    
    def via_system_api() -> T.Size1:  # macos only
        r = sp.run(
            'echo $(system_profiler SPDisplaysDataType)',
            text=True, shell=True, stdout=sp.PIPE
        )
        m = re.search(r'Resolution: (\d+) x (\d+)', r.stdout)
        w, h = map(int, m.groups())
        # print(ret, (w, h), ':v')
        return w, h - 80
    
    if sys.platform == 'darwin':
        try:
            return via_system_api()
        except Exception:
            pass
    return via_tkinter()


def normalize_position(pos: T.Position0, size: T.Size1 = None) -> T.Position1:
    if isinstance(pos, tuple):
        x, y = pos
        
        # resolve negative value
        w0, h0 = get_screen_size()
        if x < 0 or y < 0:
            assert size
            w1, h1 = size
            if x < 0:
                x = w0 - abs(x) - w1
            if y < 0:
                y = h0 - abs(y) - h1
        assert x >= 0 and y >= 0
        
        # adapt to screen size
        if x > w0:
            x = w0 - 10
        if y > h0:
            y = h0 - 10
        
        return x, y
    else:
        assert pos == 'center'
        assert size
        w0, h0 = get_screen_size()
        w1, h1 = size
        x, y = (w0 - w1) // 2, (h0 - h1) // 2
        return (x if x >= 0 else 0), (y if y >= 0 else 0)


def normalize_size(size: T.Size0) -> T.Size1:
    if isinstance(size, tuple):
        w, h = size
        
        # resolve fractional value
        w0, h0 = get_screen_size()
        # print((w0, h0), (w, h), ':v')
        
        if w < 1 or h < 1:
            if w < 1:
                w = round(w0 * w)
            if h < 1:
                h = round(h0 * h)
        assert w > 0 and h > 0
        
        # adapt to screen size
        if sys.platform == 'win32':
            # detect scale factor
            import ctypes
            factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
            #   e.g. 1.5, means 150%
            w, h = round(w / factor), round(h / factor)
        
        if w > w0:
            r = h / w
            w = round(w0 * 0.95)
            h = round(w * r)
        if h > h0:
            r = w / h
            h = round(h0 * 0.95)
            w = round(h * r)
        assert w <= w0 and h <= h0
        
        return w, h
    else:
        assert size == 'fullscreen', ('not supported type', size)
        return get_screen_size()


def wait_webpage_ready(url: str, timeout: float = 30) -> None:
    start = time()
    with lk_logger.timing():
        while True:
            try:
                if _has_proxy_set_before:
                    r = requests.head(url)
                else:
                    r = requests.head(
                        url, proxies={'http': None, 'https': None}
                    )
            except requests.exceptions.ConnectionError as e:
                if 'WinError 10061' in str(e):
                    print(
                        'stop checking url since we encountered proxy error',
                        ':ptv6'
                    )
                    break
            if (
                200 <= r.status_code < 400 or
                r.status_code in (400, 405, 500)
            ):
                print('webpage ready', url, ':ptv4')
                break
            elif r.status_code == 502:
                sleep(0.5)
                if time() - start > timeout:
                    raise TimeoutError('timeout waiting for webpage ready')
                continue
            else:
                raise Exception(r.status_code)


# TODO: not proven yet
def wait_webpage_ready_2(timeout: float = 30) -> None:
    import os
    from lk_utils import wait
    with lk_logger.timing():
        for _ in wait(timeout, 0.2):
            if os.getenv('PYAPP_WINDOW_TARGET_READY'):
                print('webpage ready', ':t')
                break
