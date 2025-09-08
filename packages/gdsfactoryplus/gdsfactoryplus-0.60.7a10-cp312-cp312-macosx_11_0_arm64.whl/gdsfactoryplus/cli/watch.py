"""GDSFactory+ File Watcher."""

from __future__ import annotations

import os

from .app import app

__all__ = ["watch"]


@app.command()
def watch(path: str, server_url: str = "") -> None:
    """Watch a folder for changes.

    Args:
        path: Path to the folder.
        server_url: URL of the GDSFactory+ server.
    """
    import gdsfactoryplus.core.watch as watcher

    if not server_url:
        server_url = os.environ.get("SERVER_URL", "")

    if not server_url:
        host = os.environ.get("GFP_KWEB_HOST", "localhost")
        if os.environ.get("GFP_KWEB_HTTPS", "false") == "true":
            server_url = f"https://{host}"
        else:
            server_url = f"http://{host}:8787"
    return watcher.watch(path, server_url)
