import subprocess
from typing import Any
from urllib.parse import quote

def download_file(url: str, dest: str, filename: str, headers: dict[str, str] = {}) -> None:
    url_scheme: str = f"motrix://new-task?uri={quote(url)}&out={quote(filename)}&dir={quote(dest)}&silent=true"
    subprocess.run(["open", url_scheme])