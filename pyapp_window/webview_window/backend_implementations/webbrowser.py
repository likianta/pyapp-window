import webbrowser

from ._base import BaseApplication


class Application(BaseApplication):
    
    def start(self) -> None:
        webbrowser.open_new_tab(self.url)
