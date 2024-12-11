import sys
import typing as t

from lk_utils import fs
from lk_utils import run_cmd_args
from lk_utils.subproc import Popen

from .backend import T as T0
from .backend import select_backend
from .util import T as T1
from .util import normalize_position
from .util import normalize_size
from .util import wait_webpage_ready


class T:
    Backend = T0.Backend
    Position = T1.Position0
    Size = T1.Size0


def open_window(
    title: str = 'PyApp Window',
    url: str = None,
    icon: str = None,
    host: str = None,
    port: int = None,
    pos: T.Position = 'center',
    size: T.Size = (1200, 900),
    check_url: bool = False,
    splash_screen: str = None,
    blocking: bool = True,
    verbose: bool = False,
    backend: T.Backend = None,
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
    if not url and backend != 'terminal':
        assert port
        url = 'http://{}:{}'.format(host or 'localhost', port)
    
    size_kw = {
        'fullscreen': size == 'fullscreen',
        'maximized' : size == 'maximized',
        'size'      : None
    }
    if backend == 'terminal':
        if isinstance(size, str):
            size_kw['size'] = {
                'fullscreen': (160, 60),
                'maximized' : (160, 60),
                'large'     : (160, 60),
                'medium'    : (120, 40),
                'small'     : (80, 24),
            }
        else:
            assert (
                isinstance(size, tuple) and
                isinstance(size[0], int) and
                isinstance(size[1], int)
            )
            size_kw['size'] = size
    else:
        size_kw['size'] = normalize_size(size)
    assert size_kw['size']
    
    pos = normalize_position(pos, size)
    print(pos, size, ':v')
    
    if check_url and not splash_screen:
        wait_webpage_ready(url)
    
    if blocking:
        select_backend(prefer=backend)(
            icon=fs.abspath(icon) if icon else None,
            pos=pos,
            size=size,
            splash_screen=splash_screen,
            title=title,
            url=url,
            **size_kw,
        )
        if close_window_to_exit:
            sys.exit()
    else:
        return run_cmd_args(
            (sys.executable, '-m', 'pyapp_window'),
            ('--title', title),
            ('--url', url),
            ('--pos', '{},{}'.format(*pos)),
            ('--size', size if isinstance(size, str) else '{}x{}'.format(*size)),
            ('--splash_screen', splash_screen),
            blocking=False,
            verbose=verbose,
        )
