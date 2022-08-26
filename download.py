import json
import os
from pathlib import Path


class Tracer:

    def trace(self, _):
        pass


def download_attachment(url, name):
    try:
        from full_offline_backup_for_todoist.url_downloader import TodoistAuthURLDownloader
    except ModuleNotFoundError:
        print("Not downloading attachment because full_offline_backup_for_todoist not installed")
        return False

    with open("creds.json") as f:
        creds = json.load(f)

    downloader = TodoistAuthURLDownloader(Tracer(), creds["email"], creds["password"])

    os.makedirs("attachments", exist_ok=True)
    with open(Path("attachments") / name, "wb") as f:
        contents = downloader.get(url)
        f.write(contents)

    return True
