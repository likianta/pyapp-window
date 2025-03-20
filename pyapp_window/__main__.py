import re

from argsense import cli

from .opener import open_window


@cli.cmd()
def launch(
    # primary params
    url: str = None,
    port: int = None,
    # secondary params
    backend: str = None,
    host: str = None,
    icon: str = None,
    pos: str = 'center',
    size: str = '1600x1200',
    title: str = 'PyApp Window',
) -> None:
    """
    kwargs:
        title (-t):
        url (-u):
        port (-p):
            if `url` is not specified but `port` is set, it will open a -
            localhost url.
        pos:
            - "center": in the screen center.
            - `<x>,<y>`, e.g. "100,200".
                you can use negative values to indicate "right/bottom -
                margin to the edge of screen".
                if x/y values are larger than screen size, it will be auto -
                transformed to 10px to the edge of screen.
            - `<x>,center` or `center,<y>`, e.g. "100,center".
        size (-s):
            format: `<width>x<height>`, e.g. "1600x1200".
        icon (-i): if given, must be ".ico" type.
    """
    assert url or port, 'either `url` or `port` must be set.'
    if ':' in pos or ',' in pos:
        x, y = map(int, re.split(r'[:,]', pos))
        pos = (x, y)
    if ':' in size or 'x' in size:
        w, h = map(int, re.split(r'[:x]', size))
        size = (w, h)
    open_window(
        title,
        url,
        icon=icon,
        host=host,
        port=port,
        pos=pos,
        size=size,
        blocking=True,
        verbose=False,
        backend=backend,
    )


if __name__ == '__main__':
    # pox -m pyapp_window -h
    # pox -m pyapp_window -p 2030 -s 1300x1700
    cli.run(launch)
