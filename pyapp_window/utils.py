import re
import subprocess as sp
import sys
import typing as t
from time import sleep


class T:
    Position0 = t.Union[t.Tuple[int, int], t.Literal['center']]
    Position1 = t.Tuple[int, int]
    Size0 = t.Union[
        t.Tuple[t.Union[int, float], t.Union[int, float]],
        t.Literal['fullscreen']
    ]
    Size1 = t.Tuple[int, int]


def normalize_pos(pos: T.Position0, size: T.Size1 = None) -> T.Position1:
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
        if w < 1 or h < 1:
            if w < 1:
                w = round(w0 * w)
            if h < 1:
                h = round(h0 * h)
        assert w > 0 and h > 0
        
        # adapt to screen size
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


def get_screen_size() -> T.Size1:
    def via_tkinter() -> T.Size1:
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


# def wait_webpage_ready(url: str, timeout: float = 10) -> None:
#     print(':t2s')
#     for _ in _wait(timeout, 0.1):
#         try:
#             if urlopen(url, timeout=1):
#                 print('webpage ready', ':t2')
#                 return
#         except (TimeoutError, URLError):
#             continue
#     # raise TimeoutError('url is not accessible', url)


def _wait(timeout: float, interval: float = 1) -> t.Iterator[int]:
    count = int(timeout / interval)
    for i in range(count):
        yield i
        sleep(interval)
    raise TimeoutError(f'timeout in {timeout} seconds (with {count} loops)')
