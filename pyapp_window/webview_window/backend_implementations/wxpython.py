"""
TODO: refactor based on `._base.BaseApplication`
"""

import typing as t

import wx  # noqa
from wx.html2 import WebView  # noqa

from ..util import wait_webpage_ready


class MyFrame(wx.Frame):
    """
    https://realpython.com/python-gui-with-wxpython/
    """
    
    def __init__(
        self,
        title: str,
        url: str,
        size: t.Tuple[int, int] = (800, 600),
        **_
    ):
        super().__init__(parent=None, title=title)
        self._view = WebView.New(self)
        self._view.LoadURL(url)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._view, 1, wx.EXPAND, 10)
        self.SetSizer(sizer)
        self.SetSize(size)
        self.Show()


def open_native_window(
    title: str,
    url: str,
    size: t.Tuple[int, int] = (800, 600),
    check_url: bool = False,
    **kwargs
) -> None:
    if check_url:
        wait_webpage_ready(url)
    app = wx.App()
    frame = MyFrame(title, url, size, **kwargs)
    app.MainLoop()
