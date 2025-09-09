import asyncio
import os
import threading

import pystray
from PIL import Image

from buildwizard.core import start


def to_tray():
    return pystray.Icon(
        (0, 0),
        icon=Image.open("logo.png"),
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
