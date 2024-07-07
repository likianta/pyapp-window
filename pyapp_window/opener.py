import os
import sys
import typing as t
from subprocess import Popen
from threading import Thread
from time import sleep
from urllib.error import URLError
from urllib.request import urlopen

import psutil
from lk_utils import run_cmd_args
from lk_utils import wait

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
    blocking: bool = True,
    verbose: bool = False,
    backend: str = None,
    close_window_to_exit: bool = True,
) -> None:
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
    
    if wait_url_ready:
        _wait_webpage_ready(url)
    if blocking:
        select_backend(prefer=backend)(
            icon=icon,
            fullscreen=fullscreen,
            pos=pos,
            size=size,
            title=title,
            url=url,
        )
        if close_window_to_exit:
            _clean_exit()
    else:
        # fmt:off
        proc = run_cmd_args(
            (sys.executable, '-m', 'pyapp_window', title, url),
            ('--pos', '{}:{}'.format(*pos)),
            ('--size', 'fullscreen' if fullscreen else '{}:{}'.format(*size)),
            blocking=False,
            verbose=verbose,
        )
        # fmt:on
        if close_window_to_exit:
            Thread(target=_watch_status, args=(proc,), daemon=True).start()


def _wait_webpage_ready(url: str, timeout: float = 10) -> None:
    print(':t2s')
    for _ in wait(timeout, 0.1):
        try:
            if urlopen(url, timeout=1):
                print('webpage ready', ':t2')
                return
        except (TimeoutError, URLError):
            continue


def _watch_status(popen_proc: Popen) -> None:
    while True:
        if popen_proc.poll() is not None:
            print('user closed window', ':vs')
            # sys.exit()
            _clean_exit()
            return
        sleep(1)


def _clean_exit() -> None:
    pid = os.getpid()
    host = psutil.Process(pid)
    print('exit process', ':vs')
    # print('kill process [{}] {}'.format(pid, host.name()), ':v4s')
    for child in host.children(recursive=True):
        try:
            print('[red dim]|- kill \\[{}] {}[/]'.format(
                child.pid, child.name()), ':sr'
            )
            child.kill()
        except psutil.NoSuchProcess:
            pass
    # host.kill()
    sys.exit()
