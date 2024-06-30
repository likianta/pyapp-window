from argsense import cli

from .opener import open_window


@cli.cmd()
def launch(
    title: str = 'Pyapp Window',
    url: str = None,
    host: str = None,
    port: int = None,
    pos: str = 'center',
    size: str = '800:600',
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
    )


if __name__ == '__main__':
    # pox -m pyapp_window -h
    cli.run(launch)
