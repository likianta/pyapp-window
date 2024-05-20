import typing as t

import toga  # noqa

from ._base import BaseApplication


# noinspection PyUnresolvedReferences
class Application(BaseApplication, toga.App):
    main_window: toga.MainWindow
    _view: toga.WebView
    
    def __init__(
        self,
        title: str,
        url: str,
        *,
        size: t.Tuple[int, int] = (800, 600),
        pos: t.Optional[t.Tuple[int, int]] = None,
        **kwargs
    ) -> None:
        BaseApplication.__init__(
            self, title, url, size=size, pos=pos
        )
        toga.App.__init__(
            self,
            formal_name=title,
            app_id=kwargs.get('appid', 'dev.likianta.pyapp_window'),
            icon=kwargs.get('icon', None),
        )
    
    # override BaseApplication
    def start(self) -> None:
        self.main_loop()
    
    # override toga.App
    def startup(self) -> None:
        # noinspection PyTypeChecker
        self.main_window = toga.MainWindow(
            title=self.formal_name,
            size=self._size,
            position=self._pos,
        )
        self._view = toga.WebView(
            url=self.url,
            on_webview_load=lambda _: print('webview loaded', self.url),
        )
        self.main_window.content = self._view
        self.main_window.show()
