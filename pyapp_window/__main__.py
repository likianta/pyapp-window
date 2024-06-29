from argsense import cli

from .webview_window import open_native_window


@cli.cmd()
def launch(
    title: str = 'My Application',
    url: str = None,
    port: int = None,
    size: str = '800:600'
) -> None:
    """
    kwargs:
        port (-p): if `url` is not specified but `port` is set, it will open a -
            localhost url.
        size (-s):
    """
    if url is None:
        assert port is not None
        url = f'http://localhost:{port}'
    elif not url.startswith('http'):
        url = 'http://' + url
    print(f'opening {url}')
    w, h = map(int, size.split(':'))
    open_native_window(title, url, size=(w, h), check_url=True)


if __name__ == '__main__':
    # pox -m pyapp_window -h
    cli.run(launch)
