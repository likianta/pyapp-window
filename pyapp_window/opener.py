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
    AnyPos = T1.Position0
    AnySize = T1.Size0
    Backend = T0.Backend
    Geometry = t.TypedDict('Geometry', {
        'pos': t.Tuple[int, int],
        'size': t.Tuple[int, int],
        'maximized': bool,
        'fullscreen': bool,
    })


def open_window(
    title: str = 'PyApp Window',
    url: str = None,
    icon: str = None,
    host: str = None,
    port: int = None,
    pos: T.AnyPos = 'center',
    size: T.AnySize = (1200, 900),
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
    
    geometry: T.Geometry = {
        'pos': (0, 0),
        'size': (0, 0),
        'maximized': size == 'maximized',
        'fullscreen': size == 'fullscreen',
    }
    if backend == 'terminal':
        if isinstance(size, str):
            geometry['size'] = {
                'fullscreen': (160, 60),
                'maximized' : (160, 60),
                'large'     : (160, 60),
                'medium'    : (120, 40),
                'small'     : (80, 24),
            }[size]
        else:
            assert (
                isinstance(size, tuple) and
                isinstance(size[0], int) and
                isinstance(size[1], int)
            )
            geometry['size'] = size  # type: ignore
    else:
        geometry['size'] = normalize_size(size)
    assert geometry['size']
    geometry['pos'] = normalize_position(pos, geometry['size'])
    del pos, size
    print('finalize window geometry', geometry['pos'], geometry['size'])
    
    if check_url and not splash_screen:
        assert url
        wait_webpage_ready(url)
    
    if blocking:
        select_backend(prefer=backend)(
            icon=fs.abspath(icon) if icon else None,
            splash_screen=splash_screen,
            title=title,
            url=url,
            **geometry,
        )
        if close_window_to_exit:
            sys.exit()
    else:
        return t.cast(t.Optional[Popen], run_cmd_args(
            (sys.executable, '-m', 'pyapp_window'),
            ('--title', title),
            ('--url', url),
            ('--pos', '{},{}'.format(*geometry['pos'])),
            ('--size', (
                'fullscreen' if geometry['fullscreen'] else
                'maximized' if geometry['maximized'] else
                '{}x{}'.format(*geometry['size'])
            )),
            ('--splash_screen', splash_screen),
            blocking=False,
            verbose=verbose,
        ))
