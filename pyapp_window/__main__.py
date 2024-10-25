from argsense import cli

from .opener import open_window


@cli.cmd()
def launch(
    # main params
    url: str = None,
    port: int = None,
    # secondary params
    host: str = None,
    size: str = '1600:1200',
    title: str = 'Pyapp Window',
    pos: str = 'center',
    backend: str = None,
) -> None:
    """
    kwargs:
        port (-p): if `url` is not specified but `port` is set, it will open a -
            localhost url.
        size (-s):
    """
    assert url or port, 'either `url` or `port` must be set.'
    if ':' in pos:
        x, y = map(int, pos.split(':'))
        pos = (x, y)
    if ':' in size:
        w, h = map(int, size.split(':'))
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
    cli.run(launch)
