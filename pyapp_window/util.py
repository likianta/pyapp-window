import re
import subprocess as sp
import sys
import typing as tp
from functools import cache
from socket import socket
from time import monotonic
from time import sleep
from urllib.parse import urlsplit


class T:
    OversizeScheme = tp.Literal['aspect_ratio', 'crop', 'keep']
    Position0 = tp.Union[
        tp.Literal['center'],
        tp.Tuple[int, int],
        tp.Tuple[int, tp.Literal['center']],
        tp.Tuple[tp.Literal['center'], int],
    ]
    Position1 = tp.Tuple[int, int]
    Size0 = tp.Union[
        tp.Tuple[tp.Union[int, float], tp.Union[int, float]],
        tp.Literal['fullscreen', 'landscape', 'maximized', 'portrait'],
    ]
    Size1 = tp.Tuple[int, int]


@cache
def get_screen_size() -> T.Size1:
    """
    The primary display's size in **logical (css) pixels**, minus the taskbar.

    Logical pixels are the unit this library takes everywhere (both `pos` and
    `size`), i.e. the one a web page lays out in. It has to be read
    deliberately on windows: `GetSystemMetrics` answers in physical pixels
    when the calling process declared itself dpi aware and in logical ones
    when it did not, so the very same display reports two different screens
    depending on who asks (see also `normalize_size`, which compares a `size`
    against this).
    """
    if sys.platform == 'darwin':
        r = sp.run(
            'echo $(system_profiler SPDisplaysDataType)',
            text=True,
            shell=True,
            stdout=sp.PIPE,
        )
        m = re.search(r'Resolution: (\d+) x (\d+)', r.stdout)
        w, h = map(int, m.groups())
        # print(ret, (w, h), ':v')
        return w, h - 80
    elif sys.platform == 'win32':
        import ctypes

        user32 = ctypes.windll.user32
        gdi = ctypes.windll.gdi32
        # ask gdi for the *physical* desktop size -- 118 and 117 are
        # `DESKTOPHORZRES` and `DESKTOPVERTRES` -- then undo the scale factor,
        # so the answer does not depend on this process' dpi awareness.
        hdc = user32.GetDC(0)
        w = gdi.GetDeviceCaps(hdc, 118)
        h = gdi.GetDeviceCaps(hdc, 117)
        user32.ReleaseDC(0, hdc)
        if not (w and h):  # pragma: nocover
            # desktop composition is off (or an exotic driver): there is no
            # physical size to be had, fall back to whatever we are given.
            w, h = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        else:
            factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
            w, h = round(w / factor), round(h / factor)
        return w, h - 80  # -80: strip the height of the taskbar

    # notice: linux (tkinter) already answers in logical pixels.
    # see also `normalize_size`, which compares a `size` against this.
    import tkinter

    root = tkinter.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.destroy()
    return width, height - 80  # -80: strip the height of the taskbar


def normalize_position(
    pos: T.Position0, size: tp.Optional[T.Size1] = None
) -> T.Position1:
    w0: int
    h0: int
    w1: int
    h1: int
    w0, h0 = get_screen_size()
    w1, h1 = size if size else (None, None)  # type: ignore

    if pos == 'center':
        x, y = (w0 - w1) // 2, (h0 - h1) // 2
        return (x if x >= 0 else 0), (y if y >= 0 else 0)

    if isinstance(pos, str):
        x, y = pos.split(',')
    else:
        x, y = pos
    if x == 'center':
        x = (w0 - w1) // 2
    else:
        x = int(x)
    if y == 'center':
        y = (h0 - h1) // 2
    else:
        y = int(y)
    # assert isinstance(x, int) and isinstance(y, int)

    # adapt to screen size
    if x < 0 or y < 0:
        if x < 0:
            x = w0 - abs(x) - w1
        if y < 0:
            y = h0 - abs(y) - h1
    if x > w0:
        x = w0 - 10
    if y > h0:
        y = h0 - 10

    assert x >= 0 and y >= 0
    return x, y


def normalize_size(
    size: T.Size0, oversize_scheme: T.OversizeScheme = 'aspect_ratio'
) -> T.Size1:
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
        #   note: `size` is in logical pixels, the same unit `get_screen_size`
        #   returns, so the two are compared as they are -- a window is asked
        #   for in the unit the page lays out in, and the backends convert it
        #   to native pixels themselves (`toga` scales by the display's dpi).
        if w > w0:
            if oversize_scheme == 'aspect_ratio':
                r = h / w
                w = round(w0 * 0.95)
                h = round(w * r)
            elif oversize_scheme == 'crop':
                w = w0 - 16
        if h > h0:
            if oversize_scheme == 'aspect_ratio':
                r = w / h
                h = round(h0 * 0.95)
                w = round(h * r)
            elif oversize_scheme == 'crop':
                h = h0 - 16
        assert w <= w0 and h <= h0

        # if (w, h) != size:
        #     print('finalize window size: {} x {}'.format(w, h))
        return w, h  # type: ignore
    else:
        if size == 'fullscreen':
            return get_screen_size()
        elif size == 'maximized':
            w0, h0 = get_screen_size()
            return round(w0 * 0.95), round(h0 * 0.95)
        elif size == 'landscape':
            return normalize_size((1200, 900))
        elif size == 'portrait':
            return normalize_size((640, 960))


def wait_webpage_ready(url: str, timeout: tp.Union[int, float] = 10) -> None:
    parts = urlsplit(url)
    host = parts.hostname or 'localhost'
    port = parts.port or (443 if parts.scheme == 'https' else 80)

    deadline = monotonic() + timeout
    while True:
        with socket() as s:
            # a refused connect may sit on the timeout instead of failing fast,
            # so keep it short and let `deadline` pace the loop.
            s.settimeout(0.5)
            if s.connect_ex((host, port)) == 0:
                print('webpage ready', url, ':ptv4')
                return
            if monotonic() >= deadline:
                raise TimeoutError('timeout waiting for webpage ready', url)
            else:
                sleep(0.1)
