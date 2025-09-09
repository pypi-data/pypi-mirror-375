import asyncio
import os
import tempfile
import threading
import urllib
import urllib.request

import pystray
from PIL import Image

from leaguewizard.core import start


def to_tray():
    dest = f"{tempfile.gettempdir()}\\logo.png"
    urllib.request.urlretrieve(
        "https://github.com/amburgao/leaguewizard/blob/main/.github/images/logo.png?raw=true",
        dest,
    )
    return pystray.Icon(
        (0, 0),
        icon=Image.open(dest),
        menu=pystray.Menu(pystray.MenuItem("Exit", lambda icon, item: os._exit(0))),
    )


def main() -> None:
    tray = to_tray()
    tray_thread = threading.Thread(target=tray.run, daemon=True)
    tray_thread.start()

    asyncio.run(start())
    tray.stop()


if __name__ == "__main__":
    main()
