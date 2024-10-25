if 1:
    import os
    if 'HTTP_PROXY' not in os.environ:
        # see `.util.wait_webpage_ready : r = requests.head(url)`
        os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
        os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

from .opener import open_window
from .util import get_screen_size
from .util import wait_webpage_ready

__version__ = '2.1.0'
