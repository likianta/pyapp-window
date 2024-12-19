import re

from argsense import cli

from .opener import open_window


@cli.cmd()
def launch(
    # main params
    url: str = None,
    port: int = None,
    # secondary params
    host: str = None,
    size: str = '1600x1200',
    title: str = 'PyApp Window',
    pos: str = 'center',
    backend: str = None,
) -> None:
    """
    kwargs:
        port (-p):
            if `url` is not specified but `port` is set, it will open a -
            localhost url.
        size (-s):
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
