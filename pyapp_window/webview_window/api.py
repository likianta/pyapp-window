import typing as t

import sys


def open_native_window(
    title: str,
    url: str,
    size: t.Tuple[int, int] = (800, 600),
    check_url: bool = False,
    backend_engine: str = 'auto',
    **kwargs
) -> int:
    """
    returns: 0 for one-off process, 1 for consistent running process.
    """
    if check_url:
        from .util import wait_webpage_ready
        wait_webpage_ready(url)
    
    if backend_engine == 'auto':
        if sys.platform == 'linux':
            backend_engine = 'webbrowser'
        else:
            try:
                import toga
            except ImportError:
                backend_engine = 'chrome_appmode'
            else:
                backend_engine = 'toga'
        print(backend_engine)
    else:
        if sys.platform == 'linux':
            assert backend_engine == 'webbrowser'
    
    if backend_engine == 'chrome_appmode':
        from .backend_implementations.chrome_appmode import Application
        app = Application(title, url, size=size, **kwargs)
        app.start()
        return 1
    elif backend_engine == 'toga':
        from .backend_implementations.toga import Application
        app = Application(title, url, size=size, **kwargs)
        app.start()
        return 1
    elif backend_engine == 'webbrowser':
        from .backend_implementations.webbrowser import Application
        app = Application(title, url, size=size, **kwargs)
        app.start()
        return 0
    else:
        raise NotImplementedError(backend_engine)
