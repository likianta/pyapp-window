import re
import subprocess as sp
import sys
import typing as t
from time import sleep
from urllib.error import URLError
from urllib.request import urlopen


def adapt_size_to_screen(window_size: t.Tuple[int, int]) -> t.Tuple[int, int]:
    """
    if window size is larger than screen size, adapt it to the screen size.
    """
    w0, h0 = get_screen_size()
    w1, h1 = window_size
    ratio1 = h1 / w1
    if h1 > h0:
        h1 = int(h0 * 0.95)
        w1 = int(h1 / ratio1)
    if w1 > w0:
        w1 = int(w0 * 0.95)
        h1 = int(w1 * ratio1)
    return w1, h1


def get_center_pos(window_size: t.Tuple[int, int]) -> t.Tuple[int, int]:
    w0, h0 = get_screen_size()
    w1, h1 = window_size
    x, y = (w0 - w1) // 2, (h0 - h1) // 2
    return (x if x >= 0 else 0), (y if y >= 0 else 0)


def get_screen_size() -> t.Tuple[int, int]:
    def via_tkinter() -> t.Tuple[int, int]:
        import tkinter
        root = tkinter.Tk()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return width, height - 80  # -80: strip the height of the taskbar
    
    def via_system_api() -> t.Tuple[int, int]:
        ret = sp.run(
            'echo $(system_profiler SPDisplaysDataType)',
            text=True,
            shell=True,
            stdout=sp.PIPE,
        )
        m = re.search(r'Resolution: (\d+) x (\d+)', ret.stdout)
        w, h = map(int, m.groups())
        # print(ret, (w, h), ':v')
        return w, h - 80
    
    if sys.platform == 'darwin':
        try:
            return via_system_api()
        except Exception:
            pass
    return via_tkinter()


def wait_webpage_ready(url: str, timeout: float = 10) -> None:
    print(':t2s')
    for _ in _wait(timeout, 0.1):
        try:
            if urlopen(url, timeout=1):
                print('webpage ready', ':t2')
                return
        except (TimeoutError, URLError):
            continue
    # raise TimeoutError('url is not accessible', url)


def _wait(timeout: float, interval: float = 1) -> t.Iterator[int]:
    count = int(timeout / interval)
    for i in range(count):
        yield i
        sleep(interval)
    raise TimeoutError(f'timeout in {timeout} seconds (with {count} loops)')
