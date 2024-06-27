# PyApp Window

A general-purpose native window launcher for a given url.

## Install

```sh
pip install pyapp-window
```

## Usage

Use in terminal:

```sh
py -m pyapp_window -h
py -m pyapp_window http://localhost:3001
```

Use in script:

```py
import sys
import pyapp_window
from lk_utils import run_cmd_args

# get a popen object
port = 3001
proc = run_cmd_args(
    sys.executable, '-m', 'streamlit', 'run', your_target_script,
    '--browser.gatherUsageStats', 'false',
    '--global.developmentMode', 'false',
    '--server.headless', 'true',
    '--server.port', port,
    blocking=False,
    verbose=True,
)


pyapp_window.launch(
    'Example App',
    url=f'http://localhost:{port}',
    copilot_backend=proc,
    size=(800, 600),
)
```
