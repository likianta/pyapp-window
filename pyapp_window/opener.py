import os
import sys
import typing as t
from time import sleep
from time import time

from lk_logger import logger
from lk_utils import run_cmd_args
from lk_utils import wait
from lk_utils.subproc import Popen

from .backend import select_backend
from .utils import normalize_pos
from .utils import normalize_size


def open_window(
    title: str = 'Pyapp Window',
    url: str = None,
    icon: str = None,
    host: str = None,
    port: int = None,
    pos: t.Union[t.Tuple[int, int], t.Literal['center']] = 'center',
    size: t.Union[t.Tuple[int, int], t.Literal['fullscreen']] = (1200, 900),
    wait_url_ready: bool = False,
    splash_screen: str = None,
    blocking: bool = True,
    verbose: bool = False,
    backend: str = None,
    close_window_to_exit: bool = True,
) -> t.Optional[Popen]:
    """
    params:
        url: if url is set, host and port will be ignored.
        pos: (x, y) or 'center'.
            x is started from left, y is started from top.
            trick: use negative value to start from right or bottom.
            if x or y exceeds the screen size, it will be adjusted.
        size: (w, h) or 'fullscreen'.
            trick: use fractional value to set the window size as a ratio of -
            the screen size. for example (0.8, 0.6) will set the window size -
            to 80% width and 60% height of the screen.
            if w or h exceeds the screen size, it will be adjusted.
    """
    # check params
    if not url:
        if not host:
            host = 'localhost'
        assert port
        url = 'http://{}:{}'.format(host, port)
    
    if size == 'fullscreen':  # another way to set fullscreen
        fullscreen = True
        size = (1200, 900)
    else:
        fullscreen = False
        size = normalize_size(size)
    pos = normalize_pos(pos, size)
    print(pos, size, ':v')
    
    if wait_url_ready and not splash_screen:
        _wait_webpage_ready(url)
        # _wait_webpage_ready_2()
    
    if blocking:
        select_backend(prefer=backend)(
            icon=icon,
            fullscreen=fullscreen,
            pos=pos,
            size=size,
            splash_screen=splash_screen,
            title=title,
            url=url,
        )
        if close_window_to_exit:
            sys.exit()
    else:
        return run_cmd_args(
            (sys.executable, '-m', 'pyapp_window'),
            ('--title', title),
            ('--url', url),
            ('--pos', '{}:{}'.format(*pos)),
            ('--size', 'fullscreen' if fullscreen else '{}:{}'.format(*size)),
            ('--splash_screen', splash_screen),
            blocking=False,
            verbose=verbose,
        )


def _wait_webpage_ready(url: str, timeout: float = 30) -> None:
    import requests
    start = time()
    with logger.timing():
        while True:
            r = requests.head(url)
            if r.status_code in (200, 405):
                print('webpage ready', url, ':tv2')
                break
            elif r.status_code == 502:
                sleep(0.5)
                if time() - start > timeout:
                    raise TimeoutError('timeout waiting for webpage ready')
                continue
            else:
                raise Exception(r.status_code)


def _wait_webpage_ready_2(timeout: float = 30) -> None:
    with logger.timing():
        for _ in wait(timeout, 0.2):
            if os.getenv('PYAPP_WINDOW_TARGET_READY'):
                print('webpage ready', ':t')
                break
