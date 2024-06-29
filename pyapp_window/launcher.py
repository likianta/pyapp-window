import sys
import typing as t
from multiprocessing import Process
from subprocess import Popen
from threading import Thread
from time import sleep

import psutil
from lk_utils import run_cmd_args

from .process import ProcessWrapper
from .webview_window import open_native_window


def launch(
    title: str,
    url: str,
    copilot_backend: t.Union[
        Popen, Process, Thread, t.Callable[[], t.Any]
    ] = None,
    wait_url_ready: bool = False,
    **kwargs
) -> None:
    print(copilot_backend, ':v')
    if copilot_backend:
        proc_back = ProcessWrapper(
            copilot_backend
            if isinstance(copilot_backend, (Popen, Process, Thread))
            else Process(target=copilot_backend, daemon=True)
        )
        # print('start backend', ':v')
        proc_back.start()
        
        proc_front = ProcessWrapper(
            Process(
                target=open_native_window,
                kwargs={
                    'title'    : title,
                    'url'      : url,
                    'check_url': wait_url_ready,
                    **kwargs
                },
                daemon=True
            )
        )
        # print('start frontend', ':v')
        proc_front.start()
        
        while True:
            if not proc_front.alive:
                print('frontend closed', ':vsp')
                proc_back.close()
                break
            if not proc_back.alive:
                print('backend shutdown', ':vsp')
                proc_front.close()
                break
            sleep(1)
    else:
        open_native_window(title=title, url=url, **kwargs)
    
    print('exit program', ':v4sp')


# -----------------------------------------------------------------------------

class Window:
    def __init__(self, popen_proc: Popen) -> None:
        self._proc = popen_proc
    
    def close(self) -> None:
        pid = self._proc.pid
        parent = psutil.Process(pid)
        # print('kill process [{}] {}'.format(pid, parent.name()), ':v4s')
        for child in parent.children(recursive=True):
            # print('    |- kill [{}] {}'.format(
            #     child.pid, child.name()), ':v4s')
            child.kill()
        parent.kill()
        print(':p', 'window is closed')


def open_widow(
    title: str,
    url: str,
    *,
    size: t.Tuple[int, int] = (800, 600),
    blocking: bool = True,
    verbose: bool = False,
) -> t.Optional[Window]:
    if blocking:
        open_native_window(title=title, url=url, size=size)
    return Window(run_cmd_args(
        (sys.executable, '-m', 'pyapp_window', title, url),
        ('--size', '{}:{}'.format(*size)),
        blocking=False,
        verbose=verbose,
    ))
