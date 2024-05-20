"""
ref: https://github.com/mhils/native_web_app/blob/master/native_web_app.py
"""
import shutil
import subprocess as sp
import typing as t
import webbrowser

import sys

from ._base import BaseApplication


class Application(BaseApplication):
    
    def __init__(
        self,
        title: str,
        url: str,
        *,
        size: t.Tuple[int, int] = (800, 600),
        pos: t.Optional[t.Tuple[int, int]] = None,
        icon: str = None,
    ) -> None:
        super().__init__(title, url, size=size, pos=pos)
        self._favicon = icon  # TODO
    
    def start(self) -> None:
        if exe := find_executable():
            # TODO: more flags
            #   --app-auto-launched
            #   --app-id
            #   --app-shell-host-window-size
            #   --ash-host-window-bounds=100+300-800x600
            #                             x   y   w   h
            #   --auto-accept-camera-and-microphone-capture
            #   --force-dark-mode
            #   --headless
            #   --hide-scrollbars
            #   --install-chrome-app
            #   --no-experiments
            #   --no-startup-window
            #       something like tray mode
            #   --single-process
            #   --start-maximized
            #   --trusted-download-sources
            proc = sp.Popen(
                (
                    exe,
                    '--app={}'.format(self.url),
                    '--window-size={}'.format(','.join(map(str, self._size))),
                    '--window-position={}'.format(','.join(map(str, self._pos))),
                    '--ash-no-nudges',  # do not show first-run dialog. if -
                    #   disable this flag, chrome may occcasionally show `set -
                    #   chrome as default browser`, `send anonymous feedbacks -
                    #   to google for analysis` in app startup.
                    '--no-crash-upload',
                    '--no-default-browser-check',
                    '--no-first-run',  # don't show "what's new"
                ),
                close_fds=True,
                start_new_session=True,
            )
            if proc.poll() is None:  # means worked
                return
        # fallback to stdlib webbrowser
        webbrowser.open_new_tab(self.url)


def find_executable() -> t.Optional[str]:
    is_win = sys.platform == 'win32'
    # noinspection PyTypeChecker
    possible_names: t.Iterator[str] = filter(None, (
        sys.platform == 'darwin' and
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        sys.platform == 'win32' and 'msedge',
        'chrome',
        'google-chrome',
        'google-chrome-stable',
        'chromium',
        'chromium-browser',
    ))
    for name in possible_names:
        if x := shutil.which(name):
            return x
        if is_win and (x := _find_in_registry(name)):
            return x
    return None


def _find_in_registry(browser_name: str) -> t.Optional[str]:
    import winreg  # this only available on windows
    try:
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths',
                0,
                winreg.KEY_READ
            ) as key:
                return winreg.QueryValue(key, browser_name + '.exe')
        except FileNotFoundError:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths',
                0,
                winreg.KEY_READ
            ) as key:
                return winreg.QueryValue(key, browser_name + '.exe')
    except OSError:
        return None
