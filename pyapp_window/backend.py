"""
FIXME: issue list:
    toga:
        - minimize then restore window, the size goes very small.
    webui2:
        - too slow to detect window close event
            (https://github.com/webui-dev/python-webui/issues/21)
        - the launcher icon is in low resolution.
    wxpython:
        ...
    kivy:
        ...
    chrome_appmode:
        - when close the window, will popup a new window with blank page.
        - requires that user PC has chrome installed.
    pywebview:
        - cannot set launch icon and window icon.
        - maybe crashed in older windows (caused by pythonnet, .NET etc.)
        - cannot show the window in macos when running in poetry venv.
    pyside6:
        - too heavy.
"""
import os
import sys
import typing as t


class T:
    Backend = t.Literal[
        'chrome_appmode',
        'pywebview',
        'toga',
        'webbrowser',
        'webui2',
    ]
    Position = t.Tuple[int, int]
    Size = t.Tuple[int, int]


def select_backend(
    prefer: t.Optional[T.Backend] = os.getenv('PYAPP_WINDOW_BACKEND', None)
) -> t.Callable:
    if prefer:
        backend = prefer
    else:
        if sys.platform == 'linux':
            try:
                import webui
                backend = 'webui2'
            except ImportError:
                backend = 'webbrowser'
        elif sys.platform == 'win32':
            backend = 'toga'
        else:
            try:
                import toga
                backend = 'toga'
            except ImportError:
                backend = 'webui2'
    print(backend)
    del prefer
    
    return {
        'chrome_appmode': open_with_chrome_appmode,
        'pywebview'     : open_with_pywebview,
        'toga'          : open_with_toga,
        'webbrowser'    : open_with_webbrowser,
        'webui2'        : open_with_webui2,
    }[backend]


# -----------------------------------------------------------------------------


def open_with_chrome_appmode(*_, **__):
    raise NotImplementedError


def open_with_pywebview(
    *,
    fullscreen: bool = False,
    pos: T.Position,
    size: T.Size,
    title: str,
    url: str,
    **_
) -> None:
    import webview  # pip install pywebview
    webview.create_window(
        title,
        url,
        x=pos[0],
        y=pos[1],
        width=size[0],
        height=size[1],
        fullscreen=fullscreen,
    )
    webview.start()


def open_with_toga(
    *,
    appid: str = 'dev.likianta.pyapp_window',
    fullscreen: bool = False,
    icon: str = None,
    pos: T.Position,
    size: T.Size,
    splash_screen: str = None,
    title: str,
    url: str,
    **_
) -> None:
    import toga
    from lk_utils import new_thread
    from toga.style.pack import CENTER, COLUMN, Pack
    from .util import wait_webpage_ready
    
    class MyApp(toga.App):
        _progress_bar: t.Optional[toga.ProgressBar]
        
        def __init__(self) -> None:
            super().__init__(formal_name=title, app_id=appid, icon=icon)
        
        # noinspection PyTypeChecker
        def startup(self) -> None:
            if splash_screen:
                img_width = round(size[0] * 0.8)
                h_padding = (size[0] - img_width) // 2
                print(size[0], img_width, h_padding, ':v')
                # view = toga.ImageView(
                #     toga.Image(splash_screen),
                #     style=Pack(
                #         alignment=CENTER,
                #         flex=1,
                #         padding_left=h_padding,
                #         padding_right=h_padding,
                #     )
                # )
                view = toga.Box(
                    children=(
                        toga.ImageView(
                            toga.Image(splash_screen),
                            style=Pack(
                                alignment=CENTER,
                                flex=1,
                                padding_left=h_padding,
                                padding_right=h_padding,
                            )
                        ),
                        # toga.ImageView(
                        #     toga.Image(xpath('loading_motion_blur_2.png')),
                        #     style=Pack(
                        #         alignment=CENTER,
                        #         # flex=1,
                        #         width=img_width,
                        #         padding_left=h_padding,
                        #         padding_right=h_padding,
                        #     )
                        # ),
                        bar := toga.ProgressBar(
                            max=None,
                            style=Pack(
                                alignment=CENTER,
                                # color='#E31B25',
                                # background_color='#E31B25',
                                padding_left=h_padding,
                                padding_right=h_padding,
                                padding_bottom=20,
                                width=img_width,
                            )
                        ),
                    ),
                    style=Pack(
                        direction=COLUMN
                    )
                )
                self._progress_bar = bar
                self._progress_bar.start()
                # TEST: if you want to test only splash screen, comment below
                #   line.
                self._wait_webpage_ready(url)
            else:
                view = toga.WebView(url=url)
                self._progress_bar = None
            self.main_window = toga.MainWindow(
                id='main', title=title, position=pos, size=size, content=view,
            )
            if fullscreen:
                self.main_window.full_screen = True
            self.main_window.show()
        
        @new_thread()
        def _wait_webpage_ready(self, url: str, timeout: float = 30) -> None:
            wait_webpage_ready(url, timeout)
            
            # don't update ui in non-main thread directly, instead, toga has
            # pre-set `self.loop` for this purpose.
            # https://stackoverflow.com/a/77350586/9695911
            def _replace_view() -> None:
                self._progress_bar.stop()
                self.main_window.content = toga.WebView(url=url)
            
            self.loop.call_soon_threadsafe(_replace_view)  # noqa
    
    app = MyApp()
    app.main_loop()


def open_with_webbrowser(
    *,
    url: str,
    **_
) -> None:
    import webbrowser
    webbrowser.open_new_tab(url)


# def open_with_wxpython(
#     *,
#     pos: T.Position,
#     size: T.Size,
#     title: str,
#     url: str,
#     **_
# ):
#     raise NotImplementedError


def open_with_webui2(
    *,
    icon: str = None,
    pos: T.Position,
    size: T.Size,
    title: str,
    url: str,
    **_
) -> None:
    """
    pros: webui2 is small and lightning fast.
    https://github.com/webui-dev/python-webui
    """
    from lk_utils import xpath
    from textwrap import dedent
    from webui import webui
    
    if icon:
        assert icon.endswith('.svg')
    else:
        icon = xpath('./favicon.svg')
    
    win = webui.window()
    html = dedent(
        '''
        <html>
        <head>
            <title>{title}</title>
            <link
                rel="icon"
                type="image/svg+xml"
                href="data:image/svg+xml,{svg}" />
        </head>
        <body>
            <iframe
                src="{target_url}"
                width="100%"
                height="100%"
                frameBorder="0"
            ></iframe>
        </body>
        '''.format(
            title=title,
            # https://stackoverflow.com/a/75832198
            svg=(
                open(icon, 'r').read()
                .replace('\n', ' ')
                .replace('"', "%22")
                .replace('#', '%23')
            ),
            target_url=url,
        )
    )
    # print(html, ':v')
    win.set_position(pos[0], pos[1])
    win.set_size(size[0], size[1])
    
    # print(win.get_parent_process_id(), win.get_child_process_id(), ':v')
    # pid = win.get_child_process_id()
    win.show(html)  # blocking
    
    # webui.wait()
    # while win.is_shown() and webui.is_app_running():
    #     sleep(1)
    # print(win.get_parent_process_id(), win.get_child_process_id(), ':v')
    # print('[red dim]webui window closed[/]', ':vr')
