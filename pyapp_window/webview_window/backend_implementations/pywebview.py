import typing as t

import webview  # pip install pywebview

from ._base import BaseApplication


class Application(BaseApplication):
    
    def __init__(
        self,
        title: str,
        url: str,
        size: t.Tuple[int, int] = (800, 600),
        pos: t.Optional[t.Tuple[int, int]] = None,
        **_
    ) -> None:
        super().__init__(title, url, size=size, pos=pos)
    
    def start(self) -> None:
        webview.create_window(
            self.title,
            self.url,
            width=self._size[0],
            height=self._size[1],
            x=self._pos[0],
            y=self._pos[1],
        )
        webview.start()
